import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    include: ["frontend/tests/**/*.test.js"],
    restoreMocks: true,
    coverage: {
      provider: "v8",
      all: true,
      include: ["frontend/js/**/*.js"],
      reporter: ["text", "json-summary"],
      reportsDirectory: "coverage-frontend",
      thresholds: {
        lines: 90,
        branches: 85,
      },
    },
  },
});
