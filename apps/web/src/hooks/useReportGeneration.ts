import { useState } from "react";
import type { ReportResponse } from "../types/workflow";

interface UseReportGenerationReturn {
  generateReport: (
    reportType: string,
    entityId: string,
    snapshotId?: string
  ) => Promise<ReportResponse | null>;
  downloading: boolean;
  error: string | null;
}

export function useReportGeneration(): UseReportGenerationReturn {
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateReport = async (
    reportType: string,
    entityId: string,
    snapshotId?: string
  ): Promise<ReportResponse | null> => {
    setDownloading(true);
    setError(null);

    try {
      const body: Record<string, string> = {
        report_type: reportType,
        entity_id: entityId,
      };
      if (snapshotId) body.snapshot_id = snapshotId;

      const res = await fetch("/api/v1/copilot/reports/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        throw new Error(`Report generation failed: ${res.status}`);
      }

      return (await res.json()) as ReportResponse;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      return null;
    } finally {
      setDownloading(false);
    }
  };

  return { generateReport, downloading, error };
}

export function downloadMarkdown(report: ReportResponse): void {
  const slug = report.report_type.replace(/_/g, "-");
  const filename = `bsm-${slug}-${report.snapshot_date}.md`;
  const blob = new Blob([report.content_markdown], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
