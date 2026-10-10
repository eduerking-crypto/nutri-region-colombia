"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import {
  GROUP_LABELS,
  NUTRIENT_LABELS,
  REGION_LABELS,
  type FoodDetail,
  type Nutrient,
} from "@/lib/types";
import {
  Alert,
  Button,
  Card,
  EmptyState,
  Reveal,
  Skeleton,
  TrustBadge,
  formatNumber,
  useAsync,
} from "@/components/ui";

const MACROS = ["proteina", "grasa_total", "carbohidratos"];

function MacroBar({ nutrientes }: { nutrientes: Nutrient[] }) {
  const macros = MACROS.map((key) => ({
    key,
    label: NUTRIENT_LABELS[key],
    value: nutrientes.find((nutriente) => nutriente.nutrient === key)?.value ?? 0,
  }));
  const total = macros.reduce((sum, macro) => sum + macro.value, 0);
  if (!total) {
    return <p className="text-sm text-tinta-suave">Sin datos de macronutrientes.</p>;
  }
  const colors: Record<string, string> = {
    proteina: "var(--salvia)",
    grasa_total: "var(--tierra)",
    carbohidratos: "var(--botanico)",
  };
  return (
    <div>
      <div
        className="flex h-4 w-full overflow-hidden rounded-full border border-borde"
        role="img"
        aria-label={macros
          .map((macro) => `${macro.label}: ${Math.round((macro.value / total) * 100)}%`)
          .join(", ")}
      >
        {macros.map(
          (macro) =>
            macro.value > 0 && (
              <div
                key={macro.key}
                style={{ width: `${(macro.value / total) * 100}%`, background: colors[macro.key] }}
              />
            )
        )}
      </div>
      <div className="mt-3 flex flex-wrap gap-4 text-xs text-tinta-suave">
        {macros.map((macro) => (
          <span key={macro.key} className="flex items-center gap-1.5">
            <span
              aria-hidden
              className="h-2.5 w-2.5 rounded-full"
              style={{ background: colors[macro.key] }}
            />
            {macro.label}: {formatNumber(macro.value)} g
          </span>
        ))}
      </div>
    </div>
  );
}

export default function FichaAlimento() {
  const params = useParams<{ id: string }>();
  const { data: alimento, loading, error, reload } = useAsync<FoodDetail>(
    () => api.get<FoodDetail>(`/api/alimentos/${params.id}`),
    [params.id]
  );
  const { data: sustituciones } = useAsync<{ sustituciones: { food_id: string; name: string; reason: string }[] }>(
    () =>
      api
        .get<{ sustituciones: { food_id: string; name: string; reason: string }[] }>(
          `/api/alimentos/${params.id}/sustituciones`
        )
        .catch(() => ({ sustituciones: [] })),
    [params.id]
  );

  if (loading) {
    return (
      <div className="space-y-6 pt-10">
        <Skeleton className="h-10 w-2/3" />
        <Skeleton className="h-64" />
      </div>
    );
  }
  if (error || !alimento) {
    return (
      <div className="pt-16">
        <EmptyState
          title="No encontramos ese alimento"
          message={error ?? "El identificador no existe en el catálogo."}
          action={
            <Link href="/alimentos" className="text-sm font-medium text-botanico underline">
              Volver al explorador
            </Link>
          }
        />
      </div>
    );
  }

  const macros = alimento.nutrients.filter((nutriente) => MACROS.includes(nutriente.nutrient));
  const otros = alimento.nutrients.filter((nutriente) => !MACROS.includes(nutriente.nutrient));
  const calorias = alimento.nutrients.find((nutriente) => nutriente.nutrient === "energia");

  return (
    <div className="pt-10">
      <Link href="/alimentos" className="text-sm text-tinta-suave hover:text-tinta">
        ← Explorador
      </Link>

      <Reveal>
        <div className="mt-4 flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-salvia">
              {GROUP_LABELS[alimento.food_group] ?? alimento.food_group} · estado:{" "}
              {alimento.state}
            </p>
            <h1 className="mt-1 font-display text-4xl font-semibold">{alimento.name_common}</h1>
            {alimento.name_scientific && (
              <p className="mt-1 text-sm italic text-tinta-suave">{alimento.name_scientific}</p>
            )}
            {alimento.name_variants.length > 0 && (
              <p className="mt-1 text-sm text-tinta-suave">
                También llamado: {alimento.name_variants.join(", ")}
              </p>
            )}
          </div>
          <div className="text-right">
            <TrustBadge tier={alimento.trust_tier} size="md" />
            <p className="mt-2 text-xs text-tinta-suave">
              Fuente: {alimento.source_id.replace("SRC-", "")}
              <br />
              Consultado: {alimento.retrieved_at}
            </p>
          </div>
        </div>
      </Reveal>

      {alimento.allergy_conflicts.length > 0 && (
        <Alert kind="danger" title="Conflicto con tus alergias registradas">
          Este alimento contiene:{" "}
          {alimento.allergy_conflicts
            .map((conflicto) => `${conflicto.allergen} (${conflicto.kind})`)
            .join(", ")}
          . Queda excluido de tus planes. Nunca consideres una sustitución como segura sin
          verificar ingredientes y contaminación cruzada.
        </Alert>
      )}

      <div className="mt-8 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <Reveal>
          <Card className="px-6 py-6">
            <h2 className="font-display text-xl">Composición por 100 g de porción comestible</h2>
            {calorias && (
              <div className="mt-4 flex items-baseline gap-3 rounded-xl bg-salvia-suave/60 px-5 py-4">
                <span className="font-display text-4xl text-botanico">
                  {formatNumber(calorias.value)}
                </span>
                <div>
                  <p className="text-sm font-medium">kcal / 100 g</p>
                  <TrustBadge tier={calorias.trust_tier} size="sm" />
                </div>
              </div>
            )}
            <div className="mt-6">
              <MacroBar nutrientes={alimento.nutrients} />
            </div>
            <table className="mt-8 w-full text-sm">
              <caption className="sr-only">
                Composición nutricional por 100 g con capa de confianza por nutriente
              </caption>
              <thead>
                <tr className="border-b border-borde text-left text-xs text-tinta-suave">
                  <th scope="col" className="pb-2 font-medium">Nutriente</th>
                  <th scope="col" className="pb-2 font-medium">Valor</th>
                  <th scope="col" className="pb-2 font-medium">Confianza</th>
                  <th scope="col" className="pb-2 font-medium">Método</th>
                </tr>
              </thead>
              <tbody>
                {[...macros, ...otros].map((nutriente) => (
                  <tr key={nutriente.nutrient} className="border-b border-borde/60">
                    <td className="py-2.5 font-medium">
                      {NUTRIENT_LABELS[nutriente.nutrient] ?? nutriente.nutrient}
                    </td>
                    <td className="py-2.5">
                      {formatNumber(nutriente.value)} {nutriente.unit}
                    </td>
                    <td className="py-2.5">
                      <TrustBadge tier={nutriente.trust_tier} />
                    </td>
                    <td className="max-w-56 py-2.5 text-xs text-tinta-suave">
                      {nutriente.method ?? "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="mt-4 text-xs text-tinta-suave">
              Los valores "asumidos como cero" por la fuente se omiten: ausente ≠ cero.
            </p>
          </Card>
        </Reveal>

        <div className="space-y-6">
          <Reveal delay={0.1}>
            <Card className="px-6 py-6">
              <h2 className="font-display text-lg">Procedencia</h2>
              <p className="mt-3 text-sm text-tinta-suave">{alimento.source_citation}</p>
              <dl className="mt-4 space-y-2 text-sm">
                <div className="flex justify-between gap-2">
                  <dt className="text-tinta-suave">Capa de confianza</dt>
                  <dd><TrustBadge tier={alimento.trust_tier} /></dd>
                </div>
                <div className="flex justify-between gap-2">
                  <dt className="text-tinta-suave">Fecha de consulta</dt>
                  <dd>{alimento.retrieved_at}</dd>
                </div>
                <div className="flex justify-between gap-2">
                  <dt className="text-tinta-suave">Verificación</dt>
                  <dd className="font-medium text-ambar">
                    {alimento.verification_status === "verified"
                      ? "Verificada"
                      : "Pendiente de verificación"}
                  </dd>
                </div>
                {alimento.region_associations.length > 0 && (
                  <div className="flex justify-between gap-2">
                    <dt className="text-tinta-suave">Asociación territorial*</dt>
                    <dd>{alimento.region_associations.map((region) => REGION_LABELS[region] ?? region).join(", ")}</dd>
                  </div>
                )}
              </dl>
              <p className="mt-4 text-xs text-tinta-suave">
                *Curaduría educativa pendiente de verificación formal. La composición
                proviene de muestras de EE. UU. (USDA FDC); variedades y condiciones
                colombianas pueden diferir.
              </p>
            </Card>
          </Reveal>

          {sustituciones && sustituciones.sustituciones.length > 0 && (
            <Reveal delay={0.15}>
              <Card className="px-6 py-6">
                <h2 className="font-display text-lg">Sustituciones posibles</h2>
                <ul className="mt-3 space-y-3">
                  {sustituciones.sustituciones.map((sustitucion) => (
                    <li key={sustitucion.food_id}>
                      <Link
                        href={`/alimentos/${sustitucion.food_id}`}
                        className="font-medium text-botanico underline underline-offset-2"
                      >
                        {sustitucion.name}
                      </Link>
                      <p className="text-xs text-tinta-suave">{sustitucion.reason}</p>
                    </li>
                  ))}
                </ul>
              </Card>
            </Reveal>
          )}

          <Reveal delay={0.2}>
            <Card className="px-6 py-6">
              <h2 className="font-display text-lg">Explicación con IA</h2>
              <p className="mt-2 text-sm text-tinta-suave">
                Capa opcional desactivada por defecto. Cuando se active, solo explica
                datos ya verificados de esta ficha y su salida se valida contra los
                mismos. Nunca altera cálculos.
              </p>
              <Button variant="secondary" className="mt-4" disabled aria-disabled>
                Desactivada (ver ADR-0009)
              </Button>
            </Card>
          </Reveal>
        </div>
      </div>
    </div>
  );
}
