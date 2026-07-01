import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ThemeProvider, useTheme } from "../ThemeContext";

function ThemeConsumer() {
  const { theme, toggleTheme } = useTheme();
  return (
    <div>
      <span data-testid="theme">{theme}</span>
      <button onClick={toggleTheme}>Toggle</button>
    </div>
  );
}

describe("ThemeContext", () => {
  beforeEach(() => {
    if (typeof localStorage !== "undefined" && localStorage) {
      localStorage.clear();
    }
    document.documentElement.classList.remove("dark");
  });

  it("defaults to light theme", () => {
    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    );
    expect(screen.getByTestId("theme").textContent).toBe("light");
  });

  it("toggles to dark theme", () => {
    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    );
    fireEvent.click(screen.getByText("Toggle"));
    expect(screen.getByTestId("theme").textContent).toBe("dark");
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("toggles back to light from dark", () => {
    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    );
    fireEvent.click(screen.getByText("Toggle"));
    fireEvent.click(screen.getByText("Toggle"));
    expect(screen.getByTestId("theme").textContent).toBe("light");
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });

  it("reads stored theme from localStorage", () => {
    if (typeof localStorage !== "undefined" && localStorage) {
      localStorage.setItem("bsm-theme", "dark");
    } else {
      vi.spyOn(Storage.prototype, "getItem").mockImplementation((key) =>
        key === "bsm-theme" ? "dark" : null
      );
    }
    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    );
    expect(screen.getByTestId("theme").textContent).toBe("dark");
  });
});
