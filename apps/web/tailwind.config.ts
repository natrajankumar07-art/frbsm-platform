import type { Config } from "tailwindcss";

/**
 * Design tokens from UI_Polish.md §2 mapped to Tailwind configuration.
 * These are the ONLY colours and spacing values used in the application.
 * Never use arbitrary Tailwind values for semantic design tokens.
 */
const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Surface
        surface: {
          DEFAULT: "#FAFAF7",
          dark: "#0E0F12",
          raised: {
            DEFAULT: "#FFFFFF",
            dark: "#16181D",
          },
        },
        // Text
        text: {
          primary: {
            DEFAULT: "#0E1116",
            dark: "#E6E8EC",
          },
          secondary: {
            DEFAULT: "#5A6270",
            dark: "#8B93A1",
          },
        },
        // Border
        border: {
          DEFAULT: "#E6E4DE",
          dark: "#23262D",
        },
        // Semantic
        accent: {
          DEFAULT: "#2B5BD7",
          dark: "#5C82E6",
        },
        warning: {
          DEFAULT: "#B8730F",
          dark: "#E0972E",
        },
        critical: {
          DEFAULT: "#B0312C",
          dark: "#E25852",
        },
        positive: {
          DEFAULT: "#1F7A4A",
          dark: "#3FA972",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      fontSize: {
        display: ["28px", { lineHeight: "1.2", fontWeight: "600" }],
        heading: ["18px", { lineHeight: "1.4", fontWeight: "600" }],
        body: ["14px", { lineHeight: "1.5", fontWeight: "400" }],
        caption: ["12px", { lineHeight: "1.4", fontWeight: "400" }],
      },
      spacing: {
        // 4px grid
        "0.5": "2px",
        "1": "4px",
        "2": "8px",
        "3": "12px",
        "4": "16px",
        "6": "24px",
        "8": "32px",
        "12": "48px",
      },
      transitionDuration: {
        DEFAULT: "120ms",
      },
      transitionTimingFunction: {
        DEFAULT: "ease-out",
      },
    },
  },
  plugins: [],
};

export default config;
