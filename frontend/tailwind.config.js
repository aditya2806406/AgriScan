/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        forest: '#1E3626',
        'forest-2': '#24402C',
        'forest-3': '#2B4A33',
        cream: '#F6F3EA',
        'cream-dim': '#C9D3C7',
        gold: '#C9963B',
        sage: '#7FA37A',
        brick: '#A6503E',
      },
      fontFamily: {
        display: ['Newsreader', 'Georgia', 'serif'],
        body: ['"Work Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
