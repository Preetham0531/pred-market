import { Suspense } from "react";
import { AuthPanel } from "@/components/auth-panel";

export default function SignUpPage() {
  return (
    <Suspense fallback={null}>
      <AuthPanel mode="sign-up" />
    </Suspense>
  );
}
