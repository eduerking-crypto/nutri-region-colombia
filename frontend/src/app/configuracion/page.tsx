"use client";

import Link from "next/link";
import { useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { api } from "@/lib/api";
import type { UserMe } from "@/lib/types";
import { Alert, Button, Card, SectionTitle } from "@/components/ui";

export default function Configuracion() {
  const { user, cargando, cerrarSesion, refrescar } = useAuth();
  const [exportado, setExportado] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [confirmando, setConfirmando] = useState(false);

  async function exportarDatos() {
    setError(null);
    try {
      const datos = await api.get<Record<string, unknown>>("/api/configuracion/datos");
      const blob = new Blob([JSON.stringify(datos, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `nutriregion-mis-datos-${new Date().toISOString().slice(0, 10)}.json`;
      link.click();
      URL.revokeObjectURL(url);
      setExportado("Tus datos fueron exportados. Se descargaron como archivo JSON.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No fue posible exportar.");
    }
  }

  async function eliminarCuenta() {
    setError(null);
    try {
      await api.delete("/api/configuracion/cuenta");
      refrescar();
      window.location.href = "/";
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No fue posible eliminar la cuenta.");
    }
  }

  if (cargando) return <div className="pt-20 text-center text-tinta-suave">Cargando…</div>;
  if (!user) {
    return (
      <div className="mx-auto max-w-md pt-20 text-center">
        <h1 className="font-display text-3xl">Configuración</h1>
        <p className="mt-3 text-sm text-tinta-suave">Inicia sesión para gestionar tus datos.</p>
        <Link href="/ingresar" className="mt-6 inline-block rounded-full bg-botanico px-6 py-2.5 text-sm font-medium text-papel">
          Ingresar
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl pt-10">
      <SectionTitle
        eyebrow="Privacidad"
        title="Tus datos son tuyos"
        description="Ejercicio de tus derechos: acceso (exportación) y supresión (eliminación total). Sin letra pequeña."
      />

      <Card className="px-6 py-6">
        <h3 className="text-sm font-semibold">Tu cuenta</h3>
        <p className="mt-2 text-sm text-tinta-suave">
          {user.email} · rol: {user.role} · consentimiento: {user.consent_version ?? "—"}
        </p>
      </Card>

      <Card className="mt-6 px-6 py-6">
        <h3 className="text-sm font-semibold">Exportar mis datos</h3>
        <p className="mt-2 text-sm text-tinta-suave">
          Descarga todo lo que tenemos de ti: perfil, alergias, indicadores de salud,
          planes y seguimiento. Formato JSON legible.
        </p>
        <Button variant="secondary" className="mt-4" onClick={exportarDatos}>
          Descargar mis datos
        </Button>
        {exportado && <div className="mt-3"><Alert kind="success">{exportado}</Alert></div>}
      </Card>

      <Card className="mt-6 border-alerta/30 px-6 py-6">
        <h3 className="text-sm font-semibold text-alerta">Eliminar mi cuenta</h3>
        <p className="mt-2 text-sm text-tinta-suave">
          Se eliminan permanentemente tu perfil, alergias, indicadores de salud, planes y
          seguimiento. En el registro de auditoría queda solo el hecho de la eliminación,
          sin datos personales.
        </p>
        {!confirmando ? (
          <Button variant="danger" className="mt-4" onClick={() => setConfirmando(true)}>
            Quiero eliminar mi cuenta
          </Button>
        ) : (
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <Button variant="danger" onClick={eliminarCuenta}>
              Confirmar eliminación definitiva
            </Button>
            <Button variant="ghost" onClick={() => setConfirmando(false)}>
              Cancelar
            </Button>
          </div>
        )}
      </Card>

      {error && <div className="mt-4"><Alert kind="danger">{error}</Alert></div>}

      <div className="mt-6">
        <Button variant="ghost" onClick={cerrarSesion}>
          Cerrar sesión en este dispositivo
        </Button>
      </div>
    </div>
  );
}
