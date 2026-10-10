import type { Metadata } from "next";
import { Fraunces, Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/components/auth-provider";
import { Header } from "@/components/header";

const display = Fraunces({
  subsets: ["latin"],
  variable: "--fuente-display",
});

const body = Inter({
  subsets: ["latin"],
  variable: "--fuente-body",
});

export const metadata: Metadata = {
  title: {
    default: "NutriRegión Colombia",
    template: "%s — NutriRegión Colombia",
  },
  description:
    "Recomendaciones alimentarias con evidencia trazable, adaptadas a tu territorio, presupuesto y cultura gastronómica. Datos con capas de confianza visibles.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es-CO" className={`${display.variable} ${body.variable}`}>
      <body className="min-h-screen bg-marfil text-tinta antialiased">
        <AuthProvider>
          <a
            href="#contenido"
            className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-botanico focus:px-4 focus:py-2 focus:text-papel"
          >
            Saltar al contenido principal
          </a>
          <Header />
          <main id="contenido" className="mx-auto w-full max-w-6xl px-4 pb-20 sm:px-6">
            {children}
          </main>
          <footer className="border-t border-borde bg-papel">
            <div className="mx-auto max-w-6xl px-4 py-10 text-sm text-tinta-suave sm:px-6">
              <p className="font-display text-base text-tinta">NutriRegión Colombia</p>
              <p className="mt-2 max-w-2xl">
                Plataforma de nutrición territorial con rigor científico. Los datos de
                composición provienen de fuentes verificadas con fecha de consulta y capa
                de confianza visibles. Referencias OMS/OPS citadas como normativa de
                diseño; sin aval institucional. No sustituye atención profesional de salud.
              </p>
              <p className="mt-3 text-xs">
                Reglas clínicas candidatas pendientes de validación profesional ·{" "}
                <a href="/evidencia" className="underline hover:text-botanico">
                  ver transparencia del sistema
                </a>
              </p>
            </div>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
