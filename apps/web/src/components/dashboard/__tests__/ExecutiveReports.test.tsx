import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { ExecutiveReports } from "../ExecutiveReports";

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...(actual as object), useNavigate: () => mockNavigate };
});

describe("ExecutiveReports", () => {
  beforeEach(() => {
    mockNavigate.mockClear();
    sessionStorage.clear();
  });

  it("renders all 7 report actions", () => {
    render(
      <MemoryRouter>
        <ExecutiveReports />
      </MemoryRouter>
    );
    expect(screen.getByTestId("executive-reports")).toBeInTheDocument();
    expect(screen.getByText("CEO Summary")).toBeInTheDocument();
    expect(screen.getByText("CRO Summary")).toBeInTheDocument();
    expect(screen.getByText("Board Pack")).toBeInTheDocument();
    expect(screen.getByText("ICAAP Snapshot")).toBeInTheDocument();
    expect(screen.getByText("ILAAP Snapshot")).toBeInTheDocument();
    expect(screen.getByText("Liquidity Summary")).toBeInTheDocument();
    expect(screen.getByText("Capital Summary")).toBeInTheDocument();
  });

  it("navigates to /copilot and stores prefill on click", () => {
    render(
      <MemoryRouter>
        <ExecutiveReports />
      </MemoryRouter>
    );
    fireEvent.click(screen.getByText("CEO Summary"));
    expect(mockNavigate).toHaveBeenCalledWith("/copilot");
    expect(sessionStorage.getItem("bsm-copilot-prefill")).toContain("CEO Summary");
  });

  it("stores report type for Board Pack", () => {
    render(
      <MemoryRouter>
        <ExecutiveReports />
      </MemoryRouter>
    );
    fireEvent.click(screen.getByText("Board Pack"));
    expect(sessionStorage.getItem("bsm-report-type")).toBe("board_pack");
  });

  it("renders executive reports heading", () => {
    render(
      <MemoryRouter>
        <ExecutiveReports />
      </MemoryRouter>
    );
    expect(screen.getByText("Executive Reports")).toBeInTheDocument();
  });
});
