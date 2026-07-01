import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { IssuesPage } from "../IssuesPage";

function makeClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}

function wrapper({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={makeClient()}>{children}</QueryClientProvider>
  );
}

const emptyResponse = {
  issues: [],
  total: 0,
  open_count: 0,
  monitoring_count: 0,
  resolved_count: 0,
};

const issuesResponse = {
  issues: [
    {
      id: "i1",
      title: "LCR Monitoring Required",
      description: "LCR is approaching minimum levels.",
      category: "liquidity",
      severity: "warning",
      status: "open",
      created_at: "2026-07-01T06:00:00Z",
      resolved_at: null,
      context: {},
    },
    {
      id: "i2",
      title: "NSFR Under Review",
      description: "NSFR is being closely monitored.",
      category: "funding",
      severity: "notice",
      status: "monitoring",
      created_at: "2026-07-01T05:00:00Z",
      resolved_at: null,
      context: {},
    },
  ],
  total: 2,
  open_count: 1,
  monitoring_count: 1,
  resolved_count: 0,
};

beforeEach(() => {
  vi.resetAllMocks();
});

describe("IssuesPage", () => {
  it("renders without crashing", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<IssuesPage />, { wrapper });
    expect(screen.getByTestId("issues-page")).toBeInTheDocument();
  });

  it("shows Outstanding Issues header", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<IssuesPage />, { wrapper });
    expect(screen.getByText("Outstanding Issues")).toBeInTheDocument();
  });

  it("shows New Issue button", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<IssuesPage />, { wrapper });
    expect(screen.getByText("New Issue")).toBeInTheDocument();
  });

  it("shows summary counters with data", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => issuesResponse,
    });
    render(<IssuesPage />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("Open")).toBeInTheDocument();
      expect(screen.getByText("Monitoring")).toBeInTheDocument();
      expect(screen.getByText("Resolved")).toBeInTheDocument();
    });
  });

  it("shows issue items", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => issuesResponse,
    });
    render(<IssuesPage />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("LCR Monitoring Required")).toBeInTheDocument();
      expect(screen.getByText("NSFR Under Review")).toBeInTheDocument();
    });
  });

  it("shows status badges", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => issuesResponse,
    });
    render(<IssuesPage />, { wrapper });
    await waitFor(() => {
      expect(screen.getAllByText("open").length).toBeGreaterThan(0);
      expect(screen.getByText("monitoring")).toBeInTheDocument();
    });
  });

  it("shows empty state when no issues", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<IssuesPage />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("No issues found.")).toBeInTheDocument();
    });
  });

  it("opens create form when New Issue is clicked", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<IssuesPage />, { wrapper });
    fireEvent.click(screen.getByText("New Issue"));
    expect(screen.getByText("Create Issue")).toBeInTheDocument();
  });

  it("shows filter buttons", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<IssuesPage />, { wrapper });
    expect(screen.getByText("All")).toBeInTheDocument();
  });
});
