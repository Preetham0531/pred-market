import { redirect } from "next/navigation";

export default function LegacyMarketIssueRedirectPage() {
  redirect("/admin/markets/issue");
}
