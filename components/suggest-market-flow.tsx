"use client";

import { useMemo, useState } from "react";
import { CheckCircle2, CircleDashed, ShieldCheck } from "lucide-react";
import { Category3DIcon } from "@/components/category-3d-icon";
import { Button } from "@/components/ui/button";
import { ApiModeHint, DataSkeleton, DataState } from "@/components/ui/data-state";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { USE_MOCK_DATA } from "@/lib/api-client";
import { useCategories, useSuggestMarket } from "@/lib/api-hooks";
import { cn } from "@/lib/utils";

const marketTypes = ["Binary", "Multiple-choice", "Range", "Threshold", "Conditional", "Combo"];
const steps = [
  "Category",
  "Market type",
  "Question",
  "Source",
  "Automation checks",
  "Submit"
];

export function SuggestMarketFlow() {
  const { data: categories = [], isLoading, error } = useCategories();
  const suggestMutation = useSuggestMarket();
  const [step, setStep] = useState(0);
  const [category, setCategory] = useState("sports");
  const [marketType, setMarketType] = useState("Binary");
  const [question, setQuestion] = useState("Will India beat Australia in the next T20 final?");
  const [source, setSource] = useState("Official tournament result page");
  const [resolutionRule, setResolutionRule] = useState("YES resolves if the official source declares the named outcome true before the close-defined settlement deadline. Otherwise NO resolves, unless the void policy applies.");
  const [submitted, setSubmitted] = useState(false);

  const selectedCategory = useMemo(() => categories.find((item) => item.slug === category) ?? categories[0], [categories, category]);

  async function continueOrSubmit() {
    if (step < steps.length - 1) {
      setStep((value) => Math.min(steps.length - 1, value + 1));
      return;
    }
    if (USE_MOCK_DATA) {
      setSubmitted(true);
      return;
    }
    await suggestMutation.mutateAsync({
      category_slug: category,
      market_type: marketType,
      question,
      outcomes: marketType === "Binary" || marketType === "Threshold" || marketType === "Conditional" || marketType === "Combo" ? ["YES", "NO"] : ["Outcome A", "Outcome B"],
      source,
      resolution_rule: resolutionRule
    });
    setSubmitted(true);
  }

  if (isLoading) {
    return <DataSkeleton rows={5} />;
  }

  if (error || !selectedCategory) {
    return (
      <div className="mx-auto max-w-3xl space-y-3">
        <DataState
          title="Suggestion flow could not load categories"
          message="Market suggestions need the approved category list before automation checks can run."
          actionLabel="Retry"
          onAction={() => window.location.reload()}
          tone="error"
          badge="Category data"
        />
        <ApiModeHint />
      </div>
    );
  }

  return (
    <div className="grid gap-5 lg:grid-cols-[280px_1fr]">
      <aside className="rounded-md border border-[var(--border)] bg-[var(--surface)] p-3 lg:sticky lg:top-[82px] lg:self-start">
        <h2 className="text-sm font-semibold">Suggestion steps</h2>
        <div className="mt-3 space-y-1">
          {steps.map((label, index) => {
            const complete = index < step;
            const active = index === step;

            return (
              <button
                key={label}
                onClick={() => setStep(index)}
                className={cn(
                  "flex w-full items-center gap-2 rounded-md px-2 py-2 text-left text-sm transition",
                  active ? "bg-[var(--primary-soft)] text-[var(--primary-strong)]" : "text-[var(--muted)] hover:bg-[var(--surface-muted)]"
                )}
              >
                {complete ? <CheckCircle2 className="h-4 w-4 text-[var(--green-text)]" /> : <CircleDashed className="h-4 w-4" />}
                {label}
              </button>
            );
          })}
        </div>
      </aside>

      <section className="rounded-md border border-[var(--border)] bg-[var(--surface)] p-4">
        <div className="mb-4 flex items-center justify-between gap-3">
          <div>
            <h1 className="text-xl font-semibold">Suggest a market</h1>
            <p className="mt-1 text-sm text-[var(--muted)]">Users submit ideas. Automation checks them. Admins approve before listing.</p>
          </div>
          <Category3DIcon category={selectedCategory} size="lg" />
        </div>

        {step === 0 ? (
          <div>
            <h2 className="text-sm font-semibold">Choose category</h2>
            <div className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {categories.map((item) => (
                <button
                  key={item.slug}
                  onClick={() => setCategory(item.slug)}
                  className={cn(
                    "flex items-center gap-3 rounded-md border p-3 text-left",
                    category === item.slug ? "border-[var(--primary-border)] bg-[var(--primary-soft)]" : "border-[var(--border)]"
                  )}
                >
                  <Category3DIcon category={item} size="sm" />
                  <div>
                    <div className="text-sm font-medium">{item.name}</div>
                    <div className="text-xs text-[var(--muted)]">Risk: {item.risk}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ) : null}

        {step === 1 ? (
          <div>
            <h2 className="text-sm font-semibold">Choose market type</h2>
            <div className="mt-3 grid gap-2 sm:grid-cols-3">
              {marketTypes.map((type) => (
                <button
                  key={type}
                  onClick={() => setMarketType(type)}
                  className={cn(
                    "rounded-md border p-3 text-left text-sm",
                    marketType === type ? "border-[var(--primary-border)] bg-[var(--primary-soft)]" : "border-[var(--border)]"
                  )}
                >
                  <div className="font-medium">{type}</div>
                  <div className="mt-1 text-xs text-[var(--muted)]">Contract model check required</div>
                </button>
              ))}
            </div>
          </div>
        ) : null}

        {step === 2 ? (
          <div className="max-w-2xl space-y-3">
            <label className="block">
              <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Market question</span>
              <Input value={question} onChange={(event) => setQuestion(event.target.value)} />
            </label>
            <label className="block">
              <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Default outcome model</span>
              <Select
                value={marketType}
                onValueChange={setMarketType}
                options={marketTypes.map((type) => ({ label: type, value: type }))}
              />
            </label>
          </div>
        ) : null}

        {step === 3 ? (
          <div className="max-w-2xl space-y-3">
            <label className="block">
              <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Resolution source</span>
              <Input value={source} onChange={(event) => setSource(event.target.value)} />
            </label>
            <label className="block">
              <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Resolution rule</span>
              <textarea
                className="min-h-28 w-full rounded-md border border-[var(--border)] bg-[var(--surface)] p-3 text-sm outline-none focus:ring-2 focus:ring-[var(--ring)]"
                value={resolutionRule}
                onChange={(event) => setResolutionRule(event.target.value)}
              />
            </label>
          </div>
        ) : null}

        {step === 4 ? (
          <div className="space-y-2">
            {[
              "Category policy check",
              "Duplicate market check",
              "Source availability check",
              "Prohibited topic screen",
              "Resolution ambiguity check"
            ].map((label, index) => (
              <div key={label} className="flex items-center justify-between rounded-md border border-[var(--border)] px-3 py-2">
                <div className="flex items-center gap-2 text-sm">
                  <ShieldCheck className="h-4 w-4 text-[var(--primary)]" />
                  {label}
                </div>
                <span className={index === 4 ? "text-xs text-[var(--brass-text)]" : "text-xs text-[var(--green-text)]"}>
                  {index === 4 ? "Admin review" : "Passed"}
                </span>
              </div>
            ))}
          </div>
        ) : null}

        {step === 5 ? (
          <div className="rounded-md border border-[var(--green-border)] bg-[var(--green-soft)] p-4">
            <h2 className="text-sm font-semibold text-[var(--green-text)]">{submitted ? "Submitted for admin approval" : "Ready for admin approval"}</h2>
            <div className="mt-3 space-y-2 text-sm">
              <div><span className="text-[var(--muted)]">Category:</span> {selectedCategory.name}</div>
              <div><span className="text-[var(--muted)]">Type:</span> {marketType}</div>
              <div><span className="text-[var(--muted)]">Question:</span> {question}</div>
              <div><span className="text-[var(--muted)]">Source:</span> {source}</div>
            </div>
            {suggestMutation.error ? <div className="mt-3 text-sm text-[var(--red-text)]">Submission failed. Sign in and try again.</div> : null}
          </div>
        ) : null}

        <div className="mt-5 flex items-center justify-between border-t border-[var(--border)] pt-4">
          <Button variant="secondary" disabled={step === 0} onClick={() => setStep((value) => Math.max(0, value - 1))}>
            Back
          </Button>
          <Button variant="primary" onClick={() => void continueOrSubmit()} disabled={suggestMutation.isPending || submitted}>
            {suggestMutation.isPending ? "Submitting" : step === steps.length - 1 ? submitted ? "Submitted" : "Submit for review" : "Continue"}
          </Button>
        </div>
      </section>
    </div>
  );
}
