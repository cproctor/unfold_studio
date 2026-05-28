import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    manifest: true,
    outDir: 'static/dist',
    rollupOptions: {
      input: {
        app: 'src/main.ts',
        embed: 'src/embed.ts',
      },
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
  },
})
