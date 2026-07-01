import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BriefingsPage } from "../BriefingsPage";

function makeClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}

function wrapper({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={makeClient()}>{children}</QueryClientProvider>
  );
}

const emptyResponse = { briefings: [], total: 0 };
const briefingsResponse = {
  briefings: [
    {
      id: "b1",
      briefing_type: "morning",
      content: "# Morning Briefing\n\nAll systems operational.",
      key_metrics: { lcr_ratio: 1.25 },
      status: "generated",
      created_at: "2026-07-01T06:00:00Z",
      entity_id: null,
    },
  ],
  total: 1,
};

beforeEach(() => {
  vi.resetAllMocks();
});

describe("BriefingsPage", () => {
  it("renders the page header", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<BriefingsPage />, { wrapper });
    expect(screen.getByText("Executive Briefings")).toBeInTheDocument();
  });

  it("shows data-testid", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<BriefingsPage />, { wrapper });
    expect(screen.getByTestId("briefings-page")).toBeInTheDocument();
  });

  it("shows generate button", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<BriefingsPage />, { wrapper });
    expect(screen.getByText("Generate")).toBeInTheDocument();
  });

  it("shows type selector", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<BriefingsPage />, { wrapper });
    expect(screen.getByDisplayValue("Morning Briefing")).toBeInTheDocument();
  });

  it("shows empty state when no briefings", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<BriefingsPage />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("No briefings generated yet.")).toBeInTheDocument();
    });
  });

  it("shows briefing items when available", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => briefingsResponse,
    });
    render(<BriefingsPage />, { wrapper });
    await waitFor(() => {
      expect(screen.getByTestId("briefing-item")).toBeInTheDocument();
      // "Morning Briefing" appears in the type selector <option> and in the briefing item
      expect(screen.getAllByText("Morning Briefing").length).toBeGreaterThanOrEqual(1);
    });
  });

  it("shows briefing content on expand", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => briefingsResponse,
    });
    render(<BriefingsPage />, { wrapper });
    await waitFor(() => {
      expect(screen.getByTestId("briefing-item")).toBeInTheDocument();
    });
    // Click the briefing to expand
    const item = screen.getByTestId("briefing-item");
    const btn = item.querySelector("button");
    if (btn) fireEvent.click(btn);
    await waitFor(() => {
      expect(screen.getByText(/All systems operational/)).toBeInTheDocument();
    });
  });
});
