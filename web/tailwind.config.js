/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'dark': '#0f172a',
        'dark-lighter': '#1e293b',
        'accent': '#06b6d4',
        'accent-dark': '#0891b2',
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Monaco', 'Courier New', 'monospace'],
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
