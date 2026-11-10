import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const reportPath = process.argv[2]
? path.resolve(process.argv[2])
: path.join(root, "coverage-frontend", "coverage-summary.json");
const minimumLines = 90;
const minimumBranches = 85;

function productionFiles() {
  return fs
  .readdirSync(path.join(root, "frontend", "js"), { withFileTypes: true })
  .filter((entry) => entry.isFile() && entry.name.endsWith(".js"))
  .map((entry) => path.join(root, "frontend", "js", entry.name))
  .sort();
}

function normalizedKey(value) {
  return path.resolve(value).replaceAll("\\", "/").toLowerCase();
}

export function validateCoverage(report) {
  const files = new Map(
    Object.entries(report)
    .filter(([name]) => name !== "total")
    .map(([name, summary]) => [normalizedKey(name), summary]),
  );
  const errors = [];
  let coveredLines = 0;
  let totalLines = 0;
  let coveredBranches = 0;
  let totalBranches = 0;

  for (const file of productionFiles()) {
    const relative = path.relative(root, file).replaceAll("\\", "/");
    const summary = files.get(normalizedKey(file));
    if (!summary) {
      errors.push(`Arquivo ausente do relatorio: ${relative}`);
      continue;
    }
    totalLines += summary.lines.total;
    coveredLines += summary.lines.covered;
    totalBranches += summary.branches.total;
    coveredBranches += summary.branches.covered;
    if (summary.lines.total > 0 && summary.lines.covered === 0) {
      errors.push(`Arquivo executavel com zero linhas cobertas: ${relative}`);
    }
  }

  const linePercent = totalLines === 0 ? 100 : (coveredLines * 100) / totalLines;
  const branchPercent =
  totalBranches === 0 ? 100 : (coveredBranches * 100) / totalBranches;
  if (linePercent < minimumLines) {
    errors.push(
      `Cobertura agregada de linhas ${linePercent.toFixed(2)}% abaixo de ${minimumLines}%`,
    );
  }
  if (branchPercent < minimumBranches) {
    errors.push(
      `Cobertura agregada de branches ${branchPercent.toFixed(2)}% abaixo de ${minimumBranches}%`,
    );
  }
  return { errors, linePercent, branchPercent, coveredLines, totalLines, coveredBranches, totalBranches };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  if (!fs.existsSync(reportPath)) {
    console.error(`Relatorio nao encontrado: ${reportPath}`);
    process.exitCode = 1;
  } else {
    const result = validateCoverage(JSON.parse(fs.readFileSync(reportPath, "utf8")));
    console.log(
      `Frontend: linhas ${result.linePercent.toFixed(2)}% (${result.coveredLines}/${result.totalLines}); ` +
      `branches ${result.branchPercent.toFixed(2)}% (${result.coveredBranches}/${result.totalBranches}).`,
    );
    for (const error of result.errors) console.error(`ERRO: ${error}`);
    process.exitCode = result.errors.length ? 1 : 0;
  }
}
