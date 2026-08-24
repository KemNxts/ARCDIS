/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#0f172a', // slate-900
        surface: '#1e293b',    // slate-800
        primary: '#10b981',    // emerald-500
        primary_dark: '#059669', // emerald-600
        accent: '#06b6d4',     // cyan-500
        danger: '#ef4444',     // red-500
        warning: '#f59e0b',    // amber-500
        text: '#f8fafc',       // slate-50
        text_muted: '#94a3b8', // slate-400
        border: '#334155',     // slate-700
      },
      fontFamily: {
        mono: ['Fira Code', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', 'monospace'],
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
