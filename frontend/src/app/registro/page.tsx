"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { Alert, Button, Card, Field, Input } from "@/components/ui";

export default function Registro() {
  const { registrarse } = useAuth();
  const router = useRouter();
  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [acepta, setAcepta] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    if (!acepta) {
      setError("El consentimiento informado es obligatorio.");
      return;
    }
    setCargando(true);
    try {
      await registrarse(email, password, acepta, nombre || undefined);
      router.push("/onboarding");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No fue posible crear la cuenta.");
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg pt-16">
      <h1 className="font-display text-3xl font-semibold">Crear cuenta</h1>
      <p className="mt-2 text-sm text-tinta-suave">
        Recogemos únicamente lo necesario para orientar tu alimentación. Puedes exportar
        o eliminar tus datos cuando quieras.
      </p>
      <Card className="mt-8 px-6 py-8">
        <form onSubmit={onSubmit} className="space-y-5" noValidate>
          <Field label="Nombre para mostrarte (opcional)">
            <Input
              value={nombre}
              onChange={(event) => setNombre(event.target.value)}
              placeholder="¿Cómo quieres que te llamemos?"
              autoComplete="nickname"
            />
          </Field>
          <Field label="Correo electrónico">
            <Input
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="tucorreo@ejemplo.com"
            />
          </Field>
          <Field
            label="Contraseña"
            hint="Mínimo 8 caracteres. Se almacena con hash PBKDF2, nunca en texto plano."
          >
            <Input
              type="password"
              required
              minLength={8}
              autoComplete="new-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="••••••••"
            />
          </Field>
          <div className="rounded-xl border border-borde bg-marfil px-4 py-3 text-sm">
            <label className="flex cursor-pointer items-start gap-3">
              <input
                type="checkbox"
                checked={acepta}
                onChange={(event) => setAcepta(event.target.checked)}
                className="mt-0.5 h-4 w-4 accent-[#3e5c47]"
              />
              <span className="text-tinta-suave">
                <strong className="text-tinta">Consentimiento informado.</strong>{" "}
                Autorizo el tratamiento de mis datos para recibir recomendaciones
                alimentarias. Los datos de salud que decida compartir se usan
                exclusivamente para proteger mi seguridad alimentaria. Puedo exportar o
                eliminar mi cuenta en cualquier momento.
              </span>
            </label>
          </div>
          {error && <Alert kind="danger">{error}</Alert>}
          <Button type="submit" disabled={cargando} className="w-full">
            {cargando ? "Creando cuenta…" : "Crear cuenta y continuar"}
          </Button>
        </form>
        <p className="mt-6 text-center text-sm text-tinta-suave">
          ¿Ya tienes cuenta?{" "}
          <Link href="/ingresar" className="font-medium text-botanico underline underline-offset-2">
            Ingresa aquí
          </Link>
        </p>
      </Card>
    </div>
  );
}
