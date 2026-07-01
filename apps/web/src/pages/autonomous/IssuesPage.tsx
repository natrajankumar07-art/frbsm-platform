import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { clsx } from "clsx";
import { Plus, CheckCircle2, Eye } from "lucide-react";
import { format } from "date-fns";

interface Issue {
  id: string;
  title: string;
  description: string;
  category: string | null;
  severity: string;
  status: "open" | "monitoring" | "resolved";
  created_at: string;
  resolved_at: string | null;
}

interface IssuesResponse {
  issues: Issue[];
  total: number;
  open_count: number;
  monitoring_count: number;
  resolved_count: number;
}

async function fetchIssues(status?: string): Promise<IssuesResponse> {
  const q = status ? `?status=${status}` : "";
  const r = await fetch(`/api/v1/autonomous/issues${q}&limit=50`);
  if (!r.ok) return { issues: [], total: 0, open_count: 0, monitoring_count: 0, resolved_count: 0 };
  return r.json();
}

async function createIssue(body: { title: string; description: string; category: string; severity: string }): Promise<Issue> {
  const r = await fetch("/api/v1/autonomous/issues", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error("Failed to create issue");
  return r.json();
}

async function updateIssueStatus(id: string, status: string): Promise<void> {
  await fetch(`/api/v1/autonomous/issues/${id}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
}

const STATUS_FILTERS = [
  { value: "", label: "All" },
  { value: "open", label: "Open" },
  { value: "monitoring", label: "Monitoring" },
  { value: "resolved", label: "Resolved" },
];

function severityDot(s: string) {
  if (s === "critical") return "bg-critical";
  if (s === "warning") return "bg-yellow-500";
  if (s === "notice") return "bg-accent";
  return "bg-text-secondary";
}

function statusBadge(s: string) {
  if (s === "open") return "bg-critical/15 text-critical";
  if (s === "monitoring") return "bg-yellow-500/15 text-yellow-500";
  return "bg-green-500/15 text-green-500";
}

export function IssuesPage() {
  const qc = useQueryClient();
  const [statusFilter, setStatusFilter] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ title: "", description: "", category: "regulatory", severity: "warning" });

  const { data, isLoading } = useQuery({
    queryKey: ["autonomous-issues", statusFilter],
    queryFn: () => fetchIssues(statusFilter || undefined),
    staleTime: 30_000,
  });

  const createMutation = useMutation({
    mutationFn: createIssue,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["autonomous-issues"] });
      setShowCreate(false);
      setForm({ title: "", description: "", category: "regulatory", severity: "warning" });
    },
  });

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => updateIssueStatus(id, status),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["autonomous-issues"] }),
  });

  const issues = data?.issues ?? [];

  return (
    <div className="space-y-6 pb-8" data-testid="issues-page">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-text-primary dark:text-gray-100">
            Outstanding Issues
          </h1>
          <p className="text-body text-text-secondary dark:text-gray-400 mt-0.5">
            Track regulatory and operational issues identified by SAM
          </p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-body font-medium bg-accent text-white hover:bg-accent/90 transition-colors"
        >
          <Plus className="h-3.5 w-3.5" />
          New Issue
        </button>
      </div>

      {/* Summary counters */}
      {data && (
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: "Open", count: data.open_count, color: "text-critical" },
            { label: "Monitoring", count: data.monitoring_count, color: "text-yellow-500" },
            { label: "Resolved", count: data.resolved_count, color: "text-green-500" },
          ].map(({ label, count, color }) => (
            <div key={label} className="rounded-xl border border-border bg-surface p-3 text-center">
              <p className={clsx("text-xl font-bold", color)}>{count}</p>
              <p className="text-caption text-text-secondary">{label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Create form */}
      {showCreate && (
        <div className="rounded-xl border border-border bg-surface p-4 space-y-3">
          <h3 className="text-body font-semibold text-text-primary">Create Issue</h3>
          <input
            placeholder="Title"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            className="w-full rounded-md border border-border bg-background px-3 py-1.5 text-body text-text-primary focus:outline-none focus:ring-1 focus:ring-accent"
          />
          <textarea
            placeholder="Description"
            rows={3}
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            className="w-full rounded-md border border-border bg-background px-3 py-1.5 text-body text-text-primary focus:outline-none focus:ring-1 focus:ring-accent resize-none"
          />
          <div className="flex gap-2">
            <select
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
              className="rounded-md border border-border bg-surface px-2 py-1.5 text-body text-text-primary focus:outline-none focus:ring-1 focus:ring-accent"
            >
              {["regulatory", "liquidity", "capital", "funding", "operational"].map((c) => (
                <option key={c} value={c} className="capitalize">{c}</option>
              ))}
            </select>
            <select
              value={form.severity}
              onChange={(e) => setForm({ ...form, severity: e.target.value })}
              className="rounded-md border border-border bg-surface px-2 py-1.5 text-body text-text-primary focus:outline-none focus:ring-1 focus:ring-accent"
            >
              {["info", "notice", "warning", "critical"].map((s) => (
                <option key={s} value={s} className="capitalize">{s}</option>
              ))}
            </select>
            <div className="flex-1" />
            <button
              onClick={() => setShowCreate(false)}
              className="text-body text-text-secondary hover:text-text-primary px-3 py-1.5"
            >
              Cancel
            </button>
            <button
              onClick={() => createMutation.mutate(form)}
              disabled={!form.title || !form.description || createMutation.isPending}
              className="rounded-lg px-3 py-1.5 text-body font-medium bg-accent text-white hover:bg-accent/90 disabled:opacity-50 transition-colors"
            >
              Create
            </button>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex gap-1">
        {STATUS_FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => setStatusFilter(f.value)}
            className={clsx(
              "rounded px-3 py-1 text-body transition-colors",
              statusFilter === f.value ? "bg-accent/20 text-accent font-medium" : "text-text-secondary hover:text-text-primary"
            )}
          >
            {f.label}
          </button>
        ))}
      </div>

      {isLoading && (
        <p className="text-body text-text-secondary py-8 text-center">Loading issues…</p>
      )}

      {!isLoading && issues.length === 0 && (
        <div className="flex flex-col items-center gap-3 py-12">
          <CheckCircle2 className="h-12 w-12 text-green-500 opacity-40" />
          <p className="text-body text-text-secondary">No issues found.</p>
        </div>
      )}

      <div className="space-y-2">
        {issues.map((issue) => (
          <div
            key={issue.id}
            className="rounded-xl border border-border bg-surface p-4 space-y-2"
            data-testid="issue-item"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-2 flex-1 min-w-0">
                <div className={clsx("h-2 w-2 rounded-full flex-shrink-0 mt-1", severityDot(issue.severity))} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-body font-semibold text-text-primary dark:text-gray-100 truncate">{issue.title}</span>
                    <span className={clsx("rounded-full px-2 py-0.5 text-xs font-medium capitalize", statusBadge(issue.status))}>
                      {issue.status}
                    </span>
                    {issue.category && (
                      <span className="rounded-full bg-border text-text-secondary text-xs px-2 py-0.5 capitalize">
                        {issue.category}
                      </span>
                    )}
                  </div>
                  <p className="text-caption text-text-secondary mt-0.5 line-clamp-2">{issue.description}</p>
                  <p className="text-caption text-text-secondary/60 mt-0.5">
                    {format(new Date(issue.created_at), "dd MMM yyyy, HH:mm")}
                    {issue.resolved_at && ` · Resolved ${format(new Date(issue.resolved_at), "dd MMM yyyy")}`}
                  </p>
                </div>
              </div>
              {issue.status !== "resolved" && (
                <div className="flex gap-1 flex-shrink-0">
                  {issue.status === "open" && (
                    <button
                      onClick={() => statusMutation.mutate({ id: issue.id, status: "monitoring" })}
                      className="flex items-center gap-1 text-caption text-yellow-500 hover:bg-yellow-500/10 rounded px-2 py-1 transition-colors"
                    >
                      <Eye className="h-3 w-3" />
                      Monitor
                    </button>
                  )}
                  <button
                    onClick={() => statusMutation.mutate({ id: issue.id, status: "resolved" })}
                    className="flex items-center gap-1 text-caption text-green-500 hover:bg-green-500/10 rounded px-2 py-1 transition-colors"
                  >
                    <CheckCircle2 className="h-3 w-3" />
                    Resolve
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
