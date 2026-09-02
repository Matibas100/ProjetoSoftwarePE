import { spawnSync } from "node:child_process";
import { chmodSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const hook = path.join(root, ".githooks", "pre-push");

try {
  chmodSync(hook, 0o755);
} catch (error) {
  console.error(`Não foi possível tornar o hook executável: ${error.message}`);
  process.exit(1);
}

const result = spawnSync(
  "git",
  ["config", "--local", "core.hooksPath", ".githooks"],
  { cwd: root, stdio: "inherit" },
);

if (result.error) {
  console.error(`Não foi possível executar o Git: ${result.error.message}`);
  process.exit(1);
}

if (result.status !== 0) {
  process.exit(result.status ?? 1);
}

console.log("Hooks Git configurados em .githooks.");
