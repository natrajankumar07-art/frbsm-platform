import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { TourProvider, useTour } from "../TourContext";

const TOUR_KEY = "bsm-tour-complete";

function TourConsumer() {
  const { isActive, currentStep, totalSteps, step, next, prev, dismiss, restart } = useTour();
  return (
    <div>
      <span data-testid="active">{String(isActive)}</span>
      <span data-testid="step">{currentStep}</span>
      <span data-testid="total">{totalSteps}</span>
      <span data-testid="title">{step.title}</span>
      <button onClick={next} data-testid="next">next</button>
      <button onClick={prev} data-testid="prev">prev</button>
      <button onClick={dismiss} data-testid="dismiss">dismiss</button>
      <button onClick={restart} data-testid="restart">restart</button>
    </div>
  );
}

describe("TourContext", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("starts active when tour not completed", () => {
    render(<TourProvider><TourConsumer /></TourProvider>);
    expect(screen.getByTestId("active").textContent).toBe("true");
  });

  it("starts inactive when tour already completed", () => {
    localStorage.setItem(TOUR_KEY, "1");
    render(<TourProvider><TourConsumer /></TourProvider>);
    expect(screen.getByTestId("active").textContent).toBe("false");
  });

  it("starts at step 0", () => {
    render(<TourProvider><TourConsumer /></TourProvider>);
    expect(screen.getByTestId("step").textContent).toBe("0");
  });

  it("has 6 total steps", () => {
    render(<TourProvider><TourConsumer /></TourProvider>);
    expect(screen.getByTestId("total").textContent).toBe("6");
  });

  it("step 0 title is Welcome", () => {
    render(<TourProvider><TourConsumer /></TourProvider>);
    expect(screen.getByTestId("title").textContent).toContain("Welcome");
  });

  it("next() advances to step 1", () => {
    render(<TourProvider><TourConsumer /></TourProvider>);
    fireEvent.click(screen.getByTestId("next"));
    expect(screen.getByTestId("step").textContent).toBe("1");
  });

  it("prev() does nothing at step 0", () => {
    render(<TourProvider><TourConsumer /></TourProvider>);
    fireEvent.click(screen.getByTestId("prev"));
    expect(screen.getByTestId("step").textContent).toBe("0");
  });

  it("prev() goes back after advancing", () => {
    render(<TourProvider><TourConsumer /></TourProvider>);
    fireEvent.click(screen.getByTestId("next"));
    fireEvent.click(screen.getByTestId("prev"));
    expect(screen.getByTestId("step").textContent).toBe("0");
  });

  it("dismiss() deactivates tour and sets localStorage", () => {
    render(<TourProvider><TourConsumer /></TourProvider>);
    fireEvent.click(screen.getByTestId("dismiss"));
    expect(screen.getByTestId("active").textContent).toBe("false");
    expect(localStorage.getItem(TOUR_KEY)).toBe("1");
  });

  it("restart() removes localStorage and reactivates", () => {
    localStorage.setItem(TOUR_KEY, "1");
    render(<TourProvider><TourConsumer /></TourProvider>);
    expect(screen.getByTestId("active").textContent).toBe("false");
    fireEvent.click(screen.getByTestId("restart"));
    expect(screen.getByTestId("active").textContent).toBe("true");
    expect(localStorage.getItem(TOUR_KEY)).toBeNull();
  });

  it("restart() resets to step 0", () => {
    render(<TourProvider><TourConsumer /></TourProvider>);
    fireEvent.click(screen.getByTestId("next"));
    fireEvent.click(screen.getByTestId("next"));
    fireEvent.click(screen.getByTestId("restart"));
    expect(screen.getByTestId("step").textContent).toBe("0");
  });

  it("next() on last step dismisses tour", () => {
    render(<TourProvider><TourConsumer /></TourProvider>);
    for (let i = 0; i < 6; i++) fireEvent.click(screen.getByTestId("next"));
    expect(screen.getByTestId("active").textContent).toBe("false");
  });
});
