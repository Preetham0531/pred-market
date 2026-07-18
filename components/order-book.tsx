import { type Market } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

type OrderBookProps = {
  market: Market;
};

type OrderLevelRow = Market["orderBook"]["yesBids"][number];
type EmptyLevelRow = { price: 0; quantity: 0; empty: true; index: number };

function OrderRows({ label, rows, tone }: { label: string; rows: Market["orderBook"]["yesBids"]; tone: "green" | "red" }) {
  const maxQuantity = Math.max(...rows.map((row) => row.quantity), 1);
  const visibleRows: Array<OrderLevelRow | EmptyLevelRow> = rows.length
    ? rows
    : Array.from({ length: 5 }, (_, index) => ({ price: 0, quantity: 0, empty: true, index }));

  return (
    <div>
      <div className="exchange-table-header grid grid-cols-[72px_1fr_1fr] rounded-t-md px-2 py-2">
        <span>{label}</span>
        <span className="text-right">Qty</span>
        <span className="text-right">Total</span>
      </div>
      <div className="space-y-1 overflow-hidden pt-1">
        {visibleRows.map((row) => (
          <div
            key={"empty" in row ? `${label}-empty-${row.index}` : `${label}-${row.price}`}
            className={cn(
              "exchange-live-row relative grid min-h-9 grid-cols-[72px_1fr_1fr] items-center overflow-hidden rounded-md px-2 text-sm",
              "empty" in row ? "text-[var(--muted)]" : ""
            )}
            aria-label={"empty" in row ? `${label} empty level` : `${label} price ${row.price}, quantity ${row.quantity}`}
          >
            {"empty" in row ? null : (
              <div
                className={cn("exchange-bar-fill absolute inset-y-0 right-0", tone === "green" ? "bg-[color-mix(in_srgb,var(--green-border)_24%,transparent)]" : "bg-[color-mix(in_srgb,var(--red-border)_24%,transparent)]")}
                style={{ width: `${Math.max(10, (row.quantity / maxQuantity) * 100)}%` }}
              />
            )}
            <span className={cn("numeric relative font-semibold", tone === "green" ? "text-[var(--green-text)]" : "text-[var(--red-text)]")}>
              {"empty" in row ? "-" : row.price}
            </span>
            <span className="numeric relative text-right">{"empty" in row ? "-" : row.quantity}</span>
            <span className="numeric relative text-right text-[var(--muted)]">{"empty" in row ? "-" : row.price * row.quantity}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function OrderBook({ market }: OrderBookProps) {
  const yesBest = market.orderBook.yesBids[0]?.price ?? 0;
  const noBest = market.orderBook.noBids[0]?.price ?? 0;
  const yesAsk = 100 - noBest;
  const spread = Math.max(0, yesAsk - yesBest);

  return (
    <section className="rounded-md bg-[var(--surface)]/38 p-3" aria-label="Market depth">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold">Market depth</h2>
          <p className="text-xs text-[var(--muted)]">Binary YES/NO book with complementary pricing.</p>
        </div>
        <div className="grid grid-cols-3 overflow-hidden rounded-md bg-[var(--surface-raised)]/42 text-center text-xs">
          <div className="px-3 py-2">
            <div className="text-[var(--muted)]">Best YES</div>
            <div className="numeric mt-0.5 font-semibold text-[var(--green-text)]">{yesBest}</div>
          </div>
          <div className="border-x border-[color-mix(in_srgb,var(--border)_55%,transparent)] px-3 py-2">
            <div className="text-[var(--muted)]">Spread</div>
            <div className="numeric mt-0.5 font-semibold">{spread} pts</div>
          </div>
          <div className="px-3 py-2">
            <div className="text-[var(--muted)]">YES ask</div>
            <div className="numeric mt-0.5 font-semibold text-[var(--red-text)]">{yesAsk}</div>
          </div>
        </div>
      </div>
      {!market.orderBook.yesBids.length && !market.orderBook.noBids.length ? (
        <div className="mb-3 rounded-md border border-[var(--brass-border)] bg-[var(--brass-soft)] px-3 py-2 text-xs text-[var(--brass-text)]">
          No live limit orders yet. Static seeded levels will appear once liquidity is available.
        </div>
      ) : null}
      <div className="grid gap-4 md:grid-cols-2">
        <OrderRows label="YES bids" rows={market.orderBook.yesBids} tone="green" />
        <OrderRows label="NO bids" rows={market.orderBook.noBids} tone="red" />
      </div>
    </section>
  );
}
