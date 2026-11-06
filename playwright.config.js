import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./frontend/e2e",
  testMatch: "**/*.spec.js",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  forbidOnly: !!process.env.CI,
  timeout: 180_000,
  globalTimeout: 840_000,
  expect: { timeout: 10_000 },
  reporter: [["list"], ["json", { outputFile: "test-results/e2e.json" }]],
  outputDir: "test-results/browser",
  use: {
    baseURL: process.env.E2E_BASE_URL,
    browserName: "chromium",
    viewport: { width: 1440, height: 1000 },
    trace: "off",
    video: "off",
    screenshot: "off",
  },
});
