import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { settle } from "./helpers/classic-app.js";
import { prepareGlobalDom } from "./helpers/global-app.js";


describe("tela de questoes", () => {
  let app;
  let api;
  let assuntos;
  let questoes;

  beforeEach(async () => {
    vi.resetModules();
    prepareGlobalDom();
    assuntos = [{ id: 4, nome: "Algebra" }];
    questoes = [];
    api = vi.fn(async (path, options = {}) => {
      if (path === "/assuntos") return assuntos;
      if (path === "/questoes" && options.method === "POST") return { id: 8 };
      if (path.startsWith("/questoes/por-assunto")) return questoes;
      throw new Error("chamada inesperada");
    });
    globalThis.apiRequest = api;
    app = { document, window };
    await import("../js/questoes.js");
    await settle();
  });

  afterEach(() => delete globalThis.apiRequest);

  it("carrega e atualiza os dois seletores", () => {
    expect(app.document.querySelector("#questao-assunto-id").options).toHaveLength(2);
    app.document.querySelector("#questao-assunto-id").value = "4";
    app.document.querySelector("#busca-assunto-id").value = "4";
    app.document.dispatchEvent(
      new app.window.CustomEvent("assuntos:atualizados", {
        detail: [{ id: 4, nome: "Geometria" }],
      }),
    );
    expect(app.document.querySelector("#busca-assunto-id").textContent).toContain("Geometria");
    expect(app.document.querySelector("#questao-assunto-id").value).toBe("4");
    expect(app.document.querySelector("#busca-assunto-id").value).toBe("4");
  });

  it("exige selecao e representa busca vazia, resultado e falha", async () => {
    const form = app.document.querySelector("#busca-questoes-form");
    form.dispatchEvent(new app.window.Event("submit", { bubbles: true, cancelable: true }));
    expect(app.document.querySelector("#questoes-lista-status").textContent).toContain("Selecione");

    app.document.querySelector("#busca-assunto-id").value = "4";
    form.dispatchEvent(new app.window.Event("submit", { bubbles: true, cancelable: true }));
    await settle();
    expect(app.document.querySelector("#questoes-lista-status").hidden).toBe(false);

    questoes = [{
      id: 8, assunto_id: 4, dificuldade: "<media>", enunciado: "<Quanto?>",
      alternativa_a: "<A>", alternativa_b: "B", alternativa_c: "C",
      alternativa_d: "D", alternativa_e: "E", resposta_correta: "A", explicacao: "Porque",
    }];
    form.dispatchEvent(new app.window.Event("submit", { bubbles: true, cancelable: true }));
    await settle();
    expect(app.document.querySelector(".questao-card h3").textContent).toBe("<Quanto?>");
    expect(app.document.querySelector("#questoes-lista").innerHTML).not.toContain("<quanto?>");

    questoes[0].assunto_id = 999;
    form.dispatchEvent(new app.window.Event("submit", { bubbles: true, cancelable: true }));
    await settle();
    expect(app.document.querySelector(".vinculo").textContent).toContain("#999");

    api.mockRejectedValueOnce(new Error("falha busca"));
    form.dispatchEvent(new app.window.Event("submit", { bubbles: true, cancelable: true }));
    await settle();
    expect(app.document.querySelector("#questoes-lista-status").textContent).toBe("falha busca");
  });

  it("cadastra e busca a questao criada", async () => {
    app.document.querySelector("#questao-assunto-id").value = "4";
    app.document.querySelector("#questao-enunciado").value = "Quanto?";
    for (const letter of ["a", "b", "c", "d", "e"]) {
      app.document.querySelector(`#alternativa-${letter}`).value = letter.toUpperCase();
    }
    app.document.querySelector("#resposta-correta").value = "A";
    app.document.querySelector("#questao-dificuldade").value = "facil";
    app.document.querySelector("#questao-explicacao").value = "Porque";
    app.document.querySelector("#questao-form").dispatchEvent(
      new app.window.Event("submit", { bubbles: true, cancelable: true }),
    );
    await settle();
    expect(api).toHaveBeenCalledWith("/questoes", expect.objectContaining({ method: "POST" }));
    expect(api).toHaveBeenCalledWith("/questoes/por-assunto?assunto_id=4");
    expect(app.document.querySelector("#questao-mensagem").className).toContain("sucesso");
  });

  it("trata falhas no carregamento e cadastro e ausencia de assuntos", async () => {
    api.mockRejectedValueOnce(new Error("falha cadastro"));
    app.document.querySelector("#questao-assunto-id").value = "4";
    app.document.querySelector("#questao-form").dispatchEvent(
      new app.window.Event("submit", { bubbles: true, cancelable: true }),
    );
    await settle();
    expect(app.document.querySelector("#questao-mensagem").textContent).toBe("falha cadastro");

    app.document.dispatchEvent(
      new app.window.CustomEvent("assuntos:atualizados", { detail: [] }),
    );
    expect(app.document.querySelector("#questao-assunto-id").disabled).toBe(true);
    expect(app.document.querySelector("#buscar-questoes-button").disabled).toBe(true);

    vi.resetModules();
    prepareGlobalDom();
    api = vi.fn().mockRejectedValue(new Error("falha assuntos"));
    globalThis.apiRequest = api;
    await import("../js/questoes.js");
    await settle();
    app = { document, window };
    expect(app.document.querySelector("#questao-mensagem").textContent).toContain("falha assuntos");
  });
});
