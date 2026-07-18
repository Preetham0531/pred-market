import { NextResponse } from "next/server";

export async function POST() {
  return NextResponse.json({
    status: "accepted",
    message: "Email verification delivery is mocked until the FastAPI mailer is implemented."
  });
}
