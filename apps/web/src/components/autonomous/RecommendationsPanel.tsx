import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { clsx } from "clsx";
import { Lightbulb, CheckCircle2, XCircle, ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";

interface Recommendation {
  id: string;
  category: string;
  priority: number;
  title: string;
  description: string;
  expected_benefit: string | null;
  potential_impact: string | null;
  status: "active" | "implemented" | "dismissed";
  created_at: string;
}

interface RecsResponse {
  recommendations: Recommendation[];
  total: number;
}

async function fetchRecs(): Promise<RecsResponse> {
  const r = await fetch("/api/v1/autonomous/recommendations?status=active&limit=10");
  if (!r.ok) return { recommendations: [], total: 0 };
  return r.json();
}

async function updateRecStatus(id: string, status: string): Promise<void> {
  await fetch(`/api/v1/autonomous/recommendations/${id}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
}

function priorityLabel(p: number) {
  if (p === 1) return { label: "Urgent", color: "text-critical" };
  if (p === 2) return { label: "High", color: "text-yellow-500" };
  if (p === 3) return { label: "Medium", color: "text-accent" };
  if (p === 4) return { label: "Low", color: "text-text-secondary" };
  return { label: "Info", color: "text-text-secondary/60" };
}

function categoryBadge(cat: string) {
  const map: Record<string, string> = {
    liquidity: "bg-blue-500/15 text-blue-500",
    capital: "bg-purple-500/15 text-purple-500",
    funding: "bg-green-500/15 text-green-500",
    stress: "bg-yellow-500/15 text-yellow-500",
    regulatory: "bg-red-500/15 text-red-500",
  };
  return map[cat.toLowerCase()] ?? "bg-border text-text-secondary";
}

export function RecommendationsPanel() {
  const qc = useQueryClient();
  const [expanded, setExpanded] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["autonomous-recs"],
    queryFn: fetchRecs,
    staleTime: 60_000,
  });

  const mutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => updateRecStatus(id, status),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["autonomous-recs"] }),
  });

  const recs = data?.recommendations ?? [];

  return (
    <div className="rounded-xl border border-border bg-surface p-4 space-y-3" data-testid="recommendations-panel">
      <div className="flex items-center gap-2">
        <Lightbulb className="h-4 w-4 text-accent flex-shrink-0" />
        <span className="text-body font-semibold text-text-primary">SAM Recommendations</span>
        {recs.length > 0 && (
          <span className="text-caption text-text-secondary ml-auto">{recs.length} active</span>
        )}
      </div>

      {isLoading && (
        <p className="text-body text-text-secondary py-4 text-center">Loading recommendations…</p>
      )}

      {!isLoading && recs.length === 0 && (
        <div className="flex flex-col items-center gap-2 py-6">
          <CheckCircle2 className="h-8 w-8 text-green-500 opacity-60" />
          <p className="text-body text-text-secondary">No active recommendations</p>
        </div>
      )}

      <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
        {recs.map((rec) => {
          const { label, color } = priorityLabel(rec.priority);
          const isOpen = expanded === rec.id;
          return (
            <div
              key={rec.id}
              className="rounded-lg border border-border bg-background/40 p-3 space-y-1.5"
              data-testid="recommendation-item"
            >
              <div className="flex items-start gap-2">
                <span className={clsx("text-caption font-bold flex-shrink-0 mt-0.5 w-12", color)}>
                  {label}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-caption font-semibold text-text-primary">{rec.title}</span>
                    <span className={clsx("rounded-full px-1.5 py-0.5 text-xs font-medium capitalize", categoryBadge(rec.category))}>
                      {rec.category}
                    </span>
                  </div>
                  <p className={clsx("text-caption text-text-secondary mt-0.5", isOpen ? "" : "line-clamp-2")}>
                    {rec.description}
                  </p>
                  {isOpen && rec.expected_benefit && (
                    <p className="text-caption text-green-500 mt-1">
                      <span className="font-medium">Benefit:</span> {rec.expected_benefit}
                    </p>
                  )}
                  {isOpen && rec.potential_impact && (
                    <p className="text-caption text-yellow-500 mt-0.5">
                      <span className="font-medium">Impact:</span> {rec.potential_impact}
                    </p>
                  )}
                </div>
                <button
                  onClick={() => setExpanded(isOpen ? null : rec.id)}
                  className="text-text-secondary hover:text-text-primary flex-shrink-0"
                >
                  {isOpen ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
                </button>
              </div>

              {isOpen && (
                <div className="flex gap-2 pt-1 border-t border-border">
                  <button
                    onClick={() => mutation.mutate({ id: rec.id, status: "implemented" })}
                    disabled={mutation.isPending}
                    className="flex items-center gap-1 text-caption text-green-500 hover:bg-green-500/10 rounded px-2 py-0.5 transition-colors"
                  >
                    <CheckCircle2 className="h-3 w-3" />
                    Implemented
                  </button>
                  <button
                    onClick={() => mutation.mutate({ id: rec.id, status: "dismissed" })}
                    disabled={mutation.isPending}
                    className="flex items-center gap-1 text-caption text-text-secondary hover:bg-border rounded px-2 py-0.5 transition-colors"
                  >
                    <XCircle className="h-3 w-3" />
                    Dismiss
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
