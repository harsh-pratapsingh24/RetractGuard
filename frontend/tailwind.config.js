/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "surface": "#0f131d",
        "surface-dim": "#0f131d",
        "surface-bright": "#353944",
        "surface-container-lowest": "#0a0e18",
        "surface-container-low": "#171b26",
        "surface-container": "#1c1f2a",
        "surface-container-high": "#262a35",
        "surface-container-highest": "#313540",
        "on-surface": "#dfe2f1",
        "on-surface-variant": "#c7c4d7",
        "outline": "#908fa0",
        "outline-variant": "#464554",
        "surface-tint": "#c0c1ff",
        "surface-variant": "#313540",
        "primary": "#c0c1ff",
        "on-primary": "#1000a9",
        "primary-container": "#8083ff",
        "on-primary-container": "#0d0096",
        "secondary": "#bdc2ff",
        "on-secondary": "#131e8c",
        "secondary-container": "#2f3aa3",
        "on-secondary-container": "#a8afff",
        "tertiary": "#4edea3",
        "on-tertiary": "#003824",
        "tertiary-container": "#00885d",
        "error": "#ffb4ab",
        "on-error": "#690005",
        "error-container": "#93000a",
        "on-error-container": "#ffdad6"
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"]
      }
    }
  },
  plugins: [],
}
