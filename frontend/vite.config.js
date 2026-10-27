import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Prefer VITE_API_BASE_URL in client; proxy helps local same-origin /api calls
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/health': { target: 'http://localhost:8000', changeOrigin: true },
      '/diagnose': { target: 'http://localhost:8000', changeOrigin: true },
      '/prices': { target: 'http://localhost:8000', changeOrigin: true },
      '/eligibility': { target: 'http://localhost:8000', changeOrigin: true },
      '/checklist': { target: 'http://localhost:8000', changeOrigin: true },
      '/chat': { target: 'http://localhost:8000', changeOrigin: true },
      '/weather': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
