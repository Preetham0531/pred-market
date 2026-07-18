import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { AUTH_COOKIE, decodeSession, encodeSession } from "@/lib/auth-session";

export async function POST() {
  const cookieStore = await cookies();
  const user = decodeSession(cookieStore.get(AUTH_COOKIE)?.value);

  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHENTICATED", message: "Session is not active." } }, { status: 401 });
  }

  const refreshed = {
    ...user,
    expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
  };
  const response = NextResponse.json({ user: refreshed });
  response.cookies.set(AUTH_COOKIE, encodeSession(refreshed), {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 7 * 24 * 60 * 60
  });

  return response;
}
