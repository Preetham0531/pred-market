"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import * as Dialog from "@radix-ui/react-dialog";
import {
  AlertTriangle,
  Bell,
  BriefcaseBusiness,
  ChevronRight,
  ClipboardList,
  LogOut,
  LineChart,
  LockKeyhole,
  Search,
  SearchX,
  ShieldCheck,
  Star,
  UserRound,
  Wallet
} from "lucide-react";
import { motion } from "motion/react";
import { useEffect, useMemo, useRef, useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getInitials } from "@/lib/auth-session";
import { useMarkets, useWalletData } from "@/lib/api-hooks";
import { cn, formatCurrency } from "@/lib/utils";

const navItems = [
  { label: "Markets", href: "/", icon: LineChart },
  { label: "Watchlist", href: "/watchlist", icon: Star },
  { label: "Portfolio", href: "/portfolio", icon: BriefcaseBusiness },
  { label: "Orders", href: "/orders", icon: ClipboardList },
  { label: "Wallet", href: "/wallet", icon: Wallet }
];

const protectedPrefixes = ["/watchlist", "/profile", "/portfolio", "/orders", "/wallet", "/markets/suggest", "/admin", "/account/security"];
const adminPrefixes = ["/admin"];

function isActive(pathname: string, href: string) {
  const cleanHref = href.split("?")[0];
  if (cleanHref === "/") return pathname === "/" || pathname === "/markets" || pathname.startsWith("/markets/");
  return pathname === cleanHref || pathname.startsWith(`${cleanHref}/`);
}

function MobileBottomNav() {
  const pathname = usePathname();
  const mobileItems = navItems;

  return (
    <nav className="fixed inset-x-0 bottom-0 z-[var(--z-bottom-nav)] border-t border-[var(--border)] bg-[var(--surface)] px-2 pb-[calc(0.5rem+env(safe-area-inset-bottom))] pt-1 shadow-[0_-8px_20px_rgba(15,23,42,0.06)] lg:hidden">
      <div className="grid grid-cols-5 gap-1">
        {mobileItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(pathname, item.href);

          return (
            <Link
              key={item.label}
              href={item.href}
              className={cn(
                "flex min-w-0 flex-col items-center gap-1 rounded-md px-1 py-1.5 text-[11px]",
                active ? "text-[var(--primary-strong)]" : "text-[var(--muted)]"
              )}
            >
              <Icon className="h-4 w-4" />
              <span className="truncate">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

function MarketSearch() {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const { data: markets = [], isLoading: marketsLoading, error: marketsError } = useMarkets();
  const normalizedQuery = query.trim().toLowerCase();
  const marketResults = useMemo(
    () =>
      markets
        .filter((market) => {
          if (!normalizedQuery) return true;
          return (
            market.title.toLowerCase().includes(normalizedQuery) ||
            market.subcategory.toLowerCase().includes(normalizedQuery) ||
            market.categorySlug.toLowerCase().includes(normalizedQuery)
          );
        })
        .slice(0, 5),
    [markets, normalizedQuery]
  );
  const loading = marketsLoading;
  const hasError = Boolean(marketsError);
  const noResults = !loading && !hasError && normalizedQuery.length > 0 && marketResults.length === 0;

  useEffect(() => {
    function closeOnOutsideClick(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) setOpen(false);
    }
    function closeOnEscape(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", closeOnOutsideClick);
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.removeEventListener("mousedown", closeOnOutsideClick);
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, []);

  return (
    <div className="relative" ref={containerRef}>
      <Button
        variant="ghost"
        aria-label="Search markets"
        aria-expanded={open}
        aria-haspopup="dialog"
        className="inline-flex w-9 justify-center bg-transparent px-0 text-[var(--muted)] hover:bg-[var(--surface-muted)]/60 md:w-[260px] md:justify-start md:px-3"
        onClick={() => setOpen((current) => !current)}
      >
          <Search className="h-4 w-4" />
          <span className="hidden md:inline">Search markets</span>
      </Button>
      {open ? (
        <div
          role="dialog"
          aria-label="Search markets"
          className="fixed inset-x-0 top-0 z-50 min-h-dvh bg-[var(--surface)] p-4 shadow-2xl md:absolute md:inset-auto md:right-0 md:top-full md:mt-2 md:min-h-0 md:w-[480px] md:rounded-md md:border md:border-[var(--border)] md:p-3"
        >
          <div className="flex items-center gap-2 border-b border-[color-mix(in_srgb,var(--border)_70%,transparent)] px-1">
            <Search className="h-4 w-4 text-[var(--muted)]" />
            <Input
              className="border-0 px-0 shadow-none focus:ring-0"
              placeholder="Search markets"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              autoFocus
            />
            <Button variant="ghost" size="icon" aria-label="Close search" onClick={() => setOpen(false)}>
              <SearchX className="h-4 w-4" />
            </Button>
          </div>
          <div className="mt-3 max-h-[420px] overflow-y-auto">
            {hasError ? (
              <div className="rounded-md border border-[var(--red-border)] bg-[var(--red-soft)] p-3 text-sm text-[var(--red-text)]">
                <div className="flex items-center gap-2 font-medium">
                  <AlertTriangle className="h-4 w-4" aria-hidden="true" />
                  Search data unavailable
                </div>
                <p className="mt-1 text-xs leading-5">Try again in a moment.</p>
              </div>
            ) : loading ? (
              <div className="space-y-2 p-2" aria-busy="true">
                <div className="exchange-skeleton h-9 rounded" />
                <div className="exchange-skeleton h-9 rounded" />
                <div className="exchange-skeleton h-9 rounded" />
              </div>
            ) : noResults ? (
              <div className="rounded-md border border-[var(--border)] bg-[var(--surface-muted)] p-3 text-sm text-[var(--muted)]">
                <div className="flex items-center gap-2 font-medium text-[var(--foreground)]">
                  <SearchX className="h-4 w-4" aria-hidden="true" />
                  No matches
                </div>
                <p className="mt-1 text-xs leading-5">Try a shorter market phrase.</p>
              </div>
            ) : (
              <>
                <div className="mb-2 px-2 text-xs font-medium text-[var(--muted)]">Markets</div>
                <div className="space-y-1">
                  {marketResults.map((market) => (
                  <Link
                    key={market.id}
                    href={`/markets/${market.id}`}
                    className="flex items-center justify-between gap-3 rounded-md px-3 py-2 text-sm hover:bg-[var(--surface-muted)]"
                    onClick={() => setOpen(false)}
                  >
                    <span className="min-w-0">
                      <span className="block truncate font-medium">{market.title.replace(/^Simulation:\s*/i, "")}</span>
                      <span className="mt-0.5 block text-xs text-[var(--muted)]">{market.subcategory}</span>
                    </span>
                    <ChevronRight className="h-4 w-4 shrink-0 text-[var(--muted)]" />
                  </Link>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}

function WalletBalance() {
  const { data } = useWalletData();
  return (
    <div className="numeric hidden px-2 py-1.5 text-sm font-medium text-[var(--foreground)] sm:block">
      {formatCurrency(data?.available ?? 0)}
    </div>
  );
}

function NotificationDialog() {
  return (
    <Dialog.Root>
      <Dialog.Trigger asChild>
        <Button variant="ghost" size="icon" aria-label="Notifications" className="bg-transparent">
          <Bell className="h-4 w-4" />
        </Button>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-black/20" />
        <Dialog.Content className="fixed right-4 top-16 z-50 w-[min(360px,calc(100vw-32px))] rounded-lg border border-[var(--border)] bg-[var(--surface)] p-3 shadow-2xl">
          <Dialog.Title className="text-sm font-semibold">Notifications</Dialog.Title>
          <div className="mt-3 space-y-2">
            {[
              ["Order partially filled", "Your India YES order filled 4 of 10 contracts."],
              ["Market closing soon", "Weather rainfall range market closes in 42 minutes."],
              ["Settlement evidence added", "Admin uploaded source evidence for a commodities market."]
            ].map(([title, detail]) => (
              <div key={title} className="rounded-md bg-[var(--surface-muted)]/70 p-3 text-sm">
                <div className="font-medium">{title}</div>
                <div className="mt-1 text-xs leading-5 text-[var(--muted)]">{detail}</div>
              </div>
            ))}
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

function ProfileDialog() {
  const { user, signOut, searchSwitchUsers, startImpersonation, stopImpersonation } = useAuth();
  const [switchQuery, setSwitchQuery] = useState("");
  const [switchReason, setSwitchReason] = useState("Support review");
  const [switchUsers, setSwitchUsers] = useState<Array<{ id: string; email: string; displayName: string; roles: string[]; status: string }>>([]);
  const [switchLoading, setSwitchLoading] = useState(false);
  const [switchError, setSwitchError] = useState("");
  if (!user) return null;
  const actor = user.actor;
  const isAdminActor = Boolean(actor?.roles.includes("ADMIN") || user.roles.includes("ADMIN"));
  const isImpersonating = Boolean(user.impersonation?.active);

  async function searchUsers() {
    setSwitchLoading(true);
    setSwitchError("");
    try {
      setSwitchUsers(await searchSwitchUsers(switchQuery));
    } catch (error) {
      setSwitchError(error instanceof Error ? error.message : "User search failed.");
    } finally {
      setSwitchLoading(false);
    }
  }

  return (
    <Dialog.Root>
      <Dialog.Trigger asChild>
        <button className="grid h-9 w-9 place-items-center rounded-full bg-[var(--surface-muted)]/80 text-xs font-semibold text-[var(--foreground)] transition hover:bg-[var(--surface-muted)]" aria-label="Open profile menu">
          {getInitials(user)}
        </button>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-black/20" />
        <Dialog.Content className="fixed right-4 top-16 z-50 w-[min(340px,calc(100vw-32px))] rounded-lg border border-[var(--border)] bg-[var(--surface)] p-3 shadow-2xl">
          <Dialog.Title className="text-sm font-semibold">Profile</Dialog.Title>
          <div className="mt-3 rounded-md bg-[var(--surface-muted)]/70 p-3">
            <div className="text-sm font-medium">{user.displayName}</div>
            <div className="mt-1 text-xs text-[var(--muted)]">{user.email}</div>
            {isImpersonating && actor ? (
              <div className="mt-2 rounded border border-[var(--brass-border)] bg-[var(--brass-soft)] px-2 py-1 text-xs text-[var(--brass-text)]">
                Viewing as user. Actor: {actor.email}
              </div>
            ) : null}
            <div className="mt-2 flex flex-wrap gap-1">
              {user.roles.map((role) => (
                <Badge key={role} tone={role === "ADMIN" ? "brass" : "blue"}>{role}</Badge>
              ))}
            </div>
          </div>
          <div className="mt-3 space-y-1">
            <Dialog.Close asChild>
              <Link className="flex items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-[var(--surface-muted)]" href="/account/security">
                <LockKeyhole className="h-4 w-4" />
                Account security
              </Link>
            </Dialog.Close>
            <Dialog.Close asChild>
              <Link className="flex items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-[var(--surface-muted)]" href="/profile">
                <UserRound className="h-4 w-4" />
                Profile
              </Link>
            </Dialog.Close>
            {isAdminActor ? (
              <Dialog.Close asChild>
                <Link className="flex items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-[var(--surface-muted)]" href="/admin">
                  <ShieldCheck className="h-4 w-4" />
                  Admin
                </Link>
              </Dialog.Close>
            ) : null}
            {isImpersonating ? (
              <Button className="w-full justify-start" variant="secondary" onClick={() => void stopImpersonation()}>
                <ShieldCheck className="h-4 w-4" />
                Return to admin
              </Button>
            ) : null}
            {isAdminActor && !isImpersonating ? (
              <Dialog.Root>
                <Dialog.Trigger asChild>
                  <Button className="w-full justify-start" variant="secondary" onClick={() => void searchUsers()}>
                    <UserRound className="h-4 w-4" />
                    Switch user view
                  </Button>
                </Dialog.Trigger>
                <Dialog.Portal>
                  <Dialog.Overlay className="fixed inset-0 z-[60] bg-black/30" />
                  <Dialog.Content className="fixed left-1/2 top-24 z-[60] w-[min(460px,calc(100vw-32px))] -translate-x-1/2 rounded-lg border border-[var(--border)] bg-[var(--surface)] p-3 shadow-2xl">
                    <Dialog.Title className="text-sm font-semibold">Switch user view</Dialog.Title>
                    <p className="mt-1 text-xs leading-5 text-[var(--muted)]">Read-only admin view. Trading and user-owned writes are blocked while switched.</p>
                    <div className="mt-3 grid gap-2">
                      <label className="text-xs font-medium text-[var(--muted)]">
                        User search
                        <div className="mt-1 flex gap-2">
                          <Input value={switchQuery} onChange={(event) => setSwitchQuery(event.target.value)} placeholder="email or display name" />
                          <Button variant="secondary" onClick={() => void searchUsers()} disabled={switchLoading}>
                            Search
                          </Button>
                        </div>
                      </label>
                      <label className="text-xs font-medium text-[var(--muted)]">
                        Reason
                        <Input className="mt-1" value={switchReason} onChange={(event) => setSwitchReason(event.target.value)} />
                      </label>
                    </div>
                    {switchError ? (
                      <div className="mt-3 rounded-md border border-[var(--red-border)] bg-[var(--red-soft)] p-2 text-xs text-[var(--red-text)]">{switchError}</div>
                    ) : null}
                    <div className="mt-3 max-h-64 space-y-1 overflow-y-auto">
                      {switchUsers.map((item) => {
                        const blocked = item.roles.includes("ADMIN");
                        return (
                          <button
                            key={item.id}
                            className="w-full rounded-md border border-[var(--border)] bg-[var(--surface-muted)] px-3 py-2 text-left text-sm transition hover:border-[var(--primary)] disabled:cursor-not-allowed disabled:opacity-60"
                            disabled={blocked}
                            onClick={async () => {
                              await startImpersonation(item.id, switchReason);
                            }}
                          >
                            <span className="block font-medium">{item.displayName}</span>
                            <span className="mt-0.5 block text-xs text-[var(--muted)]">{item.email}{blocked ? " / admin profile blocked" : ""}</span>
                          </button>
                        );
                      })}
                      {!switchLoading && switchUsers.length === 0 ? (
                        <div className="rounded-md border border-[var(--border)] bg-[var(--surface-muted)] p-3 text-xs text-[var(--muted)]">No switchable users found.</div>
                      ) : null}
                    </div>
                  </Dialog.Content>
                </Dialog.Portal>
              </Dialog.Root>
            ) : null}
            <Button className="w-full justify-start" variant="ghost" onClick={() => void signOut()}>
              <LogOut className="h-4 w-4" />
              Sign out
            </Button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

function ImpersonationBanner() {
  const { user, stopImpersonation } = useAuth();
  if (!user?.impersonation?.active || !user.actor) return null;
  return (
    <div className="border-b border-[var(--brass-border)] bg-[var(--brass-soft)] px-4 py-2 text-xs text-[var(--brass-text)] lg:px-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span>
          Read-only user view: <strong>{user.email}</strong>. Real actor: <strong>{user.actor.email}</strong>.
        </span>
        <Button size="sm" variant="secondary" onClick={() => void stopImpersonation()}>
          Return to admin
        </Button>
      </div>
    </div>
  );
}

function TopNavigation() {
  const { user, loading } = useAuth();
  const pathname = usePathname();
  const visibleItems = navItems;

  return (
    <header className="sticky top-0 z-30 border-b border-[color-mix(in_srgb,var(--border)_55%,transparent)] bg-[var(--surface)] px-4 py-3 lg:px-8">
      <div className="mx-auto flex max-w-[1680px] items-center gap-4">
        <Link href="/" className="flex shrink-0 items-center gap-3">
          <div className="grid h-9 w-9 place-items-center rounded-md bg-[var(--primary)] text-sm font-semibold text-white shadow-sm">
            PM
          </div>
          <div className="hidden sm:block">
            <div className="text-sm font-semibold text-[var(--foreground)]">Pred-Market</div>
            <div className="text-xs text-[var(--green-text)]">Simulated funds</div>
          </div>
        </Link>

        <nav className="hidden min-w-0 flex-1 items-center gap-1 lg:flex" aria-label="Primary navigation">
          {visibleItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(pathname, item.href);
            return (
              <Link
                key={item.label}
                href={item.href}
                className={cn(
                  "inline-flex h-9 items-center gap-2 rounded-md px-2.5 text-sm font-medium transition",
                  active ? "bg-[var(--primary-soft)] text-[var(--primary-strong)]" : "text-[var(--muted)] hover:bg-[var(--surface-muted)]/64 hover:text-[var(--foreground)]"
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="min-w-0 flex-1 lg:hidden" />
        <MarketSearch />
        {user ? <NotificationDialog /> : null}
        {user ? (
          <>
            <WalletBalance />
            <ProfileDialog />
          </>
        ) : loading ? (
          <div className="h-9 w-24 rounded-md border border-[var(--border)] bg-[var(--surface-muted)]" />
        ) : (
          <>
          <div className="hidden items-center gap-2 sm:flex">
            <Link className={buttonVariants({ variant: "secondary", size: "md" })} href="/sign-in">
              Sign in
            </Link>
            <Link className={buttonVariants({ variant: "primary", size: "md" })} href="/sign-up">
              Create account
            </Link>
          </div>
          <Link className={cn(buttonVariants({ variant: "secondary", size: "icon" }), "sm:hidden")} href="/sign-in" aria-label="Sign in">
            <LockKeyhole className="h-4 w-4" />
          </Link>
          </>
        )}
      </div>
    </header>
  );
}

function ProtectedRedirect() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, loading } = useAuth();
  const protectedPath = protectedPrefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
  const adminPath = adminPrefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));

  useEffect(() => {
    if (loading) return;
    if (protectedPath && !user) {
      router.replace(`/sign-in?next=${encodeURIComponent(pathname)}`);
      return;
    }
    if (adminPath && user && !user.roles.includes("ADMIN")) {
      router.replace("/markets");
    }
  }, [adminPath, loading, pathname, protectedPath, router, user]);

  return null;
}

function RouteAccessGate({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, loading } = useAuth();
  const protectedPath = protectedPrefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
  const adminPath = adminPrefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
  const blocked = protectedPath && (!user || (adminPath && !user.roles.includes("ADMIN")));

  if ((protectedPath && loading) || blocked) {
    return (
      <div className="exchange-panel rounded-md p-4 text-sm text-[var(--muted)]" aria-live="polite">
        Checking access...
      </div>
    );
  }

  return <>{children}</>;
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isAuthSurface =
    pathname === "/sign-in" ||
    pathname === "/sign-up" ||
    pathname === "/forgot-password" ||
    pathname === "/reset-password" ||
    pathname === "/verify-email";

  if (isAuthSurface) {
    return <div className="min-h-dvh bg-[var(--background)] text-[var(--foreground)]">{children}</div>;
  }

  return (
    <div className="min-h-dvh bg-[var(--background)] text-[var(--foreground)]">
      <TopNavigation />
      <ImpersonationBanner />
      <ProtectedRedirect />
      <motion.main
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.22, ease: "easeOut" }}
        className="mx-auto w-full max-w-[1680px] px-4 pb-36 pt-5 sm:px-6 lg:px-8 lg:pb-8"
      >
        <RouteAccessGate>{children}</RouteAccessGate>
      </motion.main>
      <MobileBottomNav />
    </div>
  );
}
