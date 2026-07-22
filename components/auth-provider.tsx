"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { SessionUser } from "@/lib/auth-session";
import { apiRequest, USE_MOCK_DATA } from "@/lib/api-client";
import { mapAuthMe, mapUser, type BackendAuthMe, type BackendMfaStatus, type BackendUser } from "@/lib/api-mappers";

export type AdminSwitchUser = {
  id: string;
  email: string;
  displayName: string;
  roles: string[];
  status: string;
};

type AuthContextValue = {
  user: SessionUser | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<SignInResult>;
  verifyMfa: (code: string) => Promise<void>;
  signUp: (email: string, password: string, displayName: string) => Promise<void>;
  signOut: () => Promise<void>;
  refresh: () => Promise<void>;
  searchSwitchUsers: (query: string) => Promise<AdminSwitchUser[]>;
  startImpersonation: (targetUserId: string, reason: string) => Promise<void>;
  stopImpersonation: () => Promise<void>;
};

export type SignInResult = {
  mfaRequired: boolean;
  mfaSetupRequired: boolean;
};

const AuthContext = createContext<AuthContextValue | null>(null);

function hasCookie(name: string) {
  if (typeof document === "undefined") return false;
  return document.cookie.split("; ").some((row) => row.startsWith(`${name}=`));
}

async function readError(response: Response) {
  try {
    const payload = (await response.json()) as { error?: { message?: string } };
    return payload.error?.message ?? "Authentication request failed.";
  } catch {
    return "Authentication request failed.";
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<SessionUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      if (!USE_MOCK_DATA) {
        if (!hasCookie("pred_market_v1_csrf_token")) {
          setUser(null);
          return;
        }
        try {
          const payload = await apiRequest<BackendAuthMe>("/api/v1/auth/me");
          setUser(mapAuthMe(payload));
        } catch {
          try {
            await apiRequest("/api/v1/auth/refresh", { method: "POST" });
            const payload = await apiRequest<BackendAuthMe>("/api/v1/auth/me");
            setUser(mapAuthMe(payload));
          } catch {
            setUser(null);
          }
        }
        return;
      }
      const response = await fetch("/api/v1/auth/me", { credentials: "include" });
      if (!response.ok) {
        setUser(null);
        return;
      }
      const payload = (await response.json()) as { user: SessionUser };
      setUser(payload.user);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void refresh();
    }, 0);

    return () => window.clearTimeout(timer);
  }, [refresh]);

  const signIn = useCallback(async (email: string, password: string) => {
    if (!USE_MOCK_DATA) {
      const payload = await apiRequest<
        | { user: BackendUser; mfa_setup_required?: boolean }
        | { mfa_required: true; expires_in_seconds: number }
      >("/api/v1/auth/sign-in", {
        method: "POST",
        body: JSON.stringify({ email, password })
      });
      if ("mfa_required" in payload) {
        return { mfaRequired: true, mfaSetupRequired: false };
      }
      const setupRequired = Boolean(payload.mfa_setup_required);
      const mfa: BackendMfaStatus = {
        enrolled: false,
        required: setupRequired,
        verified_for_session: false,
        factor_id: null,
        recovery_codes_remaining: 0
      };
      setUser(mapUser(payload.user, 0, mfa));
      return { mfaRequired: false, mfaSetupRequired: setupRequired };
    }
    const response = await fetch("/api/v1/auth/sign-in", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) throw new Error(await readError(response));
    const payload = (await response.json()) as { user: SessionUser };
    setUser(payload.user);
    return { mfaRequired: false, mfaSetupRequired: false };
  }, []);

  const verifyMfa = useCallback(async (code: string) => {
    if (USE_MOCK_DATA) return;
    const payload = await apiRequest<{ user: BackendUser }>("/api/v1/auth/mfa/challenge/verify", {
      method: "POST",
      body: JSON.stringify({ code })
    });
    await refresh();
    if (!payload.user) throw new Error("Authenticator verification did not complete.");
  }, [refresh]);

  const signUp = useCallback(async (email: string, password: string, displayName: string) => {
    if (!USE_MOCK_DATA) {
      const payload = await apiRequest<{ user: BackendUser }>("/api/v1/auth/sign-up", {
        method: "POST",
        body: JSON.stringify({ email, password, display_name: displayName, terms_acceptance: true })
      });
      setUser(mapUser(payload.user));
      return;
    }
    const response = await fetch("/api/v1/auth/sign-up", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password, displayName })
    });

    if (!response.ok) throw new Error(await readError(response));
    const payload = (await response.json()) as { user: SessionUser };
    setUser(payload.user);
  }, []);

  const signOut = useCallback(async () => {
    if (!USE_MOCK_DATA) {
      await apiRequest("/api/v1/auth/sign-out", { method: "POST" });
      setUser(null);
      window.location.href = "/sign-in";
      return;
    }
    await fetch("/api/v1/auth/sign-out", { method: "POST", credentials: "include" });
    setUser(null);
    window.location.href = "/sign-in";
  }, []);

  const searchSwitchUsers = useCallback(async (query: string) => {
    if (USE_MOCK_DATA) {
      return [
        { id: "user_trader_demo", email: "trader@predmarket.dev", displayName: "Demo Trader", roles: ["USER"], status: "ACTIVE" }
      ].filter((item) => item.email.includes(query.toLowerCase()) || item.displayName.toLowerCase().includes(query.toLowerCase()));
    }
    const search = new URLSearchParams();
    if (query.trim()) search.set("q", query.trim());
    const payload = await apiRequest<{ items: BackendUser[] }>(`/api/v1/admin/users?${search.toString()}`);
    return payload.items.map((item) => ({
      id: item.id,
      email: item.email,
      displayName: item.display_name || item.email.split("@")[0],
      roles: item.roles,
      status: item.status
    }));
  }, []);

  const startImpersonation = useCallback(async (targetUserId: string, reason: string) => {
    if (USE_MOCK_DATA) return;
    const payload = await apiRequest<BackendAuthMe>("/api/v1/admin/impersonation/start", {
      method: "POST",
      body: JSON.stringify({ target_user_id: targetUserId, reason })
    });
    setUser(mapAuthMe(payload));
  }, []);

  const stopImpersonation = useCallback(async () => {
    if (USE_MOCK_DATA) return;
    const payload = await apiRequest<BackendAuthMe>("/api/v1/admin/impersonation/stop", { method: "POST" });
    setUser(mapAuthMe(payload));
  }, []);

  const value = useMemo(
    () => ({ user, loading, signIn, verifyMfa, signUp, signOut, refresh, searchSwitchUsers, startImpersonation, stopImpersonation }),
    [loading, refresh, searchSwitchUsers, signIn, signOut, signUp, startImpersonation, stopImpersonation, user, verifyMfa]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
