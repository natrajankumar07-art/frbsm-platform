import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RecommendationsPanel } from "../RecommendationsPanel";

function makeClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}

function wrapper({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={makeClient()}>{children}</QueryClientProvider>
  );
}

const emptyResponse = { recommendations: [], total: 0 };

const recsResponse = {
  recommendations: [
    {
      id: "r1",
      category: "liquidity",
      priority: 1,
      title: "Restore LCR Compliance",
      description: "LCR is below 100%. Immediate action required.",
      expected_benefit: "Return to regulatory compliance.",
      potential_impact: "Risk of regulatory intervention.",
      status: "active",
      created_at: "2026-07-01T06:00:00Z",
      implemented_at: null,
      dismissed_at: null,
    },
    {
      id: "r2",
      category: "capital",
      priority: 3,
      title: "Monitor CET1 Buffer",
      description: "CET1 is within acceptable range.",
      expected_benefit: "Maintain capital headroom.",
      potential_impact: "Minimal.",
      status: "active",
      created_at: "2026-07-01T06:00:00Z",
      implemented_at: null,
      dismissed_at: null,
    },
  ],
  total: 2,
};

beforeEach(() => {
  vi.resetAllMocks();
});

describe("RecommendationsPanel", () => {
  it("renders without crashing", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<RecommendationsPanel />, { wrapper });
    expect(screen.getByTestId("recommendations-panel")).toBeInTheDocument();
  });

  it("shows SAM Recommendations label", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<RecommendationsPanel />, { wrapper });
    expect(screen.getByText("SAM Recommendations")).toBeInTheDocument();
  });

  it("shows recommendation items", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => recsResponse,
    });
    render(<RecommendationsPanel />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("Restore LCR Compliance")).toBeInTheDocument();
      expect(screen.getByText("Monitor CET1 Buffer")).toBeInTheDocument();
    });
  });

  it("shows active count", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => recsResponse,
    });
    render(<RecommendationsPanel />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("2 active")).toBeInTheDocument();
    });
  });

  it("shows empty state when no recommendations", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<RecommendationsPanel />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("No active recommendations")).toBeInTheDocument();
    });
  });

  it("shows priority label for urgent", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => recsResponse,
    });
    render(<RecommendationsPanel />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("Urgent")).toBeInTheDocument();
    });
  });

  it("shows category badge", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => recsResponse,
    });
    render(<RecommendationsPanel />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("liquidity")).toBeInTheDocument();
    });
  });

  it("expands recommendation to show details", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => recsResponse,
    });
    render(<RecommendationsPanel />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("Restore LCR Compliance")).toBeInTheDocument();
    });
    // Click expand button for first item
    const expandBtns = screen.getAllByRole("button");
    const chevronBtn = expandBtns.find((b) => b.title === undefined || b.title === "");
    // Find the chevron button in the first recommendation item
    const items = screen.getAllByTestId("recommendation-item");
    const btn = items[0].querySelector("button");
    if (btn) fireEvent.click(btn);
    await waitFor(() => {
      expect(screen.getByText(/Return to regulatory compliance/)).toBeInTheDocument();
    });
  });

  it("handles fetch failure gracefully", async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: false, json: async () => ({}) });
    render(<RecommendationsPanel />, { wrapper });
    await waitFor(() => {
      expect(screen.getByTestId("recommendations-panel")).toBeInTheDocument();
    });
  });
});
