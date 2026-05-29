import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: '/static/dist/',
  resolve: {
    dedupe: ['@codemirror/state', '@codemirror/view', '@codemirror/language'],
  },
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
