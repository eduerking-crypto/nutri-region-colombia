"use client";

import Link from "next/link";
import { useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { api } from "@/lib/api";
import type { Rule } from "@/lib/types";
import {
  Alert,
  Button,
  Card,
  EmptyState,
  SectionTitle,
  useAsync,
} from "@/components/ui";

interface PlanPendiente {
  plan_id: number;
  user_id: number;
  created_at: string;
  status: string;
  warnings: string[];
  triage_result: string | null;
}

export default function PanelProfesional() {
  const { user, cargando } = useAuth();
  const { data: planes, reload: recargarPlanes } = useAsync<PlanPendiente[]>(
    () => api.get<PlanPendiente[]>("/api/profesional/planes").catch(() => []),
    []
  );
  const { data: reglas, reload: recargarReglas } = useAsync<Rule[]>(
    () => api.get<Rule[]>("/api/evidencia/reglas"),
    []
  );
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function revisar(planId: number, accion: "aprobar" | "rechazar" | "observaciones") {
    setError(null);
    try {
      await api.post(`/api/profesional/planes/${planId}/revision`, {
        action: accion,
        notes: `Revisión registrada desde el panel profesional (${new Date().toLocaleString("es-CO")}).`,
      });
      setMensaje(`Plan #${planId}: ${accion}.`);
      recargarPlanes();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No fue posible registrar la revisión.");
    }
  }

  async function aprobarRegla(reglaId: string) {
    setError(null);
    try {
      await api.post(`/api/profesional/reglas/${reglaId}/aprobar`, null);
      setMensaje(`Regla ${reglaId} aprobada. Queda registrado tu usuario y la fecha.`);
      recargarReglas();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No fue posible aprobar la regla.");
    }
  }

  if (cargando) return <div className="pt-20 text-center text-tinta-suave">Cargando…</div>;
  if (!user || (user.role !== "profesional" && user.role !== "admin")) {
    return (
      <div className="mx-auto max-w-md pt-20 text-center">
        <h1 className="font-display text-3xl">Panel profesional</h1>
        <p className="mt-3 text-sm text-tinta-suave">
          Esta sección es para profesionales de la salud que revisan planes y aprueban
          reglas clínicas. Requiere rol autorizado.
        </p>
        <Link href="/ingresar" className="mt-6 inline-block rounded-full bg-botanico px-6 py-2.5 text-sm font-medium text-papel">
          Ingresar con cuenta profesional
        </Link>
      </div>
    );
  }

  const candidatas = (reglas ?? []).filter((regla) => regla.status === "candidate");

  return (
    <div className="pt-10">
      <SectionTitle
    as={"h1"}
    eyebrow="Modo profesional"
        title="Revisión de planes y aprobación de reglas"
        description="Cada acción queda en auditoría con usuario y fecha. La verificación de credenciales profesionales es un requisito abierto antes de producción (PD-11)."
      />

      <Alert kind="pilot" title="Responsabilidad del revisor">
        Al aprobar una regla clínica declaras que, como profesional competente,
        revisaste su criterio y fuente. Las reglas aprobadas se aplican a todos los
        usuarios en producción.
      </Alert>

      {mensaje && <div className="mt-4"><Alert kind="success">{mensaje}</Alert></div>}
      {error && <div className="mt-4"><Alert kind="danger">{error}</Alert></div>}

      <div className="mt-8">
        <h2 className="font-display text-xl">Planes pendientes de revisión</h2>
        {(planes ?? []).length === 0 ? (
          <div className="mt-4">
            <EmptyState
              title="Sin planes pendientes"
              message="Cuando un usuario requiera acompañamiento profesional, su plan aparecerá aquí con las advertencias del triage."
            />
          </div>
        ) : (
          <div className="mt-4 space-y-3">
            {(planes ?? []).map((plan) => (
              <Card key={plan.plan_id} className="px-6 py-5">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="text-sm font-medium">
                      Plan #{plan.plan_id} · usuario #{plan.user_id}
                    </p>
                    <p className="text-xs text-tinta-suave">
                      {new Date(plan.created_at).toLocaleString("es-CO")} · triage:{" "}
                      {plan.triage_result}
                    </p>
                    {plan.warnings.slice(0, 2).map((warning, index) => (
                      <p key={index} className="mt-1 text-xs text-ambar">{warning}</p>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <Button variant="secondary" onClick={() => revisar(plan.plan_id, "aprobar")}>
                      Aprobar
                    </Button>
                    <Button variant="secondary" onClick={() => revisar(plan.plan_id, "observaciones")}>
                      Observaciones
                    </Button>
                    <Button variant="danger" onClick={() => revisar(plan.plan_id, "rechazar")}>
                      Rechazar
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      <div className="mt-12">
        <h2 className="font-display text-xl">Reglas candidatas a tu aprobación</h2>
        {candidatas.length === 0 ? (
          <p className="mt-3 text-sm text-tinta-suave">
            Todas las reglas del catálogo ya fueron revisadas.
          </p>
        ) : (
          <div className="mt-4 space-y-3">
            {candidatas.map((regla) => (
              <Card key={regla.id} className="px-6 py-5">
                <p className="text-sm font-medium">{regla.name}</p>
                <p className="mt-1 font-mono text-[11px] text-tinta-suave">
                  {regla.id} v{regla.version} · {regla.action.replace(/_/g, " ")}
                </p>
                <p className="mt-2 text-sm">{regla.message}</p>
                <p className="mt-2 text-xs text-tinta-suave">Justificación: {regla.justification}</p>
                <p className="mt-1 text-xs text-tinta-suave">Fuente: {regla.source_desc}</p>
                <Button className="mt-4" onClick={() => aprobarRegla(regla.id)}>
                  Aprobar regla (queda en auditoría)
                </Button>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
