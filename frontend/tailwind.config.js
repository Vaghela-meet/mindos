/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['Newsreader', 'Playfair Display', 'Georgia', 'Cambria', 'serif'],
        sans: ['Geist', 'Plus Jakarta Sans', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      colors: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        surface: {
          DEFAULT: 'hsl(var(--surface))',
          muted: 'hsl(var(--surface-muted))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        'muted-text': 'hsl(var(--muted-foreground))',
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          muted: 'hsl(var(--accent-muted))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        border: {
          DEFAULT: 'hsl(var(--border))',
          subtle: 'hsl(var(--border-subtle))',
        },
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        status: {
          attention: 'hsl(var(--status-attention))',
          risk: 'hsl(var(--status-risk))',
          healthy: 'hsl(var(--status-healthy))',
          adaptation: 'hsl(var(--status-adaptation))',
        },
      },
      borderRadius: {
        none: '0px',
        sm: '2px',
        DEFAULT: '4px',
        md: '6px',
        lg: '8px',
      },
    },
  },
  plugins: [],
}
