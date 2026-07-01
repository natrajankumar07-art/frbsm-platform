import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { BankHealthIndicator } from "../BankHealthIndicator";

describe("BankHealthIndicator", () => {
  it("renders healthy status", () => {
    render(
      <BankHealthIndicator health="healthy" passCount={3} totalChecks={3} />
    );
    expect(screen.getByTestId("bank-health-indicator")).toBeInTheDocument();
    expect(screen.getByText("Healthy")).toBeInTheDocument();
    expect(screen.getByText("3/3 checks passing")).toBeInTheDocument();
  });

  it("renders warning status", () => {
    render(
      <BankHealthIndicator health="warning" passCount={2} totalChecks={3} />
    );
    expect(screen.getByText("Warning")).toBeInTheDocument();
    expect(screen.getByText("2/3 checks passing")).toBeInTheDocument();
  });

  it("renders critical status", () => {
    render(
      <BankHealthIndicator health="critical" passCount={0} totalChecks={3} />
    );
    expect(screen.getByText("Critical")).toBeInTheDocument();
    expect(screen.getByText("0/3 checks passing")).toBeInTheDocument();
  });

  it("displays Bank Health label", () => {
    render(
      <BankHealthIndicator health="healthy" passCount={3} totalChecks={3} />
    );
    expect(screen.getByText("Bank Health")).toBeInTheDocument();
  });
});
