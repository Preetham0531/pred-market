import { NextResponse, type NextRequest } from "next/server";

const AUTH_COOKIE = "pm_session";
const BACKEND_ACCESS_COOKIE = "pred_market_v1_access_token";
const BACKEND_REFRESH_COOKIE = "pred_market_v1_refresh_token";
const USE_REAL_BACKEND_AUTH = process.env.NEXT_PUBLIC_USE_MOCK_DATA === "false";

const AUTH_REQUIRED_PREFIXES = ["/watchlist", "/profile", "/portfolio", "/orders", "/wallet", "/markets/suggest", "/account"];
const ADMIN_PREFIXES = ["/admin"];

function decodeSession(value?: string) {
  if (!value) return null;

  try {
    const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
    const decoded = atob(normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "="));
    const session = JSON.parse(decoded) as { roles?: string[]; expiresAt?: string };
    if (!session.expiresAt || new Date(session.expiresAt).getTime() <= Date.now()) return null;
    return session;
  } catch {
    return null;
  }
}

function requiresAuth(pathname: string) {
  return AUTH_REQUIRED_PREFIXES.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
}

function requiresAdmin(pathname: string) {
  return ADMIN_PREFIXES.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
}

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const backendSession = request.cookies.has(BACKEND_ACCESS_COOKIE) || request.cookies.has(BACKEND_REFRESH_COOKIE);
  const session = USE_REAL_BACKEND_AUTH && backendSession ? { roles: [] } : decodeSession(request.cookies.get(AUTH_COOKIE)?.value);
  const needsAuth = requiresAuth(pathname) || requiresAdmin(pathname);

  if (needsAuth && !session) {
    const url = new URL("/sign-in", request.url);
    url.searchParams.set("next", pathname);
    return NextResponse.redirect(url);
  }

  if (!USE_REAL_BACKEND_AUTH && requiresAdmin(pathname) && !session?.roles?.includes("ADMIN")) {
    return NextResponse.redirect(new URL("/markets", request.url));
  }

  if (!USE_REAL_BACKEND_AUTH && (pathname === "/sign-in" || pathname === "/sign-up") && session) {
    return NextResponse.redirect(new URL("/markets", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/admin/:path*",
    "/account/:path*",
    "/orders/:path*",
    "/portfolio/:path*",
    "/wallet/:path*",
    "/watchlist/:path*",
    "/markets/suggest/:path*",
    "/sign-in",
    "/sign-up"
  ]
};
