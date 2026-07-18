"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/auth-provider";

export default function HomePage() {
  const router = useRouter();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (loading) return;
    if (!user) {
      router.replace("/sign-in");
      return;
    }
    router.replace(user.roles.includes("ADMIN") ? "/admin" : "/markets");
  }, [loading, router, user]);

  return (
    <div className="flex min-h-[50dvh] items-center justify-center">
      <div className="exchange-panel rounded-md p-4 text-sm text-[var(--muted)]">Checking session...</div>
    </div>
  );
}
