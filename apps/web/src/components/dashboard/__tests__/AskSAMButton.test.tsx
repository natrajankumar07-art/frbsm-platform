import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AskSAMButton } from "../AskSAMButton";

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...(actual as object), useNavigate: () => mockNavigate };
});

describe("AskSAMButton", () => {
  beforeEach(() => {
    mockNavigate.mockClear();
    sessionStorage.clear();
  });

  it("renders with default label", () => {
    render(
      <MemoryRouter>
        <AskSAMButton context="Test context" />
      </MemoryRouter>
    );
    expect(screen.getByTestId("ask-sam-button")).toBeInTheDocument();
    expect(screen.getByText(/Ask SAM/)).toBeInTheDocument();
  });

  it("renders with custom label", () => {
    render(
      <MemoryRouter>
        <AskSAMButton context="Test" label="Get Analysis" />
      </MemoryRouter>
    );
    expect(screen.getByText(/Get Analysis/)).toBeInTheDocument();
  });

  it("stores context in sessionStorage on click", () => {
    render(
      <MemoryRouter>
        <AskSAMButton context="Explain LCR ratio" />
      </MemoryRouter>
    );
    fireEvent.click(screen.getByTestId("ask-sam-button"));
    expect(sessionStorage.getItem("bsm-copilot-prefill")).toBe("Explain LCR ratio");
  });

  it("navigates to /copilot on click", () => {
    render(
      <MemoryRouter>
        <AskSAMButton context="Explain LCR ratio" />
      </MemoryRouter>
    );
    fireEvent.click(screen.getByTestId("ask-sam-button"));
    expect(mockNavigate).toHaveBeenCalledWith("/copilot");
  });
});
