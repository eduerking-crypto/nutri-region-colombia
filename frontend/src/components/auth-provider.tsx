"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, setToken } from "@/lib/api";
import type { UserMe } from "@/lib/types";

interface AuthState {
  user: UserMe | null;
  cargando: boolean;
  iniciarSesion: (email: string, password: string) => Promise<void>;
  registrarse: (
    email: string,
    password: string,
    acepta: boolean,
    nombre?: string
  ) => Promise<void>;
  cerrarSesion: () => void;
  refrescar: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserMe | null>(null);
  const [cargando, setCargando] = useState(true);

  const refrescar = useCallback(async () => {
    try {
      const me = await api.get<UserMe>("/api/auth/me");
      setUser(me);
    } catch {
      setUser(null);
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    void refrescar();
  }, [refrescar]);

  const iniciarSesion = useCallback(
    async (email: string, password: string) => {
      const response = await api.post<{ access_token: string }>("/api/auth/login", {
        email,
        password,
      });
      setToken(response.access_token);
      await refrescar();
    },
    [refrescar]
  );

  const registrarse = useCallback(
    async (email: string, password: string, acepta: boolean, nombre?: string) => {
      const response = await api.post<{ access_token: string }>("/api/auth/registro", {
        email,
        password,
        accept_consent: acepta,
        display_name: nombre ?? null,
      });
      setToken(response.access_token);
      await refrescar();
    },
    [refrescar]
  );

  const cerrarSesion = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, cargando, iniciarSesion, registrarse, cerrarSesion, refrescar }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return context;
}
