/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        f1red: "#e10600",
        f1dark: "#15151e",
        f1gray: "#38383f",
      },
    },
  },
  plugins: [],
};
