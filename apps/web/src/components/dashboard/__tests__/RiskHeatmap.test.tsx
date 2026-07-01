import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { RiskHeatmap } from "../RiskHeatmap";
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
  nsfr_ratio: "1.2",
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
  cet1_ratio: "0.0900",
  tier1_ratio: "0.1",
  total_capital_ratio: "0.1167",
  leverage_ratio: "0.045",
  passes_all: true,
  currency: "USD",
};

describe("RiskHeatmap", () => {
  it("renders all 6 risk categories", () => {
    render(<RiskHeatmap lcr={mockLCR} nsfr={mockNSFR} capital={mockCapital} />);
    expect(screen.getByTestId("risk-heatmap")).toBeInTheDocument();
    expect(screen.getByTestId("risk-cell-liquidity")).toBeInTheDocument();
    expect(screen.getByTestId("risk-cell-capital")).toBeInTheDocument();
    expect(screen.getByTestId("risk-cell-funding")).toBeInTheDocument();
    expect(screen.getByTestId("risk-cell-market")).toBeInTheDocument();
    expect(screen.getByTestId("risk-cell-operational")).toBeInTheDocument();
    expect(screen.getByTestId("risk-cell-interest_rate")).toBeInTheDocument();
  });

  it("shows 'Low' for liquidity when LCR >= 1.20", () => {
    render(<RiskHeatmap lcr={mockLCR} nsfr={mockNSFR} capital={mockCapital} />);
    const liquidityCell = screen.getByTestId("risk-cell-liquidity");
    expect(liquidityCell).toHaveTextContent("Low");
  });

  it("shows tooltip on hover", () => {
    render(<RiskHeatmap lcr={mockLCR} nsfr={mockNSFR} capital={mockCapital} />);
    const liquidityCell = screen.getByTestId("risk-cell-liquidity");
    fireEvent.mouseEnter(liquidityCell);
    expect(screen.getByText(/Green: ≥120%/)).toBeInTheDocument();
  });

  it("shows 'N/A' for unknown data", () => {
    render(<RiskHeatmap lcr={null} nsfr={null} capital={null} />);
    const liquidityCell = screen.getByTestId("risk-cell-liquidity");
    expect(liquidityCell).toHaveTextContent("N/A");
  });

  it("renders methodology footnote", () => {
    render(<RiskHeatmap lcr={mockLCR} nsfr={mockNSFR} capital={mockCapital} />);
    expect(screen.getByText(/Ratings derived from engine outputs/)).toBeInTheDocument();
  });
});
