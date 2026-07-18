"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { XCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { USE_MOCK_DATA } from "@/lib/api-client";
import { useCancelOrder, useMarkets, useOrdersData } from "@/lib/api-hooks";
import { markets, userOrders, type UserOrder } from "@/lib/mock-data";

export function OrdersWorkspace() {
  const { data: ordersPayload, isLoading, error } = useOrdersData();
  const { data: liveMarkets = markets } = useMarkets();
  const cancelMutation = useCancelOrder();
  const [mockOrders, setMockOrders] = useState<UserOrder[]>(userOrders);
  const [statusFilter, setStatusFilter] = useState<"All" | UserOrder["status"]>("All");
  const [lastCancelled, setLastCancelled] = useState("");
  const orders = useMemo(() => (USE_MOCK_DATA ? mockOrders : ordersPayload?.items ?? []), [mockOrders, ordersPayload]);
  const visibleOrders = useMemo(() => (statusFilter === "All" ? orders : orders.filter((order) => order.status === statusFilter)), [orders, statusFilter]);

  function cancelOrder(orderId: string) {
    if (!USE_MOCK_DATA) {
      cancelMutation.mutate(orderId);
      setLastCancelled(orderId);
      return;
    }
    setMockOrders((current) =>
      current.map((order) =>
        order.id === orderId && order.status === "Open"
          ? { ...order, status: "Cancelled" }
          : order
      )
    );
    setLastCancelled(orderId);
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold">Orders</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">Open, filled, and cancelled limit orders across markets.</p>
      </div>
      {error ? (
        <div className="rounded-md border border-[var(--red-border)] bg-[var(--red-soft)] px-3 py-2 text-sm text-[var(--red-text)]">
          Orders could not be loaded. Sign in and try again.
        </div>
      ) : null}
      {lastCancelled ? (
        <div className="rounded-md border border-[var(--green-border)] bg-[var(--green-soft)] px-3 py-2 text-sm text-[var(--green-text)]" role="status">
          Cancel request recorded for {lastCancelled}. Open order collateral will release after backend confirmation.
        </div>
      ) : null}
      <div className="exchange-panel overflow-hidden rounded-md">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--border)] px-3 py-2">
          <div className="text-sm font-semibold">Order blotter</div>
          <div className="inline-flex rounded-md border border-[var(--border)] bg-[var(--surface-muted)] p-1">
            {(["All", "Open", "Filled", "Cancelled"] as const).map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => setStatusFilter(item)}
                className={
                  statusFilter === item
                    ? "h-7 rounded bg-[var(--surface)] px-2 text-xs font-medium text-[var(--foreground)]"
                    : "h-7 rounded px-2 text-xs font-medium text-[var(--muted)] hover:text-[var(--foreground)]"
                }
              >
                {item}
              </button>
            ))}
          </div>
        </div>
        <div className="exchange-table-header hidden grid-cols-[110px_1fr_80px_90px_90px_90px_110px_96px] px-3 py-2 md:grid">
          <div>ID</div>
          <div>Market</div>
          <div>Side</div>
          <div>Outcome</div>
          <div>Price</div>
          <div>Filled</div>
          <div>Status</div>
          <div>Action</div>
        </div>
        <div className="divide-y divide-[var(--border)]">
          {isLoading && !USE_MOCK_DATA ? (
            <div className="px-3 py-6 text-sm text-[var(--muted)]">Loading orders...</div>
          ) : visibleOrders.length ? visibleOrders.map((order) => {
            const market = liveMarkets.find((item) => item.id === order.marketId);
            return (
              <div key={order.id} className="grid min-h-[62px] gap-2 px-3 py-3 text-sm md:grid-cols-[110px_1fr_80px_90px_90px_90px_110px_96px] md:items-center">
                <div className="font-mono text-xs text-[var(--muted)]">{order.id}</div>
                <Link href={`/markets/${order.marketId}`} className="min-w-0 hover:text-[var(--primary-strong)]">
                  <div className="truncate font-medium">{market?.title}</div>
                  <div className="mt-1 text-xs text-[var(--muted)]">{order.createdAt}</div>
                </Link>
                <div>{order.side}</div>
                <div>{order.outcome}</div>
                <div className="numeric">{order.price}</div>
                <div className="numeric">{order.filled}/{order.quantity}</div>
                <Badge tone={order.status === "Open" ? "green" : order.status === "Cancelled" ? "red" : "blue"}>{order.status}</Badge>
                {order.status === "Open" ? (
                  <Button size="sm" variant="secondary" onClick={() => cancelOrder(order.id)} disabled={cancelMutation.isPending}>
                    <XCircle className="h-3.5 w-3.5" />
                    Cancel
                  </Button>
                ) : (
                  <span className="text-xs text-[var(--muted)]">No action</span>
                )}
              </div>
            );
          }) : (
            <div className="px-3 py-6 text-sm text-[var(--muted)]">No {statusFilter === "All" ? "" : statusFilter.toLowerCase()} orders yet.</div>
          )}
        </div>
      </div>
    </div>
  );
}
