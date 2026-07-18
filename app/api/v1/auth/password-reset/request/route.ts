import { NextResponse } from "next/server";

export async function POST() {
  return NextResponse.json({
    status: "accepted",
    message: "Password reset delivery is mocked until the FastAPI mailer is implemented."
  });
}
