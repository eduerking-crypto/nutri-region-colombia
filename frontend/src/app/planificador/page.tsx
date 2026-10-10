"use client";

import Link from "next/link";
import { useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { api } from "@/lib/api";
import type { Plan } from "@/lib/types";
import {
  Alert,
  Button,
  Card,
  EmptyState,
  Reveal,
  SectionTitle,
  Skeleton,
  formatNumber,
  useAsync,
} from "@/components/ui";

export default function Planificador() {
  const { user, cargando } = useAuth();
  const [dias, setDias] = useState(2);
  const [plan, setPlan] = useState<Plan | null>(null);
  const [generando, setGenerando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { data: historial, reload: recargarHistorial } = useAsync<
    { plan_id: number; created_at: string; status: string; warnings: string[] }[]
  >(
    () =>
      api
        .get<{ plan_id: number; created_at: string; status: string; warnings: string[] }[]>(
          "/api/planificador/historial"
        )
        .catch((): { plan_id: number; created_at: string; status: string; warnings: string[] }[] => []),
    []
  );

  async function generar() {
    setGenerando(true);
    setError(null);
    try {
      const resultado = await api.post<Plan>("/api/planificador/generar", { days: dias });
      setPlan(resultado);
      recargarHistorial();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No fue posible generar el plan.");
    } finally {
      setGenerando(false);
    }
  }

  if (cargando) return <div className="pt-20 text-center text-tinta-suave">Cargando…</div>;
  if (!user) {
    return (
      <div className="mx-auto max-w-md pt-20 text-center">
        <h1 className="font-display text-3xl">El planificador necesita conocerte</h1>
        <p className="mt-3 text-sm text-tinta-suave">
          La seguridad primero: con tu perfil podemos respetar tus alergias y detectar
          cuándo derivar a un profesional.
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <Link href="/ingresar" className="rounded-full bg-botanico px-6 py-2.5 text-sm font-medium text-papel">Ingresar</Link>
          <Link href="/registro" className="rounded-full border border-borde bg-papel px-6 py-2.5 text-sm font-medium">Crear cuenta</Link>
        </div>
      </div>
    );
  }

  const bloqueado = plan && ["bloqueado", "urgencia", "requiere_profesional"].includes(plan.status);

  return (
    <div className="pt-10">
      <SectionTitle
    as={"h1"}
    eyebrow="Planificador"
        title="Menús explicables, no recetas mágicas"
        description="El motor determinista genera tu menú con porciones nominales, respeta tus alergias y registra qué reglas se aplicaron. Mismas condiciones, mismo resultado: auditable."
      />

      <Card className="px-6 py-6">
        <div className="flex flex-wrap items-center gap-4">
          <label className="flex items-center gap-3 text-sm font-medium">
            Días del plan
            <select
              value={dias}
              onChange={(event) => setDias(Number(event.target.value))}
              className="rounded-lg border border-borde bg-papel px-3 py-2 text-sm"
            >
              {[1, 2, 3, 4, 5, 6, 7].map((dia) => (
                <option key={dia} value={dia}>{dia}</option>
              ))}
            </select>
          </label>
          <Button onClick={generar} disabled={generando}>
            {generando ? "Generando…" : "Generar mi plan"}
          </Button>
          <Link href="/presupuesto" className="text-sm text-botanico underline underline-offset-2">
            Ver presupuesto y lista de compras →
          </Link>
        </div>
      </Card>

      {error && <div className="mt-6"><Alert kind="danger">{error}</Alert></div>}

      {plan && (
        <div className="mt-8 space-y-6">
          {/* Mensajes de seguridad */}
          {plan.safety_messages.length > 0 && (
            <div className="space-y-3">
              {plan.safety_messages.map((mensaje) => (
                <Alert
                  key={mensaje.code}
                  kind={
                    mensaje.severity === "urgencia" || mensaje.severity === "bloqueo"
                      ? "danger"
                      : mensaje.severity === "profesional"
                        ? "warning"
                        : "info"
                  }
                  title={
                    mensaje.severity === "urgencia"
                      ? "Atención médica primero"
                      : mensaje.severity === "bloqueo"
                        ? "Plan bloqueado por tu seguridad"
                        : mensaje.severity === "profesional"
                          ? "Requiere acompañamiento profesional"
                          : "Para tu información"
                  }
                >
                  {mensaje.message}
                </Alert>
              ))}
            </div>
          )}

          {bloqueado && plan.menu === null ? (
            <EmptyState
              title="No generamos un plan automático esta vez"
              message="Es lo correcto cuando tu seguridad requiere acompañamiento profesional. Tu registro queda como pendiente de revisión y puedes consultar el detalle de reglas aplicadas."
            />
          ) : (
            plan.menu && (
              <>
                <div className="grid gap-4 lg:grid-cols-2">
                  {plan.menu.dias.map((dia) => (
                    <Reveal key={dia.dia}>
                      <Card className="h-full px-6 py-6">
                        <h3 className="font-display text-lg">Día {dia.dia}</h3>
                        <div className="mt-4 space-y-4">
                          {dia.comidas.map((comida) => (
                            <div key={comida.tipo}>
                              <p className="text-xs font-semibold uppercase tracking-widest text-salvia">
                                {comida.tipo}
                              </p>
                              <ul className="mt-1.5 space-y-1">
                                {comida.items.map((item) => (
                                  <li key={item.food_id} className="flex items-baseline justify-between gap-3 text-sm">
                                    <Link href={`/alimentos/${item.food_id}`} className="underline-offset-2 hover:text-botanico hover:underline">
                                      {item.name}
                                    </Link>
                                    <span className="text-tinta-suave">
                                      {formatNumber(item.grams)} g
                                    </span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          ))}
                        </div>
                      </Card>
                    </Reveal>
                  ))}
                </div>

                {/* Nutrición por día */}
                {plan.nutrition_per_day && (
                  <Card className="px-6 py-6">
                    <h3 className="font-display text-lg">Nutrición diaria estimada</h3>
                    <p className="text-xs text-tinta-suave">
                      Suma de composición de ingredientes crudos por 100 g; no incluye
                      cambios por cocción. Porciones nominales ajustables.
                    </p>
                    <div className="mt-4 grid gap-3 sm:grid-cols-3">
                      {Object.entries(plan.nutrition_per_day).map(([dia, valores]) => (
                        <div key={dia} className="rounded-xl bg-marfil px-4 py-3 text-sm">
                          <p className="text-xs font-semibold text-salvia">Día {dia}</p>
                          <p className="mt-1">{formatNumber(valores.energia ?? 0)} kcal</p>
                          <p className="text-xs text-tinta-suave">
                            Proteína {formatNumber(valores.proteina ?? 0)} g · Grasa{" "}
                            {formatNumber(valores.grasa_total ?? 0)} g · Carbohidratos{" "}
                            {formatNumber(valores.carbohidratos ?? 0)} g
                          </p>
                        </div>
                      ))}
                    </div>
                  </Card>
                )}

                {/* Adecuación */}
                {plan.adequacy && (
                  <Card className="px-6 py-6">
                    <h3 className="font-display text-lg">
                      Distribución de macronutrientes frente a rangos de referencia
                    </h3>
                    <p className="text-xs text-tinta-suave">
                      Rangos de OMS/FAO (Informe Técnico 916, 2003) usados como
                      referencia <strong>no vinculante</strong>, citados de memoria por
                      el equipo y pendientes de verificación profesional.
                    </p>
                    <div className="mt-4 space-y-3">
                      {plan.adequacy.map((item) => (
                        <div key={item.metric} className="flex items-center gap-4">
                          <span className="w-28 text-sm font-medium">{item.label}</span>
                          <div className="relative h-3 flex-1 overflow-hidden rounded-full bg-borde/50">
                            <div
                              className={`h-full ${item.in_range ? "bg-salvia" : "bg-tierra"}`}
                              style={{ width: `${Math.min((item.value ?? 0) * 1.2, 100)}%` }}
                            />
                          </div>
                          <span className={`w-40 text-right text-xs ${item.in_range ? "text-exito" : "text-ambar"}`}>
                            {item.value === null ? "Sin datos" : `${item.value}% · rango ${item.range[0]}–${item.range[1]}%`}
                          </span>
                        </div>
                      ))}
                    </div>
                  </Card>
                )}

                <Card className="px-6 py-5">
                  <h3 className="text-sm font-semibold">Reglas aplicadas</h3>
                  <p className="mt-2 font-mono text-xs text-tinta-suave">
                    {plan.applied_rules.length ? plan.applied_rules.join(" · ") : "Ninguna regla específica del catálogo se activó."}
                  </p>
                  {plan.limitations.map((limitacion) => (
                    <p key={limitacion} className="mt-2 text-xs text-tinta-suave">• {limitacion}</p>
                  ))}
                </Card>
              </>
            )
          )}
        </div>
      )}

      {historial && historial.length > 0 && (
        <div className="mt-12">
          <SectionTitle eyebrow="Historial" title="Planes anteriores" />
          <div className="space-y-2">
            {historial.slice(0, 5).map((item) => (
              <Card key={item.plan_id} className="flex items-center justify-between px-5 py-3 text-sm">
                <span>{new Date(item.created_at).toLocaleString("es-CO")}</span>
                <span className="text-xs text-tinta-suave">{item.status.replace(/_/g, " ")}</span>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
