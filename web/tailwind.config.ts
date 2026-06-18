import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: { DEFAULT: "#07080C", soft: "#0B0D12", surface: "#11131A", raised: "#171A24" },
        line: "rgba(255,255,255,0.08)",
        ink: { DEFAULT: "#EDEFF5", muted: "#9BA1B0", faint: "#6B7180" },
        brand: { DEFAULT: "#7C6EFF", light: "#A99BFF", glow: "#8B7DFF" },
        cyan: "#22D3EE",
        blue: "#3B82F6",
        fuchsia: "#C026D3",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      letterSpacing: { tightest: "-0.04em" },
      maxWidth: { content: "1120px" },
      boxShadow: {
        glow: "0 0 80px -20px rgba(124,110,255,0.45)",
        card: "0 1px 0 0 rgba(255,255,255,0.04) inset, 0 20px 50px -20px rgba(0,0,0,0.6)",
      },
      backgroundImage: {
        "brand-gradient": "linear-gradient(100deg, #22D3EE 0%, #3B82F6 45%, #C026D3 100%)",
        "radial-faint": "radial-gradient(60% 60% at 50% 0%, rgba(124,110,255,0.16), transparent 70%)",
      },
      keyframes: {
        marquee: { from: { transform: "translateX(0)" }, to: { transform: "translateX(-50%)" } },
        aurora: {
          "0%,100%": { transform: "translate(-10%,-10%) rotate(0deg)" },
          "50%": { transform: "translate(10%,10%) rotate(180deg)" },
        },
        shimmer: { "100%": { transform: "translateX(100%)" } },
      },
      animation: {
        marquee: "marquee 32s linear infinite",
        aurora: "aurora 22s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
export default config;
