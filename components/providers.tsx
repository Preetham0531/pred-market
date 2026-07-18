"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { AuthProvider, useAuth } from "@/components/auth-provider";
import { useUserRealtime } from "@/lib/realtime";

function RealtimeBridge() {
  const { user } = useAuth();
  useUserRealtime(Boolean(user));
  return null;
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            refetchOnWindowFocus: false,
            retry: false
          }
        }
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <RealtimeBridge />
        {children}
      </AuthProvider>
    </QueryClientProvider>
  );
}
