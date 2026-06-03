import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/  +  https://vitest.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: true, // listen on 0.0.0.0 — reachable from the LAN / dev container
    port: 5173,
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/tests/setup.js',
    css: true,
    passWithNoTests: true,
    // Pin the API base in tests so MSW handlers match regardless of .env
    // (dev/.env points at localhost:8000; tests mock goatfarm.local).
    env: {
      VITE_API_BASE_URL: 'http://goatfarm.local/api/v1',
    },
  },
})
