/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        croc: {
          ink: "#10231f",
          emerald: "#063c30",
          moss: "#0d5c49",
          mint: "#dff7ea",
          lime: "#a8e6b1",
          cream: "#f8fbf6",
          gold: "#f6c85f",
          coral: "#ee7b72",
          sky: "#7bb7f0"
        }
      },
      boxShadow: {
        card: "0 18px 45px rgba(16, 35, 31, 0.08)"
      }
    }
  },
  plugins: []
};

