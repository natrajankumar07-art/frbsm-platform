import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { ExecutiveSAMPanel } from "../ExecutiveSAMPanel";

vi.mock("../../copilot/SamAvatar", () => ({
  SamAvatar: ({ size }: { size: string }) => (
    <div data-testid={`sam-avatar-${size}`} />
  ),
}));

describe("ExecutiveSAMPanel", () => {
  const defaultProps = {
    entityName: "Test Bank Ltd",
    snapshotDate: "31 Mar 2025",
    health: "healthy" as const,
    alertCount: 0,
  };

  it("renders SAM identity", () => {
    render(
      <MemoryRouter>
        <ExecutiveSAMPanel {...defaultProps} />
      </MemoryRouter>
    );
    expect(screen.getByTestId("executive-sam-panel")).toBeInTheDocument();
    expect(screen.getByText("SAM")).toBeInTheDocument();
    expect(screen.getByText("Senior Banking Intelligence Advisor")).toBeInTheDocument();
    expect(screen.getByText("● Online")).toBeInTheDocument();
  });

  it("renders snapshot date", () => {
    render(
      <MemoryRouter>
        <ExecutiveSAMPanel {...defaultProps} />
      </MemoryRouter>
    );
    expect(screen.getByText(/Snapshot: 31 Mar 2025/)).toBeInTheDocument();
  });

  it("shows morning greeting for healthy bank", () => {
    render(
      <MemoryRouter>
        <ExecutiveSAMPanel {...defaultProps} />
      </MemoryRouter>
    );
    expect(
      screen.getByText(/Test Bank Ltd is in a strong regulatory position/)
    ).toBeInTheDocument();
  });

  it("shows alert button when alertCount > 0", () => {
    render(
      <MemoryRouter>
        <ExecutiveSAMPanel {...defaultProps} alertCount={3} health="warning" />
      </MemoryRouter>
    );
    expect(screen.getByText(/3 Alerts/)).toBeInTheDocument();
  });

  it("hides alert button when alertCount is 0", () => {
    render(
      <MemoryRouter>
        <ExecutiveSAMPanel {...defaultProps} alertCount={0} />
      </MemoryRouter>
    );
    expect(screen.queryByText(/Alert/)).not.toBeInTheDocument();
  });

  it("renders Full Briefing and Recommended Actions buttons", () => {
    render(
      <MemoryRouter>
        <ExecutiveSAMPanel {...defaultProps} />
      </MemoryRouter>
    );
    expect(screen.getByText(/Full Briefing/)).toBeInTheDocument();
    expect(screen.getByText(/Recommended Actions/)).toBeInTheDocument();
  });
});
