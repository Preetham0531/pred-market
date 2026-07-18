"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Bot, CheckCircle2, Database, FileSearch, Play, Plus, Send, ShieldAlert, Wand2, XCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  useAdminCreateDataSource,
  useAdminCreateMarketDraft,
  useAdminDataSources,
  useAdminGenerateAiDrafts,
  useAdminMarketDraftAction,
  useAdminMarketDrafts,
  useAdminRunIngestion,
  useAdminSourceEvents,
  useCategories
} from "@/lib/api-hooks";
import type { MarketDraft } from "@/lib/api-mappers";
import { cn } from "@/lib/utils";

const marketTypes = ["Binary", "Multiple-choice", "Range", "Threshold", "Conditional", "Combo"];

export default function AdminMarketIssuePage() {
  const { data: categories = [] } = useCategories();
  const { data: sources = [] } = useAdminDataSources();
  const { data: events = [] } = useAdminSourceEvents();
  const { data: drafts = [], isLoading: draftsLoading, error: draftsError } = useAdminMarketDrafts();
  const runIngestion = useAdminRunIngestion();
  const generateAiDrafts = useAdminGenerateAiDrafts();
  const createDataSource = useAdminCreateDataSource();
  const createDraft = useAdminCreateMarketDraft();
  const approveDraft = useAdminMarketDraftAction("approve");
  const rejectDraft = useAdminMarketDraftAction("reject");
  const listDraft = useAdminMarketDraftAction("list");

  const [ingestionCategory, setIngestionCategory] = useState("tech-science");
  const [ingestionQuery, setIngestionQuery] = useState("frontier AI official product releases");
  const [sourceCategory, setSourceCategory] = useState("economics");
  const [sourceName, setSourceName] = useState("Official source registry entry");
  const [sourceProvider, setSourceProvider] = useState("Official provider");
  const [sourceUrl, setSourceUrl] = useState("https://example.gov/data");
  const [directCategory, setDirectCategory] = useState("sports");
  const [directType, setDirectType] = useState("Binary");
  const [directQuestion, setDirectQuestion] = useState("Will India be declared winner by the official source?");
  const [directSourceId, setDirectSourceId] = useState("");
  const [directCloseTime, setDirectCloseTime] = useState("Jul 31, 2026 23:59 UTC");
  const [directRule, setDirectRule] = useState("YES resolves if the approved settlement source confirms the market question before the deadline. Otherwise NO resolves, unless the void policy applies.");
  const [directListImmediately, setDirectListImmediately] = useState(true);

  const aiDrafts = useMemo(() => drafts.filter((draft) => draft.origin === "AI"), [drafts]);
  const traderDrafts = useMemo(() => drafts.filter((draft) => draft.origin === "TRADER"), [drafts]);
  const adminDrafts = useMemo(() => drafts.filter((draft) => draft.origin === "ADMIN"), [drafts]);
  const settlementSources = useMemo(() => sources.filter((source) => source.settlementEligible), [sources]);

  async function submitDataSource() {
    await createDataSource.mutateAsync({
      name: sourceName,
      provider: sourceProvider,
      source_type: "OFFICIAL_API",
      category_slug: sourceCategory,
      base_url: sourceUrl,
      license_status: "PUBLIC_OFFICIAL",
      automation_level: 1,
      refresh_schedule: "MANUAL",
      settlement_eligible: true,
      discovery_eligible: true,
      notes: "Created from admin issuing workspace."
    });
  }

  async function submitDirectMarket() {
    const source = settlementSources.find((item) => item.id === directSourceId) ?? settlementSources.find((item) => item.categorySlug === directCategory) ?? settlementSources[0];
    await createDraft.mutateAsync({
      origin: "ADMIN",
      category_slug: directCategory,
      subcategory: "Admin direct",
      market_type: directType,
      question: directQuestion,
      outcomes: directType === "Binary" || directType === "Threshold" || directType === "Conditional" || directType === "Combo" ? ["YES", "NO"] : ["Outcome A", "Outcome B", "Other"],
      close_time: directCloseTime,
      source: source?.name ?? "Approved settlement source",
      resolution_rule: directRule,
      void_policy: "Void only if the approved source is unavailable or the category rulebook requires voiding.",
      settlement_source_id: source?.id,
      discovery_source_id: source?.id,
      admin_notes: "Created directly by admin.",
      list_immediately: directListImmediately
    });
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Market issuing</h1>
          <p className="mt-1 max-w-3xl text-sm text-[var(--muted)]">
            One pipeline for AI candidates, admin-created markets, and trader suggestions. Markets list only after source, rule, outcome, and admin checks pass.
          </p>
        </div>
        <Link className={cn(buttonVariants({ variant: "secondary", size: "md" }), "w-fit")} href="/admin">
          Review queue
        </Link>
      </div>

      {draftsError ? (
        <div className="rounded-md border border-[var(--red-border)] bg-[var(--red-soft)] px-3 py-2 text-sm text-[var(--red-text)]">
          Market issuing data could not be loaded. Confirm you are signed in as admin and the backend is reachable.
        </div>
      ) : null}

      <section className="grid gap-3 md:grid-cols-4">
        <Metric label="Sources" value={sources.length} detail={`${sources.filter((source) => source.settlementEligible).length} settlement approved`} />
        <Metric label="Source events" value={events.length} detail="Normalized ingestion records" />
        <Metric label="Drafts" value={drafts.length} detail={`${drafts.filter((draft) => draft.status === "LISTED").length} listed`} />
        <Metric label="Needs review" value={drafts.filter((draft) => ["NEEDS_REVIEW", "NEEDS_CHANGES"].includes(draft.status)).length} detail="Admin action required" />
      </section>

      <section className="grid gap-3 lg:grid-cols-3">
        <AIPolicyCard
          title="AI can draft"
          detail="Source events can become structured market candidates with category, outcomes, rule text, evidence, confidence, and rationale."
          tone="blue"
        />
        <AIPolicyCard
          title="Validators decide readiness"
          detail="Deterministic checks still control duplicates, prohibited topics, approved settlement sources, close time, outcomes, and rule completeness."
          tone="brass"
        />
        <AIPolicyCard
          title="Admins control listing"
          detail="AI cannot list, settle, trade, or override policy. Every approved market still requires admin action and audit logs."
          tone="green"
        />
      </section>

      <Tabs defaultValue="ai" className="space-y-4">
        <TabsList className="overflow-x-auto">
          <TabsTrigger value="ai"><Bot className="mr-1 h-3.5 w-3.5" />AI candidates</TabsTrigger>
          <TabsTrigger value="direct"><Plus className="mr-1 h-3.5 w-3.5" />Direct create</TabsTrigger>
          <TabsTrigger value="trader"><Send className="mr-1 h-3.5 w-3.5" />Trader suggestions</TabsTrigger>
          <TabsTrigger value="sources"><Database className="mr-1 h-3.5 w-3.5" />Data sources</TabsTrigger>
        </TabsList>

        <TabsContent value="ai" className="space-y-4">
          <div className="grid gap-4 xl:grid-cols-[360px_1fr]">
            <section className="exchange-panel rounded-md p-3">
              <h2 className="text-sm font-semibold">Ingest and generate</h2>
              <p className="mt-1 text-xs leading-5 text-[var(--muted)]">V1 creates auditable draft candidates from source events. External provider fetchers plug into this layer later.</p>
              <div className="mt-4 space-y-3">
                <label className="block">
                  <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Category</span>
                  <select className="h-9 w-full rounded-md border border-[var(--border)] bg-[var(--surface)] px-3 text-sm" value={ingestionCategory} onChange={(event) => setIngestionCategory(event.target.value)}>
                    {categories.map((category) => <option key={category.slug} value={category.slug}>{category.name}</option>)}
                  </select>
                </label>
                <label className="block">
                  <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Discovery query</span>
                  <Input value={ingestionQuery} onChange={(event) => setIngestionQuery(event.target.value)} />
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <Button disabled={runIngestion.isPending} onClick={() => runIngestion.mutate({ category_slug: ingestionCategory, query: ingestionQuery, limit: 5 })}>
                    <Play className="h-4 w-4" />{runIngestion.isPending ? "Running" : "Ingest"}
                  </Button>
                  <Button disabled={generateAiDrafts.isPending} variant="secondary" onClick={() => generateAiDrafts.mutate({ category_slug: ingestionCategory, limit: 5 })}>
                    <Wand2 className="h-4 w-4" />{generateAiDrafts.isPending ? "Drafting" : "Generate"}
                  </Button>
                </div>
                {runIngestion.data ? <p className="text-xs text-[var(--muted)]">Created {runIngestion.data.created_events} event(s), skipped {runIngestion.data.skipped_duplicates} duplicate(s).</p> : null}
                {generateAiDrafts.data ? <p className="text-xs text-[var(--muted)]">Generated {generateAiDrafts.data.created_drafts} draft candidate(s).</p> : null}
              </div>
            </section>
            <DraftBoard drafts={aiDrafts} loading={draftsLoading} approveDraft={approveDraft.mutate} rejectDraft={rejectDraft.mutate} listDraft={listDraft.mutate} />
          </div>
        </TabsContent>

        <TabsContent value="direct" className="grid gap-4 xl:grid-cols-[440px_1fr]">
          <section className="exchange-panel rounded-md p-3">
            <h2 className="text-sm font-semibold">Admin direct create</h2>
            <p className="mt-1 text-xs leading-5 text-[var(--muted)]">Admin-created markets still run the same checks. If all checks pass, they can list immediately.</p>
            <div className="mt-4 space-y-3">
              <label className="block">
                <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Category</span>
                <select className="h-9 w-full rounded-md border border-[var(--border)] bg-[var(--surface)] px-3 text-sm" value={directCategory} onChange={(event) => setDirectCategory(event.target.value)}>
                  {categories.map((category) => <option key={category.slug} value={category.slug}>{category.name}</option>)}
                </select>
              </label>
              <label className="block">
                <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Market type</span>
                <select className="h-9 w-full rounded-md border border-[var(--border)] bg-[var(--surface)] px-3 text-sm" value={directType} onChange={(event) => setDirectType(event.target.value)}>
                  {marketTypes.map((type) => <option key={type} value={type}>{type}</option>)}
                </select>
              </label>
              <label className="block">
                <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Question</span>
                <Input value={directQuestion} onChange={(event) => setDirectQuestion(event.target.value)} />
              </label>
              <label className="block">
                <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Approved settlement source</span>
                <select className="h-9 w-full rounded-md border border-[var(--border)] bg-[var(--surface)] px-3 text-sm" value={directSourceId} onChange={(event) => setDirectSourceId(event.target.value)}>
                  <option value="">Auto-select category source</option>
                  {settlementSources.map((source) => <option key={source.id} value={source.id}>{source.name}</option>)}
                </select>
              </label>
              <label className="block">
                <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Close time</span>
                <Input value={directCloseTime} onChange={(event) => setDirectCloseTime(event.target.value)} />
              </label>
              <label className="block">
                <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Resolution rule</span>
                <textarea className="min-h-28 w-full rounded-md border border-[var(--border)] bg-[var(--surface)] p-3 text-sm outline-none focus:ring-2 focus:ring-[var(--ring)]" value={directRule} onChange={(event) => setDirectRule(event.target.value)} />
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={directListImmediately} onChange={(event) => setDirectListImmediately(event.target.checked)} />
                List immediately if checks pass
              </label>
              <Button className="w-full" disabled={createDraft.isPending} onClick={() => void submitDirectMarket()}>
                {createDraft.isPending ? "Creating" : "Create market draft"}
              </Button>
              {createDraft.error ? <p className="text-xs text-[var(--red-text)]">Create failed. Confirm source approval, duplicate title, and admin session.</p> : null}
            </div>
          </section>
          <DraftBoard drafts={adminDrafts} loading={draftsLoading} approveDraft={approveDraft.mutate} rejectDraft={rejectDraft.mutate} listDraft={listDraft.mutate} />
        </TabsContent>

        <TabsContent value="trader">
          <DraftBoard drafts={traderDrafts} loading={draftsLoading} approveDraft={approveDraft.mutate} rejectDraft={rejectDraft.mutate} listDraft={listDraft.mutate} />
        </TabsContent>

        <TabsContent value="sources" className="grid gap-4 xl:grid-cols-[380px_1fr]">
          <section className="exchange-panel rounded-md p-3">
            <h2 className="text-sm font-semibold">Register source</h2>
            <p className="mt-1 text-xs leading-5 text-[var(--muted)]">A source can be discovery-only, settlement-approved, or both. No market should list without a settlement-approved source.</p>
            <div className="mt-4 space-y-3">
              <Input value={sourceName} onChange={(event) => setSourceName(event.target.value)} aria-label="Source name" />
              <Input value={sourceProvider} onChange={(event) => setSourceProvider(event.target.value)} aria-label="Provider" />
              <Input value={sourceUrl} onChange={(event) => setSourceUrl(event.target.value)} aria-label="Source URL" />
              <select className="h-9 w-full rounded-md border border-[var(--border)] bg-[var(--surface)] px-3 text-sm" value={sourceCategory} onChange={(event) => setSourceCategory(event.target.value)}>
                {categories.map((category) => <option key={category.slug} value={category.slug}>{category.name}</option>)}
              </select>
              <Button className="w-full" disabled={createDataSource.isPending} onClick={() => void submitDataSource()}>
                {createDataSource.isPending ? "Saving" : "Add settlement source"}
              </Button>
            </div>
          </section>
          <section className="exchange-panel overflow-x-auto rounded-md">
            <div className="border-b border-[var(--border)] px-3 py-2 text-sm font-semibold">Source registry</div>
            <div className="exchange-table-header grid min-w-[900px] grid-cols-[minmax(220px,1fr)_140px_150px_120px_130px_100px] px-3 py-2">
              <span>Source</span>
              <span>Category</span>
              <span>License</span>
              <span>Automation</span>
              <span>Usage</span>
              <span>Health</span>
            </div>
            <div className="divide-y divide-[var(--border)]">
              {sources.map((source) => (
                <div key={source.id} className="grid min-w-[900px] grid-cols-[minmax(220px,1fr)_140px_150px_120px_130px_100px] items-center gap-3 px-3 py-3 text-sm">
                  <div>
                    <div className="font-medium">{source.name}</div>
                    <a href={source.baseUrl} target="_blank" rel="noreferrer" className="text-xs text-[var(--muted)] hover:text-[var(--foreground)]">{source.provider}</a>
                  </div>
                  <span>{source.categorySlug}</span>
                  <Badge tone={source.licenseStatus.includes("PUBLIC") || source.licenseStatus.includes("LICENSED") ? "green" : "brass"}>{source.licenseStatus}</Badge>
                  <span>Level {source.automationLevel}</span>
                  <span className="text-xs text-[var(--muted)]">{source.settlementEligible ? "Settlement" : "Discovery only"}</span>
                  <Badge tone={source.healthStatus === "PASS" ? "green" : "blue"}>{source.healthStatus}</Badge>
                </div>
              ))}
            </div>
          </section>
        </TabsContent>
      </Tabs>
    </div>
  );
}

function Metric({ label, value, detail }: { label: string; value: number; detail: string }) {
  return (
    <div className="exchange-panel rounded-md px-3 py-2">
      <div className="text-xs uppercase tracking-[0.08em] text-[var(--muted)]">{label}</div>
      <div className="mt-1 text-2xl font-semibold tabular-nums">{value}</div>
      <div className="mt-1 text-xs text-[var(--muted)]">{detail}</div>
    </div>
  );
}

function AIPolicyCard({ title, detail, tone }: { title: string; detail: string; tone: "blue" | "brass" | "green" }) {
  const toneClass =
    tone === "blue"
      ? "border-[var(--blue-border)] bg-[var(--blue-soft)] text-[var(--blue-text)]"
      : tone === "brass"
        ? "border-[var(--brass-border)] bg-[var(--brass-soft)] text-[var(--brass-text)]"
        : "border-[var(--green-border)] bg-[var(--green-soft)] text-[var(--green-text)]";

  return (
    <div className={cn("rounded-md border px-3 py-2", toneClass)}>
      <div className="flex items-center gap-2 text-sm font-semibold">
        <Bot className="h-4 w-4" />
        {title}
      </div>
      <p className="mt-1 text-xs leading-5 opacity-90">{detail}</p>
    </div>
  );
}

function DraftBoard({
  drafts,
  loading,
  approveDraft,
  rejectDraft,
  listDraft
}: {
  drafts: MarketDraft[];
  loading: boolean;
  approveDraft: (draftId: string) => void;
  rejectDraft: (draftId: string) => void;
  listDraft: (draftId: string) => void;
}) {
  if (loading) {
    return <div className="exchange-panel rounded-md p-6 text-sm text-[var(--muted)]">Loading market drafts...</div>;
  }
  if (!drafts.length) {
    return <div className="exchange-panel rounded-md p-6 text-sm text-[var(--muted)]">No drafts in this lane yet.</div>;
  }
  return (
    <section className="space-y-3">
      {drafts.map((draft) => {
        const failedChecks = Object.entries(draft.checks).filter(([, check]) => check.passed === false);
        return (
          <article key={draft.id} className="exchange-panel rounded-md p-3">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
              <div className="min-w-0">
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <Badge tone={draft.origin === "AI" ? "blue" : draft.origin === "TRADER" ? "brass" : "green"}>{draft.origin}</Badge>
                  <Badge tone={draft.status === "LISTED" ? "green" : draft.status === "NEEDS_CHANGES" ? "red" : "blue"}>{draft.status}</Badge>
                  <span className="text-xs text-[var(--muted)]">{draft.categorySlug} / {draft.marketType}</span>
                </div>
                <h3 className="text-base font-semibold leading-6">{draft.question}</h3>
                <p className="mt-1 text-xs leading-5 text-[var(--muted)]">Source: {draft.source} / Close: {draft.closeTime}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <Button size="sm" disabled={draft.status === "APPROVED" || draft.status === "LISTED" || failedChecks.length > 0} onClick={() => approveDraft(draft.id)}>
                  <CheckCircle2 className="h-3.5 w-3.5" />Approve
                </Button>
                <Button size="sm" variant="secondary" disabled={draft.status !== "APPROVED"} onClick={() => listDraft(draft.id)}>
                  <FileSearch className="h-3.5 w-3.5" />List
                </Button>
                <Button size="sm" variant="danger" disabled={draft.status === "LISTED" || draft.status === "REJECTED"} onClick={() => rejectDraft(draft.id)}>
                  <XCircle className="h-3.5 w-3.5" />Reject
                </Button>
              </div>
            </div>

            <div className="mt-3 grid gap-3 lg:grid-cols-[1fr_280px]">
              <div className="space-y-2">
                <div className="rounded-md bg-[var(--surface-muted)] px-3 py-2 text-sm">
                  <div className="text-xs font-medium text-[var(--muted)]">Resolution rule</div>
                  <div className="mt-1 leading-5">{draft.resolutionRule}</div>
                </div>
                {draft.aiRationale ? (
                  <div className="rounded-md bg-[var(--blue-soft)] px-3 py-2 text-sm text-[var(--blue-text)]">
                    <Bot className="mr-1 inline h-3.5 w-3.5" />
                    {draft.aiRationale}
                  </div>
                ) : null}
                {draft.evidence.length ? (
                  <div className="space-y-1 text-xs text-[var(--muted)]">
                    {draft.evidence.map((item) => (
                      <a key={item.id} href={item.url ?? "#"} target="_blank" rel="noreferrer" className="block rounded border border-[var(--border)] px-2 py-1 hover:text-[var(--foreground)]">
                        Evidence: {item.title}
                      </a>
                    ))}
                  </div>
                ) : null}
              </div>

              <div className="space-y-2">
                <div className="text-xs font-semibold uppercase tracking-[0.08em] text-[var(--muted)]">Checks</div>
                {Object.entries(draft.checks).slice(0, 7).map(([key, check]) => (
                  <div key={key} className="flex items-start gap-2 text-xs">
                    {check.passed ? <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-[var(--green-text)]" /> : <ShieldAlert className="mt-0.5 h-3.5 w-3.5 shrink-0 text-[var(--red-text)]" />}
                    <span>
                      <span className="font-medium">{key.replaceAll("_", " ")}</span>
                      <span className="block text-[var(--muted)]">{check.detail}</span>
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </article>
        );
      })}
    </section>
  );
}
