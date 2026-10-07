import fs from "node:fs";
import { JSDOM } from "jsdom";
import { describe, expect, it, vi } from "vitest";

import {
  createClassicApp,
  declaredScripts,
  htmlPath,
  settle,
} from "./helpers/classic-app.js";


describe("contrato estrutural do HTML", () => {
  it("preserva elementos obrigatorios e ids consumidos pelos scripts", () => {
    const dom = new JSDOM(fs.readFileSync(htmlPath, "utf8"));
    const ids = [
      "api-status", "materia-form", "materia-id", "nome", "descricao",
      "materia-area-enem-id",
      "salvar-button", "cancelar-button", "recarregar-button", "mensagem",
      "lista-status", "materias-lista", "assunto-form", "assunto-id",
      "assunto-nome", "assunto-materia-id", "assunto-descricao",
      "assunto-salvar-button", "assunto-cancelar-button",
      "assuntos-recarregar-button", "assunto-mensagem", "assuntos-lista-status",
      "assuntos-lista", "questao-form", "questao-assunto-id",
      "questao-enunciado", "alternativa-a", "alternativa-b", "alternativa-c",
      "alternativa-d", "alternativa-e", "resposta-correta",
      "questao-dificuldade", "questao-explicacao", "questao-salvar-button",
      "questao-mensagem", "busca-questoes-form", "busca-assunto-id",
      "buscar-questoes-button", "questoes-lista-status", "questoes-lista",
    ];
    for (const id of ids) expect(dom.window.document.getElementById(id), id).not.toBeNull();
  });

  it("mantem os scripts classicos com verificacao de sessao antes da gestao", () => {
    expect(declaredScripts()).toEqual([
      "js/api.js",
      "js/auth-session.js",
      "js/app.js",
      "js/assuntos.js",
      "js/questoes.js",
    ]);
  });

  it("executa os quatro scripts classicos juntos e na ordem declarada", async () => {
    const apiRequest = vi.fn(async (path) => {
      if (path === "/health") return { status: "online" };
      if (path === "/areas-enem") return [];
      if (path === "/materias" || path === "/assuntos") return [];
      throw new Error(`chamada inesperada: ${path}`);
    });
    const app = createClassicApp({ apiRequest });

    try {
      await settle();
      expect(app.executedScripts).toEqual(declaredScripts());
      expect(apiRequest.mock.calls.slice(0, 6).map(([path]) => path)).toEqual([
        "/health",
        "/areas-enem",
        "/materias",
        "/materias",
        "/assuntos",
        "/assuntos",
      ]);
      expect(app.document.querySelector("#api-status").textContent).toContain("online");
    } finally {
      app.close();
    }
  });
});
