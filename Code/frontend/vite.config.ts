import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Frontend dev server. In Docker Compose, Traefik/host mapping exposes
// this at http://app.localhost (see 12_Deployment.md, docker-compose.yml).
export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
  },
  resolve: {
    alias: {
      "@": "/src",
    },
  },
});
