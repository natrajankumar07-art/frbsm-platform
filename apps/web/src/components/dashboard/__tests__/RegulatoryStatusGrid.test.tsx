import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { RegulatoryStatusGrid } from "../RegulatoryStatusGrid";
import type { LCRResult, NSFRResult, CapitalResult } from "../../../types/api";

const mockLCR: LCRResult = {
  snapshot_id: "s1",
  entity_id: "e1",
  hqla_total: "1000000",
  net_cash_outflows: "800000",
  total_outflows: "1000000",
  total_inflows: "200000",
  inflow_cap_applied: false,
  lcr_ratio: "1.25",
  minimum_ratio: "1.0",
  passes: true,
  currency: "USD",
};

const mockNSFR: NSFRResult = {
  snapshot_id: "s1",
  entity_id: "e1",
  available_stable_funding: "2000000",
  required_stable_funding: "1800000",
  nsfr_ratio: "1.111",
  minimum_ratio: "1.0",
  passes: true,
  currency: "USD",
};

const mockCapital: CapitalResult = {
  snapshot_id: "s1",
  entity_id: "e1",
  cet1_capital: "500000",
  additional_tier1: "100000",
  tier2_capital: "100000",
  total_capital: "700000",
  rwa_credit: "5000000",
  rwa_market: "500000",
  rwa_operational: "500000",
  total_rwa: "6000000",
  cet1_ratio: "0.0833",
  tier1_ratio: "0.1",
  total_capital_ratio: "0.1167",
  leverage_ratio: "0.035",
  passes_all: true,
  currency: "USD",
};

describe("RegulatoryStatusGrid", () => {
  it("renders all 6 metric cells", () => {
    render(
      <MemoryRouter>
        <RegulatoryStatusGrid lcr={mockLCR} nsfr={mockNSFR} capital={mockCapital} />
      </MemoryRouter>
    );
    expect(screen.getByTestId("regulatory-status-grid")).toBeInTheDocument();
    expect(screen.getByText("LCR")).toBeInTheDocument();
    expect(screen.getByText("NSFR")).toBeInTheDocument();
    expect(screen.getByText("CET1")).toBeInTheDocument();
    expect(screen.getByText("Tier 1")).toBeInTheDocument();
    expect(screen.getByText("Total Capital")).toBeInTheDocument();
    expect(screen.getByText("Leverage")).toBeInTheDocument();
  });

  it("renders pass indicators for all passing metrics", () => {
    render(
      <MemoryRouter>
        <RegulatoryStatusGrid lcr={mockLCR} nsfr={mockNSFR} capital={mockCapital} />
      </MemoryRouter>
    );
    const checks = screen.getAllByText("✓");
    expect(checks.length).toBeGreaterThanOrEqual(4);
  });

  it("shows dashes when data is missing", () => {
    render(
      <MemoryRouter>
        <RegulatoryStatusGrid lcr={null} nsfr={null} capital={null} />
      </MemoryRouter>
    );
    const dashes = screen.getAllByText("—");
    expect(dashes.length).toBe(6);
  });

  it("renders LCR ratio percentage", () => {
    render(
      <MemoryRouter>
        <RegulatoryStatusGrid lcr={mockLCR} nsfr={mockNSFR} capital={mockCapital} />
      </MemoryRouter>
    );
    expect(screen.getByText("125.00%")).toBeInTheDocument();
  });

  it("renders Ask SAM buttons for each metric", () => {
    render(
      <MemoryRouter>
        <RegulatoryStatusGrid lcr={mockLCR} nsfr={mockNSFR} capital={mockCapital} />
      </MemoryRouter>
    );
    const askButtons = screen.getAllByTestId("ask-sam-button");
    expect(askButtons).toHaveLength(6);
  });
});
