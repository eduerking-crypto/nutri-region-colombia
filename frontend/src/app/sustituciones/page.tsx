"use client";

import Link from "next/link";
import { useState } from "react";
import { api } from "@/lib/api";
import type { Food } from "@/lib/types";
import {
  Card,
  EmptyState,
  Field,
  SectionTitle,
  Select,
  SkeletonList,
  useAsync,
} from "@/components/ui";

export default function Sustituciones() {
  const { data: alimentos, loading } = useAsync<Food[]>(
    () => api.get<Food[]>("/api/alimentos"),
    []
  );
  const [target, setTarget] = useState("");

  const { data: resultado, loading: cargando } = useAsync<{
    target: { food_id: string; name: string; food_group: string };
    sustituciones: { food_id: string; name: string; reason: string; distance: number }[];
    aviso: string;
  } | null>(
    () =>
      target
        ? api.get(`/api/alimentos/${target}/sustituciones`)
        : Promise.resolve(null),
    [target]
  );

  return (
    <div className="pt-10">
      <SectionTitle
    as={"h1"}
    eyebrow="Comparador"
        title="Sustituciones con criterio, no con recetas mágicas"
        description="Buscamos alternativas del mismo grupo alimentario con composición similar (distancia sobre macro y energía). Si tienes alergias, los alérgenos quedan excluidos."
      />
      <Card className="px-6 py-6">
        <Field label="¿Qué alimento quieres sustituir?">
          <Select value={target} onChange={(event) => setTarget(event.target.value)}>
            <option value="">Selecciona un alimento…</option>
            {(alimentos ?? []).map((alimento) => (
              <option key={alimento.id} value={alimento.id}>
                {alimento.name_common}
              </option>
            ))}
          </Select>
        </Field>
      </Card>

      {loading && <div className="mt-8"><SkeletonList count={3} /></div>}
      {!loading && !target && (
        <div className="mt-8">
          <EmptyState
            title="Elige un alimento para ver alternativas"
            message="El comparador prioriza lo que ya conoces: mismo grupo, composición parecida, disponible en tu territorio."
          />
        </div>
      )}
      {target && resultado && (
        <div className="mt-8">
          {resultado.sustituciones.length === 0 ? (
            <EmptyState
              title="Sin sustituciones disponibles aún"
              message="El catálogo real es pequeño y crece con fuentes verificadas. Es preferible a llenar la pantalla con datos inventados."
            />
          ) : (
            <>
              <p className="text-sm text-tinta-suave">{resultado.aviso}</p>
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                {resultado.sustituciones.map((sustitucion) => (
                  <Card key={sustitucion.food_id} className="px-5 py-5">
                    <Link
                      href={`/alimentos/${sustitucion.food_id}`}
                      className="font-display text-lg text-botanico hover:underline"
                    >
                      {sustitucion.name}
                    </Link>
                    <p className="mt-2 text-xs text-tinta-suave">{sustitucion.reason}</p>
                  </Card>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
