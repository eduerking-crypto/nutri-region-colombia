"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { Alert, Button, Card, Field, Input } from "@/components/ui";

export default function Ingresar() {
  const { iniciarSesion } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setCargando(true);
    try {
      await iniciarSesion(email, password);
      router.push("/panel");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No fue posible iniciar sesión.");
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="mx-auto max-w-md pt-16">
      <h1 className="font-display text-3xl font-semibold">Ingresar</h1>
      <p className="mt-2 text-sm text-tinta-suave">
        Bienvenido de nuevo. Tus datos de salud están protegidos y nunca se comparten.
      </p>
      <Card className="mt-8 px-6 py-8">
        <form onSubmit={onSubmit} className="space-y-5" noValidate>
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
          <Field label="Contraseña">
            <Input
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="••••••••"
            />
          </Field>
          {error && <Alert kind="danger">{error}</Alert>}
          <Button type="submit" disabled={cargando} className="w-full">
            {cargando ? "Ingresando…" : "Ingresar"}
          </Button>
        </form>
        <p className="mt-6 text-center text-sm text-tinta-suave">
          ¿No tienes cuenta?{" "}
          <Link href="/registro" className="font-medium text-botanico underline underline-offset-2">
            Créala aquí
          </Link>
        </p>
      </Card>
    </div>
  );
}
