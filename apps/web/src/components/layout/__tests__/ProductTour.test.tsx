import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { TourProvider } from "../../../context/TourContext";
import { ProductTour } from "../ProductTour";

const TOUR_KEY = "bsm-tour-complete";

function Wrapper({ children }: { children: React.ReactNode }) {
  return <TourProvider>{children}</TourProvider>;
}

describe("ProductTour", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("renders nothing when tour is complete", () => {
    localStorage.setItem(TOUR_KEY, "1");
    const { container } = render(<Wrapper><ProductTour /></Wrapper>);
    expect(container.firstChild).toBeNull();
  });

  it("renders tour card when active", () => {
    render(<Wrapper><ProductTour /></Wrapper>);
    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });

  it("shows step 1 of 6 on first render", () => {
    render(<Wrapper><ProductTour /></Wrapper>);
    expect(screen.getByText(/Step 1 of 6/)).toBeInTheDocument();
  });

  it("shows Welcome title on first step", () => {
    render(<Wrapper><ProductTour /></Wrapper>);
    expect(screen.getByText(/Welcome to BSM Platform/)).toBeInTheDocument();
  });

  it("Next button advances to step 2", () => {
    render(<Wrapper><ProductTour /></Wrapper>);
    fireEvent.click(screen.getByLabelText("Next step"));
    expect(screen.getByText(/Step 2 of 6/)).toBeInTheDocument();
  });

  it("dismiss button closes the tour", () => {
    render(<Wrapper><ProductTour /></Wrapper>);
    fireEvent.click(screen.getByLabelText("Dismiss tour"));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(localStorage.getItem(TOUR_KEY)).toBe("1");
  });

  it("Skip tour link closes the tour", () => {
    render(<Wrapper><ProductTour /></Wrapper>);
    fireEvent.click(screen.getByText("Skip tour"));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("Back button is disabled on first step", () => {
    render(<Wrapper><ProductTour /></Wrapper>);
    expect(screen.getByLabelText("Previous step")).toBeDisabled();
  });

  it("last step shows Get started button", () => {
    render(<Wrapper><ProductTour /></Wrapper>);
    for (let i = 0; i < 5; i++) fireEvent.click(screen.getByLabelText("Next step"));
    expect(screen.getByLabelText("Finish tour")).toBeInTheDocument();
  });
});
