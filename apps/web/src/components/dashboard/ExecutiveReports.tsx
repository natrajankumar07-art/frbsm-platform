import { FileText, ExternalLink } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface ReportAction {
  id: string;
  label: string;
  description: string;
  reportType: string;
}

const EXECUTIVE_REPORTS: ReportAction[] = [
  { id: "ceo_brief", label: "CEO Summary", description: "High-level briefing for the CEO", reportType: "ceo_brief" },
  { id: "cro_report", label: "CRO Summary", description: "Chief Risk Officer report", reportType: "cro_report" },
  { id: "board_pack", label: "Board Pack", description: "Full board risk pack", reportType: "board_pack" },
  { id: "icaap", label: "ICAAP Snapshot", description: "Internal Capital Adequacy Assessment", reportType: "capital_adequacy" },
  { id: "ilaap", label: "ILAAP Snapshot", description: "Internal Liquidity Adequacy Assessment", reportType: "liquidity_risk" },
  { id: "liquidity_summary", label: "Liquidity Summary", description: "LCR/NSFR position summary", reportType: "liquidity_risk" },
  { id: "capital_summary", label: "Capital Summary", description: "Capital ratios and adequacy", reportType: "capital_adequacy" },
];

export function ExecutiveReports() {
  const navigate = useNavigate();

  const handleOpen = (report: ReportAction) => {
    sessionStorage.setItem(
      "bsm-copilot-prefill",
      `Generate a ${report.label} report`
    );
    sessionStorage.setItem("bsm-report-type", report.reportType);
    navigate("/copilot");
  };

  return (
    <div
      className="card dark:bg-gray-900 dark:border-gray-700"
      data-testid="executive-reports"
    >
      <div className="flex items-center gap-2 mb-4">
        <FileText className="h-4 w-4 text-accent" />
        <h3 className="text-body font-semibold text-text-primary dark:text-gray-100">
          Executive Reports
        </h3>
      </div>
      <div className="grid grid-cols-1 gap-2">
        {EXECUTIVE_REPORTS.map((r) => (
          <button
            key={r.id}
            onClick={() => handleOpen(r)}
            className="flex items-center justify-between px-3 py-2.5 rounded-md border border-border dark:border-gray-700 bg-surface dark:bg-gray-800 hover:border-accent dark:hover:border-blue-600 hover:bg-accent/5 dark:hover:bg-blue-900/20 transition-colors text-left group"
          >
            <div>
              <p className="text-caption font-semibold text-text-primary dark:text-gray-100 group-hover:text-accent dark:group-hover:text-blue-400 transition-colors">
                {r.label}
              </p>
              <p className="text-caption text-text-secondary dark:text-gray-400" style={{ fontSize: "10px" }}>
                {r.description}
              </p>
            </div>
            <ExternalLink className="h-3 w-3 text-text-secondary dark:text-gray-400 group-hover:text-accent dark:group-hover:text-blue-400 flex-shrink-0 transition-colors" />
          </button>
        ))}
      </div>
    </div>
  );
}
