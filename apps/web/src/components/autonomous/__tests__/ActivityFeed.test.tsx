import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ActivityFeed } from "../ActivityFeed";

function makeClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}

function wrapper({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={makeClient()}>{children}</QueryClientProvider>
  );
}

const emptyResponse = { items: [], total: 0 };

const activityResponse = {
  items: [
    {
      id: "act1",
      type: "alert_raised",
      title: "Alert: LCR Breach",
      detail: "LCR fell below 100%",
      severity: "critical",
      timestamp: "2026-07-01T06:00:00Z",
    },
    {
      id: "act2",
      type: "briefing_generated",
      title: "Briefing: Morning Briefing",
      detail: "SAM generated a morning executive briefing.",
      severity: null,
      timestamp: "2026-07-01T06:01:00Z",
    },
    {
      id: "act3",
      type: "monitoring_run",
      title: "Monitoring Cycle Completed",
      detail: "2 alert(s), 1 recommendation(s) generated. Duration: 120ms.",
      severity: null,
      timestamp: "2026-07-01T05:45:00Z",
    },
  ],
  total: 3,
};

beforeEach(() => {
  vi.resetAllMocks();
});

describe("ActivityFeed", () => {
  it("renders without crashing", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<ActivityFeed />, { wrapper });
    expect(screen.getByTestId("activity-feed")).toBeInTheDocument();
  });

  it("shows Autonomous Activity label", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<ActivityFeed />, { wrapper });
    expect(screen.getByText("Autonomous Activity")).toBeInTheDocument();
  });

  it("shows activity items", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => activityResponse,
    });
    render(<ActivityFeed />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("Alert: LCR Breach")).toBeInTheDocument();
      expect(screen.getByText("Briefing: Morning Briefing")).toBeInTheDocument();
      expect(screen.getByText("Monitoring Cycle Completed")).toBeInTheDocument();
    });
  });

  it("shows empty state when no activity", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<ActivityFeed />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("No recent activity")).toBeInTheDocument();
    });
  });

  it("shows activity item details", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => activityResponse,
    });
    render(<ActivityFeed />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("LCR fell below 100%")).toBeInTheDocument();
    });
  });

  it("handles fetch failure gracefully", async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: false, json: async () => ({}) });
    render(<ActivityFeed />, { wrapper });
    await waitFor(() => {
      expect(screen.getByTestId("activity-feed")).toBeInTheDocument();
    });
  });
});
