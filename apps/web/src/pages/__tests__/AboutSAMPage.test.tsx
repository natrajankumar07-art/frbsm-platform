import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AboutSAMPage } from "../AboutSAMPage";

vi.mock("../../components/copilot/SamAvatar", () => ({
  SamAvatar: () => <div data-testid="sam-avatar">SAM</div>,
}));

vi.mock("../../components/dashboard/AskSAMButton", () => ({
  AskSAMButton: ({ label }: { label?: string }) => (
    <button data-testid="ask-sam-btn">{label ?? "Ask SAM"}</button>
  ),
}));

function render_page() {
  return render(
    <MemoryRouter>
      <AboutSAMPage />
    </MemoryRouter>
  );
}

describe("AboutSAMPage", () => {
  it("renders the about-sam-page container", () => {
    render_page();
    expect(screen.getByTestId("about-sam-page")).toBeInTheDocument();
  });

  it("shows SAM name and title", () => {
    render_page();
    expect(screen.getByRole("heading", { name: "SAM" })).toBeInTheDocument();
    expect(screen.getByText(/Supervisory AI Manager/i)).toBeInTheDocument();
  });

  it("renders the SAM avatar", () => {
    render_page();
    expect(screen.getByTestId("sam-avatar")).toBeInTheDocument();
  });

  it("shows Capabilities section", () => {
    render_page();
    expect(screen.getByText(/Capabilities/i)).toBeInTheDocument();
  });

  it("shows Financial Boundaries section", () => {
    render_page();
    expect(screen.getByText(/Financial Boundaries/i)).toBeInTheDocument();
  });

  it("shows that SAM never computes LCR", () => {
    render_page();
    expect(screen.getByText(/NEVER computes LCR/i)).toBeInTheDocument();
  });

  it("shows Regulatory Expertise section", () => {
    render_page();
    expect(screen.getByText(/Regulatory Expertise/i)).toBeInTheDocument();
  });

  it("shows AI Safety Statement", () => {
    render_page();
    expect(screen.getByText(/AI Safety Statement/i)).toBeInTheDocument();
  });

  it("shows How SAM Works architecture section", () => {
    render_page();
    expect(screen.getByText(/How SAM Works/i)).toBeInTheDocument();
  });
});
