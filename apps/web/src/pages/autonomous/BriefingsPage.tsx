import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { clsx } from "clsx";
import { FileText, RefreshCw, ChevronDown, ChevronUp } from "lucide-react";
import { format } from "date-fns";

interface Briefing {
  id: string;
  briefing_type: string;
  content: string;
  key_metrics: Record<string, unknown>;
  status: string;
  created_at: string;
  entity_id: string | null;
}

interface BriefingsResponse {
  briefings: Briefing[];
  total: number;
}

const BRIEFING_TYPES = [
  { value: "morning", label: "Morning Briefing" },
  { value: "daily", label: "Daily Summary" },
  { value: "weekly", label: "Weekly Summary" },
  { value: "monthly_board", label: "Monthly Board Brief" },
  { value: "quarterly_exec", label: "Quarterly Executive Review" },
];

async function fetchBriefings(): Promise<BriefingsResponse> {
  const r = await fetch("/api/v1/autonomous/briefings?limit=20");
  if (!r.ok) return { briefings: [], total: 0 };
  return r.json();
}

async function generateBriefing(briefing_type: string): Promise<Briefing> {
  const r = await fetch("/api/v1/autonomous/briefings/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ briefing_type }),
  });
  if (!r.ok) throw new Error("Failed to generate briefing");
  return r.json();
}

export function BriefingsPage() {
  const qc = useQueryClient();
  const [selectedType, setSelectedType] = useState("morning");
  const [expanded, setExpanded] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["autonomous-briefings"],
    queryFn: fetchBriefings,
    staleTime: 30_000,
  });

  const mutation = useMutation({
    mutationFn: generateBriefing,
    onSuccess: (newBriefing) => {
      qc.invalidateQueries({ queryKey: ["autonomous-briefings"] });
      setExpanded(newBriefing.id);
    },
  });

  const briefings = data?.briefings ?? [];

  return (
    <div className="space-y-6 pb-8" data-testid="briefings-page">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-text-primary dark:text-gray-100">
            Executive Briefings
          </h1>
          <p className="text-body text-text-secondary dark:text-gray-400 mt-0.5">
            SAM-generated executive briefings from validated engine outputs
          </p>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="rounded-md border border-border bg-surface px-2 py-1.5 text-body text-text-primary dark:text-gray-100 focus:outline-none focus:ring-1 focus:ring-accent"
          >
            {BRIEFING_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
          <button
            onClick={() => mutation.mutate(selectedType)}
            disabled={mutation.isPending}
            className={clsx(
              "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-body font-medium transition-colors",
              "bg-accent text-white hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed"
            )}
          >
            <RefreshCw className={clsx("h-3.5 w-3.5", mutation.isPending && "animate-spin")} />
            Generate
          </button>
        </div>
      </div>

      {mutation.isError && (
        <div className="rounded-lg border border-critical/30 bg-critical/10 p-3 text-body text-critical">
          Failed to generate briefing. Ensure at least one snapshot with analytics results exists.
        </div>
      )}

      {isLoading && (
        <p className="text-body text-text-secondary py-8 text-center">Loading briefings…</p>
      )}

      {!isLoading && briefings.length === 0 && (
        <div className="flex flex-col items-center gap-3 py-12">
          <FileText className="h-12 w-12 text-text-secondary opacity-40" />
          <p className="text-body text-text-secondary">No briefings generated yet.</p>
          <p className="text-caption text-text-secondary/60">Select a type and click Generate to create one.</p>
        </div>
      )}

      <div className="space-y-3">
        {briefings.map((b) => {
          const isOpen = expanded === b.id;
          const typeLabel = BRIEFING_TYPES.find((t) => t.value === b.briefing_type)?.label ?? b.briefing_type;
          return (
            <div
              key={b.id}
              className="rounded-xl border border-border bg-surface overflow-hidden"
              data-testid="briefing-item"
            >
              <button
                className="w-full flex items-center justify-between px-4 py-3 hover:bg-border/30 transition-colors"
                onClick={() => setExpanded(isOpen ? null : b.id)}
              >
                <div className="flex items-center gap-3 text-left">
                  <FileText className="h-4 w-4 text-accent flex-shrink-0" />
                  <div>
                    <span className="text-body font-semibold text-text-primary dark:text-gray-100">
                      {typeLabel}
                    </span>
                    <p className="text-caption text-text-secondary">
                      {format(new Date(b.created_at), "dd MMM yyyy, HH:mm")} UTC
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="rounded-full bg-accent/15 text-accent text-caption px-2 py-0.5 capitalize">
                    {b.status}
                  </span>
                  {isOpen ? <ChevronUp className="h-4 w-4 text-text-secondary" /> : <ChevronDown className="h-4 w-4 text-text-secondary" />}
                </div>
              </button>

              {isOpen && (
                <div className="border-t border-border px-4 py-4">
                  <div className="prose prose-sm max-w-none text-text-primary dark:text-gray-100 whitespace-pre-wrap font-mono text-xs leading-relaxed bg-background/40 rounded-lg p-4 overflow-auto max-h-[60vh]">
                    {b.content}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
