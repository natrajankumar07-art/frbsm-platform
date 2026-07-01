import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ExecutiveDashTimeline } from "../ExecutiveDashTimeline";
import type { ExecutiveTimelineEvent } from "../ExecutiveDashTimeline";

const sampleEvents: ExecutiveTimelineEvent[] = [
  {
    id: "ev-1",
    type: "snapshot_processed",
    title: "Snapshot Processed",
    detail: "31 Mar 2025 · 15,000 positions · locked",
    timestamp: "2025-03-31T12:00:00Z",
  },
  {
    id: "ev-2",
    type: "engines_executed",
    title: "Engines Executed",
    detail: "LCR, NSFR, Capital computed.",
    timestamp: "2025-03-31T12:01:00Z",
  },
  {
    id: "ev-3",
    type: "alert_raised",
    title: "Alert: LCR Below Buffer",
    detail: "LCR ratio dropped to 101%.",
    timestamp: "2025-03-31T12:02:00Z",
  },
];

describe("ExecutiveDashTimeline", () => {
  it("renders timeline events", () => {
    render(<ExecutiveDashTimeline events={sampleEvents} />);
    expect(screen.getByTestId("executive-dash-timeline")).toBeInTheDocument();
    expect(screen.getByText("Snapshot Processed")).toBeInTheDocument();
    expect(screen.getByText("Engines Executed")).toBeInTheDocument();
    expect(screen.getByText("Alert: LCR Below Buffer")).toBeInTheDocument();
  });

  it("renders event details", () => {
    render(<ExecutiveDashTimeline events={sampleEvents} />);
    expect(screen.getByText(/31 Mar 2025/)).toBeInTheDocument();
    expect(screen.getByText(/LCR, NSFR, Capital computed/)).toBeInTheDocument();
  });

  it("shows empty state when no events", () => {
    render(<ExecutiveDashTimeline events={[]} />);
    expect(screen.getByText("No events yet.")).toBeInTheDocument();
  });

  it("renders timeline heading", () => {
    render(<ExecutiveDashTimeline events={sampleEvents} />);
    expect(screen.getByText("Executive Timeline")).toBeInTheDocument();
  });
});
