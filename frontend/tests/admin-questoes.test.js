import path from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { root, settle } from "./helpers/classic-app.js";
import { prepareAdminGlobalDom } from "./helpers/global-app.js";

const catalog = {
  "/areas-enem": [{ id: 4, nome: "Matemática" }],
  "/materias?status=todos": [{ id: 2, nome: "Matemática", area_enem_id: 4, status: "ativa" }],
  "/assuntos?status=todos": [{ id: 3, nome: "Geometria", materia_id: 2, status: "ativa" }],
};
const question = {
  id: 7,
  enunciado: "<img src=x onerror=alert(1)>",
  alternativa_a: "A",
  alternativa_b: "B",
  alternativa_c: "C",
  alternativa_d: "D",
  alternativa_e: "E",
  resposta_correta: "A",
  dificuldade: "media",
  assunto_id: 3,
  explicacao: null
};
const detail = () => ({ questao: { ...question }, status: "rascunho", revisao: 1, versao_publicada_id: null, versoes: [] });
const item = () => ({
  ...question,
  status: "rascunho",
  area_enem: { nome: "Matemática" },
  materia: { nome: "Matemática" },
  assunto: { nome: "Geometria" }
});
const envelope = (itens = [item()], pages = 2) => ({ itens, pagina: 1, total_paginas: pages, total_itens: itens.length });
let apps = [];
afterEach(() => {
  apps.forEach((app) => app.close());
  apps = [];
});
async function open(view = "editor", handler = null, query = "?id=7") {
  apps.forEach((app) => app.close());
  apps = [];
  vi.restoreAllMocks();
  vi.resetModules();
  const request = vi.fn(async (url, options) => {
    if (url in catalog) return catalog[url];
    if (handler) return handler(url, options);
    if (url.startsWith("/admin/questoes")) return envelope();
    return detail();
  });
  prepareAdminGlobalDom(path.join(root, "frontend/admin", view === "editor" ? "questao.html" : "questoes.html"));
  history.replaceState(null, "", `/admin/${view === "editor" ? "questao.html" : "questoes.html"}${query}`);
  globalThis.AuthUI = {ready: Promise.resolve(true), blocked: false, changedAccount: false, user: {id: 1}, registerGuard: vi.fn()};
  globalThis.apiRequest = request;
  const listeners = [];
  for(const target of [document, window]) {
    const original = target.addEventListener.bind(target);
    vi.spyOn(target, "addEventListener").mockImplementation((name, callback, options) => {
      listeners.push([target, name, callback, options]);
      original(name, callback, options);
    });
  }
  await import("../js/admin-common.js");
  await import("../js/admin-questoes.js");
  const app = {
    document,
    window,
    close: () => listeners.forEach(([target, name, callback, options]) => target.removeEventListener(name, callback, options))
  };
  apps.push(app);
  app.window.confirm = vi.fn(() => true);
  await settle();
  await settle();
  return { ...app, request, $: (id) => app.document.getElementById(id) };
}
function input(app, id, value) {
  app.$(id).value = value;
  app.$(id).dispatchEvent(new app.window.Event("input", { bubbles: true }));
}
function submit(app, id) {
  app.$(id).dispatchEvent(new app.window.Event("submit", { cancelable: true, bubbles: true }));
}
async function confirm(app, id) {
  app.$(id).click();
  await settle();
  app.$("admin-modal-confirmar").click();
  await settle();
}

describe("gestão de questões", () => {
  it("lista texto seguro, mantém filtros e paginação", async () => {
    const app = await open("lista", null, "?busca=Texto&area_enem_id=4&materia_id=2&assunto_id=3&pagina=1");
    expect(app.$("questoes-corpo").textContent).toContain(question.enunciado);
    expect(app.$("questoes-corpo").querySelector("img")).toBeNull();
    expect(app.$("questoes-corpo").querySelector("a").href).toContain("retorno=");
    expect(app.$("materia_id").value).toBe("2");
    app.$("questoes-proxima").click();
    await settle();
    expect(app.request.mock.calls.at(-1)[0]).toContain("pagina=2");
    app.$("questoes-anterior").click();
    await settle();
    expect(app.request.mock.calls.at(-1)[0]).toContain("pagina=1");
    app.$("questoes-limpar").click();
    await settle();
    expect(app.$("busca").value).toBe("");
    submit(app, "questoes-filtros");
    await settle();
  });

  it("diferencia vazio, filtros vazios e falha sem perder filtros", async () => {
    let fail = false;
    const app = await open("lista", () => {
      if (fail) throw new Error("Rede indisponível");
      return envelope([], 0);
    }, "");
    expect(app.$("questoes-estado").textContent).toContain("primeira questão");
    input(app, "busca", "termo");
    submit(app, "questoes-filtros");
    await settle();
    expect(app.$("questoes-estado").textContent).toContain("filtros");
    fail = true;
    app.$("questoes-recarregar").click();
    await settle();
    expect(app.$("busca").value).toBe("termo");
    expect(app.$("questoes-estado").textContent).toContain("Rede");
    app.window.AuthUI.blocked = true;
    app.$("questoes-recarregar").click();
    await settle();
  });

  it("descarta lista atrasada e respeita troca de identidade", async () => {
    let resolve;
    const app = await open("lista", null, "");
    app.request.mockImplementation((url) => new Promise((r) => {
      resolve = r;
    }));
    app.$("questoes-recarregar").click();
    await settle();
    app.window.AuthUI.changedAccount = true;
    resolve(envelope());
    await settle();
    expect(app.$("questoes-corpo").children.length).toBe(0);
  });

  it("edita, mantém publicação anterior e pede descarte", async () => {
    const app = await open();
    expect(app.$("enunciado").value).toBe(question.enunciado);
    input(app, "enunciado", "Alterado");
    expect(app.$("questao-unsaved").hidden).toBe(false);
    app.window.confirm.mockReturnValue(false);
    app.$("questao-recarregar").click();
    await settle();
    expect(app.$("enunciado").value).toBe("Alterado");
    const navigation = new app.window.MouseEvent("click", { bubbles: true, cancelable: true });
    app.$("questao-voltar").dispatchEvent(navigation);
    expect(navigation.defaultPrevented).toBe(true);
    const unload = new app.window.Event("beforeunload", {cancelable: true});
    app.window.dispatchEvent(unload);
    expect(unload.defaultPrevented).toBe(true);
    app.request.mockImplementation(async () => ({...detail(), questao: {...question, enunciado: "Alterado"}, revisao: 2}));
    submit(app, "questao-form");
    await settle();
    const call = app.request.mock.calls.find(([, o]) => o?.method === "PUT");
    expect(JSON.parse(call[1].body)).toMatchObject({revisao: 1, enunciado: "Alterado"});
    expect(app.$("questao-unsaved").hidden).toBe(true);
    app.window.confirm.mockReturnValue(true);
    app.$("area_enem_id").value = "4";
    app.$("area_enem_id").dispatchEvent(new app.window.Event("change", {bubbles: true}));
    app.$("materia_id").value = "2";
    app.$("materia_id").dispatchEvent(new app.window.Event("change", {bubbles: true}));
  });

  it("cadastra rascunho e recarrega o ID confirmado sem duplicar POST", async () => {
    const app = await open("editor", async (url, options) => options?.method === "POST"?question: detail(), "");
    for(const [field, value] of Object.entries(question)) if(app.$(field)) input(app, field, String(value ?? ""));
    input(app, "area_enem_id", "4");
    input(app, "materia_id", "2");
    submit(app, "questao-form");
    await settle();
    expect(app.request.mock.calls.filter(([, o]) => o?.method === "POST")).toHaveLength(1);
    expect(app.window.location.search).toContain("id=7");
    app.$("questao-recarregar").click();
    await settle();
    expect(app.request.mock.calls.at(-1)[0]).toBe("/questoes/7");
    expect(app.$("questao-unsaved").hidden).toBe(true);
  });

  it("valida conteúdo e motivo e impede publicação de rascunho não salvo", async () => {
    const app = await open();
    app.$("questao-publicar").click();
    await settle();
    expect(app.$("questao-mensagem").textContent).toContain("motivo");
    input(app, "enunciado", "");
    submit(app, "questao-form");
    await settle();
    expect(app.$("questao-mensagem").textContent).toContain("Preencha");
    app.$("questao-publicar").click();
    await settle();
    expect(app.$("questao-mensagem").textContent).toContain("Salve");
  });

  it("publica após confirmação e arquiva preservando versões", async () => {
    const app = await open();
    input(app, "questao-motivo", "Conteúdo revisado");
    app.request.mockImplementation(async (url) => ({
      ...detail(),
      status: url.endsWith("arquivar")?"arquivada": "publicada",
      versao_publicada_id: 12,
      versoes: [{id: 12, numero: 1, estado: "publicada"}]
    }));
    await confirm(app, "questao-publicar");
    expect(app.$("questao-versoes").textContent).toContain("Versão 1");
    expect(app.$("questao-mensagem").textContent).toContain("publicada");
    await confirm(app, "questao-arquivar");
    expect(app.$("questao-acoes").hidden).toBe(true);
    expect(app.$("questao-salvar").disabled).toBe(true);
    expect(app.$("questao-status").textContent).toContain("arquivada");
  });

  it("cancela confirmação e conserva conteúdo em erro de ação", async () => {
    const app = await open();
    input(app, "questao-motivo", "Revisado");
    app.$("questao-publicar").click();
    await settle();
    app.$("admin-modal-cancelar").click();
    await settle();
    expect(app.request.mock.calls.filter(([, o]) => o?.method === "POST")).toHaveLength(0);
    app.request.mockRejectedValue(new Error("Confirme sua senha novamente"));
    await confirm(app, "questao-publicar");
    expect(app.$("enunciado").value).toBe(question.enunciado);
    expect(app.$("questao-mensagem").textContent).toContain("senha");
    expect(app.request.mock.calls.filter(([, o]) => o?.method === "POST")).toHaveLength(1);
  });

  it("preserva edição em falha de sessão sem replay e bloqueia identidade anterior", async () => {
    const app = await open();
    input(app, "enunciado", "Meu rascunho");
    app.request.mockImplementation(async () => {
      app.window.AuthUI.blocked = true;
      throw new Error("Sessão expirada");
    });
    submit(app, "questao-form");
    await settle();
    expect(app.$("enunciado").value).toBe("Meu rascunho");
    app.window.AuthUI.blocked = false;
    expect(app.request.mock.calls.filter(([, o]) => o?.method === "PUT")).toHaveLength(1);
    app.window.AuthUI.changedAccount = true;
    submit(app, "questao-form");
    await settle();
    expect(app.request.mock.calls.filter(([, o]) => o?.method === "PUT")).toHaveLength(1);
  });

  it("ignora gravação atrasada de outra identidade", async () => {
    const app = await open();
    let resolve;
    input(app, "enunciado", "Mudança");
    app.request.mockImplementation(() => new Promise((r) => {
      resolve = r;
    }));
    submit(app, "questao-form");
    await settle();
    app.window.AuthUI.changedAccount = true;
    resolve({...detail(), questao: {...question, enunciado: "Resposta antiga"}});
    await settle();
    expect(app.$("enunciado").value).toBe("Mudança");
  });

  it("erro de leitura mantém formulário bloqueado e ID inválido não faz consulta", async () => {
    const app = await open("editor", () => {
      throw new Error("Questão ausente");
    });
    expect(app.$("questao-carregando").textContent).toContain("ausente");
    expect(app.$("questao-salvar").disabled).toBe(true);
    const invalid = await open("editor", null, "?id=abc&retorno=https%3A%2F%2Findevido.test");
    expect(invalid.request).not.toHaveBeenCalled();
    expect(invalid.$("questao-voltar").href).toContain("/admin/questoes.html");
  });
});
