"use client";

import { useMemo, useState } from "react";
import { PlusCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { USE_MOCK_DATA } from "@/lib/api-client";
import { useTestDeposit, useWalletData } from "@/lib/api-hooks";
import { walletEntries, type WalletEntry } from "@/lib/mock-data";
import { formatCurrency } from "@/lib/utils";

export function WalletWorkspace() {
  const { data, isLoading, error } = useWalletData();
  const depositMutation = useTestDeposit();
  const [mockEntries, setMockEntries] = useState<WalletEntry[]>(walletEntries);
  const [amount, setAmount] = useState("10000");
  const entries = USE_MOCK_DATA ? mockEntries : data?.entries ?? [];

  const canDeposit = useMemo(() => Number(amount) > 0 && Number(amount) <= 500000, [amount]);

  function simulateDeposit() {
    if (!canDeposit) return;
    const parsedAmount = Math.round(Number(amount));
    if (!USE_MOCK_DATA) {
      depositMutation.mutate(parsedAmount);
      return;
    }
    setMockEntries((current) => [
      {
        id: `LED-${3010 + current.length}`,
        type: "Deposit",
        amount: parsedAmount,
        status: "Complete",
        createdAt: "Now"
      },
      ...current
    ]);
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold">Wallet</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">Available cash, locked funds, and ledger activity.</p>
      </div>
      {error ? (
        <div className="rounded-md border border-[var(--red-border)] bg-[var(--red-soft)] px-3 py-2 text-sm text-[var(--red-text)]">
          Wallet data could not be loaded. Sign in and try again.
        </div>
      ) : null}
      <section className="exchange-panel rounded-md p-3">
        <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-sm font-semibold">Simulated deposit</h2>
              <Badge tone="brass">V1 test funds</Badge>
            </div>
            <p className="mt-1 text-xs leading-5 text-[var(--muted)]">
              V1 uses simulated funds only. Real deposits and withdrawals stay disabled until KYC, AML, payment provider, and legal approval are complete.
            </p>
          </div>
          <div className="flex gap-2">
            <Input className="w-36" inputMode="numeric" value={amount} onChange={(event) => setAmount(event.target.value)} aria-label="Simulated deposit amount" />
            <Button variant="primary" onClick={simulateDeposit} disabled={!canDeposit || depositMutation.isPending}>
              <PlusCircle className="h-4 w-4" />
              {depositMutation.isPending ? "Adding" : "Add funds"}
            </Button>
          </div>
        </div>
      </section>

      <div className="exchange-panel overflow-hidden rounded-md">
        <div className="border-b border-[var(--border)] px-3 py-2 text-sm font-semibold">Ledger</div>
        <div className="exchange-table-header hidden grid-cols-[120px_1fr_140px_110px] px-3 py-2 md:grid">
          <span>ID</span>
          <span>Entry</span>
          <span>Amount</span>
          <span>Status</span>
        </div>
        <div className="divide-y divide-[var(--border)]">
          {isLoading && !USE_MOCK_DATA ? (
            <div className="px-3 py-6 text-sm text-[var(--muted)]">Loading ledger...</div>
          ) : entries.length ? entries.map((entry) => (
            <div key={entry.id} className="grid min-h-[62px] gap-2 px-3 py-3 text-sm md:grid-cols-[120px_1fr_140px_110px] md:items-center">
              <div className="font-mono text-xs text-[var(--muted)]">{entry.id}</div>
              <div>
                <div className="font-medium">{entry.type}</div>
                <div className="mt-1 text-xs text-[var(--muted)]">{entry.createdAt}</div>
              </div>
              <div className={entry.amount >= 0 ? "numeric font-medium text-[var(--green-text)]" : "numeric font-medium text-[var(--red-text)]"}>
                {formatCurrency(entry.amount)}
              </div>
              <Badge tone={entry.status === "Complete" ? "green" : "brass"}>{entry.status}</Badge>
            </div>
          )) : (
            <div className="px-3 py-6 text-sm text-[var(--muted)]">No ledger entries yet.</div>
          )}
        </div>
      </div>
    </div>
  );
}
