import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'
import os from 'os'

function readBackendPort(): number {
  try {
    const portFile = path.join(os.homedir(), '.faircheck', 'port')
    const port = parseInt(fs.readFileSync(portFile, 'utf-8').trim(), 10)
    if (!isNaN(port)) {
      console.log(`[vite] FairCheck backend detected on port ${port}`)
      return port
    }
  } catch { /* port file not found */ }
  console.log('[vite] No port file found, defaulting to 8000')
  return 8000
}

const backendPort = readBackendPort()

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: `http://127.0.0.1:${backendPort}`,
        changeOrigin: true,
      },
    },
  },
})
