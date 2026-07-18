import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0A2540",      // deep navy — primary text / dark surfaces
        jet: "#0FA697",      // teal — primary accent / CTA
        sky: "#2A7DE1",      // blue — links / flight path
        gold: "#E0A83B",     // amber — premium / VIP
        paper: "#F2F6F9",    // cool sky-tinted background
        line: "#DCE6EE",     // hairlines
      },
      fontFamily: {
        display: ["var(--font-display)", "sans-serif"],
        body: ["var(--font-body)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;
