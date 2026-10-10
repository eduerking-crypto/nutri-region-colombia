"use client";

import Link from "next/link";
import { useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { api } from "@/lib/api";
import type { Plan, Profile } from "@/lib/types";
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
  formatCop,
  useAsync,
} from "@/components/ui";

interface CostoItem {
  food_id: string;
  name: string;
  grams: number;
  price_cop: number | null;
  price_date?: string;
  data_type?: string;
  aviso?: string;
}

interface CostoPlan {
  total_cop: number | null;
  items_con_precio: number;
  items_sin_precio: number;
  aviso: string;
  items: CostoItem[];
}

export default function Presupuesto() {
  const { user, cargando } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [costo, setCosto] = useState<CostoPlan | null>(null);
  const [calculando, setCalculando] = useState(false);

  // Formulario de observación de precio
  const { data: alimentos } = useAsync<{ id: string; name_common: string }[]>(
    () => api.get("/api/alimentos"),
    []
  );
  const { data: perfil } = useAsync<Profile | null>(
    () => api.get<Profile>("/api/perfil").catch(() => null),
    []
  );
  const { data: precios, reload: recargarPrecios } = useAsync<
    { id: number; product_desc: string; municipality: string; commercial_unit: string; price_cop: number; observed_at: string; data_type: string; source_desc: string }[]
  >(
    () =>
      api
        .get<{ id: number; product_desc: string; municipality: string; commercial_unit: string; price_cop: number; observed_at: string; data_type: string; source_desc: string }[]>(
          "/api/presupuesto/precios"
        )
        .catch((): { id: number; product_desc: string; municipality: string; commercial_unit: string; price_cop: number; observed_at: string; data_type: string; source_desc: string }[] => []),
    []
  );

  const [planId, setPlanId] = useState("");
  const { data: historial } = useAsync<{ plan_id: number; created_at: string }[]>(
    () =>
      api
        .get<{ plan_id: number; created_at: string }[]>("/api/planificador/historial")
        .catch((): { plan_id: number; created_at: string }[] => []),
    []
  );

  const [form, setForm] = useState({
    food_id: "",
    product_desc: "",
    municipality: "",
    commercial_unit: "libra",
    price_cop: "",
    observed_at: new Date().toISOString().slice(0, 10),
    source_desc: "Observación propia en plaza de mercado",
  });
  const [guardandoPrecio, setGuardandoPrecio] = useState(false);
  const [precioGuardado, setPrecioGuardado] = useState(false);

  async function calcularCosto() {
    setCalculando(true);
    setError(null);
    try {
      const resultado = await api.post<CostoPlan>(`/api/presupuesto/${planId}/costo`);
      setCosto(resultado);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No fue posible calcular el costo.");
    } finally {
      setCalculando(false);
    }
  }

  async function guardarPrecio(event: React.FormEvent) {
    event.preventDefault();
    setGuardandoPrecio(true);
    setError(null);
    try {
      await api.post("/api/presupuesto/precios", {
        ...form,
        price_cop: Number(form.price_cop),
        data_type: "observado",
      });
      setPrecioGuardado(true);
      setForm({ ...form, product_desc: "", price_cop: "" });
      recargarPrecios();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No fue posible registrar el precio.");
    } finally {
      setGuardandoPrecio(false);
    }
  }

  if (cargando) return <div className="pt-20 text-center text-tinta-suave">Cargando…</div>;
  if (!user) {
    return (
      <div className="mx-auto max-w-md pt-20 text-center">
        <h1 className="font-display text-3xl">Presupuesto honesto</h1>
        <p className="mt-3 text-sm text-tinta-suave">Inicia sesión para calcular costos de tus planes.</p>
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
    eyebrow="Presupuesto"
        title="Cada peso, con fecha y fuente"
        description="Solo sumamos precios observados o publicados con fecha. Sin datos, lo decimos expresamente: la plataforma nunca interpola precios por ubicación."
      />

      {historial && historial.length === 0 ? (
        <EmptyState
          title="Primero genera un plan"
          message="La lista de compras y su costo se calculan sobre un plan tuyo."
          action={
            <Link href="/planificador" className="rounded-full bg-botanico px-5 py-2.5 text-sm font-medium text-papel">
              Ir al planificador
            </Link>
          }
        />
      ) : (
        <Card className="px-6 py-6">
          <div className="flex flex-wrap items-end gap-3">
            <Field label="Plan a costear">
              <Select value={planId} onChange={(event) => setPlanId(event.target.value)}>
                <option value="">Selecciona un plan…</option>
                {historial?.map((item) => (
                  <option key={item.plan_id} value={item.plan_id}>
                    #{item.plan_id} — {new Date(item.created_at).toLocaleString("es-CO")}
                  </option>
                ))}
              </Select>
            </Field>
            <Button onClick={calcularCosto} disabled={!planId || calculando}>
              {calculando ? "Calculando…" : "Calcular costo"}
            </Button>
          </div>
        </Card>
      )}

      {costo && (
        <div className="mt-8">
          <Alert kind={costo.items_sin_precio > 0 ? "warning" : "success"}>
            {costo.aviso}
          </Alert>
          <Card className="mt-4 px-6 py-6">
            <div className="flex items-baseline justify-between">
              <h3 className="font-display text-lg">Lista de compras consolidada</h3>
              <p className="text-2xl font-semibold text-botanico">{formatCop(costo.total_cop)}</p>
            </div>
            <table className="mt-4 w-full text-sm">
              <thead>
                <tr className="border-b border-borde text-left text-xs text-tinta-suave">
                  <th className="pb-2 font-medium">Alimento</th>
                  <th className="pb-2 font-medium">Cantidad</th>
                  <th className="pb-2 font-medium">Precio</th>
                  <th className="pb-2 font-medium">Dato</th>
                </tr>
              </thead>
              <tbody>
                {costo.items.map((item) => (
                  <tr key={item.food_id} className="border-b border-borde/60">
                    <td className="py-2.5">
                      <Link href={`/alimentos/${item.food_id}`} className="hover:text-botanico hover:underline">
                        {item.name}
                      </Link>
                    </td>
                    <td className="py-2.5 text-tinta-suave">{item.grams} g</td>
                    <td className="py-2.5 font-medium">{formatCop(item.price_cop)}</td>
                    <td className="py-2.5 text-xs text-tinta-suave">
                      {item.price_cop !== null ? (
                        <>
                          {item.data_type} · {item.price_date}{" "}
                          {item.aviso && <span className="text-ambar">({item.aviso})</span>}
                        </>
                      ) : (
                        item.aviso
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      )}

      {/* Registro de precios por la comunidad */}
      <div className="mt-12 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <Card className="px-6 py-6">
          <h3 className="font-display text-lg">Aporta un precio observado</h3>
          <p className="mt-2 text-sm text-tinta-suave">
            Los precios territoriales reales son el dato más difícil de conseguir. Si
            viste un precio en tu plaza, regístralo: queda con fecha, tipo de dato
            (observado) y tu autoría anónima.
          </p>
          <form onSubmit={guardarPrecio} className="mt-4 space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Alimento">
                <Select
                  required
                  value={form.food_id}
                  onChange={(event) => setForm({ ...form, food_id: event.target.value })}
                >
                  <option value="">Selecciona…</option>
                  {alimentos?.map((alimento) => (
                    <option key={alimento.id} value={alimento.id}>
                      {alimento.name_common}
                    </option>
                  ))}
                </Select>
              </Field>
              <Field label="Descripción del producto">
                <Input
                  required
                  value={form.product_desc}
                  onChange={(event) => setForm({ ...form, product_desc: event.target.value })}
                  placeholder="Ej. Yuca por libra, plaza central"
                />
              </Field>
              <Field label="Municipio">
                <Input
                  required
                  value={form.municipality}
                  onChange={(event) => setForm({ ...form, municipality: event.target.value })}
                  placeholder={perfil?.municipality ?? "Ej. Sincelejo"}
                />
              </Field>
              <Field label="Unidad comercial">
                <Select
                  value={form.commercial_unit}
                  onChange={(event) => setForm({ ...form, commercial_unit: event.target.value })}
                >
                  <option value="libra">Libra</option>
                  <option value="unidad">Unidad</option>
                  <option value="kilo">Kilo</option>
                  <option value="arroba">Arroba</option>
                </Select>
              </Field>
              <Field label="Precio (COP)">
                <Input
                  required
                  type="number"
                  min={1}
                  value={form.price_cop}
                  onChange={(event) => setForm({ ...form, price_cop: event.target.value })}
                  placeholder="Ej. 2500"
                />
              </Field>
              <Field label="Fecha de observación">
                <Input
                  required
                  type="date"
                  value={form.observed_at}
                  onChange={(event) => setForm({ ...form, observed_at: event.target.value })}
                />
              </Field>
            </div>
            {precioGuardado && <Alert kind="success">Precio registrado. ¡Gracias por alimentar datos reales!</Alert>}
            {error && <Alert kind="danger">{error}</Alert>}
            <Button type="submit" disabled={guardandoPrecio}>
              {guardandoPrecio ? "Guardando…" : "Registrar precio"}
            </Button>
          </form>
        </Card>

        <Card className="px-6 py-6">
          <h3 className="font-display text-lg">Precios registrados</h3>
          {precios && precios.length > 0 ? (
            <ul className="mt-4 space-y-3 text-sm">
              {precios.slice(0, 8).map((precio) => (
                <li key={precio.id} className="rounded-lg bg-marfil px-4 py-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-medium">{precio.product_desc}</span>
                    <span className="font-semibold">{formatCop(precio.price_cop)}</span>
                  </div>
                  <p className="mt-1 text-xs text-tinta-suave">
                    {precio.municipality} · {precio.commercial_unit} · observado el{" "}
                    {precio.observed_at}
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <div className="mt-4">
              <Alert kind="info">
                Aún no hay precios observados en el sistema. El presupuesto funcionará
                en modo "sin datos" — por diseño, no inventamos precios.
              </Alert>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
