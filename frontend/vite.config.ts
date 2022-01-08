import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: process.env.APP_HOST,
    port: parseInt(process.env.APP_PORT),
  },
})
