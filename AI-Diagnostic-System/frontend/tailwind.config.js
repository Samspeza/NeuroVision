/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#2563eb",
        secondary: "#1e40af",
        accent: "#38bdf8",
        background: "#f9fafb",
        surface: "#ffffff",
        danger: "#ef4444"
      },
      boxShadow: {
        soft: "0 2px 8px rgba(0, 0, 0, 0.1)"
      },
      borderRadius: {
        xl: "1rem"
      }
    },
  },
  plugins: [],
};
