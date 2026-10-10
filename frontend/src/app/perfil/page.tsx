"use client";

import Link from "next/link";
import { useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { api } from "@/lib/api";
import type { Allergy, HealthFlag, Profile } from "@/lib/types";
import {
  Alert,
  Button,
  Card,
  Field,
  Input,
  SectionTitle,
  Select,
  useAsync,
} from "@/components/ui";

const SALUD_LABELS: Record<string, string> = {
  diabetes_medicamentos: "Diabetes con medicamentos",
  enfermedad_renal: "Enfermedad renal",
  embarazo: "Embarazo",
  lactancia: "Lactancia",
  posible_tca: "Preocupaciones en mi relación con la comida",
  perdida_peso_involuntaria: "Pérdida de peso involuntaria",
  sintomas_alarma: "Síntomas de alarma (requiere atención médica)",
};

export default function Perfil() {
  const { user, cargando } = useAuth();
  const { data: perfil, reload: recargarPerfil } = useAsync<Profile | null>(
    () => api.get<Profile>("/api/perfil").catch(() => null),
    []
  );
  const { data: alergias, reload: recargarAlergias } = useAsync<Allergy[]>(
    () => api.get<Allergy[]>("/api/perfil/alergias").catch(() => []),
    []
  );
  const { data: salud, reload: recargarSalud } = useAsync<HealthFlag[]>(
    () => api.get<HealthFlag[]>("/api/perfil/salud").catch(() => []),
    []
  );

  const [guardando, setGuardando] = useState(false);
  const [guardado, setGuardado] = useState(false);
  const [nuevaAlergia, setNuevaAlergia] = useState("");

  async function guardarPerfil(perfilActualizado: Partial<Profile>) {
    if (!perfil) return;
    setGuardando(true);
    try {
      await api.put("/api/perfil", { ...perfil, ...perfilActualizado });
      setGuardado(true);
      recargarPerfil();
    } finally {
      setGuardando(false);
    }
  }

  async function agregarAlergia() {
    if (!nuevaAlergia.trim()) return;
    await api.post("/api/perfil/alergias", {
      allergen: nuevaAlergia.trim(),
      kind: "alergia_confirmada",
      severity: "desconocida",
    });
    setNuevaAlergia("");
    recargarAlergias();
  }

  async function agregarQuitarSalud(flag: string, agregar: boolean) {
    if (agregar) {
      await api.post("/api/perfil/salud", { flag, self_reported: true }).catch(() => undefined);
    } else {
      const existente = salud?.find((item) => item.flag === flag);
      if (existente) await api.delete(`/api/perfil/salud/${existente.id}`);
    }
    recargarSalud();
  }

  if (cargando) return <div className="pt-20 text-center text-tinta-suave">Cargando…</div>;
  if (!user) {
    return (
      <div className="mx-auto max-w-md pt-20 text-center">
        <h1 className="font-display text-3xl">Tu perfil alimentario</h1>
        <Link href="/ingresar" className="mt-6 inline-block rounded-full bg-botanico px-6 py-2.5 text-sm font-medium text-papel">
          Ingresar
        </Link>
      </div>
    );
  }

  const flagsActivos = new Set((salud ?? []).map((item) => item.flag));

  return (
    <div className="pt-10">
      <SectionTitle
    as={"h1"}
    eyebrow="Perfil"
        title="Tu contexto, tus reglas"
        description="Los cambios aquí afectan inmediatamente la seguridad de tus planes: las alergias excluyen alimentos y los indicadores de salud activan derivaciones."
      />

      {perfil && (
        <Card className="px-6 py-6">
          <h3 className="font-display text-lg">Contexto territorial y presupuesto</h3>
          <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Field label="Departamento">
              <Input
                defaultValue={perfil.department ?? ""}
                onBlur={(event) => guardarPerfil({ department: event.target.value || null })}
              />
            </Field>
            <Field label="Municipio">
              <Input
                defaultValue={perfil.municipality ?? ""}
                onBlur={(event) => guardarPerfil({ municipality: event.target.value || null })}
              />
            </Field>
            <Field label="Zona">
              <Select
                defaultValue={perfil.zone ?? "urbana"}
                onChange={(event) => guardarPerfil({ zone: event.target.value as "urbana" | "rural" })}
              >
                <option value="urbana">Urbana</option>
                <option value="rural">Rural</option>
              </Select>
            </Field>
            <Field label="Personas en el hogar">
              <Input
                type="number"
                min={1}
                defaultValue={perfil.household_size}
                onBlur={(event) => guardarPerfil({ household_size: Number(event.target.value) })}
              />
            </Field>
            <Field label="Presupuesto semanal (COP)">
              <Input
                type="number"
                min={0}
                defaultValue={perfil.budget_weekly_cop ?? ""}
                onBlur={(event) => guardarPerfil({ budget_weekly_cop: event.target.value ? Number(event.target.value) : null })}
              />
            </Field>
            <Field label="Patrón alimentario">
              <Select
                defaultValue={perfil.dietary_pattern}
                onChange={(event) => guardarPerfil({ dietary_pattern: event.target.value as Profile["dietary_pattern"] })}
              >
                <option value="omnivoro">Omnívoro</option>
                <option value="vegetariano">Vegetariano</option>
                <option value="vegano">Vegano</option>
              </Select>
            </Field>
          </div>
          {guardado && <Alert kind="success">Perfil actualizado.</Alert>}
        </Card>
      )}

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <Card className="px-6 py-6">
          <h3 className="font-display text-lg">Alergias y reacciones</h3>
          <ul className="mt-4 space-y-2">
            {(alergias ?? []).map((alergia) => (
              <li key={alergia.id} className="flex items-center justify-between rounded-lg bg-marfil px-4 py-2.5 text-sm">
                <span>
                  {alergia.allergen}{" "}
                  <span className="text-xs text-tinta-suave">({alergia.kind.replace(/_/g, " ")})</span>
                </span>
                <button
                  onClick={async () => {
                    await api.delete(`/api/perfil/alergias/${alergia.id}`);
                    recargarAlergias();
                  }}
                  className="text-xs text-alerta hover:underline"
                >
                  Quitar
                </button>
              </li>
            ))}
            {(alergias ?? []).length === 0 && (
              <p className="text-sm text-tinta-suave">Sin alergias registradas.</p>
            )}
          </ul>
          <div className="mt-4 flex gap-2">
            <Input
              value={nuevaAlergia}
              onChange={(event) => setNuevaAlergia(event.target.value)}
              placeholder="Ej. leche, huevo, pescado…"
            />
            <Button variant="secondary" onClick={agregarAlergia}>Agregar</Button>
          </div>
          <p className="mt-3 text-xs text-tinta-suave">
            Si una alergia es grave, ningún plan la incluirá y verás advertencias sobre
            contaminación cruzada.
          </p>
        </Card>

        <Card className="px-6 py-6">
          <h3 className="font-display text-lg">Indicadores de salud (autorreportados)</h3>
          <p className="mt-1 text-xs text-tinta-suave">
            Nunca son diagnósticos. Activan derivaciones profesionales conservadoras.
          </p>
          <div className="mt-4 space-y-2">
            {Object.entries(SALUD_LABELS).map(([flag, label]) => (
              <label key={flag} className="flex cursor-pointer items-center gap-3 rounded-lg border border-borde px-4 py-2.5 text-sm">
                <input
                  type="checkbox"
                  checked={flagsActivos.has(flag)}
                  onChange={(event) => agregarQuitarSalud(flag, event.target.checked)}
                  className="h-4 w-4 accent-[#3e5c47]"
                />
                {label}
              </label>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
