import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { settle } from "./helpers/classic-app.js";
import { prepareGlobalDom } from "./helpers/global-app.js";


describe("tela de assuntos", () => {
  let app;
  let api;
  let confirm;
  let materias;
  let assuntos;

  beforeEach(async () => {
    vi.resetModules();
    prepareGlobalDom();
    globalThis.AuthUI.registerGuard = vi.fn();
    materias = [{ id: 1, nome: "Matematica" }];
    assuntos = [{ id: 2, nome: "<Algebra>", descricao: null, materia_id: 1 }];
    api = vi.fn(async (path, options = {}) => {
      if (path === "/materias") return materias;
      if (path === "/assuntos" && !options.method) return assuntos;
      if (path === "/assuntos" && options.method === "POST") return { id: 3 };
      if (path.startsWith("/assuntos/") && options.method === "PUT") return { id: 2 };
      if (path.startsWith("/assuntos/") && options.method === "DELETE") return null;
      throw new Error("chamada inesperada");
    });
    confirm = vi.fn(() => true);
    globalThis.apiRequest = api;
    window.confirm = confirm;
    app = { document, window, evaluate: (source) => window.eval(source) };
    await import("../js/assuntos.js");
    await settle();
  });

  afterEach(() => delete globalThis.apiRequest);

  it("carrega seletores, lista, eventos e escapa conteudo", async () => {
    expect(app.document.querySelector("#assunto-materia-id").options).toHaveLength(2);
    expect(app.document.querySelector(".assunto-card h3").textContent).toBe("<Algebra>");
    expect(app.document.querySelector("#assuntos-lista").innerHTML).not.toContain("<algebra>");
    app.document.querySelector("#assunto-materia-id").value = "1";
    app.document.dispatchEvent(
      new app.window.CustomEvent("materias:atualizadas", {
        detail: [{ id: 1, nome: "Matematica nova" }],
      }),
    );
    await settle();
    expect(app.document.querySelector("#assunto-materia-id").textContent).toContain("Matematica nova");
    expect(app.document.querySelector("#assunto-materia-id").value).toBe("1");
  });

  it("edita, cancela, cadastra e atualiza", async () => {
    app.document.querySelector('[data-acao="editar"]').click();
    expect(app.document.querySelector("#assunto-id").value).toBe("2");
    app.document.querySelector("#assunto-cancelar-button").click();
    expect(app.document.querySelector("#assunto-id").value).toBe("");

    app.document.querySelector("#assunto-nome").value = "Geometria";
    app.document.querySelector("#assunto-materia-id").value = "1";
    app.document.querySelector("#assunto-descricao").value = "Plana";
    app.document.querySelector("#assunto-form").dispatchEvent(
      new app.window.Event("submit", { bubbles: true, cancelable: true }),
    );
    await settle();
    expect(api).toHaveBeenCalledWith("/assuntos", expect.objectContaining({ method: "POST" }));

    app.document.querySelector('[data-acao="editar"]').click();
    app.document.querySelector("#assunto-form").dispatchEvent(
      new app.window.Event("submit", { bubbles: true, cancelable: true }),
    );
    await settle();
    expect(api).toHaveBeenCalledWith("/assuntos/2", expect.objectContaining({ method: "PUT" }));
  });

  it("protege exclusao e trata item ausente", async () => {
    confirm.mockReturnValueOnce(false).mockReturnValueOnce(true);
    const deleteButton = app.document.querySelector('[data-acao="excluir"]');
    deleteButton.click();
    expect(api).not.toHaveBeenCalledWith("/assuntos/2", expect.anything());
    app.document.querySelector('[data-acao="editar"]').click();
    deleteButton.click();
    await settle();
    expect(api).toHaveBeenCalledWith("/assuntos/2", { method: "DELETE" });
    expect(app.document.querySelector("#assunto-id").value).toBe("");

    app.document.querySelector("#assuntos-lista").click();
    api.mockRejectedValueOnce(new Error("falha excluir"));
    app.document.querySelector('[data-acao="excluir"]').click();
    await settle();
    expect(app.document.querySelector("#assunto-mensagem").textContent).toBe("falha excluir");

    const edit = app.document.querySelector('[data-acao="editar"]');
    edit.dataset.id = "999";
    edit.click();
    expect(app.document.querySelector("#assunto-mensagem").className).toContain("erro");
  });

  it("distingue abrir edicao de alterar campos para a protecao de logout", async () => {
    const dirty = globalThis.AuthUI.registerGuard.mock.calls[0][0];
    expect(dirty()).toBe(false);
    app.document.querySelector('[data-acao="editar"]').click();
    expect(dirty()).toBe(false);
    const name = app.document.querySelector("#assunto-nome");
    name.value = "Algebra editada";
    expect(dirty()).toBe(true);
    name.value = assuntos[0].nome;
    expect(dirty()).toBe(false);
    app.document.querySelector("#assunto-descricao").value = "Descricao editada";
    expect(dirty()).toBe(true);
    app.document.querySelector("#assunto-cancelar-button").click();
    await settle();
    expect(dirty()).toBe(false);
  });

  it("mostra estados vazios e falhas", async () => {
    assuntos = [];
    app.document.querySelector("#assuntos-recarregar-button").click();
    await settle();
    expect(app.document.querySelector("#assuntos-lista-status").hidden).toBe(false);

    api.mockRejectedValueOnce(new Error("falha assuntos"));
    app.document.querySelector("#assuntos-recarregar-button").click();
    await settle();
    expect(app.document.querySelector("#assuntos-lista-status").textContent).toBe("falha assuntos");

    api.mockRejectedValueOnce(new Error("falha salvar"));
    app.document.querySelector("#assunto-nome").value = "Novo";
    app.document.querySelector("#assunto-materia-id").value = "1";
    app.document.querySelector("#assunto-form").dispatchEvent(
      new app.window.Event("submit", { bubbles: true, cancelable: true }),
    );
    await settle();
    expect(app.document.querySelector("#assunto-mensagem").textContent).toBe("falha salvar");

    app.document.dispatchEvent(new app.window.CustomEvent("materias:atualizadas", { detail: [] }));
    expect(app.document.querySelector("#assunto-materia-id").disabled).toBe(true);

    vi.resetModules();
    prepareGlobalDom();
    api = vi.fn(async (path) => {
      if (path === "/materias") throw new Error("falha materias");
      if (path === "/assuntos") return [];
      throw new Error("chamada inesperada");
    });
    globalThis.apiRequest = api;
    await import("../js/assuntos.js");
    await settle();
    app = { document, window };
    expect(app.document.querySelector("#assunto-mensagem").textContent).toContain("falha materias");
  });
});
