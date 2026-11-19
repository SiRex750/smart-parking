import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The Flask API (python -m smart_parking.api) runs on :5000; the dev server proxies /api to it.
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": "http://127.0.0.1:5000" } },
  test: { environment: "jsdom", setupFiles: "./src/setupTests.js" },
});
