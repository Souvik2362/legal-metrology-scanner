import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        paper: "#EEF1EC",
        "paper-line": "#D9DFD8",
        ink: "#141A1D",
        "ink-soft": "#4A5459",
        "ink-faint": "#8A938E",
        rule: "#B7C1BA",
        gauge: "#1D3557",
        "gauge-dim": "#2E4C77",
        verified: "#2A6041",
        "verified-bg": "#E3ECE3",
        pending: "#8A5A00",
        "pending-bg": "#F1E7D2",
        flagged: "#9C3B2E",
        "flagged-bg": "#F3E1DC",
      },
      fontFamily: {
        sans: ["var(--font-plex-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-plex-mono)", "monospace"],
      },
      fontSize: {
        micro: ["0.6875rem", { lineHeight: "1rem", letterSpacing: "0.02em" }],
      },
      borderRadius: {
        none: "0px",
        sm: "1px",
        DEFAULT: "2px",
      },
      boxShadow: {
        none: "none",
      },
      keyframes: {
        sweep: {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(320%)" },
        },
        blink: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.25" },
        },
      },
      animation: {
        sweep: "sweep 1.6s ease-in-out infinite",
        blink: "blink 1.2s steps(2, start) infinite",
      },
    },
  },
  plugins: [],
};
export default config;
