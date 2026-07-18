export const AUTH_COOKIE = "pm_session";

export type UserRole = "USER" | "ADMIN" | "CHECKER" | "MARKET_CREATOR" | "MARKET_MAKER";

export type ImpersonationContext = {
  active: boolean;
  sessionId: string;
  mode: "READ_ONLY";
  actorUserId: string;
  targetUserId: string;
  startedAt: string;
};

export type SessionUser = {
  id: string;
  email: string;
  displayName: string;
  roles: UserRole[];
  emailVerified: boolean;
  mfaVerified: boolean;
  walletBalance: number;
  expiresAt: string;
  actor?: Omit<SessionUser, "actor" | "impersonation">;
  impersonation?: ImpersonationContext | null;
};

function encodeBase64Url(value: string) {
  return Buffer.from(value, "utf8").toString("base64url");
}

function decodeBase64Url(value: string) {
  return Buffer.from(value, "base64url").toString("utf8");
}

export function createSessionUser(email: string, displayName?: string): SessionUser {
  const normalizedEmail = email.trim().toLowerCase();
  const isAdmin = normalizedEmail.includes("admin");
  const fallbackName = normalizedEmail
    .split("@")[0]
    .split(/[._-]/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

  return {
    id: isAdmin ? "user_admin_demo" : "user_trader_demo",
    email: normalizedEmail,
    displayName: displayName?.trim() || fallbackName || "Pred-Market Trader",
    roles: isAdmin ? ["USER", "ADMIN", "CHECKER", "MARKET_CREATOR"] : ["USER"],
    emailVerified: true,
    mfaVerified: isAdmin,
    walletBalance: isAdmin ? 128440 : 84220,
    expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
  };
}

export function encodeSession(user: SessionUser) {
  return encodeBase64Url(JSON.stringify(user));
}

export function decodeSession(value?: string | null): SessionUser | null {
  if (!value) return null;

  try {
    const parsed = JSON.parse(decodeBase64Url(value)) as SessionUser;
    if (!parsed.email || !parsed.expiresAt || new Date(parsed.expiresAt).getTime() <= Date.now()) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

export function getInitials(user?: Pick<SessionUser, "displayName" | "email"> | null) {
  if (!user) return "PB";
  const source = user.displayName || user.email;
  const parts = source.split(/[\s@._-]/).filter(Boolean);
  return parts
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join("");
}
