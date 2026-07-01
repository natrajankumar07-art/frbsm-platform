import "@testing-library/jest-dom";

// jsdom doesn't implement ResizeObserver (used by Recharts)
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

// jsdom may not expose localStorage; provide a simple in-memory shim
if (typeof localStorage === "undefined" || localStorage === null) {
  const store: Record<string, string> = {};
  Object.defineProperty(global, "localStorage", {
    value: {
      getItem: (k: string) => store[k] ?? null,
      setItem: (k: string, v: string) => { store[k] = String(v); },
      removeItem: (k: string) => { delete store[k]; },
      clear: () => { Object.keys(store).forEach((k) => delete store[k]); },
    },
  });
}
