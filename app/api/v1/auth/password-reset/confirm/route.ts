import { NextResponse } from "next/server";

export async function POST() {
  return NextResponse.json({
    status: "updated",
    message: "Password reset confirmation is mocked for the frontend prototype."
  });
}
