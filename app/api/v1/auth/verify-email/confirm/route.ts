import { NextResponse } from "next/server";

export async function POST() {
  return NextResponse.json({
    status: "verified",
    message: "Email verification confirmation is mocked for the frontend prototype."
  });
}
