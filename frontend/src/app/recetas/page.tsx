"use client";

import Link from "next/link";
import { api } from "@/lib/api";
import type { Recipe } from "@/lib/types";
import {
  Alert,
  Card,
  EmptyState,
  SectionTitle,
  SkeletonList,
  TrustBadge,
  formatNumber,
  useAsync,
} from "@/components/ui";
import { NUTRIENT_LABELS } from "@/lib/types";

export default function Recetas() {
  const { data: recetas, loading, error } = useAsync<Recipe[]>(
    () => api.get<Recipe[]>("/api/alimentos/recetas/todas"),
    []
  );

  return (
    <div className="pt-10">
      <SectionTitle
        as="h1"
        eyebrow="Cocina regional"
        title="Recetas tradicionales, calculadas con datos reales"
        description="Cada receta es educativa y su nutrición se calcula sumando la composición de ingredientes crudos (USDA FDC): los cambios por cocción no están incluidos. La verificación cultural y de rendimiento es un criterio abierto."
      />

      {error && <Alert kind="danger">{error}</Alert>}
      {loading && <SkeletonList count={4} />}

      {!loading && recetas && recetas.length === 0 && (
        <EmptyState
          title="Las recetas esperan a sus ingredientes"
          message="El recetario solo carga recetas cuyos ingredientes ya tienen composición real descargada. Cuando el catálogo de alimentos termine de crecer (con una API key gratuita de FDC), las 10 recetas regionales cargarán automáticamente. Preferimos esto a mostrar números inventados."
          action={
            <Link href="/alimentos" className="text-sm font-medium text-botanico underline">
              Ver el catálogo actual
            </Link>
          }
        />
      )}

      <div className="grid gap-5 md:grid-cols-2">
        {!loading &&
          (recetas ?? []).map((receta) => (
            <Card key={receta.id} className="px-6 py-6">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="font-display text-xl">{receta.name}</h2>
                  <p className="mt-1 text-xs text-tinta-suave">
                    {receta.servings} porciones · {receta.time_minutes} min
                    {receta.region ? ` · región ${receta.region}` : ""}
                  </p>
                </div>
                <TrustBadge tier={receta.trust_tier} />
              </div>

              <h3 className="mt-4 text-xs font-semibold uppercase tracking-widest text-salvia">
                Ingredientes
              </h3>
              <ul className="mt-1.5 space-y-1 text-sm">
                {receta.ingredients.map((ingrediente) => (
                  <li key={ingrediente.food_id} className="flex justify-between gap-2">
                    <Link
                      href={`/alimentos/${ingrediente.food_id}`}
                      className="hover:text-botanico hover:underline"
                    >
                      {ingrediente.name}
                    </Link>
                    <span className="text-tinta-suave">
                      {formatNumber(ingrediente.grams)} g
                    </span>
                  </li>
                ))}
              </ul>

              <h3 className="mt-4 text-xs font-semibold uppercase tracking-widest text-salvia">
                Preparación
              </h3>
              <ol className="mt-1.5 list-decimal space-y-1 pl-5 text-sm text-tinta-suave">
                {receta.steps.map((paso) => (
                  <li key={paso}>{paso}</li>
                ))}
              </ol>

              {receta.nutrition_per_serving && (
                <div className="mt-4 rounded-xl bg-marfil px-4 py-3 text-sm">
                  <p className="text-xs font-semibold text-salvia">Por porción (calculado)</p>
                  <p className="mt-1">
                    {NUTRIENT_LABELS.energia}:{" "}
                    {formatNumber(receta.nutrition_per_serving.energia ?? 0)} kcal ·{" "}
                    {NUTRIENT_LABELS.proteina}:{" "}
                    {formatNumber(receta.nutrition_per_serving.proteina ?? 0)} g ·{" "}
                    {NUTRIENT_LABELS.grasa_total}:{" "}
                    {formatNumber(receta.nutrition_per_serving.grasa_total ?? 0)} g ·{" "}
                    {NUTRIENT_LABELS.carbohidratos}:{" "}
                    {formatNumber(receta.nutrition_per_serving.carbohidratos ?? 0)} g
                  </p>
                  <p className="mt-1 text-[11px] text-tinta-suave">{receta.nutrition_method}</p>
                </div>
              )}
            </Card>
          ))}
      </div>
    </div>
  );
}
