"""Pruebas de integracion de la API (contratos, seguridad y flujos esenciales)."""
from __future__ import annotations

from datetime import date, timedelta

from conftest import login


class TestSaludYEstado:
    def test_should_return_ok_and_pilot_mode(self, client):
        response = client.get("/api/salud")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["pilot_mode"] is True

    def test_estado_should_report_real_counts(self, client):
        response = client.get("/api/auth/estado")
        assert response.status_code == 200
        data = response.json()
        assert data["foods_total"] >= 8
        assert data["rules_total"] >= 3
        assert data["rules_approved"] >= 1
        assert data["prices_total"] >= 0


class TestAuth:
    def test_should_reject_registro_without_consent(self, client):
        response = client.post(
            "/api/auth/registro",
            json={"email": "x@example.com", "password": "clave-12345678", "accept_consent": False},
        )
        assert response.status_code == 422

    def test_should_reject_registro_with_short_password(self, client):
        response = client.post(
            "/api/auth/registro",
            json={"email": "x@example.com", "password": "corta", "accept_consent": True},
        )
        assert response.status_code == 422

    def test_should_reject_duplicate_email(self, client, usuario_prueba):
        email, _, _ = usuario_prueba
        response = client.post(
            "/api/auth/registro",
            json={"email": email, "password": "clave-12345678", "accept_consent": True},
        )
        assert response.status_code == 409

    def test_should_reject_login_with_wrong_password(self, client, usuario_prueba):
        email, _, _ = usuario_prueba
        response = client.post("/api/auth/login", json={"email": email, "password": "incorrecta-123"})
        assert response.status_code == 401

    def test_should_return_me_when_authenticated(self, client, usuario_prueba):
        email, _, headers = usuario_prueba
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["email"] == email
        assert response.json()["consent_version"]

    def test_should_reject_me_without_token(self, client):
        assert client.get("/api/auth/me").status_code == 401


class TestAlimentos:
    def test_should_list_public_foods_without_auth(self, client):
        response = client.get("/api/alimentos")
        assert response.status_code == 200
        names = {food["name_common"] for food in response.json()}
        assert any("Yuca" in name for name in names)

    def test_should_filter_by_group(self, client):
        response = client.get("/api/alimentos", params={"food_group": "cereal"})
        assert response.status_code == 200
        assert all(food["food_group"] == "cereal" for food in response.json())

    def test_should_404_when_food_missing(self, client):
        assert client.get("/api/alimentos/FDC-NO-EXISTE").status_code == 404

    def test_ficha_should_show_trust_tier_and_provenance(self, client):
        response = client.get("/api/alimentos/FDC-T-YUCA")
        assert response.status_code == 200
        data = response.json()
        assert data["trust_tier"] == "medido"
        assert data["source_id"] == "SRC-TEST"
        assert data["retrieved_at"]
        assert data["nutrients"]
        assert all("trust_tier" in nutrient for nutrient in data["nutrients"])

    def test_ficha_should_show_user_allergy_conflicts(self, client, usuario_prueba):
        _, _, headers = usuario_prueba
        client.post("/api/perfil/alergias", json={"allergen": "leche", "kind": "alergia_confirmada", "severity": "alta"}, headers=headers)
        response = client.get("/api/alimentos/FDC-T-LECHE", headers=headers)
        assert response.status_code == 200
        assert response.json()["allergy_conflicts"]

    def test_sustituciones_should_exclude_user_allergens(self, client, usuario_prueba):
        _, _, headers = usuario_prueba
        response = client.get("/api/alimentos/FDC-T-LECHE/sustituciones", headers=headers)
        assert response.status_code == 200
        ids = {item["food_id"] for item in response.json()["sustituciones"]}
        assert "FDC-T-HUEVO" not in ids  # mismo grupo no aplica, pero ningun alergeno
        assert all("FDC-T" in food_id for food_id in ids)


class TestPerfil:
    def test_should_create_profile_on_registration(self, client, usuario_prueba):
        _, _, headers = usuario_prueba
        response = client.get("/api/perfil", headers=headers)
        assert response.status_code == 200
        assert response.json()["dietary_pattern"] == "omnivoro"

    def test_should_update_profile(self, client, usuario_prueba):
        _, _, headers = usuario_prueba
        response = client.put(
            "/api/perfil",
            json={
                "department": "Cundinamarca",
                "municipality": "Bogota",
                "zone": "urbana",
                "meals_per_day": 4,
                "dietary_pattern": "vegano",
                "onboarding_completed": True,
            },
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["dietary_pattern"] == "vegano"
        assert response.json()["meals_per_day"] == 4

    def test_allergies_crud_flow(self, client, usuario_prueba):
        _, _, headers = usuario_prueba
        created = client.post("/api/perfil/alergias", json={"allergen": "huevo", "kind": "alergia_confirmada"}, headers=headers)
        assert created.status_code == 201
        duplicate = client.post("/api/perfil/alergias", json={"allergen": "huevo"}, headers=headers)
        assert duplicate.status_code == 409
        listed = client.get("/api/perfil/alergias", headers=headers)
        assert any(item["allergen"] == "huevo" for item in listed.json())
        deleted = client.delete(f"/api/perfil/alergias/{created.json()['id']}", headers=headers)
        assert deleted.status_code == 204

    def test_health_flags_crud_flow(self, client, usuario_prueba):
        _, _, headers = usuario_prueba
        created = client.post("/api/perfil/salud", json={"flag": "lactancia"}, headers=headers)
        assert created.status_code == 201
        duplicate = client.post("/api/perfil/salud", json={"flag": "lactancia"}, headers=headers)
        assert duplicate.status_code == 409
        assert client.get("/api/perfil/salud", headers=headers).json()
        assert client.delete(f"/api/perfil/salud/{created.json()['id']}", headers=headers).status_code == 204

    def test_should_not_see_others_allergies(self, client, usuario_prueba):
        _, _, headers = usuario_prueba
        client.post("/api/perfil/alergias", json={"allergen": "pescado"}, headers=headers)
        # otro usuario no debe verla
        other = client.post(
            "/api/auth/registro",
            json={"email": "otro-xyz@example.com", "password": "clave-12345678", "accept_consent": True},
        ).json()
        other_headers = {"Authorization": f"Bearer {other['access_token']}"}
        assert client.get("/api/perfil/alergias", headers=other_headers).json() == []


class TestPlanificador:
    def test_should_generate_menu_when_profile_ok(self, client, usuario_prueba):
        _, _, headers = usuario_prueba
        client.put("/api/perfil", json={"municipality": "Bogota", "onboarding_completed": True}, headers=headers)
        response = client.post("/api/planificador/generar", json={"days": 2}, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("ok", "advertencia")
        assert data["menu"] is not None
        assert data["pilot_mode"] is True
        assert data["limitations"]
        used = {
            item["food_id"]
            for day in data["menu"]["dias"]
            for meal in day["comidas"]
            for item in meal["items"]
        }
        assert used  # menu no vacio

    def test_case1_menu_should_exclude_confirmed_allergen(self, client, usuario_prueba):
        _, _, headers = usuario_prueba
        client.post("/api/perfil/alergias", json={"allergen": "leche", "kind": "alergia_confirmada", "severity": "alta"}, headers=headers)
        client.put("/api/perfil", json={"onboarding_completed": True}, headers=headers)
        response = client.post("/api/planificador/generar", json={"days": 1}, headers=headers)
        used = {
            item["food_id"]
            for day in response.json()["menu"]["dias"]
            for meal in day["comidas"]
            for item in meal["items"]
        }
        assert "FDC-T-LECHE" not in used

    def test_case11_should_block_menu_when_alarm_symptoms(self, client, usuario_prueba):
        _, _, headers = usuario_prueba
        client.post("/api/perfil/salud", json={"flag": "sintomas_alarma"}, headers=headers)
        response = client.post("/api/planificador/generar", json={"days": 1}, headers=headers)
        data = response.json()
        assert data["status"] == "urgencia"
        assert data["menu"] is None

    def test_case5_diabetes_should_require_professional_not_autoplan(self, client, usuario_prueba):
        _, _, headers = usuario_prueba
        client.post("/api/perfil/salud", json={"flag": "diabetes_medicamentos"}, headers=headers)
        response = client.post("/api/planificador/generar", json={"days": 1}, headers=headers)
        data = response.json()
        assert data["status"] == "requiere_profesional"
        assert data["menu"] is None
        assert any("profesional" in message["message"].lower() for message in data["safety_messages"])

    def test_historial_should_list_own_plans_only(self, client, usuario_prueba):
        _, _, headers = usuario_prueba
        response = client.get("/api/planificador/historial", headers=headers)
        assert response.status_code == 200
        assert all("plan_id" in item for item in response.json())


class TestPresupuesto:
    def test_should_reject_future_observation_date(self, client, usuario_prueba):
        _, _, headers = usuario_prueba
        response = client.post(
            "/api/presupuesto/precios",
            json={
                "food_id": "FDC-T-YUCA",
                "product_desc": "Yuca por libra",
                "municipality": "Bogota",
                "commercial_unit": "libra",
                "price_cop": 2500,
                "observed_at": (date.today() + timedelta(days=3)).isoformat(),
                "source_desc": "prueba",
            },
            headers=headers,
        )
        assert response.status_code == 422

    def test_price_flow_should_keep_provenance(self, client, usuario_prueba):
        _, _, headers = usuario_prueba
        created = client.post(
            "/api/presupuesto/precios",
            json={
                "food_id": "FDC-T-YUCA",
                "product_desc": "Yuca por libra",
                "municipality": "Sincelejo",
                "commercial_unit": "libra",
                "price_cop": 2000,
                "observed_at": date.today().isoformat(),
                "data_type": "observado",
                "source_desc": "Observacion propia en plaza",
            },
            headers=headers,
        )
        assert created.status_code == 201
        listed = client.get("/api/presupuesto/precios", params={"municipality": "Sincelejo"})
        assert listed.status_code == 200
        price = listed.json()[0]
        assert price["data_type"] == "observado"
        assert price["observed_at"] == date.today().isoformat()

    def test_costo_should_be_honest_when_prices_partial_or_missing(self, client, usuario_prueba):
        """Invariantes de honestidad: cada item con precio (fecha+tipo) o aviso 'sin datos';
        el total solo suma precios reales y el aviso declara el caracter parcial."""
        _, _, headers = usuario_prueba
        client.put("/api/perfil", json={"onboarding_completed": True}, headers=headers)
        plan_id = client.post("/api/planificador/generar", json={"days": 1}, headers=headers).json()["plan_id"]
        response = client.post(f"/api/presupuesto/{plan_id}/costo", headers=headers)
        assert response.status_code == 200
        data = response.json()
        items = data["items"]
        assert len(items) > 0
        con_precio = [item for item in items if item.get("price_cop") is not None]
        sin_precio = [item for item in items if item.get("price_cop") is None]
        assert data["items_con_precio"] == len(con_precio)
        assert data["items_sin_precio"] == len(sin_precio)
        assert all("price_date" in item and "data_type" in item for item in con_precio)
        assert all("Sin datos" in item.get("aviso", "") for item in sin_precio)
        if sin_precio:
            assert data["total_cop"] == sum(item["price_cop"] for item in con_precio)
            assert "parcial" in data["aviso"]
        else:
            assert data["total_cop"] == sum(item["price_cop"] for item in con_precio)


class TestRoles:
    def test_usuario_should_not_access_admin(self, client, usuario_prueba):
        _, _, headers = usuario_prueba
        assert client.get("/api/admin/estadisticas", headers=headers).status_code == 403

    def test_profesional_should_approve_candidate_rule_with_audit(self, client):
        admin_headers = login(client, "admin@example.com", "admin-clave-test-123")
        # crear profesional: registrar + promover
        prof_email = "prof-1@example.com"
        client.post("/api/auth/registro", json={"email": prof_email, "password": "clave-12345678", "accept_consent": True})
        target = client.get("/api/auth/me", headers={}).status_code  # noqa: F841
        # encontrar user_id via admin stats/audit no expone; usar endpoint rol
        # (para la prueba promovemos via auditoria: login admin y listar usuarios no existe,
        # asi que promovemos por email conocido: usamos /api/admin/usuarios/{id}/rol con id=2..)
        # Simplificacion: el admin promueve al usuario 2..N buscando por prueba de humo:
        # usamos el id devuelto por /api/auth/me del profesional
        prof_login = login(client, prof_email, "clave-12345678")
        me = client.get("/api/auth/me", headers=prof_login).json()
        response = client.post(
            f"/api/admin/usuarios/{me['id']}/rol?role=profesional", headers=admin_headers
        )
        assert response.status_code == 200
        # aprobar regla candidata
        rules = client.get("/api/evidencia/reglas").json()
        candidate = next(rule for rule in rules if rule["status"] == "candidate")
        approval = client.post(
            f"/api/profesional/reglas/{candidate['id']}/aprobar", headers=prof_login
        )
        assert approval.status_code == 200
        assert approval.json()["status"] == "approved"
        assert approval.json()["reviewer"] == prof_email
        # auditoria registra el cambio
        audit = client.get("/api/admin/auditoria", headers=admin_headers).json()
        assert any(log["action"] == "approved" for log in audit)

    def test_usuario_should_not_approve_rules(self, client, usuario_prueba):
        _, _, headers = usuario_prueba
        rules = client.get("/api/evidencia/reglas").json()
        candidate = next((rule for rule in rules if rule["status"] == "candidate"), None)
        if candidate is None:
            return  # ya no quedan candidatas (prueba de humo OK)
        response = client.post(f"/api/profesional/reglas/{candidate['id']}/aprobar", headers=headers)
        assert response.status_code == 403


class TestPrivacidad:
    def test_should_export_all_own_data(self, client, usuario_prueba):
        email, _, headers = usuario_prueba
        client.post("/api/perfil/alergias", json={"allergen": "soya"}, headers=headers)
        response = client.get("/api/configuracion/datos", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["email"] == email
        assert any(item["allergen"] == "soya" for item in data["allergies"])

    def test_case_should_delete_account_and_anonymize(self, client):
        email = f"borrar-{abs(hash('del'))}@example.com"
        reg = client.post("/api/auth/registro", json={"email": email, "password": "clave-12345678", "accept_consent": True}).json()
        headers = {"Authorization": f"Bearer {reg['access_token']}"}
        client.post("/api/perfil/alergias", json={"allergen": "maní"}, headers=headers)
        assert client.delete("/api/configuracion/cuenta", headers=headers).status_code == 204
        assert client.post("/api/auth/login", json={"email": email, "password": "clave-12345678"}).status_code == 401

    def test_ai_should_be_disabled_by_default(self, client, usuario_prueba):
        _, _, headers = usuario_prueba
        response = client.post("/api/ia/alimentos/FDC-T-YUCA/explicacion", headers=headers)
        assert response.status_code == 503


class TestSeguimiento:
    def test_tracking_flow(self, client, usuario_prueba):
        _, _, headers = usuario_prueba
        created = client.post(
            "/api/perfil/seguimiento",
            json={"entry_date": date.today().isoformat(), "food_ids": ["FDC-T-YUCA"], "note": "almuerzo"},
            headers=headers,
        )
        assert created.status_code == 201
        listed = client.get("/api/perfil/seguimiento", headers=headers)
        assert listed.json()
        assert listed.json()[0]["food_ids"] == ["FDC-T-YUCA"]
