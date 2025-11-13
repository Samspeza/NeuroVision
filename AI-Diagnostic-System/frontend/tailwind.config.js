/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#2563eb", // Azul principal
        surface: "#ffffff", // Fundo neutro
        accent: "#3b82f6",  // Azul de destaque
        muted: "#6b7280",   // Cinza médio
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
      boxShadow: {
        soft: "0 2px 6px rgba(0,0,0,0.08)",
      },
    },
  },
  plugins: [],
};
