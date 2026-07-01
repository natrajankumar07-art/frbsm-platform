import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import type { ReportTypeInfo, ReportResponse } from "../../types/workflow";
import { useReportGeneration, downloadMarkdown } from "../../hooks/useReportGeneration";

interface ReportPanelProps {
  entityId: string | null;
  snapshotId?: string;
}

async function fetchReportTypes(): Promise<ReportTypeInfo[]> {
  const r = await fetch("/api/v1/copilot/reports/types");
  if (!r.ok) throw new Error("Failed to load report types");
  return r.json() as Promise<ReportTypeInfo[]>;
}

const REPORT_COLORS: Record<string, string> = {
  executive_dashboard: "bg-rose-50 border-rose-200 text-rose-800",
  ceo_brief: "bg-pink-50 border-pink-200 text-pink-800",
  board_pack: "bg-purple-50 border-purple-200 text-purple-800",
  cro_report: "bg-orange-50 border-orange-200 text-orange-800",
  regulatory_compliance: "bg-blue-50 border-blue-200 text-blue-800",
  liquidity_risk: "bg-sky-50 border-sky-200 text-sky-800",
  capital_adequacy: "bg-emerald-50 border-emerald-200 text-emerald-800",
  alm_summary: "bg-amber-50 border-amber-200 text-amber-800",
  stress_testing: "bg-red-50 border-red-200 text-red-800",
  daily_treasury: "bg-teal-50 border-teal-200 text-teal-800",
};

export function ReportPanel({ entityId, snapshotId }: ReportPanelProps) {
  const [generatedReport, setGeneratedReport] = useState<ReportResponse | null>(null);
  const [generatingType, setGeneratingType] = useState<string | null>(null);
  const { generateReport, downloading, error } = useReportGeneration();

  const { data: reportTypes } = useQuery({
    queryKey: ["report-types"],
    queryFn: fetchReportTypes,
    staleTime: Infinity,
  });

  const handleGenerate = async (reportType: string) => {
    if (!entityId) return;
    setGeneratingType(reportType);
    const report = await generateReport(reportType, entityId, snapshotId);
    if (report) setGeneratedReport(report);
    setGeneratingType(null);
  };

  if (!entityId) {
    return (
      <div className="p-4 text-sm text-text-secondary text-center">
        Select an entity to generate reports.
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Report type grid */}
      <div className="p-4 border-b border-border">
        <p className="text-xs font-semibold text-text-secondary uppercase tracking-wide mb-3">
          Generate Report
        </p>
        <div className="grid grid-cols-2 gap-2">
          {reportTypes?.map((rt) => (
            <button
              key={rt.id}
              onClick={() => handleGenerate(rt.id)}
              disabled={downloading}
              className={[
                "text-left text-xs px-2.5 py-2 rounded border transition-opacity",
                REPORT_COLORS[rt.id] ?? "bg-gray-50 border-gray-200 text-gray-700",
                downloading ? "opacity-50 cursor-not-allowed" : "hover:opacity-80",
                generatingType === rt.id ? "ring-2 ring-offset-1 ring-blue-400" : "",
              ].join(" ")}
              title={rt.description}
            >
              {generatingType === rt.id ? (
                <span className="flex items-center gap-1">
                  <svg className="animate-spin h-3 w-3" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  {rt.name}
                </span>
              ) : (
                rt.name
              )}
            </button>
          ))}
        </div>
        {error && (
          <p className="mt-2 text-xs text-red-600">{error}</p>
        )}
      </div>

      {/* Generated report preview */}
      {generatedReport && (
        <div className="flex-1 overflow-y-auto p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-semibold text-text-secondary uppercase tracking-wide">
              {generatedReport.title}
            </p>
            <button
              onClick={() => downloadMarkdown(generatedReport)}
              className="text-xs px-2 py-1 rounded bg-blue-600 text-white hover:bg-blue-700 transition-colors flex items-center gap-1"
            >
              <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download .md
            </button>
          </div>
          <div className="text-xs text-text-secondary mb-2">
            {generatedReport.entity} | {generatedReport.snapshot_date} | {generatedReport.generated_at}
          </div>
          <pre className="text-xs whitespace-pre-wrap font-mono bg-gray-50 rounded p-3 border border-border overflow-x-auto max-h-96">
            {generatedReport.content_markdown}
          </pre>
        </div>
      )}
    </div>
  );
}
