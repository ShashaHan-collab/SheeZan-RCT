
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  base: "./",
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://127.0.0.1:9214", changeOrigin: true },
      "/ws": { target: "ws://127.0.0.1:9214", ws: true },
      "/ws2": { target: "ws://127.0.0.1:9214", ws: true },
    },
  },
  build: { outDir: "dist", assetsDir: "assets" },
});
