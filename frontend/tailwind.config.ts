import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        gold: "#DCAE72",
        purple: "#9F72DB",
        green: "#72DB8C",
        "warm-gray": "#867E73",
        "dark-purple": "#50485C",
        "dark-green": "#485C4D"
      },
      boxShadow: {
        soft: "0 18px 50px rgb(30 36 32 / 24%)",
        glow: "0 0 0 1px rgb(220 174 114 / 18%), 0 24px 80px rgb(30 36 32 / 32%)"
      }
    }
  },
  plugins: []
};

export default config;
