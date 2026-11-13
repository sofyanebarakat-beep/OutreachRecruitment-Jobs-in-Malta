import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  root: "seo-app",
  base: "/admin/seo/",
  build: { outDir: "../admin/seo", emptyOutDir: true, sourcemap: false }
});
