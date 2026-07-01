import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { InsightCard } from "../InsightCard";

describe("InsightCard", () => {
  const baseProps = {
    domain: "liquidity" as const,
    title: "Liquidity",
    value: "125.3%",
    trend: "up" as const,
    trendLabel: "Passing",
    drivers: ["HQLA: 1,000,000", "Net Outflows: 800,000"],
    recommendation: "LCR is above the regulatory minimum.",
  };

  it("renders title and value", () => {
    render(<InsightCard {...baseProps} />);
    expect(screen.getByText("Liquidity")).toBeInTheDocument();
    expect(screen.getByText("125.3%")).toBeInTheDocument();
  });

  it("renders drivers", () => {
    render(<InsightCard {...baseProps} />);
    expect(screen.getByText("Key Drivers")).toBeInTheDocument();
    expect(screen.getByText(/HQLA: 1,000,000/)).toBeInTheDocument();
  });

  it("renders recommendation", () => {
    render(<InsightCard {...baseProps} />);
    expect(
      screen.getByText("LCR is above the regulatory minimum.")
    ).toBeInTheDocument();
  });

  it("renders Ask SAM button when onAskSAM provided", () => {
    const onAskSAM = vi.fn();
    render(<InsightCard {...baseProps} onAskSAM={onAskSAM} />);
    const btn = screen.getByText(/Ask SAM/);
    expect(btn).toBeInTheDocument();
    fireEvent.click(btn);
    expect(onAskSAM).toHaveBeenCalledOnce();
  });

  it("does not render Ask SAM button when not provided", () => {
    render(<InsightCard {...baseProps} />);
    expect(screen.queryByText(/Ask SAM/)).not.toBeInTheDocument();
  });

  it("renders trend label", () => {
    render(<InsightCard {...baseProps} />);
    expect(screen.getByText("Passing")).toBeInTheDocument();
  });
});
