"use client";

import { api } from "@/lib/api";
import type { EvidenceRef, Rule, SourceInfo } from "@/lib/types";
import { Card, Reveal, SectionTitle, TrustBadge, useAsync } from "@/components/ui";

export default function Evidencia() {
  const { data: fuentes } = useAsync<SourceInfo[]>(() => api.get("/api/evidencia/fuentes"), []);
  const { data: referencias } = useAsync<EvidenceRef[]>(
    () => api.get("/api/evidencia/referencias"),
    []
  );
  const { data: reglas } = useAsync<Rule[]>(() => api.get("/api/evidencia/reglas"), []);

  return (
    <div className="pt-10">
      <SectionTitle
    as={"h1"}
    eyebrow="Transparencia"
        title="Fuentes, evidencia y reglas del sistema"
        description="Todo lo que esta plataforma afirma es auditable: de dónde salió cada dato, en qué estado de verificación está y qué reglas de seguridad existen (y cuáles aún no están aprobadas)."
      />

      <Reveal>
        <Card className="px-6 py-6">
          <h2 className="font-display text-xl">Catálogo de fuentes</h2>
          <div className="mt-4 space-y-4">
            {(fuentes ?? []).map((fuente) => (
              <div key={fuente.id} className="rounded-xl border border-borde bg-marfil px-5 py-4">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <p className="font-medium">{fuente.name}</p>
                    <p className="mt-1 text-xs text-tinta-suave">
                      Versión: {fuente.version} · acceso: {fuente.access_method} ·
                      consultada: {fuente.retrieved_at}
                    </p>
                  </div>
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-medium ${
                      fuente.redistribution_allowed
                        ? "bg-exito-fondo text-exito"
                        : "bg-ambar-fondo text-ambar"
                    }`}
                  >
                    {fuente.redistribution_allowed ? "Redistribución permitida" : "Pendiente de verificación"}
                  </span>
                </div>
                <p className="mt-2 text-xs text-tinta-suave">Licencia: {fuente.license}</p>
                {fuente.notes && <p className="mt-1 text-xs text-tinta-suave">{fuente.notes}</p>}
              </div>
            ))}
          </div>
        </Card>
      </Reveal>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <Reveal delay={0.05}>
          <Card className="h-full px-6 py-6">
            <h2 className="font-display text-xl">Referencias de evidencia</h2>
            <div className="mt-4 space-y-4">
              {(referencias ?? []).map((referencia) => (
                <div key={referencia.id} className="rounded-xl border border-borde bg-marfil px-5 py-4">
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm font-medium">{referencia.title}</p>
                    <TrustBadge tier={referencia.trust_tier} />
                  </div>
                  <p className="mt-2 text-xs text-tinta-suave">{referencia.citation}</p>
                  {referencia.relevant_finding && (
                    <p className="mt-2 text-xs">{referencia.relevant_finding}</p>
                  )}
                  {referencia.limitations && (
                    <p className="mt-1 text-xs text-ambar">Limitaciones: {referencia.limitations}</p>
                  )}
                  <p className="mt-2 text-[11px] text-tinta-suave">
                    Estado: {referencia.verification_status === "verified" ? "verificada" : "pendiente de verificación"} · revisada {referencia.reviewed_at}
                  </p>
                </div>
              ))}
            </div>
          </Card>
        </Reveal>

        <Reveal delay={0.1}>
          <Card className="h-full px-6 py-6">
            <h2 className="font-display text-xl">Reglas del motor determinista</h2>
            <p className="mt-1 text-xs text-tinta-suave">
              Las reglas candidatas solo se evalúan en modo piloto (visible en el banner
              superior). Ninguna regla se considera aprobada sin registro de un
              profesional sanitario.
            </p>
            <div className="mt-4 space-y-3">
              {(reglas ?? []).map((regla) => (
                <div key={regla.id} className="rounded-xl border border-borde bg-marfil px-5 py-4">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div>
                      <p className="text-sm font-medium">{regla.name}</p>
                      <p className="text-[11px] font-mono text-tinta-suave">
                        {regla.id} v{regla.version} · acción: {regla.action.replace(/_/g, " ")}
                      </p>
                    </div>
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-medium ${
                        regla.status === "approved"
                          ? "bg-exito-fondo text-exito"
                          : regla.status === "candidate"
                            ? "bg-ambar-fondo text-ambar"
                            : "bg-borde text-tinta-suave"
                      }`}
                    >
                      {regla.status === "approved"
                        ? `Aprobada (${regla.reviewer})`
                        : regla.status === "candidate"
                          ? "Candidata — pendiente de validación profesional"
                          : regla.status}
                    </span>
                  </div>
                  <p className="mt-2 text-xs text-tinta-suave">{regla.justification}</p>
                  <p className="mt-1 text-[11px] text-tinta-suave">Fuente: {regla.source_desc}</p>
                  {regla.approved_at && (
                    <p className="mt-1 text-[11px] text-exito">
                      Aprobada el {regla.approved_at.slice(0, 10)} por {regla.reviewer}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </Card>
        </Reveal>
      </div>

      <p className="mt-8 max-w-3xl text-xs text-tinta-suave">
        Nota de honestidad: la plataforma no está clínicamente validada ni avalada por
        OMS/OPS/ICBF. Las referencias normativas se citan como marco de diseño. La
        validación profesional de reglas y el acompañamiento legal en privacidad
        (Ley 1581 de 2012) son requisitos abiertos antes de cualquier uso en producción.
      </p>
    </div>
  );
}
