import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Dev: proxy /api sang FastAPI để cookie phiên cùng origin (SameSite=Lax hoạt động).
export default defineConfig({
  plugins: [react()],
  server: { proxy: { '/api': { target: 'http://127.0.0.1:8000', changeOrigin: false, ws: true } } },
})
