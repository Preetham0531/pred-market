import { NextResponse } from "next/server";
import { AUTH_COOKIE, createSessionUser, encodeSession } from "@/lib/auth-session";

type SignUpPayload = {
  email?: string;
  password?: string;
  displayName?: string;
};

export async function POST(request: Request) {
  const payload = (await request.json()) as SignUpPayload;
  const email = payload.email?.trim().toLowerCase();

  if (!email || !email.includes("@")) {
    return NextResponse.json(
      { error: { code: "INVALID_EMAIL", message: "Enter a valid email address." } },
      { status: 422 }
    );
  }

  if (!payload.password || payload.password.length < 8) {
    return NextResponse.json(
      { error: { code: "WEAK_PASSWORD", message: "Password must be at least 8 characters." } },
      { status: 422 }
    );
  }

  const user = createSessionUser(email, payload.displayName);
  const response = NextResponse.json({ user }, { status: 201 });
  response.cookies.set(AUTH_COOKIE, encodeSession(user), {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 7 * 24 * 60 * 60
  });

  return response;
}
