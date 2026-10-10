/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--bg-app)",
        surface: "var(--bg-surface)",
        border: "var(--border-subtle)",
        textMain: "var(--text-main)",
        textMuted: "var(--text-muted)",
        cisco: {
          safe: "var(--cisco-safe)",
          warn: "var(--cisco-warn)",
          danger: "var(--cisco-danger)",
        }
      }
    },
  },
  plugins: [],
}
