"use client";

import { useEffect, useState } from "react";
import { TRUST_DESCRIPTIONS, TRUST_LABELS, type TrustTier } from "@/lib/types";

/* ============ Botones ============ */
type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";

export function Button({
  variant = "primary",
  className = "",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: ButtonVariant }) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-full px-5 py-2.5 text-sm font-medium transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-50 motion-safe:hover:-translate-y-0.5";
  const styles: Record<ButtonVariant, string> = {
    primary: "bg-botanico text-papel hover:bg-botanico-oscuro shadow-sm",
    secondary: "border border-borde bg-papel text-tinta hover:border-salvia hover:bg-salvia-suave/50",
    ghost: "text-botanico hover:bg-salvia-suave",
    danger: "bg-alerta text-white hover:opacity-90",
  };
  return <button className={`${base} ${styles[variant]} ${className}`} {...props} />;
}

/* ============ Tarjetas ============ */
export function Card({
  className = "",
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div
      className={`rounded-[var(--radius-card)] border border-borde bg-papel shadow-[0_1px_3px_rgba(43,42,38,0.04)] ${className}`}
    >
      {children}
    </div>
  );
}

export function SectionTitle({
  eyebrow,
  title,
  description,
  as = "h2",
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  as?: "h1" | "h2";
}) {
  const Heading = as;
  return (
    <div className="mb-6">
      {eyebrow && (
        <p className="mb-1 text-xs font-semibold uppercase tracking-[0.18em] text-salvia">
          {eyebrow}
        </p>
      )}
      <Heading className="text-2xl font-semibold text-tinta sm:text-3xl">{title}</Heading>
      {description && <p className="mt-2 max-w-2xl text-sm text-tinta-suave">{description}</p>}
    </div>
  );
}

/* ============ Capas de confianza (ADR-0005) ============ */
const TRUST_STYLES: Record<TrustTier, { bg: string; text: string; border: string }> = {
  medido: { bg: "bg-salvia-suave", text: "text-botanico", border: "border-salvia" },
  estimado: { bg: "bg-ambar-fondo", text: "text-ambar", border: "border-[#e3c98f]" },
  literatura: { bg: "bg-[#e1e9ee]", text: "text-[#4d6577]", border: "border-[#b8cad6]" },
  educativo: { bg: "bg-tierra-suave", text: "text-tierra", border: "border-[#d5c3a8]" },
};

export function TrustBadge({
  tier,
  size = "sm",
  withIcon = true,
}: {
  tier: TrustTier;
  size?: "sm" | "md";
  withIcon?: boolean;
}) {
  const style = TRUST_STYLES[tier];
  const sizes = size === "sm" ? "px-2 py-0.5 text-[11px]" : "px-3 py-1 text-xs";
  return (
    <span
      title={TRUST_DESCRIPTIONS[tier]}
      className={`inline-flex items-center gap-1 rounded-full border font-medium ${style.bg} ${style.text} ${style.border} ${sizes}`}
    >
      {withIcon && <span aria-hidden>●</span>}
      {TRUST_LABELS[tier]}
    </span>
  );
}

/* ============ Estados ============ */
export function EmptyState({
  title,
  message,
  action,
}: {
  title: string;
  message: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center rounded-[var(--radius-card)] border border-dashed border-borde bg-papel/60 px-6 py-14 text-center">
      <div aria-hidden className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-salvia-suave text-xl text-botanico">
        ◌
      </div>
      <p className="font-display text-lg text-tinta">{title}</p>
      <p className="mt-2 max-w-md text-sm text-tinta-suave">{message}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}

export function Skeleton({ className = "" }: { className?: string }) {
  return (
    <div
      aria-hidden
      className={`animate-pulse rounded-lg bg-borde/60 ${className}`}
    />
  );
}

export function SkeletonList({ count = 4 }: { count?: number }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3" aria-busy="true" aria-label="Cargando datos">
      {Array.from({ length: count }).map((_, index) => (
        <Skeleton key={index} className="h-40" />
      ))}
    </div>
  );
}

/* ============ Alertas y mensajes de seguridad ============ */
type AlertKind = "info" | "warning" | "danger" | "success" | "pilot";

const ALERT_STYLES: Record<AlertKind, string> = {
  info: "bg-[#e1e9ee] text-[#3a4d5c] border-[#b8cad6]",
  warning: "bg-ambar-fondo text-ambar border-[#e3c98f]",
  danger: "bg-alerta-fondo text-alerta border-[#e6b3aa]",
  success: "bg-exito-fondo text-exito border-salvia",
  pilot: "bg-tierra-suave text-tierra border-[#d5c3a8]",
};

export function Alert({
  kind = "info",
  title,
  children,
}: {
  kind?: AlertKind;
  title?: string;
  children: React.ReactNode;
}) {
  return (
    <div
      role={kind === "danger" ? "alert" : "status"}
      className={`rounded-xl border px-4 py-3 text-sm ${ALERT_STYLES[kind]}`}
    >
      {title && <p className="mb-1 font-semibold">{title}</p>}
      <div>{children}</div>
    </div>
  );
}

/* ============ Formularios ============ */
export function Field({
  label,
  hint,
  error,
  children,
}: {
  label: string;
  hint?: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium text-tinta">{label}</span>
      {children}
      {hint && !error && <span className="mt-1 block text-xs text-tinta-suave">{hint}</span>}
      {error && (
        <span role="alert" className="mt-1 block text-xs font-medium text-alerta">
          {error}
        </span>
      )}
    </label>
  );
}

export const inputClass =
  "w-full rounded-lg border border-borde bg-papel px-3.5 py-2.5 text-sm text-tinta placeholder:text-tinta-suave/60 focus:border-salvia";

export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={`${inputClass} ${props.className ?? ""}`} />;
}

export function Select(props: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return <select {...props} className={`${inputClass} ${props.className ?? ""}`} />;
}

export function Textarea(props: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea {...props} className={`${inputClass} ${props.className ?? ""}`} />;
}

/* ============ Progreso (onboarding) ============ */
export function ProgressSteps({
  steps,
  current,
}: {
  steps: string[];
  current: number;
}) {
  return (
    <ol className="mb-8 flex items-center gap-2" aria-label="Progreso del cuestionario">
      {steps.map((step, index) => {
        const state = index < current ? "done" : index === current ? "active" : "todo";
        return (
          <li key={step} className="flex flex-1 items-center gap-2">
            <span
              aria-current={state === "active" ? "step" : undefined}
              className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full border text-xs font-semibold ${
                state === "done"
                  ? "border-botanico bg-botanico text-papel"
                  : state === "active"
                    ? "border-botanico bg-salvia-suave text-botanico"
                    : "border-borde bg-papel text-tinta-suave"
              }`}
            >
              {state === "done" ? "✓" : index + 1}
            </span>
            <span
              className={`hidden text-xs sm:block ${
                state === "todo" ? "text-tinta-suave/60" : "text-tinta"
              }`}
            >
              {step}
            </span>
            {index < steps.length - 1 && <span aria-hidden className="h-px flex-1 bg-borde" />}
          </li>
        );
      })}
    </ol>
  );
}

/* ============ Aparicion progresiva con Motion ============ */
import { motion, useReducedMotion } from "framer-motion";

export function Reveal({
  children,
  delay = 0,
  className = "",
}: {
  children: React.ReactNode;
  delay?: number;
  className?: string;
}) {
  const reduced = useReducedMotion();
  if (reduced) return <div className={className}>{children}</div>;
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.21, 0.47, 0.32, 0.98] }}
    >
      {children}
    </motion.div>
  );
}

/* ============ Utilidades ============ */
export function useAsync<T>(loader: () => Promise<T>, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    loader()
      .then((result) => {
        if (!cancelled) {
          setData(result);
          setError(null);
        }
      })
      .catch((cause: unknown) => {
        if (!cancelled) setError(cause instanceof Error ? cause.message : "Error inesperado");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, reloadKey]);

  return { data, error, loading, reload: () => setReloadKey((key) => key + 1) };
}

export function formatCop(value: number | null | undefined): string {
  if (value === null || value === undefined) return "Sin datos";
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatNumber(value: number | null | undefined, unit?: string): string {
  if (value === null || value === undefined) return "Sin datos";
  const formatted = new Intl.NumberFormat("es-CO", { maximumFractionDigits: 2 }).format(value);
  return unit ? `${formatted} ${unit}` : formatted;
}
