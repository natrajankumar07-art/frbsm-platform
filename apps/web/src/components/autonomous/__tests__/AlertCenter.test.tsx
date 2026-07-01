import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AlertCenter } from "../AlertCenter";

function makeClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}

function wrapper({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={makeClient()}>{children}</QueryClientProvider>
  );
}

const emptyResponse = {
  alerts: [],
  total: 0,
  critical_count: 0,
  warning_count: 0,
  notice_count: 0,
  info_count: 0,
};

const alertsResponse = {
  alerts: [
    {
      id: "a1",
      severity: "critical",
      title: "LCR Breach",
      message: "LCR fell below 100%",
      category: "liquidity",
      metric_name: "lcr",
      metric_value: 0.95,
      recommendation: "Increase HQLA",
      status: "open",
      created_at: "2026-07-01T06:00:00Z",
      threshold_value: 1.0,
    },
    {
      id: "a2",
      severity: "warning",
      title: "NSFR Low",
      message: "NSFR approaching minimum",
      category: "funding",
      metric_name: "nsfr",
      metric_value: 1.02,
      recommendation: null,
      status: "open",
      created_at: "2026-07-01T06:00:00Z",
      threshold_value: 1.0,
    },
  ],
  total: 2,
  critical_count: 1,
  warning_count: 1,
  notice_count: 0,
  info_count: 0,
};

beforeEach(() => {
  vi.resetAllMocks();
});

describe("AlertCenter", () => {
  it("renders without crashing", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<AlertCenter />, { wrapper });
    expect(screen.getByTestId("alert-center")).toBeInTheDocument();
  });

  it("shows Alert Center label", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<AlertCenter />, { wrapper });
    expect(screen.getByText("Alert Center")).toBeInTheDocument();
  });

  it("shows critical badge when there are critical alerts", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => alertsResponse,
    });
    render(<AlertCenter />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("1 CRITICAL")).toBeInTheDocument();
    });
  });

  it("renders alert items for each alert", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => alertsResponse,
    });
    render(<AlertCenter />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("LCR Breach")).toBeInTheDocument();
      expect(screen.getByText("NSFR Low")).toBeInTheDocument();
    });
  });

  it("shows empty state when no alerts", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<AlertCenter />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("No open alerts")).toBeInTheDocument();
    });
  });

  it("shows recommendation when present", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => alertsResponse,
    });
    render(<AlertCenter />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText(/Increase HQLA/)).toBeInTheDocument();
    });
  });

  it("shows filter buttons", () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    });
    render(<AlertCenter />, { wrapper });
    expect(screen.getByText("open")).toBeInTheDocument();
    expect(screen.getByText("acknowledged")).toBeInTheDocument();
  });

  it("handles fetch failure gracefully", async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: false, json: async () => ({}) });
    render(<AlertCenter />, { wrapper });
    await waitFor(() => {
      expect(screen.getByTestId("alert-center")).toBeInTheDocument();
    });
  });
});
