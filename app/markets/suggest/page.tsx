import { SuggestMarketFlow } from "@/components/suggest-market-flow";
import { redirect } from "next/navigation";

export default function SuggestMarketPage() {
  if (process.env.NEXT_PUBLIC_ENABLE_MARKET_SUGGESTIONS !== "true") redirect("/");
  return <SuggestMarketFlow />;
}
