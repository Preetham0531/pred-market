import { Suspense } from "react";
import { AuthPanel } from "@/components/auth-panel";

export default function SignInPage() {
  return (
    <Suspense fallback={null}>
      <AuthPanel mode="sign-in" />
    </Suspense>
  );
}
