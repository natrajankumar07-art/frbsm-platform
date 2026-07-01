import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { HelpCenterPage } from "../HelpCenterPage";
import { TourProvider } from "../../context/TourContext";

vi.mock("../../context/TourContext", async () => {
  const actual = await vi.importActual<typeof import("../../context/TourContext")>("../../context/TourContext");
  return {
    ...actual,
    useTour: () => ({
      isActive: false,
      currentStep: 0,
      totalSteps: 6,
      step: { id: "welcome", title: "Welcome", description: "", icon: "🏦" },
      next: vi.fn(),
      prev: vi.fn(),
      dismiss: vi.fn(),
      restart: vi.fn(),
    }),
  };
});

beforeEach(() => {
  localStorage.clear();
});

function render_page() {
  return render(
    <TourProvider>
      <MemoryRouter>
        <HelpCenterPage />
      </MemoryRouter>
    </TourProvider>
  );
}

describe("HelpCenterPage", () => {
  it("renders help-center-page container", () => {
    render_page();
    expect(screen.getByTestId("help-center-page")).toBeInTheDocument();
  });

  it("shows User Guide tab by default", () => {
    render_page();
    expect(screen.getByText("User Guide")).toBeInTheDocument();
  });

  it("shows all 6 tab labels", () => {
    render_page();
    expect(screen.getByText("User Guide")).toBeInTheDocument();
    expect(screen.getByText("Admin Guide")).toBeInTheDocument();
    expect(screen.getByText("Architecture")).toBeInTheDocument();
    expect(screen.getByText("FAQ")).toBeInTheDocument();
    expect(screen.getByText("Keyboard Shortcuts")).toBeInTheDocument();
    expect(screen.getByText("Troubleshooting")).toBeInTheDocument();
  });

  it("clicking FAQ tab shows FAQ content", () => {
    render_page();
    fireEvent.click(screen.getByText("FAQ"));
    expect(screen.getByText(/Does SAM compute LCR/)).toBeInTheDocument();
  });

  it("clicking Keyboard Shortcuts tab shows shortcut list", () => {
    render_page();
    fireEvent.click(screen.getByText("Keyboard Shortcuts"));
    expect(screen.getByText(/Open AI Copilot/)).toBeInTheDocument();
  });

  it("clicking Troubleshooting tab shows troubleshooting content", () => {
    render_page();
    fireEvent.click(screen.getByText("Troubleshooting"));
    expect(screen.getByText(/SAM says he has no data/i)).toBeInTheDocument();
  });

  it("clicking Architecture tab shows architecture content", () => {
    render_page();
    fireEvent.click(screen.getByText("Architecture"));
    expect(screen.getByText(/Three-Layer Architecture/i)).toBeInTheDocument();
  });

  it("shows page title", () => {
    render_page();
    expect(screen.getByText(/Help Center/i)).toBeInTheDocument();
  });
});
