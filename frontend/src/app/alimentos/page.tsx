"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { api } from "@/lib/api";
import { GROUP_LABELS, REGION_LABELS, type Food } from "@/lib/types";
import {
  Card,
  EmptyState,
  SkeletonList,
  TrustBadge,
  formatNumber,
  useAsync,
} from "@/components/ui";

export default function ExploradorAlimentos() {
  const [busqueda, setBusqueda] = useState("");
  const [grupo, setGrupo] = useState("");
  const [region, setRegion] = useState("");

  const { data: alimentos, loading, error, reload } = useAsync<Food[]>(
    () => api.get<Food[]>("/api/alimentos"),
    []
  );
  const { data: grupos } = useAsync<{ group: string; total: number }[]>(
    () => api.get("/api/alimentos/grupos"),
    []
  );

  const filtrados = useMemo(() => {
    if (!alimentos) return [];
    return alimentos.filter((alimento) => {
      if (grupo && alimento.food_group !== grupo) return false;
      if (region && !alimento.region_associations.includes(region)) return false;
      if (busqueda) {
        const needle = busqueda.toLowerCase();
        const inName = alimento.name_common.toLowerCase().includes(needle);
        const inVariants = alimento.name_variants.some((variant) =>
          variant.toLowerCase().includes(needle)
        );
        if (!inName && !inVariants) return false;
      }
      return true;
    });
  }, [alimentos, grupo, region, busqueda]);

  return (
    <div className="pt-10">
      <h1 className="font-display text-3xl font-semibold sm:text-4xl">Explorador de alimentos</h1>
      <p className="mt-2 max-w-2xl text-sm text-tinta-suave">
        Catálogo con datos reales y trazables de USDA FoodData Central. Cada ficha
        muestra composición por 100 g, capa de confianza, fuente y fecha de consulta.
        Sin datos inventados.
      </p>

      <div className="mt-8 flex flex-wrap items-end gap-3">
        <label className="flex-1 basis-56">
          <span className="sr-only">Buscar alimento</span>
          <input
            type="search"
            value={busqueda}
            onChange={(event) => setBusqueda(event.target.value)}
            placeholder="Buscar: yuca, arroz, frijol…"
            className="w-full rounded-full border border-borde bg-papel px-5 py-2.5 text-sm focus:border-salvia"
          />
        </label>
        <label>
          <span className="sr-only">Filtrar por grupo</span>
          <select
            value={grupo}
            onChange={(event) => setGrupo(event.target.value)}
            className="rounded-full border border-borde bg-papel px-4 py-2.5 text-sm"
          >
            <option value="">Todos los grupos</option>
            {(grupos ?? []).map((item) => (
              <option key={item.group} value={item.group}>
                {GROUP_LABELS[item.group] ?? item.group} ({item.total})
              </option>
            ))}
          </select>
        </label>
        <label>
          <span className="sr-only">Filtrar por región</span>
          <select
            value={region}
            onChange={(event) => setRegion(event.target.value)}
            className="rounded-full border border-borde bg-papel px-4 py-2.5 text-sm"
          >
            <option value="">Todas las regiones</option>
            {Object.entries(REGION_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <button
          onClick={reload}
          className="rounded-full border border-borde bg-papel px-4 py-2.5 text-sm text-tinta-suave hover:text-tinta"
          aria-label="Recargar datos"
        >
          Actualizar
        </button>
      </div>

      <div className="mt-8">
        {loading && <SkeletonList count={6} />}
        {error && (
          <EmptyState
            title="No pudimos cargar los alimentos"
            message={`Verifica que el servidor esté corriendo (${error}).`}
            action={
              <button onClick={reload} className="text-sm font-medium text-botanico underline">
                Reintentar
              </button>
            }
          />
        )}
        {!loading && !error && filtrados.length === 0 && (
          <EmptyState
            title="Sin resultados con esos filtros"
            message="El catálogo real aún es pequeño y crece conforme se verifican fuentes. Prueba quitando filtros."
          />
        )}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {!loading &&
            !error &&
            filtrados.map((alimento) => (
              <Link key={alimento.id} href={`/alimentos/${alimento.id}`} className="group">
                <Card className="h-full px-5 py-5 transition-all duration-200 group-hover:-translate-y-1 group-hover:border-salvia motion-reduce:transition-none">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-[11px] font-semibold uppercase tracking-widest text-salvia">
                        {GROUP_LABELS[alimento.food_group] ?? alimento.food_group}
                      </p>
                      <h2 className="mt-1 font-display text-xl leading-tight text-tinta">
                        {alimento.name_common}
                      </h2>
                    </div>
                    <TrustBadge tier={alimento.trust_tier} />
                  </div>
                  <dl className="mt-4 grid grid-cols-2 gap-2 text-sm">
                    <div className="rounded-lg bg-marfil px-3 py-2">
                      <dt className="text-[11px] text-tinta-suave">Energía</dt>
                      <dd className="font-medium">
                        {alimento.energia_kcal === null
                          ? "Sin datos"
                          : `${formatNumber(alimento.energia_kcal)} kcal/100 g`}
                      </dd>
                    </div>
                    <div className="rounded-lg bg-marfil px-3 py-2">
                      <dt className="text-[11px] text-tinta-suave">Proteína</dt>
                      <dd className="font-medium">
                        {alimento.proteina_g === null
                          ? "Sin datos"
                          : `${formatNumber(alimento.proteina_g)} g/100 g`}
                      </dd>
                    </div>
                  </dl>
                  <div className="mt-4 flex items-center justify-between text-xs text-tinta-suave">
                    <span>
                      Fuente: {alimento.source_id.replace("SRC-", "")} · consultado{" "}
                      {alimento.retrieved_at}
                    </span>
                    <span aria-hidden className="text-botanico transition-transform group-hover:translate-x-0.5">
                      →
                    </span>
                  </div>
                </Card>
              </Link>
            ))}
        </div>
      </div>
    </div>
  );
}
