import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ScheduledReportsPage } from "../ScheduledReportsPage";

function makeClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}

function wrapper({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={makeClient()}>{children}</QueryClientProvider>
  );
}

const emptyResponse = { configs: [], total: 0 };
const schedulesResponse = {
  configs: [
    {
      id: "s1",
      report_type: "ceo_brief",
      schedule_type: "weekly",
      enabled: true,
      last_run: null,
      next_run: null,
      created_at: "2026-07-01T06:00:00Z",
      created_by: "user",
      entity_id: null,
      updated_at: "2026-07-01T06:00:00Z",
    },
    {
      id: "s2",
      report_type: "board_pack",
      schedule_type: "monthly",
      enabled: false,
      last_run: "2026-06-01T06:00:00Z",
      next_run: null,
      created_at: "2026-06-01T06:00:00Z",
      created_by: "user",
      entity_id: null,
      updated_at: "2026-06-01T06:00:00Z",
    },
  ],
  total: 2,
};

beforeEach(() => {
  vi.resetAllMocks();
});

describe("ScheduledReportsPage", () => {
  it("renders without crashing", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<ScheduledReportsPage />, { wrapper });
    expect(screen.getByTestId("scheduled-reports-page")).toBeInTheDocument();
  });

  it("shows Scheduled Reports header", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<ScheduledReportsPage />, { wrapper });
    expect(screen.getByText("Scheduled Reports")).toBeInTheDocument();
  });

  it("shows Add Schedule button", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<ScheduledReportsPage />, { wrapper });
    expect(screen.getByText("Add Schedule")).toBeInTheDocument();
  });

  it("shows empty state when no schedules", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<ScheduledReportsPage />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("No scheduled reports configured.")).toBeInTheDocument();
    });
  });

  it("shows schedule items", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => schedulesResponse,
    });
    render(<ScheduledReportsPage />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("CEO Brief")).toBeInTheDocument();
      expect(screen.getByText("Board Pack")).toBeInTheDocument();
    });
  });

  it("shows schedule frequency badges", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => schedulesResponse,
    });
    render(<ScheduledReportsPage />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("weekly")).toBeInTheDocument();
      expect(screen.getByText("monthly")).toBeInTheDocument();
    });
  });

  it("shows Paused badge for disabled schedule", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => schedulesResponse,
    });
    render(<ScheduledReportsPage />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("Paused")).toBeInTheDocument();
    });
  });

  it("opens create form when Add Schedule is clicked", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<ScheduledReportsPage />, { wrapper });
    fireEvent.click(screen.getByText("Add Schedule"));
    expect(screen.getByText("New Schedule")).toBeInTheDocument();
  });
});
