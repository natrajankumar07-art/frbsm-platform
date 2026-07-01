import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { LandingPage } from "../LandingPage";

const mockNavigate = vi.fn();
const mockLoginDemo = vi.fn().mockResolvedValue(undefined);

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...(actual as object), useNavigate: () => mockNavigate };
});

vi.mock("../../context/AuthContext", () => ({
  useAuth: () => ({
    loginDemo: mockLoginDemo,
    isAuthenticated: false,
    isDemoMode: false,
    user: null,
    login: vi.fn(),
    logout: vi.fn(),
  }),
}));

vi.mock("../../components/copilot/SamAvatar", () => ({
  SamAvatar: ({ size }: { size?: string }) => (
    <div data-testid={`sam-avatar-${size ?? "md"}`}>SAM</div>
  ),
}));

beforeEach(() => {
  mockNavigate.mockClear();
  mockLoginDemo.mockClear();
});

function render_page() {
  return render(
    <MemoryRouter>
      <LandingPage />
    </MemoryRouter>
  );
}

describe("LandingPage", () => {
  it("renders the page", () => {
    const { container } = render_page();
    expect(container.firstChild).not.toBeNull();
  });

  it("shows platform headline", () => {
    render_page();
    expect(screen.getByText(/BSM Platform/i)).toBeInTheDocument();
  });

  it("shows Launch Demo button", () => {
    render_page();
    expect(screen.getAllByText(/Launch/i).length).toBeGreaterThan(0);
  });

  it("shows SAM introduction", () => {
    render_page();
    expect(screen.getAllByText(/SAM/).length).toBeGreaterThan(0);
  });

  it("shows capabilities section", () => {
    render_page();
    expect(screen.getAllByText(/Regulatory Analytics/i).length).toBeGreaterThan(0);
  });

  it("shows three-layer architecture section", () => {
    render_page();
    expect(screen.getByText(/Architecture/i)).toBeInTheDocument();
  });

  it("clicking Launch Demo calls loginDemo", async () => {
    render_page();
    const launchBtn = screen.getAllByText(/Launch/i)[0];
    fireEvent.click(launchBtn);
    await waitFor(() => {
      expect(mockLoginDemo).toHaveBeenCalledTimes(1);
    });
  });

  it("after loginDemo resolves, navigates to /", async () => {
    render_page();
    const launchBtn = screen.getAllByText(/Launch/i)[0];
    fireEvent.click(launchBtn);
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/");
    });
  });

  it("shows tech stack section", () => {
    render_page();
    expect(screen.getByText(/React/i)).toBeInTheDocument();
  });
});
