"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { api } from "@/lib/api";
import type { Estado } from "@/lib/types";

const NAV = [
  { href: "/alimentos", label: "Alimentos" },
  { href: "/recetas", label: "Recetas" },
  { href: "/planificador", label: "Planificador" },
  { href: "/evidencia", label: "Evidencia" },
];

const NAV_USER = [
  { href: "/panel", label: "Mi panel" },
  { href: "/seguimiento", label: "Seguimiento" },
];

export function Header() {
  const { user, cerrarSesion, cargando } = useAuth();
  const pathname = usePathname();
  const [estado, setEstado] = useState<Estado | null>(null);
  const [menuAbierto, setMenuAbierto] = useState(false);

  useEffect(() => {
    api
      .get<Estado>("/api/auth/estado")
      .then(setEstado)
      .catch(() => setEstado(null));
  }, [pathname]);

  return (
    <header className="sticky top-0 z-40 border-b border-borde bg-marfil/90 backdrop-blur">
      {estado?.pilot_mode && (
        <div className="bg-tierra-suave px-4 py-1.5 text-center text-xs text-tierra">
          <strong>Modo piloto:</strong> las reglas clínicas están pendientes de validación
          profesional. Cada resultado muestra qué reglas se aplicaron.{" "}
          <Link href="/evidencia" className="underline underline-offset-2">
            Ver reglas
          </Link>
        </div>
      )}
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <Link href="/" className="flex items-center gap-2" aria-label="NutriRegión Colombia — inicio">
          <span aria-hidden className="flex h-9 w-9 items-center justify-center rounded-full bg-botanico font-display text-lg text-papel">
            N
          </span>
          <span className="font-display text-lg font-semibold text-tinta">
            NutriRegión <span className="text-salvia">Colombia</span>
          </span>
        </Link>

        <nav aria-label="Navegación principal" className="hidden items-center gap-1 md:flex">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`rounded-full px-4 py-2 text-sm transition-colors ${
                pathname.startsWith(item.href)
                  ? "bg-salvia-suave font-medium text-botanico"
                  : "text-tinta-suave hover:bg-papel hover:text-tinta"
              }`}
            >
              {item.label}
            </Link>
          ))}
          {!cargando && user && NAV_USER.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`rounded-full px-4 py-2 text-sm transition-colors ${
                pathname.startsWith(item.href)
                  ? "bg-salvia-suave font-medium text-botanico"
                  : "text-tinta-suave hover:bg-papel hover:text-tinta"
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          {!cargando && user ? (
            <div className="flex items-center gap-2">
              {user.role !== "usuario" && (
                <Link
                  href={user.role === "admin" ? "/admin" : "/profesional"}
                  className="hidden rounded-full border border-tierra bg-tierra-suave px-3 py-1.5 text-xs font-medium text-tierra sm:block"
                >
                  {user.role === "admin" ? "Administración" : "Panel profesional"}
                </Link>
              )}
              <Link href="/configuracion" className="hidden text-sm text-tinta-suave hover:text-tinta sm:block">
                {user.display_name ?? user.email}
              </Link>
              <button
                onClick={cerrarSesion}
                className="rounded-full px-3 py-1.5 text-sm text-tinta-suave transition-colors hover:bg-papel hover:text-tinta"
              >
                Salir
              </button>
            </div>
          ) : (
            !cargando && (
              <div className="flex items-center gap-2">
                <Link
                  href="/ingresar"
                  className="rounded-full px-3 py-2 text-sm text-tinta-suave hover:text-tinta"
                >
                  Ingresar
                </Link>
                <Link
                  href="/registro"
                  className="rounded-full bg-botanico px-4 py-2 text-sm font-medium text-papel transition-colors hover:bg-botanico-oscuro"
                >
                  Crear cuenta
                </Link>
              </div>
            )
          )}
          <button
            className="rounded-lg p-2 text-tinta md:hidden"
            aria-expanded={menuAbierto}
            aria-label="Abrir menú"
            onClick={() => setMenuAbierto(!menuAbierto)}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
              {menuAbierto ? <path d="M6 6l12 12M18 6L6 18" /> : <path d="M4 7h16M4 12h16M4 17h16" />}
            </svg>
          </button>
        </div>
      </div>

      {menuAbierto && (
        <nav aria-label="Navegación móvil" className="border-t border-borde bg-papel px-4 py-3 md:hidden">
          {[...NAV, ...(user ? NAV_USER : [])].map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMenuAbierto(false)}
              className="block rounded-lg px-3 py-2.5 text-sm text-tinta hover:bg-salvia-suave"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      )}
    </header>
  );
}
