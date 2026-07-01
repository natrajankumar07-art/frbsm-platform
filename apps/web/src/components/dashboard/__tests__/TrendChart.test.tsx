import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { TrendChart } from "../TrendChart";

describe("TrendChart", () => {
  const sampleData = [
    { date: "2025-01-31", lcr: 1.25, nsfr: 1.15, cet1: 0.085 },
    { date: "2025-02-28", lcr: 1.30, nsfr: 1.18, cet1: 0.088 },
    { date: "2025-03-31", lcr: 1.22, nsfr: 1.12, cet1: 0.082 },
  ];

  it("renders chart container", () => {
    render(<TrendChart data={sampleData} />);
    expect(screen.getByTestId("trend-chart")).toBeInTheDocument();
  });

  it("renders default title", () => {
    render(<TrendChart data={sampleData} />);
    expect(screen.getByText("Regulatory Trends")).toBeInTheDocument();
  });

  it("renders custom title", () => {
    render(<TrendChart data={sampleData} title="Capital Trends" />);
    expect(screen.getByText("Capital Trends")).toBeInTheDocument();
  });

  it("shows empty state message when data is empty", () => {
    render(<TrendChart data={[]} />);
    expect(
      screen.getByText("Multiple snapshots required for trend analysis.")
    ).toBeInTheDocument();
  });
});
