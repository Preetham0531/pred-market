import { NextResponse } from "next/server";
import { AUTH_COOKIE, createSessionUser, encodeSession } from "@/lib/auth-session";

type SignInPayload = {
  email?: string;
  password?: string;
};

export async function POST(request: Request) {
  const payload = (await request.json()) as SignInPayload;
  const email = payload.email?.trim().toLowerCase();

  if (!email || !email.includes("@") || !payload.password || payload.password.length < 8) {
    return NextResponse.json(
      {
        error: {
          code: "INVALID_CREDENTIALS",
          message: "Use an email and a password with at least 8 characters."
        }
      },
      { status: 401 }
    );
  }

  const user = createSessionUser(email);
  const response = NextResponse.json({ user });
  response.cookies.set(AUTH_COOKIE, encodeSession(user), {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 7 * 24 * 60 * 60
  });

  return response;
}
