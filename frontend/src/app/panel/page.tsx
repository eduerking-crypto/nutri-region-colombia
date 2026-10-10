"use client";

import Link from "next/link";
import { useAuth } from "@/components/auth-provider";
import { api } from "@/lib/api";
import type { Estado, Plan, Profile } from "@/lib/types";
import { Alert, Card, Reveal, SectionTitle, Skeleton, TrustBadge, useAsync } from "@/components/ui";

export default function Panel() {
  const { user, cargando } = useAuth();
  const { data: estado } = useAsync<Estado>(() => api.get<Estado>("/api/auth/estado"), []);
  const { data: perfil, loading: cargandoPerfil } = useAsync<Profile | null>(
    () => api.get<Profile>("/api/perfil").catch(() => null),
    []
  );
  const { data: ultimoPlan } = useAsync<{ plan_id: number; created_at: string; status: string; warnings: string[] }[]>(
    () =>
      api
        .get<{ plan_id: number; created_at: string; status: string; warnings: string[] }[]>(
          "/api/planificador/historial"
        )
        .catch((): { plan_id: number; created_at: string; status: string; warnings: string[] }[] => []),
    []
  );

  if (cargando) return <div className="pt-20 text-center text-tinta-suave">Cargando…</div>;
  if (!user) {
    return (
      <div className="mx-auto max-w-md pt-20 text-center">
        <h1 className="font-display text-3xl">Tu panel te espera</h1>
        <p className="mt-3 text-sm text-tinta-suave">
          Inicia sesión para ver tus recomendaciones, seguimiento y configuración de
          privacidad.
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <Link href="/ingresar" className="rounded-full bg-botanico px-6 py-2.5 text-sm font-medium text-papel">
            Ingresar
          </Link>
          <Link href="/registro" className="rounded-full border border-borde bg-papel px-6 py-2.5 text-sm font-medium">
            Crear cuenta
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="pt-10">
      <Reveal>
        <p className="text-xs font-semibold uppercase tracking-widest text-salvia">
          Panel personal
        </p>
        <h1 className="mt-1 font-display text-3xl font-semibold sm:text-4xl">
          Hola{user.display_name ? `, ${user.display_name}` : ""} 👋
        </h1>
        {cargandoPerfil ? (
          <Skeleton className="mt-4 h-5 w-64" />
        ) : perfil && !perfil.onboarding_completed ? (
          <Alert kind="pilot" title="Completa tu cuestionario inicial">
            Con tu territorio, presupuesto y preferencias podemos ajustar las
            recomendaciones.{" "}
            <Link href="/onboarding" className="font-semibold underline">
              Completar ahora
            </Link>
          </Alert>
        ) : (
          <p className="mt-2 text-sm text-tinta-suave">
            {perfil?.municipality
              ? `${perfil.municipality}${perfil.department ? `, ${perfil.department}` : ""} · `
              : ""}
            Perfil completo. Los planes se adaptan a tu contexto.
          </p>
        )}
      </Reveal>

      <div className="mt-10 grid gap-4 md:grid-cols-3">
        {[
          {
            href: "/planificador",
            titulo: "Planificador de menús",
            texto: "Genera menús deterministas que respetan tus alergias y derivan a profesionales cuando corresponde.",
          },
          {
            href: "/alimentos",
            titulo: "Explorar alimentos",
            texto: `${estado?.foods_total ?? "—"} alimentos con composición trazable y capas de confianza visibles.`,
          },
          {
            href: "/seguimiento",
            titulo: "Registrar mi consumo",
            texto: "Un registro simple y sin juicios: tu historia alimentaria es tuya y puedes exportarla o borrarla.",
          },
        ].map((item, index) => (
          <Reveal key={item.href} delay={index * 0.07}>
            <Link href={item.href} className="group block">
              <Card className="h-full px-6 py-7 transition-all group-hover:-translate-y-1 group-hover:border-salvia motion-reduce:transition-none">
                <h2 className="font-display text-xl text-botanico">{item.titulo}</h2>
                <p className="mt-2 text-sm text-tinta-suave">{item.texto}</p>
                <span aria-hidden className="mt-4 inline-block text-botanico transition-transform group-hover:translate-x-1">
                  →
                </span>
              </Card>
            </Link>
          </Reveal>
        ))}
      </div>

      {ultimoPlan && ultimoPlan.length > 0 && (
        <div className="mt-12">
          <SectionTitle eyebrow="Historial" title="Tus planes recientes" />
          <div className="space-y-3">
            {ultimoPlan.slice(0, 3).map((plan) => (
              <Card key={plan.plan_id} className="flex items-center justify-between gap-4 px-6 py-4">
                <div>
                  <p className="text-sm font-medium">
                    Plan del {new Date(plan.created_at).toLocaleString("es-CO")}
                  </p>
                  {plan.warnings.length > 0 && (
                    <p className="text-xs text-ambar">{plan.warnings[0]}</p>
                  )}
                </div>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-medium ${
                    plan.status === "activo"
                      ? "bg-exito-fondo text-exito"
                      : plan.status === "pendiente_revision"
                        ? "bg-ambar-fondo text-ambar"
                        : "bg-borde text-tinta-suave"
                  }`}
                >
                  {plan.status.replace(/_/g, " ")}
                </span>
              </Card>
            ))}
          </div>
        </div>
      )}

      {estado?.pilot_mode && (
        <div className="mt-12">
          <Alert kind="pilot" title="Sobre el modo piloto">
            Las reglas de seguridad clínicas de esta plataforma están en fase de
            validación profesional. Cada plan te muestra exactamente qué reglas se
            aplicaron y su estado. <Link href="/evidencia" className="underline">Ver el catálogo de reglas</Link>
          </Alert>
        </div>
      )}
    </div>
  );
}
