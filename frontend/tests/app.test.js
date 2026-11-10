import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { settle } from "./helpers/classic-app.js";
import { prepareGlobalDom } from "./helpers/global-app.js";


describe("tela de materias", () => {
  let app;
  let api;
  let confirm;
  let materias;

  beforeEach(async () => {
    vi.resetModules();
    prepareGlobalDom();
    globalThis.AuthUI.registerGuard = vi.fn();
    materias = [{ id: 1, nome: "<Fisica>", descricao: "Mecanica", area_enem_id: 3 }];
    api = vi.fn(async (path, options = {}) => {
      if (path === "/health") return { status: "online" };
      if (path === "/areas-enem") return [{ id: 3, nome: "Ciências da Natureza" }];
      if (path === "/materias" && !options.method) return materias;
      if (path === "/materias" && options.method === "POST") return { id: 2 };
      if (path.startsWith("/materias/") && options.method === "PUT") return { id: 1 };
      if (path.startsWith("/materias/") && options.method === "DELETE") return null;
      throw new Error(`chamada inesperada: ${path}`);
    });
    confirm = vi.fn(() => true);
    globalThis.apiRequest = api;
    window.confirm = confirm;
    app = { document, window, evaluate: (source) => window.eval(source) };
    await import("../js/app.js");
    await settle();
  });

  afterEach(() => delete globalThis.apiRequest);

  it("carrega health, lista e escapa conteudo", () => {
    expect(app.document.querySelector("#api-status").textContent).toContain("online");
    expect(app.document.querySelector("#api-status").classList).toContain("status--online");
    expect(app.document.querySelector(".materia-card h3").textContent).toBe("<Fisica>");
    expect(app.document.querySelector("#materias-lista").innerHTML).not.toContain("<fisica>");
    expect(api).toHaveBeenCalledWith("/health");
    expect(api).toHaveBeenCalledWith("/materias");
  });

  it("edita, cancela, cadastra e atualiza", async () => {
    app.document.querySelector('[data-acao="editar"]').click();
    expect(app.document.querySelector("#materia-id").value).toBe("1");
    expect(app.document.querySelector("#cancelar-button").hidden).toBe(false);
    app.document.querySelector("#cancelar-button").click();
    expect(app.document.querySelector("#materia-id").value).toBe("");

    app.document.querySelector("#nome").value = "Quimica";
    app.document.querySelector("#descricao").value = "Atomos";
    app.document.querySelector("#materia-area-enem-id").value = "3";
    app.document.querySelector("#materia-form").dispatchEvent(
      new app.window.Event("submit", { bubbles: true, cancelable: true }),
    );
    await settle();
    expect(api).toHaveBeenCalledWith(
      "/materias",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ nome: "Quimica", descricao: "Atomos", area_enem_id: 3 }),
      }),
    );
    expect(app.document.querySelector("#mensagem").className).toContain("sucesso");

    app.document.querySelector('[data-acao="editar"]').click();
    app.document.querySelector("#nome").value = "Fisica atualizada";
    app.document.querySelector("#materia-form").dispatchEvent(
      new app.window.Event("submit", { bubbles: true, cancelable: true }),
    );
    await settle();
    expect(api).toHaveBeenCalledWith("/materias/1", expect.objectContaining({ method: "PUT" }));
  });

  it("distingue abrir edicao de alterar campos para a protecao de logout", async () => {
    const dirty = globalThis.AuthUI.registerGuard.mock.calls[0][0];
    expect(dirty()).toBe(false);
    app.document.querySelector('[data-acao="editar"]').click();
    expect(dirty()).toBe(false);
    const name = app.document.querySelector("#nome");
    name.value = "Fisica editada";
    expect(dirty()).toBe(true);
    name.value = materias[0].nome;
    expect(dirty()).toBe(false);
    app.document.querySelector("#descricao").value = "Descricao editada";
    expect(dirty()).toBe(true);
    app.document.querySelector("#cancelar-button").click();
    await settle();
    expect(dirty()).toBe(false);
  });

  it("cancela e confirma exclusao, inclusive durante edicao", async () => {
    confirm.mockReturnValueOnce(false).mockReturnValueOnce(true);
    const deleteButton = app.document.querySelector('[data-acao="excluir"]');
    deleteButton.click();
    expect(api).not.toHaveBeenCalledWith("/materias/1", expect.anything());
    app.document.querySelector('[data-acao="editar"]').click();
    deleteButton.click();
    await settle();
    expect(api).toHaveBeenCalledWith("/materias/1", { method: "DELETE" });
    expect(app.document.querySelector("#materia-id").value).toBe("");

    app.document.querySelector("#materias-lista").click();
    api.mockRejectedValueOnce(new Error("falha excluir"));
    app.document.querySelector('[data-acao="excluir"]').click();
    await settle();
    expect(app.document.querySelector("#mensagem").textContent).toBe("falha excluir");
  });

  it("mostra estados vazio, item ausente e erros", async () => {
    materias = [];
    app.document.querySelector("#recarregar-button").click();
    await settle();
    expect(app.document.querySelector("#lista-status").hidden).toBe(false);

    materias = [{ id: 1, nome: "Fisica", descricao: null }];
    app.document.querySelector("#recarregar-button").click();
    await settle();
    const button = app.document.querySelector('[data-acao="editar"]');
    button.dataset.id = "999";
    button.click();
    expect(app.document.querySelector("#mensagem").className).toContain("erro");

    vi.resetModules();
    prepareGlobalDom();
    api = vi.fn(async (path) => {
      if (path === "/health") throw new Error("falha health");
      if (path === "/areas-enem") return [{ id: 3, nome: "Natureza" }];
      if (path === "/materias") return [];
      throw new Error("chamada inesperada");
    });
    globalThis.apiRequest = api;
    await import("../js/app.js");
    await settle();
    app = { document, window };
    expect(app.document.querySelector("#api-status").classList).toContain("status--offline");

    api.mockRejectedValueOnce(new Error("falha lista"));
    app.document.querySelector("#recarregar-button").click();
    await settle();
    expect(app.document.querySelector("#lista-status").textContent).toBe("falha lista");

    api.mockRejectedValueOnce(new Error("falha salvar"));
    app.document.querySelector("#nome").value = "Nova";
    app.document.querySelector("#materia-area-enem-id").value = "3";
    app.document.querySelector("#materia-form").dispatchEvent(
      new app.window.Event("submit", { bubbles: true, cancelable: true }),
    );
    await settle();
    expect(app.document.querySelector("#mensagem").textContent).toBe("falha salvar");
  });
});
