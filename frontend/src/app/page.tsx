"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Estado } from "@/lib/types";
import { Card, Reveal, SectionTitle, TrustBadge } from "@/components/ui";

const PREGUNTAS = [
  "¿Qué puedo comer de forma saludable con el dinero que tengo esta semana?",
  "¿Qué alimentos son habituales y están disponibles en mi municipio?",
  "¿Cómo preparo platos tradicionales con mejores características nutricionales?",
  "¿Qué contiene cada alimento y qué evidencia respalda cada recomendación?",
];

export default function Landing() {
  const [estado, setEstado] = useState<Estado | null>(null);

  useEffect(() => {
    api.get<Estado>("/api/auth/estado").then(setEstado).catch(() => setEstado(null));
  }, []);

  return (
    <div className="pt-10">
      {/* Hero */}
      <section className="grid items-center gap-10 lg:grid-cols-[1.15fr_0.85fr]">
        <Reveal>
          <p className="mb-4 inline-flex items-center gap-2 rounded-full border border-salvia bg-salvia-suave/60 px-4 py-1.5 text-xs font-medium text-botanico">
            Nutrición basada en evidencia · para la vida real en Colombia
          </p>
          <h1 className="text-4xl leading-[1.08] font-semibold text-tinta sm:text-5xl lg:text-6xl">
            Come bien en tu región,{" "}
            <span className="italic text-botanico">con la ciencia visible</span> y el
            bolsillo en cuenta.
          </h1>
          <p className="mt-6 max-w-xl text-lg text-tinta-suave">
            NutriRegión Colombia conecta la evidencia científica, los alimentos locales y
            las condiciones reales de vida. Cada dato muestra su fuente, su fecha y su
            nivel de confianza. Sin inventar, sin presumir, sin señalar a nadie.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/registro"
              className="rounded-full bg-botanico px-6 py-3 text-sm font-medium text-papel shadow-sm transition-all hover:bg-botanico-oscuro motion-safe:hover:-translate-y-0.5"
            >
              Comenzar ahora
            </Link>
            <Link
              href="/alimentos"
              className="rounded-full border border-borde bg-papel px-6 py-3 text-sm font-medium text-tinta transition-all hover:border-salvia motion-safe:hover:-translate-y-0.5"
            >
              Explorar alimentos
            </Link>
          </div>
          {estado && (
            <p className="mt-6 text-xs text-tinta-suave">
              Catálogo actual: {estado.foods_total} alimentos con datos verificados ·{" "}
              {estado.rules_total} reglas de seguridad ({estado.rules_approved} aprobadas,{" "}
              {estado.rules_total - estado.rules_approved} candidatas en revisión
              profesional)
            </p>
          )}
        </Reveal>

        <Reveal delay={0.15}>
          <Card className="overflow-hidden">
            <div className="bg-botanico px-6 py-4">
              <p className="text-xs font-medium uppercase tracking-widest text-salvia">
                Así se ve la confianza
              </p>
              <p className="mt-1 font-display text-lg text-papel">
                Cada dato, con su capa de confianza visible
              </p>
            </div>
            <div className="space-y-4 px-6 py-6">
              <div className="rounded-xl border border-borde bg-marfil px-4 py-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-medium">Energía — 160 kcal/100 g</span>
                  <TrustBadge tier="medido" />
                </div>
                <p className="mt-1 text-xs text-tinta-suave">
                  Valor analítico de tabla oficial, con fecha de consulta.
                </p>
              </div>
              <div className="rounded-xl border border-borde bg-marfil px-4 py-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-medium">Costo en tu municipio</span>
                  <TrustBadge tier="estimado" />
                </div>
                <p className="mt-1 text-xs text-tinta-suave">
                  Con método declarado — o "sin datos" cuando no existen precios. Nunca
                  se inventan.
                </p>
              </div>
              <div className="rounded-xl border border-borde bg-marfil px-4 py-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-medium">Beneficios descritos</span>
                  <TrustBadge tier="literatura" />
                </div>
                <p className="mt-1 text-xs text-tinta-suave">
                  Propiedades citadas de literatura revisada por pares. Un nutriente no
                  es una promesa médica.
                </p>
              </div>
              <div className="rounded-xl border border-borde bg-marfil px-4 py-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-medium">Recetas tradicionales</span>
                  <TrustBadge tier="educativo" />
                </div>
                <p className="mt-1 text-xs text-tinta-suave">
                  Cocina regional documentada con humildad, marcada como educativa.
                </p>
              </div>
            </div>
          </Card>
        </Reveal>
      </section>

      {/* Preguntas que responde */}
      <section className="mt-20">
        <SectionTitle
          eyebrow="Preguntas reales"
          title="Hecha para la vida cotidiana"
          description="No es una calculadora de calorías ni un generador genérico de dietas: es una plataforma que conecta territorio, presupuesto, cultura y evidencia."
        />
        <div className="grid gap-4 sm:grid-cols-2">
          {PREGUNTAS.map((pregunta, index) => (
            <Reveal key={pregunta} delay={index * 0.06}>
              <Card className="h-full px-6 py-6">
                <span aria-hidden className="font-display text-3xl text-salvia">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <p className="mt-3 text-[15px] font-medium text-tinta">{pregunta}</p>
              </Card>
            </Reveal>
          ))}
        </div>
      </section>

      {/* Compromisos */}
      <section className="mt-20">
        <SectionTitle
          eyebrow="Tres compromisos"
          title="Lo que NO hacemos dice tanto como lo que sí"
        />
        <div className="grid gap-4 md:grid-cols-3">
          <Card className="px-6 py-7">
            <p className="font-display text-lg text-botanico">No fingimos precios</p>
            <p className="mt-3 text-sm text-tinta-suave">
              Cada precio muestra fecha, tipo de dato y fuente. Si no hay datos para tu
              municipio, lo decimos — la plataforma sigue siendo útil.
            </p>
          </Card>
          <Card className="px-6 py-7">
            <p className="font-display text-lg text-botanico">No inventamos evidencia</p>
            <p className="mt-3 text-sm text-tinta-suave">
              Un catálogo pequeño, real y trazable vale más que uno grande y falso. La
              OMS y la OPS son referencias de diseño, no avales.
            </p>
          </Card>
          <Card className="px-6 py-7">
            <p className="font-display text-lg text-botanico">No ponemos obstáculos a tu salud</p>
            <p className="mt-3 text-sm text-tinta-suave">
              Ante alergias, señales de alerta o condiciones que requieren
              acompañamiento, derivamos a profesionales. La IA ayuda a explicar; nunca
              decide.
            </p>
          </Card>
        </div>
      </section>

      {/* Regiones */}
      <section className="mt-20">
        <SectionTitle
          eyebrow="Territorio"
          title="Las seis regiones gastronómicas de Colombia"
          description="Caribe, Andina, Pacífica, Orinoquía, Amazonía e Insular: respetamos la gastronomía, la biodiversidad y la disponibilidad local."
        />
        <div className="flex flex-wrap gap-3">
          {["Caribe", "Andina", "Pacífica", "Orinoquía", "Amazonía", "Insular"].map(
            (region) => (
              <span
                key={region}
                className="rounded-full border border-borde bg-papel px-5 py-2.5 text-sm text-tinta"
              >
                {region}
              </span>
            )
          )}
        </div>
        <p className="mt-4 max-w-2xl text-xs text-tinta-suave">
          Las asociaciones territoriales del catálogo son curaduría educativa del
          equipo, pendiente de verificación formal (decisiones abiertas en{" "}
          <Link href="/evidencia" className="underline hover:text-botanico">
            transparencia del sistema
          </Link>
          ).
        </p>
      </section>

      {/* CTA final */}
      <section className="mt-20">
        <Card className="bg-botanico px-8 py-12 text-center text-papel">
          <h2 className="font-display text-3xl">Tu alimentación, con datos que puedes auditar</h2>
          <p className="mx-auto mt-4 max-w-xl text-sm text-salvia-suave">
            Crea tu cuenta, completa el cuestionario territorial y recibe
            recomendaciones que explican por qué se generaron y qué reglas se aplicaron.
          </p>
          <Link
            href="/registro"
            className="mt-8 inline-block rounded-full bg-papel px-8 py-3 text-sm font-semibold text-botanico transition-transform motion-safe:hover:-translate-y-0.5"
          >
            Crear mi cuenta
          </Link>
        </Card>
      </section>
    </div>
  );
}
