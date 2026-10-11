import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Anything the browser sends to /api/... is forwarded to the Flask server.
      // This is why we don't need CORS: the browser thinks it's talking to one server.
      // We write 127.0.0.1 (not "localhost") on purpose: on some Windows setups
      // "localhost" resolves to IPv6 (::1) while Flask listens on IPv4, which breaks.
      "/api": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
        timeout: 180000,       // the agent can take a while: allow up to 3 minutes
        proxyTimeout: 180000,
      },
    },
  },
});