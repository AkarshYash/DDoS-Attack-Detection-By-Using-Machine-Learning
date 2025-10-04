module.exports = {
  content: [
    "./pages/*.{html,js}",
    "./index.html",
    "./src/**/*.{html,js,jsx,ts,tsx}",
    "./components/**/*.{html,js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        // Primary Colors - Electric Blue
        primary: {
          DEFAULT: "#00d4ff", // electric-blue
          50: "#f0fcff", // electric-blue-50
          100: "#e0f9ff", // electric-blue-100
          200: "#baf2ff", // electric-blue-200
          300: "#7de8ff", // electric-blue-300
          400: "#38ddff", // electric-blue-400
          500: "#00d4ff", // electric-blue-500
          600: "#00a8cc", // electric-blue-600
          700: "#007a99", // electric-blue-700
          800: "#005566", // electric-blue-800
          900: "#003344", // electric-blue-900
        },
        // Secondary Colors - Navy Blue
        secondary: {
          DEFAULT: "#2c5aa0", // navy-blue
          50: "#f1f5fb", // navy-blue-50
          100: "#e3ebf7", // navy-blue-100
          200: "#c7d7ef", // navy-blue-200
          300: "#9bb8e3", // navy-blue-300
          400: "#6b94d3", // navy-blue-400
          500: "#4a7bc8", // navy-blue-500
          600: "#3a66b8", // navy-blue-600
          700: "#2c5aa0", // navy-blue-700
          800: "#234a85", // navy-blue-800
          900: "#1a3a6b", // navy-blue-900
        },
        // Accent Colors - Purple
        accent: {
          DEFAULT: "#7c3aed", // purple-600
          50: "#f5f3ff", // purple-50
          100: "#ede9fe", // purple-100
          200: "#ddd6fe", // purple-200
          300: "#c4b5fd", // purple-300
          400: "#a78bfa", // purple-400
          500: "#8b5cf6", // purple-500
          600: "#7c3aed", // purple-600
          700: "#6d28d9", // purple-700
          800: "#5b21b6", // purple-800
          900: "#4c1d95", // purple-900
        },
        // Background Colors
        background: "#1a1d29", // dark-navy
        surface: {
          DEFAULT: "#252936", // elevated-navy
          hover: "#2d3142", // elevated-navy-hover
        },
        // Text Colors
        text: {
          primary: "#f8fafc", // slate-50
          secondary: "#94a3b8", // slate-400
          muted: "#64748b", // slate-500
        },
        // Status Colors
        success: {
          DEFAULT: "#10b981", // emerald-500
          50: "#ecfdf5", // emerald-50
          100: "#d1fae5", // emerald-100
          200: "#a7f3d0", // emerald-200
          300: "#6ee7b7", // emerald-300
          400: "#34d399", // emerald-400
          500: "#10b981", // emerald-500
          600: "#059669", // emerald-600
          700: "#047857", // emerald-700
          800: "#065f46", // emerald-800
          900: "#064e3b", // emerald-900
        },
        warning: {
          DEFAULT: "#fbbf24", // amber-400
          50: "#fffbeb", // amber-50
          100: "#fef3c7", // amber-100
          200: "#fde68a", // amber-200
          300: "#fcd34d", // amber-300
          400: "#fbbf24", // amber-400
          500: "#f59e0b", // amber-500
          600: "#d97706", // amber-600
          700: "#b45309", // amber-700
          800: "#92400e", // amber-800
          900: "#78350f", // amber-900
        },
        error: {
          DEFAULT: "#ef4444", // red-500
          50: "#fef2f2", // red-50
          100: "#fee2e2", // red-100
          200: "#fecaca", // red-200
          300: "#fca5a5", // red-300
          400: "#f87171", // red-400
          500: "#ef4444", // red-500
          600: "#dc2626", // red-600
          700: "#b91c1c", // red-700
          800: "#991b1b", // red-800
          900: "#7f1d1d", // red-900
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        inter: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        jetbrains: ['JetBrains Mono', 'monospace'],
      },
      fontSize: {
        'fluid-xs': 'clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem)',
        'fluid-sm': 'clamp(0.875rem, 0.8rem + 0.375vw, 1rem)',
        'fluid-base': 'clamp(1rem, 0.9rem + 0.5vw, 1.125rem)',
        'fluid-lg': 'clamp(1.125rem, 1rem + 0.625vw, 1.25rem)',
        'fluid-xl': 'clamp(1.25rem, 1.1rem + 0.75vw, 1.5rem)',
        'fluid-2xl': 'clamp(1.5rem, 1.3rem + 1vw, 1.875rem)',
        'fluid-3xl': 'clamp(1.875rem, 1.6rem + 1.375vw, 2.25rem)',
        'fluid-4xl': 'clamp(2.25rem, 1.9rem + 1.75vw, 3rem)',
      },
      boxShadow: {
        'cyber': '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)',
        'cyber-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2)',
        'cyber-xl': '0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)',
        'glow': '0 0 10px rgba(0, 212, 255, 0.3)',
        'glow-lg': '0 0 20px rgba(0, 212, 255, 0.5)',
      },
      borderColor: {
        'cyber': 'rgba(148, 163, 184, 0.2)', // slate-400 with opacity
        'cyber-accent': '#00d4ff', // primary
      },
      animation: {
        'pulse-slow': 'pulse 800ms cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 200ms cubic-bezier(0, 0, 0.2, 1)',
        'slide-up': 'slideUp 300ms cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'threat-pulse': 'pulse 800ms ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
      transitionDuration: {
        '150': '150ms',
        '200': '200ms',
        '300': '300ms',
        '800': '800ms',
      },
      transitionTimingFunction: {
        'out': 'cubic-bezier(0, 0, 0.2, 1)',
        'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
        'bounce': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
      },
      backdropBlur: {
        'cyber': '8px',
      },
      backgroundImage: {
        'cyber-pattern': `
          linear-gradient(45deg, rgba(0, 212, 255, 0.03) 25%, transparent 25%),
          linear-gradient(-45deg, rgba(0, 212, 255, 0.03) 25%, transparent 25%),
          linear-gradient(45deg, transparent 75%, rgba(0, 212, 255, 0.03) 75%),
          linear-gradient(-45deg, transparent 75%, rgba(0, 212, 255, 0.03) 75%)
        `,
      },
      backgroundSize: {
        'cyber-pattern': '20px 20px',
      },
      backgroundPosition: {
        'cyber-pattern': '0 0, 0 10px, 10px -10px, -10px 0px',
      },
    },
  },
  plugins: [
    function({ addUtilities }) {
      const newUtilities = {
        '.bg-cyber-pattern': {
          'background-image': `
            linear-gradient(45deg, rgba(0, 212, 255, 0.03) 25%, transparent 25%),
            linear-gradient(-45deg, rgba(0, 212, 255, 0.03) 25%, transparent 25%),
            linear-gradient(45deg, transparent 75%, rgba(0, 212, 255, 0.03) 75%),
            linear-gradient(-45deg, transparent 75%, rgba(0, 212, 255, 0.03) 75%)
          `,
          'background-size': '20px 20px',
          'background-position': '0 0, 0 10px, 10px -10px, -10px 0px',
        },
        '.threat-pulse': {
          'animation': 'pulse 800ms ease-in-out infinite',
        },
        '.expand-panel': {
          'transition': 'height 300ms cubic-bezier(0.68, -0.55, 0.265, 1.55)',
          'overflow': 'hidden',
        },
        '.tooltip-delay': {
          'transition': 'opacity 150ms cubic-bezier(0, 0, 0.2, 1)',
          'transition-delay': '150ms',
        },
        '.status-glow': {
          'box-shadow': '0 0 10px rgba(0, 212, 255, 0.3)',
          'transition': 'box-shadow 200ms cubic-bezier(0, 0, 0.2, 1)',
        },
        '.status-glow:hover': {
          'box-shadow': '0 0 20px rgba(0, 212, 255, 0.5)',
        },
      }
      addUtilities(newUtilities)
    }
  ],
}