"use client";

import Link from "next/link";
import * as Dialog from "@radix-ui/react-dialog";
import { CheckCircle2, ChevronDown, Loader2, Plus, X, XCircle } from "lucide-react";
import { useMemo, useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiError, USE_MOCK_DATA } from "@/lib/api-client";
import { useCreateOrder, useTestDeposit, useWalletData } from "@/lib/api-hooks";
import type { BackendOrder } from "@/lib/api-mappers";
import type { Market } from "@/lib/mock-data";
import { cn, formatCurrency } from "@/lib/utils";

type TradeTicketProps = {
  market: Market;
};

function executableAsk(market: Market, outcome: string) {
  if (outcome === "YES") return market.quote?.yesAsk ?? (market.orderBook.noBids[0] ? 100 - market.orderBook.noBids[0].price : null);
  return market.quote?.noAsk ?? (market.orderBook.yesBids[0] ? 100 - market.orderBook.yesBids[0].price : null);
}

function errorMessage(error: unknown) {
  if (!(error instanceof ApiError)) return error instanceof Error ? error.message : "The order could not be placed. Try again.";
  if (error.code === "INSUFFICIENT_FUNDS") return "You need more simulated funds for this trade.";
  if (error.code === "UNAUTHENTICATED") return "Your session ended. Sign in and try again.";
  if (error.code === "MARKET_NOT_OPEN") return "This market is no longer open for trading.";
  if (error.status >= 500) return "Trading is temporarily unavailable. Your funds were not changed.";
  return error.message;
}

export function TradeTicket({ market }: TradeTicketProps) {
  const { user } = useAuth();
  const { data: wallet } = useWalletData(Boolean(user));
  const createOrder = useCreateOrder();
  const deposit = useTestDeposit();
  const outcomes = [...market.outcomes].sort((a, b) => (a.label === "YES" ? -1 : b.label === "YES" ? 1 : 0));
  const [outcome, setOutcome] = useState(outcomes[0]?.label ?? "YES");
  const [budget, setBudget] = useState("1000");
  const [advanced, setAdvanced] = useState(false);
  const [limitPrice, setLimitPrice] = useState(String(executableAsk(market, outcomes[0]?.label ?? "YES") ?? ""));
  const [limitQuantity, setLimitQuantity] = useState("10");
  const [result, setResult] = useState<BackendOrder | null>(null);
  const [error, setError] = useState("");
  const [confirming, setConfirming] = useState(false);
  const [fundingOpen, setFundingOpen] = useState(false);
  const [fundAmount, setFundAmount] = useState("10000");
  const ask = executableAsk(market, outcome);
  const selectedOutcome = outcomes.find((item) => item.label === outcome);
  const available = USE_MOCK_DATA ? 84220 : wallet?.available ?? 0;
  const readOnly = Boolean(user?.impersonation?.active && user.impersonation.mode === "READ_ONLY");

  const trade = useMemo(() => {
    const parsedBudget = Math.floor(Number(budget));
    const quickQuantity = ask ? Math.floor(parsedBudget / ask) : 0;
    const price = advanced ? Number(limitPrice) : ask ?? 0;
    const quantity = advanced ? Number(limitQuantity) : quickQuantity;
    const validPrice = Number.isInteger(price) && price >= 1 && price <= 99;
    const validQuantity = Number.isInteger(quantity) && quantity >= 1;
    return {
      price,
      quantity,
      spend: validPrice && validQuantity ? price * quantity : 0,
      payout: validQuantity ? quantity * 100 : 0,
      valid: validPrice && validQuantity
    };
  }, [advanced, ask, budget, limitPrice, limitQuantity]);

  const insufficientFunds = trade.valid && trade.spend > available;
  const pending = createOrder.isPending || deposit.isPending;
  const canTrade = Boolean(user && selectedOutcome?.id && trade.valid && !readOnly && !pending);

  function selectOutcome(label: string) {
    setOutcome(label);
    setLimitPrice(String(executableAsk(market, label) ?? ""));
    setResult(null);
    setError("");
    setConfirming(false);
  }

  async function placeOrder(skipBalanceCheck = false) {
    if (!user || !selectedOutcome?.id || !trade.valid || readOnly) return;
    if (insufficientFunds && !skipBalanceCheck) {
      setFundAmount(String(Math.max(1000, trade.spend - available)));
      setFundingOpen(true);
      return;
    }
    setError("");
    setResult(null);
    try {
      if (USE_MOCK_DATA) {
        setResult({
          id: "ORD-MOCK",
          user_id: user.id,
          market_id: market.id,
          outcome_id: selectedOutcome.id,
          outcome,
          side: "BUY",
          price_minor: trade.price,
          quantity: trade.quantity,
          filled_quantity: advanced ? 0 : trade.quantity,
          cancelled_quantity: 0,
          remaining_quantity: advanced ? trade.quantity : 0,
          locked_cash_minor: advanced ? trade.spend : 0,
          locked_shares: 0,
          status: advanced ? "OPEN" : "FILLED",
          created_at: new Date().toISOString()
        });
        return;
      }
      const order = await createOrder.mutateAsync({
        market_id: market.id,
        outcome_id: selectedOutcome.id,
        side: "BUY",
        price_minor: trade.price,
        quantity: trade.quantity
      });
      setResult(order);
    } catch (caught) {
      setError(errorMessage(caught));
    }
  }

  function beginTrade() {
    if (!user) return;
    const confirmationKey = `pred-market:first-trade-confirmed:${user.id}`;
    if (window.localStorage.getItem(confirmationKey) !== "true") {
      setConfirming(true);
      return;
    }
    void placeOrder();
  }

  function confirmFirstTrade() {
    if (!user) return;
    window.localStorage.setItem(`pred-market:first-trade-confirmed:${user.id}`, "true");
    setConfirming(false);
    void placeOrder();
  }

  async function addFundsAndResume() {
    const amount = Math.floor(Number(fundAmount));
    if (!Number.isFinite(amount) || amount <= 0 || amount > 500000) return;
    try {
      if (!USE_MOCK_DATA) await deposit.mutateAsync(amount);
      setFundingOpen(false);
      beginTrade();
    } catch (caught) {
      setError(errorMessage(caught));
      setFundingOpen(false);
    }
  }

  function ticketContent() {
    return (
      <>
        <div className="mb-4">
          <h2 className="text-sm font-semibold">Trade</h2>
          <p className="mt-1 text-xs text-[var(--muted)]">Choose a side and how much you want to spend.</p>
        </div>

        <div className="grid grid-cols-2 gap-2">
          {outcomes.slice(0, 2).map((item) => {
            const price = executableAsk(market, item.label);
            const yes = item.label === "YES";
            return (
              <button
                key={item.id ?? item.label}
                onClick={() => selectOutcome(item.label)}
                className={cn(
                  "h-12 rounded-md border px-3 text-left transition",
                  outcome === item.label
                    ? yes
                      ? "border-[var(--green-border)] bg-[var(--green-soft)] text-[var(--green-text)]"
                      : "border-[var(--red-border)] bg-[var(--red-soft)] text-[var(--red-text)]"
                    : "border-[var(--border)] hover:bg-[var(--surface-muted)]"
                )}
              >
                <span className="block text-xs">{item.label}</span>
                <span className="numeric text-sm font-semibold">{price == null ? "No ask" : `${price}`}</span>
              </button>
            );
          })}
        </div>

        {!advanced ? (
          <label className="mt-4 block">
            <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Budget</span>
            <Input inputMode="numeric" value={budget} onChange={(event) => setBudget(event.target.value)} aria-label="Trade budget in rupees" />
          </label>
        ) : (
          <div className="mt-4 grid grid-cols-2 gap-2">
            <label>
              <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Limit price</span>
              <Input inputMode="numeric" value={limitPrice} onChange={(event) => setLimitPrice(event.target.value)} />
            </label>
            <label>
              <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Quantity</span>
              <Input inputMode="numeric" value={limitQuantity} onChange={(event) => setLimitQuantity(event.target.value)} />
            </label>
          </div>
        )}

        <button
          className="mt-3 flex items-center gap-1 text-xs font-medium text-[var(--primary-strong)]"
          onClick={() => {
            setAdvanced((current) => !current);
            setResult(null);
            setError("");
          }}
          aria-expanded={advanced}
        >
          Advanced limit order
          <ChevronDown className={cn("h-3.5 w-3.5 transition", advanced ? "rotate-180" : "")} />
        </button>

        <div className="mt-4 border-y border-[var(--border)] py-2 text-sm">
          <div className="flex justify-between py-1"><span className="text-[var(--muted)]">Price</span><strong className="numeric">{trade.price || "-"}</strong></div>
          <div className="flex justify-between py-1"><span className="text-[var(--muted)]">Contracts</span><strong className="numeric">{trade.quantity || "-"}</strong></div>
          <div className="flex justify-between py-1"><span className="text-[var(--muted)]">Actual spend</span><strong className="numeric">{formatCurrency(trade.spend)}</strong></div>
          <div className="flex justify-between py-1"><span className="text-[var(--muted)]">Possible payout</span><strong className="numeric">{formatCurrency(trade.payout)}</strong></div>
          <div className="flex justify-between py-1"><span className="text-[var(--muted)]">Available</span><strong className="numeric">{formatCurrency(available)}</strong></div>
        </div>

        {confirming ? (
          <div className="mt-3 border border-[var(--brass-border)] bg-[var(--brass-soft)] p-3 text-sm text-[var(--brass-text)]">
            <div className="font-medium">Confirm your first trade</div>
            <p className="mt-1 text-xs leading-5">You are buying {trade.quantity} {outcome} contracts for {formatCurrency(trade.spend)}. Each contract pays ₹100 if {outcome} wins, otherwise ₹0.</p>
            <div className="mt-3 grid grid-cols-2 gap-2">
              <Button variant="secondary" onClick={() => setConfirming(false)}>Back</Button>
              <Button variant="primary" onClick={confirmFirstTrade}>Confirm trade</Button>
            </div>
          </div>
        ) : null}

        {result?.status === "FILLED" ? (
          <div className="mt-3 border border-[var(--green-border)] bg-[var(--green-soft)] p-3 text-sm text-[var(--green-text)]" role="status">
            <div className="flex items-center gap-2 font-medium"><CheckCircle2 className="h-4 w-4" />Trade completed</div>
            <p className="mt-1 text-xs">{result.filled_quantity} contracts were added to your position.</p>
            <Link className="mt-2 inline-block text-xs font-medium underline" href="/portfolio">View position</Link>
          </div>
        ) : null}

        {result?.status === "PARTIALLY_FILLED" ? (
          <div className="mt-3 border border-[var(--blue-border)] bg-[var(--blue-soft)] p-3 text-sm text-[var(--blue-text)]" role="status">
            <div className="font-medium">Partially filled</div>
            <p className="mt-1 text-xs">{result.filled_quantity} filled, {result.remaining_quantity} still waiting.</p>
            <Link className="mt-2 inline-block text-xs font-medium underline" href="/orders">View order</Link>
          </div>
        ) : null}

        {result?.status === "OPEN" ? (
          <div className="mt-3 border border-[var(--brass-border)] bg-[var(--brass-soft)] p-3 text-sm text-[var(--brass-text)]" role="status">
            <div className="font-medium">Waiting for another order</div>
            <p className="mt-1 text-xs">Your {result.remaining_quantity} contracts are open at {result.price_minor}.</p>
            <Link className="mt-2 inline-block text-xs font-medium underline" href="/orders">View or cancel</Link>
          </div>
        ) : null}

        {error ? (
          <div className="mt-3 border border-[var(--red-border)] bg-[var(--red-soft)] p-3 text-sm text-[var(--red-text)]" role="alert">
            <div className="flex items-center gap-2 font-medium"><XCircle className="h-4 w-4" />Trade not placed</div>
            <p className="mt-1 text-xs">{error}</p>
          </div>
        ) : null}

        {!confirming ? (
          <div className="mt-4">
            {!user ? (
              <Link className="inline-flex h-10 w-full items-center justify-center rounded-md bg-[var(--primary)] px-3 text-sm font-medium text-white" href={`/sign-in?next=${encodeURIComponent(`/markets/${market.id}`)}`}>
                Sign in to trade
              </Link>
            ) : insufficientFunds ? (
              <Button className="w-full" variant="primary" onClick={() => setFundingOpen(true)}>
                <Plus className="h-4 w-4" />Add funds
              </Button>
            ) : (
              <Button className="w-full" variant="primary" disabled={!canTrade || ask == null && !advanced} onClick={beginTrade}>
                {pending ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                {pending ? "Placing trade" : advanced ? "Place limit order" : `Buy ${outcome}`}
              </Button>
            )}
            {!trade.valid ? <p className="mt-2 text-xs text-[var(--muted)]">{ask == null && !advanced ? "No executable ask is available yet." : "Enter enough to buy at least one whole contract."}</p> : null}
            {readOnly ? <p className="mt-2 text-xs text-[var(--brass-text)]">Trading is disabled in read-only admin view.</p> : null}
          </div>
        ) : null}
      </>
    );
  }

  return (
    <>
      <aside className="sticky top-[82px] hidden rounded-md bg-[var(--surface)]/50 p-4 xl:block">{ticketContent()}</aside>

      <Dialog.Root>
        <div className="exchange-bottom-bar fixed inset-x-0 border-t border-[var(--border)] bg-[var(--surface)] p-3 shadow-[0_-4px_8px_rgba(0,0,0,0.12)] xl:hidden">
          <div className="mx-auto flex max-w-3xl items-center justify-between gap-3">
            <div className="min-w-0">
              <div className="text-xs text-[var(--muted)]">{outcome} at {ask ?? "-"}</div>
              <div className="numeric truncate text-sm font-semibold">{trade.quantity || 0} contracts · {formatCurrency(trade.spend)}</div>
            </div>
            <Dialog.Trigger asChild><Button variant="primary">Trade</Button></Dialog.Trigger>
          </div>
        </div>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-50 bg-black/35" />
          <Dialog.Content className="fixed inset-x-0 bottom-0 z-50 max-h-[90dvh] overflow-y-auto rounded-t-lg bg-[var(--surface)] p-4 shadow-2xl">
            <Dialog.Title className="sr-only">Trade</Dialog.Title>
            <Dialog.Close asChild>
              <Button className="absolute right-3 top-3" variant="ghost" size="icon" aria-label="Close trade ticket"><X className="h-4 w-4" /></Button>
            </Dialog.Close>
            {ticketContent()}
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>

      <Dialog.Root open={fundingOpen} onOpenChange={setFundingOpen}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-[60] bg-black/35" />
          <Dialog.Content className="fixed left-1/2 top-1/2 z-[60] w-[min(380px,calc(100vw-32px))] -translate-x-1/2 -translate-y-1/2 rounded-md border border-[var(--border)] bg-[var(--surface)] p-4 shadow-2xl">
            <Dialog.Title className="text-sm font-semibold">Add simulated funds</Dialog.Title>
            <Dialog.Description className="mt-1 text-xs text-[var(--muted)]">Your pending trade will continue after funds are added.</Dialog.Description>
            <label className="mt-4 block">
              <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Amount</span>
              <Input inputMode="numeric" value={fundAmount} onChange={(event) => setFundAmount(event.target.value)} autoFocus />
            </label>
            <div className="mt-4 grid grid-cols-2 gap-2">
              <Dialog.Close asChild><Button variant="secondary">Cancel</Button></Dialog.Close>
              <Button variant="primary" onClick={() => void addFundsAndResume()} disabled={deposit.isPending}>
                {deposit.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                {deposit.isPending ? "Adding" : "Add and continue"}
              </Button>
            </div>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </>
  );
}
