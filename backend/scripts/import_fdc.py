"""Importador reproducible: USDA FDC crudo -> catalogo normalizado + informe.

Pipeline (Fase 2):
    raw/<slug>.json  (fetch_fdc.py)  ->  normalized.json  +  quality_report.md
    -> app/seed.py carga normalized.json en la base de datos.

Reglas de la importacion (ADR-0005, ADR-0006):
- derivationCode 'A' (analitico)            -> trust_tier=medido
- derivationCode 'Z' (valor asumido cero)   -> SE OMITE (dato ausente, no cero)
- cualquier otra derivacion (calculado/     -> trust_tier=estimado con metodo
  imputado/tomado de otra fuente)
- Todo valor fuera de rango plausible       -> rechazado con nota (no se corrige)
"""
from __future__ import annotations

import json
import sys
from datetime import UTC, date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FDC_DIR = ROOT / "data" / "imports" / "fdc"
RAW_DIR = FDC_DIR / "raw"
MANIFEST = FDC_DIR / "manifest.json"
NORMALIZED = FDC_DIR / "normalized.json"
REPORT = FDC_DIR / "quality_report.md"

# fdcId -> (clave canonica del proyecto, unidad)
NUTRIENT_MAP = {
    1008: ("energia", "kcal"),
    1003: ("proteina", "g"),
    1004: ("grasa_total", "g"),
    1005: ("carbohidratos", "g"),
    2000: ("azucares", "g"),
    1079: ("fibra", "g"),
    1087: ("calcio", "mg"),
    1089: ("hierro", "mg"),
    1090: ("magnesio", "mg"),
    1091: ("fosforo", "mg"),
    1092: ("potasio", "mg"),
    1093: ("sodio", "mg"),
    1095: ("zinc", "mg"),
    1162: ("vitamina_c", "mg"),
    1165: ("tiamina", "mg"),
    1166: ("riboflavina", "mg"),
    1167: ("niacina", "mg"),
    1175: ("vitamina_b6", "mg"),
    1177: ("folato", "ug"),
    1106: ("vitamina_a_rae", "ug"),
    1109: ("vitamina_e", "mg"),
    1185: ("vitamina_k", "ug"),
    1178: ("vitamina_b12", "ug"),
    1258: ("grasas_saturadas", "g"),
    1292: ("grasas_monoinsaturadas", "g"),
    1293: ("grasas_poliinsaturadas", "g"),
    1253: ("colesterol", "mg"),
    1051: ("agua", "g"),
    2047: ("energia", "kcal"),  # Atwater general (alimentos Foundation)
}

RANGE_CHECKS = {  # valores maximos plausibles por 100 g
    "energia": (0, 900),
    "proteina": (0, 95),
    "grasa_total": (0, 100),
    "carbohidratos": (0, 100),
    "fibra": (0, 85),
    "azucares": (0, 100),
    "calcio": (0, 2500),
    "hierro": (0, 100),
    "sodio": (0, 10000),
    "potasio": (0, 3500),
    "colesterol": (0, 5000),
    "grasas_saturadas": (0, 100),
}

# Curaduria editorial del proyecto (SIEMPRE marcada educativo/unverified):
# nombre en espanol, variantes, alergenos y asociacion territorial cultural.
SLUG_META = {
    "yuca": {"nombre": "Yuca", "variantes": ["mandioca", "yuca brava"], "alergenos": [], "regiones": ["caribe", "pacifico", "orinoquia", "amazonia"]},
    "platano": {"nombre": "Platano", "variantes": ["platano macho", "topocho"], "alergenos": [], "regiones": ["caribe", "pacifico", "andina"]},
    "arroz": {"nombre": "Arroz blanco", "variantes": ["arroz"], "alergenos": [], "regiones": []},
    "frijol_negro": {"nombre": "Frijol negro", "variantes": ["frijol", "caraota negra"], "alergenos": [], "regiones": ["caribe", "andina"]},
    "lentejas": {"nombre": "Lentejas", "variantes": [], "alergenos": [], "regiones": ["andina"]},
    "arveja_seca": {"nombre": "Arveja seca (chicharo partido)", "variantes": ["arveja partida"], "alergenos": [], "regiones": ["andina"]},
    "harina_maiz": {"nombre": "Harina de maiz", "variantes": ["masa de maiz"], "alergenos": [], "regiones": ["caribe", "andina"]},
    "papa": {"nombre": "Papa", "variantes": ["patata"], "alergenos": [], "regiones": ["andina"]},
    "tomate": {"nombre": "Tomate", "variantes": [], "alergenos": [], "regiones": []},
    "cebolla": {"nombre": "Cebolla", "variantes": ["cebolla larga", "cebolla de rama"], "alergenos": [], "regiones": []},
    "ajo": {"nombre": "Ajo", "variantes": [], "alergenos": [], "regiones": []},
    "aguacate": {"nombre": "Aguacate", "variantes": ["palta", "aguacate papelillo"], "alergenos": [], "regiones": ["caribe", "andina", "pacifico"]},
    "pollo": {"nombre": "Pollo (pechuga sin piel)", "variantes": ["pechuga"], "alergenos": [], "regiones": []},
    "res": {"nombre": "Carne de res molida", "variantes": ["res molida"], "alergenos": [], "regiones": ["andina", "orinoquia"]},
    "huevo": {"nombre": "Huevo de gallina", "variantes": ["huevo entero"], "alergenos": ["huevo"], "regiones": []},
    "leche": {"nombre": "Leche entera", "variantes": ["leche"], "alergenos": ["leche"], "regiones": []},
    "queso_fresco": {"nombre": "Queso fresco", "variantes": ["queso campesino (similar)"], "alergenos": ["leche"], "regiones": []},
    "aceite": {"nombre": "Aceite de soya", "variantes": ["aceite vegetal"], "alergenos": [], "regiones": []},
    "brocoli": {"nombre": "Brocoli", "variantes": ["brecol"], "alergenos": [], "regiones": ["andina"]},
    "zanahoria": {"nombre": "Zanahoria", "variantes": [], "alergenos": [], "regiones": ["andina"]},
    "espinaca": {"nombre": "Espinaca", "variantes": [], "alergenos": [], "regiones": ["andina"]},
    "naranja": {"nombre": "Naranja", "variantes": ["naranja de jugo"], "alergenos": [], "regiones": []},
    "mango": {"nombre": "Mango", "variantes": ["mango de azucar"], "alergenos": [], "regiones": ["caribe", "pacifico"]},
    "papaya": {"nombre": "Papaya", "variantes": ["lechosa"], "alergenos": [], "regiones": ["caribe", "pacifico"]},
    "guayaba": {"nombre": "Guayaba", "variantes": [], "alergenos": [], "regiones": ["caribe", "andina"]},
    "maracuya": {"nombre": "Maracuya", "variantes": ["curuba (nombre de otra fruta; verificar)"], "alergenos": [], "regiones": ["andina"]},
    "cacao": {"nombre": "Cacao en polvo sin azucar", "variantes": ["cocoa"], "alergenos": [], "regiones": ["pacifico", "caribe"]},
    "trucha": {"nombre": "Trucha arcoiris", "variantes": ["trucha"], "alergenos": ["pescado"], "regiones": ["andina"]},
}

CATEGORY_MAP = {
    "Vegetables and Vegetable Products": "vegetal",
    "Fruits and Fruit Juices": "fruta",
    "Cereal Grains and Pasta": "cereal",
    "Legumes and Legume Products": "legumbre",
    "Poultry Products": "proteina_animal",
    "Beef Products": "proteina_animal",
    "Finfish and Shellfish Products": "proteina_animal",
    "Dairy and Egg Products": "lacteo",
    "Fats and Oils": "grasa",
    "Spices and Herbs": "especia",
    "Sweets": "azucar",
}

LIMITACIONES_GLOBALES = [
    "Fuente: USDA FoodData Central (SR Legacy 2019 y Foundation). Muestras de EE. UU.; "
    "las variedades y condiciones colombianas pueden diferir.",
    "Composicion del alimento en estado declarado (mayormente crudo). Los cambios por "
    "coccion no estan incluidos salvo en los datos de origen.",
    "La tabla ICBF de composicion de alimentos colombianos es la fuente prioritaria "
    "pendiente de incorporar (licencia y version por verificar, PD-04).",
    "Asociaciones territoriales, nombres locales y alergenos son curaduria educativa "
    "del proyecto, marcada como 'educativo' y pendiente de verificacion formal.",
    "Alimentos prioritarios pendientes de fuente: panela, mazorca, platanos cocidos, "
    "bocachico, pargo, ahuyama, cubios, chachafruto, entre otros.",
]


def convert_food(slug: str, payload: dict) -> tuple[dict | None, list[str]]:
    observations: list[str] = []
    foods = payload.get("foods") or []
    if not foods:
        return None, [f"{slug}: sin resultados en la descarga"]
    best = foods[0]
    meta = SLUG_META.get(slug, {"nombre": slug, "variantes": [], "alergenos": [], "regiones": []})

    category = best.get("foodCategory") or "sin categoria"
    food_group = CATEGORY_MAP.get(category)
    if food_group is None:
        food_group = "otros"
        observations.append(f"{slug}: categoria FDC '{category}' sin mapeo de grupo")

    nutrients = []
    seen: set[str] = set()
    assumed_zero: list[str] = []
    for item in best.get("foodNutrients", []):
        nutrient_id = item.get("nutrientId")
        mapped = NUTRIENT_MAP.get(nutrient_id)
        if mapped is None:
            continue
        key, unit = mapped
        if item.get("unitName", "").upper() == "KJ":
            continue
        if key in seen:
            continue
        derivation = item.get("derivationCode") or ""
        if derivation == "Z":
            assumed_zero.append(f"{key} (asumido cero por la fuente)")
            continue  # dato ausente, NO cero
        value = item.get("value")
        if value is None:
            continue
        low, high = RANGE_CHECKS.get(key, (0, float("inf")))
        if not low <= value <= high:
            observations.append(
                f"{slug}: {key}={value} fuera de rango plausible ({low}-{high}); RECHAZADO"
            )
            continue
        trust = "medido" if derivation == "A" else "estimado"
        method = item.get("derivationDescription") or ("analitico" if trust == "medido" else "derivado")
        if nutrient_id == 2047:
            method = "Calculado con factores generales de Atwater (Foundation)"
        nutrients.append(
            {
                "nutrient": key,
                "value": round(float(value), 3),
                "unit": unit,
                "method": method,
                "trust_tier": trust,
            }
        )
        seen.add(key)

    measured = sum(1 for nutrient in nutrients if nutrient["trust_tier"] == "medido")
    estimated = len(nutrients) - measured
    if measured == 0:
        observations.append(f"{slug}: sin nutrientes medidos (todos estimados)")

    return (
        {
            "id": f"FDC-{best.get('fdcId')}",
            "slug": slug,
            "name_common": meta["nombre"],
            "name_variants": meta["variantes"],
            "name_scientific": best.get("scientificName"),
            "fdc_description": best.get("description"),
            "fdc_data_type": best.get("dataType"),
            "fdc_published": best.get("publishedDate"),
            "food_group": food_group,
            "state": "crudo" if "raw" in (best.get("description") or "").lower() else "segun fuente",
            "allergens": meta["alergenos"],
            "region_associations": meta["regiones"],
            "diet_tags": ["animal"] if food_group in {"proteina_animal", "lacteo", "huevo"} else ["vegetal"],
            "notes": (
                "Asociacion territorial y nombres locales: curaduria educativa "
                "pendiente de verificacion (PD-13)."
            ),
            "nutrients": nutrients,
            "nutrients_medidos": measured,
            "nutrients_estimados": estimated,
            "assumed_zero_omitidos": assumed_zero,
        },
        observations,
    )


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    retrieval_date = date.today().isoformat()
    imported, skipped, observations_all = [], [], []

    for food in manifest["foods"]:
        slug = food["slug"]
        raw_path = RAW_DIR / f"{slug}.json"
        if not raw_path.exists():
            skipped.append(f"{slug}: sin descarga cruda todavia")
            continue
        try:
            payload = json.loads(raw_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as error:
            skipped.append(f"{slug}: JSON crudo invalido ({error})")
            continue
        converted, observations = convert_food(slug, payload)
        observations_all.extend(observations)
        if converted is None:
            continue
        imported.append(converted)

    normalized = {
        "meta": {
            "source": manifest["source"],
            "retrieved_at": retrieval_date,
            "imported_at": datetime.now(UTC).isoformat(),
            "nutrient_map_fdc_ids": {str(key): value[0] for key, value in NUTRIENT_MAP.items()},
        },
        "foods": imported,
        "skipped": skipped,
        "observations": observations_all,
        "global_limitations": LIMITACIONES_GLOBALES,
    }
    NORMALIZED.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # --- Informe de calidad ---
    lines = [
        "# Informe de calidad de importacion — USDA FDC",
        "",
        f"- Fecha de importacion: {retrieval_date}",
        f"- Alimentos importados: {len(imported)}",
        f"- Alimentos pendientes de descarga: {len(skipped)}",
        f"- API: {manifest['source']['api_url']} (clave DEMO_KEY compartida; limite de tasa estricto)",
        "",
        "## Detalle por alimento",
        "",
    ]
    for food in imported:
        lines.append(
            f"### {food['name_common']} ({food['id']}) — {food['fdc_description']}"
        )
        lines.append(f"- Grupo (mapeado): {food['food_group']} | Estado: {food['state']}")
        lines.append(
            f"- Nutrientes: {len(food['nutrients'])} ({food['nutrients_medidos']} medidos, "
            f"{food['nutrients_estimados']} estimados con metodo declarado)"
        )
        if food["assumed_zero_omitidos"]:
            lines.append(
                f"- Omitidos por 'asumido cero' (ausente, no cero): {', '.join(food['assumed_zero_omitidos'])}"
            )
        lines.append("")
    if skipped:
        lines.append("## Pendientes de descarga")
        lines.extend(f"- {item}" for item in skipped)
        lines.append("")
    if observations_all:
        lines.append("## Observaciones")
        lines.extend(f"- {item}" for item in observations_all)
        lines.append("")
    lines.append("## Limitaciones globales")
    lines.extend(f"- {item}" for item in LIMITACIONES_GLOBALES)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"OK: {len(imported)} alimentos -> {NORMALIZED}")
    print(f"Saltados: {len(skipped)} | Observaciones: {len(observations_all)}")
    print(f"Informe: {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
