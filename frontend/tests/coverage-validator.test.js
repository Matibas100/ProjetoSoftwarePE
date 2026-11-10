import path from "node:path";

import { describe, expect, it } from "vitest";

import { validateCoverage } from "../../scripts/validate_frontend_coverage.mjs";
import { root } from "./helpers/classic-app.js";


function metric(covered = 100, total = 100) {
  return { covered, total, skipped: 0, pct: (covered * 100) / total };
}

function report(overrides = {}) {
  return Object.fromEntries(
    [
      "api.js",
      "app.js",
      "assuntos.js",
      "questoes.js",
      "admin-common.js",
      "admin-materias.js",
      "admin-assuntos.js",
      "admin-questoes.js",
      "admin-usuarios.js",
      "auth-page.js",
      "auth-session.js",
      "aluno-praticas.js",
      "admin-simulados.js",
      "aluno-simulados.js",
      "desempenho.js",
      "aluno-plano.js",
      "aluno-privacidade.js",
      "navigation.js",
      "aluno-tutor.js",
    ].map((name) => {
      const file = path.join(root, "frontend", "js", name);
      return [file, { lines: metric(), branches: metric(), ...overrides[name] }];
    }),
  );
}

describe("validador de cobertura frontend", () => {
  it("aceita cobertura suficiente", () => {
    expect(validateCoverage(report()).errors).toEqual([]);
  });

  it("reprova linhas, branches e arquivo executavel zerado", () => {
    const result = validateCoverage(report({
      "api.js": { lines: metric(0), branches: metric(0) },
      "app.js": { lines: metric(40), branches: metric(40) },
      "assuntos.js": { lines: metric(40), branches: metric(40) },
      "questoes.js": { lines: metric(40), branches: metric(40) },
      "admin-usuarios.js": { lines: metric(40), branches: metric(40) },
    }));
    expect(result.errors.some((error) => error.includes("zero linhas"))).toBe(true);
    expect(result.errors.some((error) => error.includes("linhas") && error.includes("abaixo"))).toBe(true);
    expect(result.errors.some((error) => error.includes("branches") && error.includes("abaixo"))).toBe(true);
  });
});
