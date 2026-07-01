import type { ToolEvidence } from "../../types/workflow";

interface EvidencePanelProps {
  evidence: ToolEvidence | null;
  toolCallsLog: Array<{ tool: string; success: boolean; timestamp?: string }>;
}

const CONFIDENCE_COLORS = {
  HIGH: "bg-green-50 text-green-700 border-green-200",
  MEDIUM: "bg-amber-50 text-amber-700 border-amber-200",
  LOW: "bg-red-50 text-red-700 border-red-200",
};

export function EvidencePanel({ evidence, toolCallsLog }: EvidencePanelProps) {
  if (!evidence && toolCallsLog.length === 0) {
    return (
      <div className="p-4 text-sm text-text-secondary text-center">
        Evidence citations will appear here after each AI response.
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4 text-xs overflow-y-auto h-full">
      {/* Tool calls log */}
      {toolCallsLog.length > 0 && (
        <div>
          <p className="font-semibold text-text-secondary uppercase tracking-wide mb-2">
            Tool Calls
          </p>
          <div className="space-y-1">
            {toolCallsLog.map((call, i) => (
              <div
                key={i}
                className={[
                  "flex items-center gap-2 px-2.5 py-1.5 rounded border",
                  call.success
                    ? "bg-green-50 border-green-200 text-green-800"
                    : "bg-red-50 border-red-200 text-red-700",
                ].join(" ")}
              >
                <span>{call.success ? "✓" : "✗"}</span>
                <span className="font-mono">{call.tool}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Evidence block */}
      {evidence && (
        <div>
          <p className="font-semibold text-text-secondary uppercase tracking-wide mb-2">
            Evidence
          </p>
          <div className="space-y-2">
            {evidence.entity && (
              <Row label="Entity" value={evidence.entity} />
            )}
            {evidence.snapshot_date && (
              <Row label="Snapshot" value={evidence.snapshot_date} />
            )}
            <div className="flex items-center gap-2">
              <span className="text-text-secondary w-24 shrink-0">Confidence</span>
              <span
                className={[
                  "px-1.5 py-0.5 rounded border text-xs font-semibold",
                  CONFIDENCE_COLORS[evidence.confidence] ?? "bg-gray-50 text-gray-700 border-gray-200",
                ].join(" ")}
              >
                {evidence.confidence}
              </span>
            </div>
            {evidence.source_tables.length > 0 && (
              <Row label="Source Tables" value={evidence.source_tables.join(", ")} />
            )}
            {evidence.regulatory_refs.length > 0 && (
              <div>
                <p className="text-text-secondary mb-1">Regulatory References</p>
                <ul className="space-y-0.5 pl-2">
                  {evidence.regulatory_refs.map((ref) => (
                    <li key={ref} className="text-text-secondary">• {ref}</li>
                  ))}
                </ul>
              </div>
            )}
            {evidence.engines_used.length > 0 && (
              <Row label="Engines" value={evidence.engines_used.join(", ")} />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex gap-2">
      <span className="text-text-secondary w-24 shrink-0">{label}</span>
      <span className="text-text-primary break-all">{value}</span>
    </div>
  );
}
