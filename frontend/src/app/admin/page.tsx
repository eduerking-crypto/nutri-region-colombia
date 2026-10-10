"use client";

import Link from "next/link";
import { useAuth } from "@/components/auth-provider";
import { api } from "@/lib/api";
import {
  Card,
  EmptyState,
  SectionTitle,
  useAsync,
} from "@/components/ui";

interface AuditoriaItem {
  id: number;
  at: string;
  actor: string;
  entity: string;
  entity_id: string;
  action: string;
  details: string | null;
}

interface Estadisticas {
  usuarios_total: number;
  usuarios_con_alergias: number;
  usuarios_con_indicadores_salud: number;
  alimentos_total: number;
  recetas_total: number;
  fuentes_total: number;
  precios_total: number;
  reglas_total: number;
  reglas_aprobadas: number;
}

export default function Admin() {
  const { user, cargando } = useAuth();
  const { data: stats } = useAsync<Estadisticas>(
    () => api.get<Estadisticas>("/api/admin/estadisticas").catch(() => null as unknown as Estadisticas),
    []
  );
  const { data: auditoria } = useAsync<AuditoriaItem[]>(
    () => api.get<AuditoriaItem[]>("/api/admin/auditoria").catch(() => []),
    []
  );

  if (cargando) return <div className="pt-20 text-center text-tinta-suave">Cargando…</div>;
  if (!user || user.role !== "admin") {
    return (
      <div className="mx-auto max-w-md pt-20 text-center">
        <h1 className="font-display text-3xl">Administración</h1>
        <p className="mt-3 text-sm text-tinta-suave">
          Área restringida a la administración del sistema.
        </p>
        <Link href="/ingresar" className="mt-6 inline-block rounded-full bg-botanico px-6 py-2.5 text-sm font-medium text-papel">
          Ingresar
        </Link>
      </div>
    );
  }

  return (
    <div className="pt-10">
      <SectionTitle
    as={"h1"}
    eyebrow="Administración"
        title="Estado real del sistema"
        description="Estadísticas verificadas contra la base de datos y registro de auditoría de cambios en reglas, roles y datos científicos."
      />

      {stats && (
        <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-3">
          {[
            { label: "Alimentos con datos reales", value: stats.alimentos_total },
            { label: "Recetas educativas cargadas", value: stats.recetas_total },
            { label: "Fuentes en catálogo", value: stats.fuentes_total },
            { label: "Reglas totales / aprobadas", value: `${stats.reglas_total} / ${stats.reglas_aprobadas}` },
            { label: "Precios observados", value: stats.precios_total },
            { label: "Usuarios", value: stats.usuarios_total },
          ].map((item) => (
            <Card key={item.label} className="px-6 py-6">
              <p className="font-display text-3xl text-botanico">{item.value}</p>
              <p className="mt-1 text-sm text-tinta-suave">{item.label}</p>
            </Card>
          ))}
        </div>
      )}

      <div className="mt-10">
        <h2 className="font-display text-xl">Auditoría</h2>
        {auditoria && auditoria.length > 0 ? (
          <Card className="mt-4 overflow-x-auto px-6 py-6">
            <table className="w-full min-w-[600px] text-sm">
              <thead>
                <tr className="border-b border-borde text-left text-xs text-tinta-suave">
                  <th className="pb-2 font-medium">Fecha</th>
                  <th className="pb-2 font-medium">Actor</th>
                  <th className="pb-2 font-medium">Entidad</th>
                  <th className="pb-2 font-medium">Acción</th>
                </tr>
              </thead>
              <tbody>
                {auditoria.map((log) => (
                  <tr key={log.id} className="border-b border-borde/60">
                    <td className="py-2 text-xs text-tinta-suave">
                      {new Date(log.at).toLocaleString("es-CO")}
                    </td>
                    <td className="py-2 font-mono text-xs">{log.actor}</td>
                    <td className="py-2 text-xs">
                      {log.entity}:{log.entity_id}
                    </td>
                    <td className="py-2 text-xs font-medium">{log.action}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        ) : (
          <div className="mt-4">
            <EmptyState title="Sin eventos de auditoría" message="Los cambios en reglas y roles aparecerán aquí." />
          </div>
        )}
      </div>
    </div>
  );
}
