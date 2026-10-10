"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { api } from "@/lib/api";
import type { Profile } from "@/lib/types";
import { Alert, Button, Card, Field, Input, ProgressSteps, Select } from "@/components/ui";

const PASOS = ["Territorio", "Presupuesto", "Preferencias", "Tu seguridad"];

const ALERGENOS = ["leche", "huevo", "pescado", "soya", "trigo/gluten", "maní", "frutos secos", "mariscos"];

const SALUD_FLAGS = [
  { flag: "diabetes_medicamentos", label: "Diabetes con medicamentos" },
  { flag: "enfermedad_renal", label: "Enfermedad renal" },
  { flag: "embarazo", label: "Embarazo" },
  { flag: "lactancia", label: "Lactancia" },
  { flag: "posible_tca", label: "Preocupaciones sobre mi relación con la comida" },
  { flag: "perdida_peso_involuntaria", label: "He perdido peso sin querer" },
  { flag: "sintomas_alarma", label: "Tengo síntomas que me preocupan ahora mismo" },
];

export default function Onboarding() {
  const { user, cargando } = useAuth();
  const router = useRouter();
  const [paso, setPaso] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [guardando, setGuardando] = useState(false);

  const [departamento, setDepartamento] = useState("");
  const [municipio, setMunicipio] = useState("");
  const [zona, setZona] = useState<"urbana" | "rural">("urbana");
  const [personasHogar, setPersonasHogar] = useState(1);
  const [presupuesto, setPresupuesto] = useState("");
  const [comidasDia, setComidasDia] = useState(3);
  const [patron, setPatron] = useState<"omnivoro" | "vegetariano" | "vegano">("omnivoro");
  const [alergias, setAlergias] = useState<string[]>([]);
  const [salud, setSalud] = useState<string[]>([]);

  useEffect(() => {
    if (!cargando && !user) router.replace("/ingresar");
    if (user) {
      api
        .get<Profile>("/api/perfil")
        .then((perfil) => {
          if (perfil.onboarding_completed) router.replace("/panel");
        })
        .catch(() => undefined);
    }
  }, [user, cargando, router]);

  async function guardarYFinalizar() {
    setGuardando(true);
    setError(null);
    try {
      const perfil = await api.put<Profile>("/api/perfil", {
        department: departamento || null,
        municipality: municipio || null,
        zone: zona,
        household_size: personasHogar,
        budget_weekly_cop: presupuesto ? Number(presupuesto) : null,
        meals_per_day: comidasDia,
        dietary_pattern: patron,
        onboarding_completed: true,
      });
      for (const alergeno of alergias) {
        await api.post("/api/perfil/alergias", {
          allergen: alergeno,
          kind: "alergia_confirmada",
          severity: "desconocida",
        }).catch(() => undefined);
      }
      for (const flag of salud) {
        await api.post("/api/perfil/salud", { flag, self_reported: true }).catch(() => undefined);
      }
      if (!perfil.onboarding_completed) throw new Error("No se pudo guardar el perfil.");
      router.push("/panel");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Error al guardar.");
    } finally {
      setGuardando(false);
    }
  }

  if (cargando || !user) {
    return <div className="pt-20 text-center text-tinta-suave">Cargando…</div>;
  }

  return (
    <div className="mx-auto max-w-2xl pt-12">
      <h1 className="font-display text-3xl font-semibold">Conozcamos tu contexto</h1>
      <p className="mt-2 text-sm text-tinta-suave">
        Solo preguntamos lo necesario. Puedes omitir lo que prefieras y completarlo
        después en tu perfil.
      </p>
      <div className="mt-10">
        <ProgressSteps steps={PASOS} current={paso} />
        <Card className="px-6 py-8 sm:px-8">
          {paso === 0 && (
            <div className="space-y-5">
              <h2 className="font-display text-xl">¿Dónde vives y comes?</h2>
              <Field label="Departamento">
                <Input value={departamento} onChange={(e) => setDepartamento(e.target.value)} placeholder="Ej. Sucre" />
              </Field>
              <Field label="Municipio">
                <Input value={municipio} onChange={(e) => setMunicipio(e.target.value)} placeholder="Ej. Sincelejo" />
              </Field>
              <Field label="Zona">
                <Select value={zona} onChange={(e) => setZona(e.target.value as "urbana" | "rural")}>
                  <option value="urbana">Urbana</option>
                  <option value="rural">Rural</option>
                </Select>
              </Field>
              <Field label="¿Para cuántas personas cocinas?" hint="Ajustamos las cantidades de la lista de compras.">
                <Input
                  type="number"
                  min={1}
                  max={20}
                  value={personasHogar}
                  onChange={(e) => setPersonasHogar(Number(e.target.value))}
                />
              </Field>
            </div>
          )}

          {paso === 1 && (
            <div className="space-y-5">
              <h2 className="font-display text-xl">Presupuesto y ritmo de cocina</h2>
              <Field
                label="Presupuesto semanal para alimentos (COP, opcional)"
                hint="Con datos de precio reales estimamos costos; sin datos, lo decimos expresamente."
              >
                <Input
                  type="number"
                  min={0}
                  value={presupuesto}
                  onChange={(e) => setPresupuesto(e.target.value)}
                  placeholder="Ej. 150000"
                />
              </Field>
              <Field label="Comidas al día">
                <Select value={comidasDia} onChange={(e) => setComidasDia(Number(e.target.value))}>
                  <option value={3}>3 (desayuno, almuerzo, cena)</option>
                  <option value={4}>4 (con onces)</option>
                  <option value={5}>5 (con media mañana y onces)</option>
                </Select>
              </Field>
              <p className="text-xs text-tinta-suave">
                No recogemos peso, talla ni fotos corporales: no son necesarios para
                orientación alimentaria general.
              </p>
            </div>
          )}

          {paso === 2 && (
            <div className="space-y-5">
              <h2 className="font-display text-xl">¿Cómo comes?</h2>
              <Field label="Patrón alimentario">
                <Select value={patron} onChange={(e) => setPatron(e.target.value as typeof patron)}>
                  <option value="omnivoro">Omnívoro</option>
                  <option value="vegetariano">Vegetariano</option>
                  <option value="vegano">Vegano</option>
                </Select>
              </Field>
              <Field label="Alergias o reacciones conocidas (marca las que apliquen)">
                <div className="grid grid-cols-2 gap-2">
                  {ALERGENOS.map((alergeno) => (
                    <label key={alergeno} className="flex cursor-pointer items-center gap-2 rounded-lg border border-borde bg-papel px-3 py-2 text-sm">
                      <input
                        type="checkbox"
                        checked={alergias.includes(alergeno)}
                        onChange={(event) =>
                          setAlergias((prev) =>
                            event.target.checked ? [...prev, alergeno] : prev.filter((item) => item !== alergeno)
                          )
                        }
                        className="h-4 w-4 accent-[#3e5c47]"
                      />
                      {alergeno}
                    </label>
                  ))}
                </div>
              </Field>
              <p className="text-xs text-tinta-suave">
                Si tu alergia es grave, excluimos esos alimentos de todo plan y te
                recordamos verificar ingredientes y contaminación cruzada.
              </p>
            </div>
          )}

          {paso === 3 && (
            <div className="space-y-5">
              <h2 className="font-display text-xl">Tu seguridad primero</h2>
              <p className="text-sm text-tinta-suave">
                Esta información es <strong>autorreportada</strong>, nunca un
                diagnóstico. Si marcas alguna de estas situaciones, priorizamos derivarte
                a un profesional de la salud por encima de cualquier plan automático.
              </p>
              <div className="space-y-2">
                {SALUD_FLAGS.map((item) => (
                  <label key={item.flag} className="flex cursor-pointer items-center gap-3 rounded-lg border border-borde bg-papel px-4 py-3 text-sm">
                    <input
                      type="checkbox"
                      checked={salud.includes(item.flag)}
                      onChange={(event) =>
                        setSalud((prev) =>
                          event.target.checked ? [...prev, item.flag] : prev.filter((item2) => item2 !== item.flag)
                        )
                      }
                      className="h-4 w-4 accent-[#3e5c47]"
                    />
                    {item.label}
                  </label>
                ))}
              </div>
              {salud.includes("sintomas_alarma") && (
                <Alert kind="danger" title="Si tus síntomas son intensos, acude a urgencias ahora">
                  NutriRegión no genera planes alimentarios ante señales de alarma.
                  Busca atención sanitaria cuanto antes.
                </Alert>
              )}
            </div>
          )}

          {error && <Alert kind="danger">{error}</Alert>}

          <div className="mt-8 flex items-center justify-between">
            <Button
              variant="ghost"
              onClick={() => setPaso((current) => Math.max(0, current - 1))}
              disabled={paso === 0}
            >
              Atrás
            </Button>
            {paso < PASOS.length - 1 ? (
              <Button onClick={() => setPaso((current) => current + 1)}>Continuar</Button>
            ) : (
              <Button onClick={guardarYFinalizar} disabled={guardando}>
                {guardando ? "Guardando…" : "Finalizar e ir a mi panel"}
              </Button>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
