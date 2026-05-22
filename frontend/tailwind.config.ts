import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          950: "#071425",
          900: "#0B1F35",
          800: "#12304E",
          700: "#17446F"
        },
        ivory: "#FBF7EE",
        mist: "#EEF2F6",
        line: "#D8E0E8",
        bluepoint: "#2F7DD1"
      },
      boxShadow: {
        soft: "0 18px 50px rgba(11, 31, 53, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
