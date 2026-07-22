"use client";

import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { apiRequest, USE_MOCK_DATA, WS_BASE_URL } from "@/lib/api-client";

type RealtimeEvent = {
  event_type: string;
  market_id?: string | null;
  sequence?: number;
  payload?: Record<string, unknown>;
};

function isRealtimeEvent(event: RealtimeEvent | { type?: string }): event is RealtimeEvent {
  return !("type" in event) && "event_type" in event;
}

export type RealtimeState = {
  connected: boolean;
  reconnecting: boolean;
  lastEventAt: string | null;
  lastSequence: number | null;
  stale: boolean;
  error: string | null;
};

const initialRealtimeState: RealtimeState = {
  connected: false,
  reconnecting: false,
  lastEventAt: null,
  lastSequence: null,
  stale: false,
  error: null
};

function websocketUrl(ticket?: string) {
  const browserOrigin =
    typeof window === "undefined"
      ? "ws://localhost:8010"
      : `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}`;
  const base = WS_BASE_URL || browserOrigin;
  const url = new URL("/ws/v1", base);
  if (ticket) url.searchParams.set("ticket", ticket);
  return url.toString();
}

export function useMarketRealtime(marketId?: string) {
  const queryClient = useQueryClient();
  const [state, setState] = useState<RealtimeState>(initialRealtimeState);

  useEffect(() => {
    if (USE_MOCK_DATA || !marketId) {
      return;
    }

    let socket: WebSocket | null = null;
    let cancelled = false;
    let retry = 0;
    let staleTimer: ReturnType<typeof setTimeout> | undefined;

    function markEvent(event?: RealtimeEvent) {
      if (staleTimer) clearTimeout(staleTimer);
      const now = new Date().toISOString();
      setState({
        connected: true,
        reconnecting: false,
        lastEventAt: now,
        lastSequence: event?.sequence ?? null,
        stale: false,
        error: null
      });
      staleTimer = setTimeout(() => {
        setState((current) => ({ ...current, stale: true }));
      }, 45_000);
    }

    function connect() {
      if (cancelled) return;
      setState((current) => ({ ...current, reconnecting: retry > 0, error: null }));
      const nextSocket = new WebSocket(websocketUrl());
      socket = nextSocket;
      nextSocket.addEventListener("open", () => {
        retry = 0;
        setState((current) => ({ ...current, connected: true, reconnecting: false, stale: false, error: null }));
      });
      nextSocket.addEventListener("open", () => {
        nextSocket.send(JSON.stringify({ type: "subscribe", channel: "market.order_book", market_id: marketId }));
        nextSocket.send(JSON.stringify({ type: "subscribe", channel: "market.trades", market_id: marketId }));
        nextSocket.send(JSON.stringify({ type: "subscribe", channel: "market.ticker", market_id: marketId }));
        nextSocket.send(JSON.stringify({ type: "subscribe", channel: "market.status", market_id: marketId }));
      });
      nextSocket.addEventListener("message", (message) => {
        const event = JSON.parse(message.data) as RealtimeEvent | { type?: string };
        if (!isRealtimeEvent(event)) return;
        markEvent(event);
        void queryClient.invalidateQueries({ queryKey: ["market", marketId] });
        void queryClient.invalidateQueries({ queryKey: ["markets"] });
      });
      nextSocket.addEventListener("close", () => {
        if (cancelled) return;
        retry += 1;
        setState((current) => ({ ...current, connected: false, reconnecting: true, stale: true }));
        setTimeout(connect, Math.min(1000 * 2 ** retry, 15_000));
      });
      nextSocket.addEventListener("error", () => {
        setState((current) => ({ ...current, connected: false, reconnecting: true, stale: true, error: "Realtime connection failed." }));
      });
    }

    connect();

    return () => {
      cancelled = true;
      if (staleTimer) clearTimeout(staleTimer);
      socket?.close();
    };
  }, [marketId, queryClient]);

  return USE_MOCK_DATA || !marketId ? initialRealtimeState : state;
}

export function useUserRealtime(enabled: boolean) {
  const queryClient = useQueryClient();
  const [state, setState] = useState<RealtimeState>(initialRealtimeState);

  useEffect(() => {
    if (USE_MOCK_DATA || !enabled) {
      return;
    }
    let socket: WebSocket | null = null;
    let cancelled = false;
    let retry = 0;
    let staleTimer: ReturnType<typeof setTimeout> | undefined;

    function markEvent(event?: RealtimeEvent) {
      if (staleTimer) clearTimeout(staleTimer);
      setState({
        connected: true,
        reconnecting: false,
        lastEventAt: new Date().toISOString(),
        lastSequence: event?.sequence ?? null,
        stale: false,
        error: null
      });
      staleTimer = setTimeout(() => {
        setState((current) => ({ ...current, stale: true }));
      }, 45_000);
    }

    function connectWithTicket() {
      if (cancelled) return;
      setState((current) => ({ ...current, reconnecting: retry > 0, error: null }));
    void apiRequest<{ ticket: string }>("/api/v1/auth/ws-ticket", { method: "POST" }).then((payload) => {
      if (cancelled) return;
      socket = new WebSocket(websocketUrl(payload.ticket));
      socket.addEventListener("open", () => {
        retry = 0;
        setState((current) => ({ ...current, connected: true, reconnecting: false, stale: false, error: null }));
        socket?.send(JSON.stringify({ type: "subscribe", channel: "user.orders" }));
        socket?.send(JSON.stringify({ type: "subscribe", channel: "user.positions" }));
        socket?.send(JSON.stringify({ type: "subscribe", channel: "user.wallet" }));
        socket?.send(JSON.stringify({ type: "subscribe", channel: "user.notifications" }));
      });
      socket.addEventListener("message", (message) => {
      const event = JSON.parse(message.data) as RealtimeEvent | { type?: string };
        if (!isRealtimeEvent(event)) return;
        markEvent(event);
        void queryClient.invalidateQueries({ queryKey: ["orders"] });
        void queryClient.invalidateQueries({ queryKey: ["portfolio"] });
        void queryClient.invalidateQueries({ queryKey: ["wallet"] });
      });
      socket.addEventListener("close", () => {
        if (cancelled) return;
        retry += 1;
        setState((current) => ({ ...current, connected: false, reconnecting: true, stale: true }));
        setTimeout(connectWithTicket, Math.min(1000 * 2 ** retry, 15_000));
      });
      socket.addEventListener("error", () => {
        setState((current) => ({ ...current, connected: false, reconnecting: true, stale: true, error: "Realtime connection failed." }));
      });
    }).catch(() => {
      if (cancelled) return;
      retry += 1;
      setState((current) => ({ ...current, connected: false, reconnecting: true, stale: true, error: "Realtime ticket could not be created." }));
      setTimeout(connectWithTicket, Math.min(1000 * 2 ** retry, 15_000));
    });
    }

    connectWithTicket();

    return () => {
      cancelled = true;
      if (staleTimer) clearTimeout(staleTimer);
      socket?.close();
    };
  }, [enabled, queryClient]);

  return USE_MOCK_DATA || !enabled ? initialRealtimeState : state;
}
