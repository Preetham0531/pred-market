"use client";

import { useId, useMemo, useState } from "react";
import Link from "next/link";
import * as Dialog from "@radix-ui/react-dialog";
import { AlertTriangle, CheckCircle2, Info, Loader2, XCircle } from "lucide-react";
import * as Tooltip from "@radix-ui/react-tooltip";
import { useAuth } from "@/components/auth-provider";
import { USE_MOCK_DATA } from "@/lib/api-client";
import { useCreateOrder, useWalletData } from "@/lib/api-hooks";
import type { Market } from "@/lib/mock-data";
import { cn, formatCurrency } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type TradeTicketProps = {
  market: Market;
};

export function TradeTicket({ market }: TradeTicketProps) {
  const priceErrorId = useId();
  const quantityErrorId = useId();
  const [outcome, setOutcome] = useState(market.outcomes[0]?.label ?? "YES");
  const [price, setPrice] = useState(String(market.outcomes[0]?.price ?? market.probability));
  const [quantity, setQuantity] = useState("10");
  const [previewed, setPreviewed] = useState(false);
  const [submitState, setSubmitState] = useState<"idle" | "submitting" | "accepted" | "rejected" | "partial">("idle");
  const [error, setError] = useState("");
  const { user } = useAuth();
  const { data: wallet } = useWalletData();
  const createOrder = useCreateOrder();
  const readOnlyImpersonation = Boolean(user?.impersonation?.active && user.impersonation.mode === "READ_ONLY");

  const calculations = useMemo(() => {
    const parsedPrice = Number(price);
    const parsedQuantity = Number(quantity);
    const priceValid = Number.isFinite(parsedPrice) && parsedPrice >= 1 && parsedPrice <= 99;
    const quantityValid = Number.isInteger(parsedQuantity) && parsedQuantity >= 1;
    const normalizedPrice = priceValid ? parsedPrice : 0;
    const normalizedQuantity = quantityValid ? parsedQuantity : 0;
    const cost = normalizedPrice * normalizedQuantity;
    const maxPayout = 100 * normalizedQuantity;
    const maxLoss = cost;
    const implied = normalizedPrice;
    const valid = priceValid && quantityValid;

    return {
      parsedPrice,
      parsedQuantity,
      normalizedPrice,
      normalizedQuantity,
      priceValid,
      quantityValid,
      valid,
      cost,
      maxPayout,
      maxLoss,
      implied
    };
  }, [price, quantity]);
  const availableBalance = USE_MOCK_DATA ? 84220 : wallet?.available ?? 0;
  const insufficientBalance = calculations.valid && calculations.cost > availableBalance;
  const canPreview = Boolean(user) && !readOnlyImpersonation && calculations.valid && !insufficientBalance && submitState !== "submitting";
  const canSubmit = previewed && canPreview;
  const blockedReason = !user
    ? "Sign in to preview and submit live limit orders."
    : readOnlyImpersonation
      ? "Read-only admin user view is active. Return to admin before trading."
    : !calculations.valid
      ? "Enter a price from 1 to 99 and at least 1 whole contract."
      : insufficientBalance
        ? "Estimated cost exceeds available simulated balance."
        : !previewed
          ? "Preview the order before submitting."
          : "";

  function previewOrder() {
    if (!user) {
      setSubmitState("rejected");
      setError("Sign in before previewing an order.");
      return;
    }
    if (readOnlyImpersonation) {
      setSubmitState("rejected");
      setError("Read-only admin user view cannot preview or submit orders.");
      return;
    }
    if (!calculations.valid) {
      setSubmitState("rejected");
      setError("Enter a price from 1 to 99 and a whole-contract quantity.");
      return;
    }
    if (insufficientBalance) {
      setSubmitState("rejected");
      setError("Estimated cost exceeds available balance.");
      return;
    }
    setPreviewed(true);
    setSubmitState("idle");
    setError("");
  }

  async function submitOrder() {
    if (!user) {
      setSubmitState("rejected");
      setError("Sign in before placing an order.");
      return;
    }
    if (readOnlyImpersonation) {
      setSubmitState("rejected");
      setError("Read-only admin user view cannot submit orders.");
      return;
    }
    if (!calculations.valid) {
      setSubmitState("rejected");
      setError("Enter a price from 1 to 99 and a whole-contract quantity.");
      return;
    }
    if (insufficientBalance) {
      setSubmitState("rejected");
      setError("Estimated cost exceeds available balance.");
      return;
    }
    setSubmitState("submitting");
    setError("");
    if (!USE_MOCK_DATA) {
      try {
        const order = await createOrder.mutateAsync({
          market_id: market.id,
          outcome,
          side: "BUY",
          price_minor: calculations.normalizedPrice,
          quantity: calculations.normalizedQuantity
        });
        setSubmitState(order.filled_quantity === order.quantity ? "accepted" : order.filled_quantity > 0 ? "partial" : "accepted");
      } catch (caught) {
        setSubmitState("rejected");
        setError(caught instanceof Error ? caught.message : "Order rejected.");
      }
      return;
    }
    window.setTimeout(() => {
      setSubmitState(calculations.normalizedQuantity > 25 ? "partial" : "accepted");
    }, 550);
  }

  function renderTicket() {
    return (
    <>
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold">Trade ticket</h2>
          <p className="text-xs text-[var(--muted)]">Limit orders only. No market orders in V1.</p>
        </div>
        <Tooltip.Provider delayDuration={150}>
          <Tooltip.Root>
            <Tooltip.Trigger asChild>
              <Button variant="ghost" size="icon" aria-label="Trade ticket details">
                <Info className="h-4 w-4" />
              </Button>
            </Tooltip.Trigger>
            <Tooltip.Portal>
              <Tooltip.Content className="max-w-[240px] rounded-md border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-xs shadow-lg" sideOffset={6}>
                {USE_MOCK_DATA ? "Orders are mocked in this frontend preview." : "Orders are submitted to the FastAPI matching engine."}
                <Tooltip.Arrow className="fill-[var(--surface)]" />
              </Tooltip.Content>
            </Tooltip.Portal>
          </Tooltip.Root>
        </Tooltip.Provider>
      </div>

      <div className="space-y-3">
        <div>
          <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Outcome</span>
          <div className="grid grid-cols-2 rounded-md bg-[var(--surface-muted)]/58 p-1">
            {market.outcomes.slice(0, 2).map((item) => (
              <button
                key={item.label}
                className={cn(
                  "numeric h-9 rounded text-sm font-semibold transition",
                  outcome === item.label
                    ? item.label.toUpperCase() === "YES"
                      ? "bg-[var(--green-soft)] text-[var(--green-text)]"
                      : "bg-[var(--red-soft)] text-[var(--red-text)]"
                    : "text-[var(--muted)] hover:text-[var(--foreground)]"
                )}
                onClick={() => {
                  setOutcome(item.label);
                  setPrice(String(item.price));
                  setPreviewed(false);
                  setSubmitState("idle");
                }}
              >
                {item.label} {item.price}
              </button>
            ))}
          </div>
        </div>
        <label className="block">
          <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Limit price</span>
          <Input
            inputMode="decimal"
            aria-invalid={!calculations.priceValid}
            aria-describedby={!calculations.priceValid ? priceErrorId : undefined}
            value={price}
            onChange={(event) => {
              setPrice(event.target.value);
              setPreviewed(false);
              setSubmitState("idle");
            }}
          />
          {!calculations.priceValid ? (
            <span id={priceErrorId} className="mt-1 block text-xs text-[var(--red-text)]">
              Price must be between 1 and 99.
            </span>
          ) : null}
        </label>
        <label className="block">
          <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Quantity</span>
          <Input
            inputMode="numeric"
            aria-invalid={!calculations.quantityValid}
            aria-describedby={!calculations.quantityValid ? quantityErrorId : undefined}
            value={quantity}
            onChange={(event) => {
              setQuantity(event.target.value);
              setPreviewed(false);
              setSubmitState("idle");
            }}
          />
          {!calculations.quantityValid ? (
            <span id={quantityErrorId} className="mt-1 block text-xs text-[var(--red-text)]">
              Enter at least 1 whole contract.
            </span>
          ) : null}
        </label>
      </div>

      <div className="mt-4 rounded-md bg-[var(--surface-muted)]/48 py-1 text-sm">
        {[
          ["Available", formatCurrency(availableBalance)],
          ["Estimated cost", formatCurrency(calculations.cost)],
          ["Max payout", formatCurrency(calculations.maxPayout)],
          ["Max loss", formatCurrency(calculations.maxLoss)],
          ["Implied probability", `${calculations.implied.toFixed(0)}%`],
          ["Fee", "0 for V1"]
        ].map(([label, value]) => (
          <div key={label} className="flex items-center justify-between px-3 py-1.5">
            <span className="text-[var(--muted)]">{label}</span>
            <span className="numeric font-medium">{value}</span>
          </div>
        ))}
      </div>

      {!user ? (
        <div className="mt-3 rounded-md border border-[var(--brass-border)] bg-[var(--brass-soft)] p-3 text-sm text-[var(--brass-text)]" role="status" aria-live="polite">
          <div className="font-medium">Authentication required</div>
          <p className="mt-1 text-xs">Sign in to preview and submit live orders.</p>
        </div>
      ) : !calculations.valid ? (
        <div className="mt-3 rounded-md border border-[var(--brass-border)] bg-[var(--brass-soft)] p-3 text-sm text-[var(--brass-text)]" role="status" aria-live="polite">
          <div className="flex items-center gap-2 font-medium">
            <AlertTriangle className="h-4 w-4" />
            Order details incomplete
          </div>
          <p className="mt-1 text-xs">Use a price from 1 to 99 and a whole quantity before previewing.</p>
        </div>
      ) : insufficientBalance ? (
        <div className="mt-3 rounded-md border border-[var(--red-border)] bg-[var(--red-soft)] p-3 text-sm text-[var(--red-text)]" role="alert">
          <div className="font-medium">Insufficient available balance</div>
          <p className="mt-1 text-xs">Reduce quantity or add simulated funds in the wallet.</p>
        </div>
      ) : readOnlyImpersonation ? (
        <div className="mt-3 rounded-md border border-[var(--brass-border)] bg-[var(--brass-soft)] p-3 text-sm text-[var(--brass-text)]" role="status" aria-live="polite">
          <div className="font-medium">Read-only admin user view</div>
          <p className="mt-1 text-xs">This view is for support review only. Trading actions are blocked and audited.</p>
        </div>
      ) : null}

      {previewed ? (
        <div className="mt-3 rounded-md border border-[var(--green-border)] bg-[var(--green-soft)] p-3 text-sm text-[var(--green-text)]" role="status" aria-live="polite">
          <div className="flex items-center gap-2 font-medium">
            <CheckCircle2 className="h-4 w-4" />
            Order preview ready
          </div>
          <p className="mt-1 text-xs">Buy {calculations.normalizedQuantity} {outcome} at {calculations.normalizedPrice}.</p>
          <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
            <div className="rounded bg-[var(--surface)]/64 px-2 py-1">
              <span className="block text-[var(--muted)]">Cost</span>
              <span className="numeric font-semibold">{formatCurrency(calculations.cost)}</span>
            </div>
            <div className="rounded bg-[var(--surface)]/64 px-2 py-1">
              <span className="block text-[var(--muted)]">Max payout</span>
              <span className="numeric font-semibold">{formatCurrency(calculations.maxPayout)}</span>
            </div>
            <div className="rounded bg-[var(--surface)]/64 px-2 py-1">
              <span className="block text-[var(--muted)]">Max loss</span>
              <span className="numeric font-semibold">{formatCurrency(calculations.maxLoss)}</span>
            </div>
            <div className="rounded bg-[var(--surface)]/64 px-2 py-1">
              <span className="block text-[var(--muted)]">Implied</span>
              <span className="numeric font-semibold">{calculations.implied.toFixed(0)}%</span>
            </div>
          </div>
        </div>
      ) : null}

      {submitState === "accepted" ? (
        <div className="mt-3 rounded-md border border-[var(--green-border)] bg-[var(--green-soft)] p-3 text-sm text-[var(--green-text)]" role="status" aria-live="polite">
          <div className="flex items-center gap-2 font-medium">
            <CheckCircle2 className="h-4 w-4" />
            Limit order accepted
          </div>
          <p className="mt-1 text-xs">{USE_MOCK_DATA ? "The order is open in the mock order book." : "The order was accepted by the backend."}</p>
        </div>
      ) : null}

      {submitState === "partial" ? (
        <div className="mt-3 rounded-md border border-[var(--blue-border)] bg-[var(--blue-soft)] p-3 text-sm text-[var(--blue-text)]" role="status" aria-live="polite">
          <div className="flex items-center gap-2 font-medium">
            <CheckCircle2 className="h-4 w-4" />
            Partially filled
          </div>
          <p className="mt-1 text-xs">A partial fill was simulated. Remaining contracts stay open.</p>
        </div>
      ) : null}

      {submitState === "rejected" ? (
        <div className="mt-3 rounded-md border border-[var(--red-border)] bg-[var(--red-soft)] p-3 text-sm text-[var(--red-text)]" role="alert">
          <div className="flex items-center gap-2 font-medium">
            <XCircle className="h-4 w-4" />
            Order rejected
          </div>
          <p className="mt-1 text-xs">{error || "Estimated cost exceeds available simulated balance."}</p>
        </div>
      ) : null}

      <div className="mt-3 grid grid-cols-2 gap-2">
        {!user ? (
          <Link className="inline-flex h-9 items-center justify-center rounded-md bg-[var(--surface-muted)]/58 px-3 text-sm font-medium hover:bg-[var(--surface-muted)]" href="/sign-in">
            Sign in
          </Link>
        ) : (
          <Button variant="secondary" onClick={previewOrder} disabled={!canPreview}>
            Preview
          </Button>
        )}
        <Button variant="primary" disabled={!canSubmit} onClick={submitOrder}>
          {submitState === "submitting" ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
          {submitState === "submitting" ? "Submitting" : "Submit order"}
        </Button>
      </div>
      {blockedReason ? (
        <p className="mt-2 text-xs leading-5 text-[var(--muted)]" role="status" aria-live="polite">
          {blockedReason}
        </p>
      ) : null}
      <div className="mt-3 text-xs leading-5 text-[var(--blue-text)]">
        Source: {market.source}. Review market rules before submitting; simulated funds only in V1.
      </div>
    </>
    );
  }

  return (
    <>
      <aside className="sticky top-[82px] hidden rounded-md bg-[var(--surface)]/38 p-3 xl:block">
        {renderTicket()}
      </aside>

      <Dialog.Root>
        <div className="exchange-bottom-bar fixed inset-x-0 border-t border-[color-mix(in_srgb,var(--border)_55%,transparent)] bg-[var(--surface)] p-3 shadow-[0_-4px_8px_rgba(23,32,27,0.06)] xl:hidden">
          <div className="mx-auto flex max-w-3xl items-center justify-between gap-3">
            <div className="min-w-0">
              <div className="text-xs text-[var(--muted)]">{user ? `Trade ${outcome}` : "Sign in to trade"}</div>
              <div className="numeric truncate text-sm font-semibold">
                {calculations.valid
                  ? `${calculations.normalizedQuantity} contracts at ${calculations.normalizedPrice}`
                  : "Enter price and quantity"}
              </div>
              <div className={cn("mt-0.5 text-xs", insufficientBalance || !calculations.valid ? "text-[var(--brass-text)]" : "text-[var(--muted)]")}>
                Cost {formatCurrency(calculations.cost)} - Available {formatCurrency(availableBalance)}
              </div>
            </div>
            <Dialog.Trigger asChild>
              <Button variant="primary">Open ticket</Button>
            </Dialog.Trigger>
          </div>
        </div>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-50 bg-black/20" />
          <Dialog.Content className="fixed inset-x-0 bottom-0 z-50 max-h-[86dvh] overflow-y-auto rounded-t-lg bg-[var(--surface)] p-3 shadow-2xl">
            <Dialog.Title className="sr-only">Trade ticket</Dialog.Title>
            {renderTicket()}
            <Dialog.Close asChild>
              <Button className="mt-2 w-full" variant="secondary">
                Close
              </Button>
            </Dialog.Close>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </>
  );
}
