"use client";

import Link from "next/link";
import { useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { api } from "@/lib/api";
import { GROUP_LABELS, type Food } from "@/lib/types";
import {
  Alert,
  Button,
  Card,
  EmptyState,
  Field,
  Input,
  SectionTitle,
  Select,
  TrustBadge,
  formatNumber,
  useAsync,
} from "@/components/ui";

interface TrackingItem {
  id: number;
  entry_date: string;
  kind: string;
  food_ids: string[];
  note: string | null;
}

export default function Seguimiento() {
  const { user, cargando } = useAuth();
  const { data: alimentos } = useAsync<Food[]>(() => api.get<Food[]>("/api/alimentos"), []);
  const { data: registros, reload } = useAsync<TrackingItem[]>(
    () => api.get<TrackingItem[]>("/api/perfil/seguimiento").catch(() => []),
    []
  );

  const [fecha, setFecha] = useState(new Date().toISOString().slice(0, 10));
  const [seleccion, setSeleccion] = useState<string[]>([]);
  const [nota, setNota] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function registrar(event: React.FormEvent) {
    event.preventDefault();
    setGuardando(true);
    setError(null);
    try {
      await api.post("/api/perfil/seguimiento", {
        entry_date: fecha,
        kind: "consumo",
        food_ids: seleccion,
        note: nota || null,
      });
      setSeleccion([]);
      setNota("");
      reload();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No fue posible registrar.");
    } finally {
      setGuardando(false);
    }
  }

  if (cargando) return <div className="pt-20 text-center text-tinta-suave">Cargando…</div>;
  if (!user) {
    return (
      <div className="mx-auto max-w-md pt-20 text-center">
        <h1 className="font-display text-3xl">Tu seguimiento</h1>
        <p className="mt-3 text-sm text-tinta-suave">Inicia sesión para registrar tu consumo.</p>
        <Link href="/ingresar" className="mt-6 inline-block rounded-full bg-botanico px-6 py-2.5 text-sm font-medium text-papel">
          Ingresar
        </Link>
      </div>
    );
  }

  const gruposConsumidos = new Set(
    (registros ?? []).flatMap((registro) => registro.food_ids)
  );
  const indiceDiversidad = new Set(
    (registros ?? [])
      .flatMap((registro) => registro.food_ids)
      .map((foodId) => alimentos?.find((alimento) => alimento.id === foodId)?.food_group)
      .filter(Boolean)
  ).size;

  return (
    <div className="pt-10">
      <SectionTitle
    as={"h1"}
    eyebrow="Seguimiento"
        title="Sin juicios, con datos"
        description="Registrar lo que comes ayuda a ver tu variedad alimentaria. Este registro es privado, exportable y eliminable; no cuenta calorías ni evalúa a nadie."
      />

      <Card className="px-6 py-6">
        <form onSubmit={registrar} className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-3">
            <Field label="Fecha">
              <Input type="date" value={fecha} onChange={(event) => setFecha(event.target.value)} required />
            </Field>
            <Field label="Nota (opcional)">
              <Input value={nota} onChange={(event) => setNota(event.target.value)} placeholder="Ej. almuerzo en casa" />
            </Field>
            <div className="flex items-end">
              <Button type="submit" disabled={guardando || seleccion.length === 0} className="w-full">
                {guardando ? "Guardando…" : "Registrar consumo"}
              </Button>
            </div>
          </div>
          <Field label="¿Qué consumiste hoy?" hint="Marca los alimentos del catálogo que consumiste.">
            <div className="grid max-h-72 gap-2 overflow-y-auto rounded-xl border border-borde bg-papel p-3 sm:grid-cols-3">
              {(alimentos ?? []).map((alimento) => (
                <label
                  key={alimento.id}
                  className="flex cursor-pointer items-center gap-2 rounded-lg px-2 py-1.5 text-sm hover:bg-salvia-suave/50"
                >
                  <input
                    type="checkbox"
                    checked={seleccion.includes(alimento.id)}
                    onChange={(event) =>
                      setSeleccion((prev) =>
                        event.target.checked ? [...prev, alimento.id] : prev.filter((id) => id !== alimento.id)
                      )
                    }
                    className="h-4 w-4 accent-[#3e5c47]"
                  />
                  {alimento.name_common}
                </label>
              ))}
            </div>
          </Field>
          {error && <Alert kind="danger">{error}</Alert>}
        </form>
      </Card>

      <div className="mt-8 grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <Card className="px-6 py-6">
          <h3 className="font-display text-lg">Índice experimental de diversidad</h3>
          <p className="mt-4 font-display text-5xl text-botanico">{indiceDiversidad}</p>
          <p className="mt-2 text-sm text-tinta-suave">
            grupos alimentarios distintos en tu registro histórico
          </p>
          <Alert kind="warning">
            Índice <strong>experimental</strong> con metodología simple (conteo de
            grupos del catálogo en tus registros). NO es una escala clínica validada.
          </Alert>
        </Card>

        <div>
          <h3 className="font-display text-lg">Tu historial</h3>
          {(registros ?? []).length === 0 ? (
            <div className="mt-4">
              <EmptyState
                title="Aún no hay registros"
                message="Tu primer registro aparecerá aquí. La constancia vale más que la perfección."
              />
            </div>
          ) : (
            <ul className="mt-4 space-y-3">
              {(registros ?? []).map((registro) => (
                <li key={registro.id}>
                  <Card className="px-5 py-4">
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-sm font-medium">{registro.entry_date}</p>
                      {registro.note && (
                        <p className="text-xs text-tinta-suave">{registro.note}</p>
                      )}
                    </div>
                    <p className="mt-1 text-xs text-tinta-suave">
                      {registro.food_ids
                        .map((foodId) => alimentos?.find((alimento) => alimento.id === foodId)?.name_common ?? foodId)
                        .join(" · ")}
                    </p>
                  </Card>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
