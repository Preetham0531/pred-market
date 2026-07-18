import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { AUTH_COOKIE, decodeSession } from "@/lib/auth-session";

export async function POST() {
  const cookieStore = await cookies();
  const user = decodeSession(cookieStore.get(AUTH_COOKIE)?.value);

  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHENTICATED", message: "Sign in before opening a private stream." } }, { status: 401 });
  }

  return NextResponse.json({
    ticket: `mock_ws_${crypto.randomUUID()}`,
    expires_at: new Date(Date.now() + 60_000).toISOString()
  });
}
