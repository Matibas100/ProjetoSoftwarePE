import fs from "node:fs";
import { JSDOM } from "jsdom";
import { describe, expect, it, vi } from "vitest";

import {
  adminMatterHtmlPath,
  adminSubjectHtmlPath,
  settle,
} from "./helpers/classic-app.js";
import { prepareAdminGlobalDom } from "./helpers/global-app.js";


const areas = [
  { id: 2, codigo: "ciencias-humanas", nome: "Ciências Humanas", ordem: 2 },
  { id: 3, codigo: "ciencias-natureza", nome: "Ciências da Natureza", ordem: 3 },
];
const matters = [
  { id: 10, nome: "Física", descricao: "Fenômenos", area_enem_id: 3, status: "ativa" },
  { id: 11, nome: "História", descricao: null, area_enem_id: 2, status: "inativa" },
];

function envelope(items) {
  return { itens: items, pagina: 1, por_pagina: 20, total_itens: items.length, total_paginas: 1 };
}

async function setupAdmin(htmlPath, script, apiRequest) {
  vi.resetModules();
  prepareAdminGlobalDom(htmlPath);
  Object.assign(globalThis.AuthUI, { user: { id: 1, perfil: "administrador" }, checkIdentity: async () => true });
  globalThis.apiRequest = apiRequest;
  await import("../js/navigation.js");
  await import("../js/admin-common.js");
  await import(script);
  await settle();
  return { document, window, close: () => {} };
}

describe("contratos das telas administrativas", () => {
  it("mantem shell, filtros, tabela, formulario e modal acessivel", () => {
    for (const path of [adminMatterHtmlPath, adminSubjectHtmlPath]) {
      const dom = new JSDOM(fs.readFileSync(path, "utf8"));
      expect(dom.window.document.querySelector(".sidebar-logo").getAttribute("src")).toContain("logo-plataforma-enem");
      expect(dom.window.document.querySelector("main h1")).not.toBeNull();
      expect(dom.window.document.querySelector("form[role=search]")).not.toBeNull();
      expect(dom.window.document.querySelector("table")).not.toBeNull();
      expect(dom.window.document.querySelector("dialog[aria-labelledby]")).not.toBeNull();
    }
  });

  it("executa utilitarios com texto seguro, estado sujo e modal", async () => {
    const api = vi.fn(async (path) => {
      if (path === "/areas-enem") return areas;
      if (path.startsWith("/admin/materias")) return envelope([]);
      throw new Error(path);
    });
    const app = await setupAdmin(adminMatterHtmlPath, "../js/admin-materias.js", api);
    const ui = app.window.AdminUI;
    const node = ui.element("div", "<img src=x>", "safe");
    expect(node.textContent).toBe("<img src=x>");
    expect(node.children).toHaveLength(0);
    const cell = ui.cell(null);
    expect(cell.textContent).toBe("—");
    const select = app.document.createElement("select");
    ui.fillSelect(select, [{ id: 1, nome: "Um" }], "Todos", 1);
    expect(select.value).toBe("1");
    const message = app.document.querySelector("#materia-mensagem");
    ui.showMessage(message, "Erro", "error");
    expect(message.hidden).toBe(false);
    ui.hideMessage(message);
    expect(message.hidden).toBe(true);
    expect(ui.statusPill("ativa").className).toContain("ativa");
    expect(ui.dateLabel("2026-09-08T12:00:00")).toContain("08");
    expect(ui.element("div").textContent).toBe("");
    expect(ui.adminQuery(2, { status: "ativa" }).toString()).toContain("pagina=2");
    const pageState = {};
    ui.applyPage(pageState, envelope([]));
    expect(pageState.page).toBe(1);
    expect(ui.dateLabel(null)).toBe("—");

    app.document.querySelector("#materia-nome").value = "Alterada";
    app.document.querySelector("#materia-nome").dispatchEvent(new app.window.Event("input", { bubbles: true }));
    expect(app.document.querySelector("#materia-unsaved").hidden).toBe(false);
    const unload = new app.window.Event("beforeunload", { cancelable: true });
    app.window.dispatchEvent(unload);
    expect(unload.defaultPrevented).toBe(true);
    app.document.querySelector("#nova-materia").click();
    await settle();
    expect(app.document.querySelector("#admin-modal").open).toBe(true);
    app.document.querySelector("#admin-modal-cancelar").click();
    await settle();
    expect(app.document.querySelector("#materia-nome").value).toBe("Alterada");
    const escaped = ui.modalController(app.document.querySelector("#admin-modal")).confirm({
      title: "Descartar alterações?", text: "Continuar editando ao pressionar Esc",
    });
    const modalElement = app.document.querySelector("#admin-modal");
    const cancelButton = app.document.querySelector("#admin-modal-cancelar");
    const confirmButton = app.document.querySelector("#admin-modal-confirmar");
    const focused = vi.spyOn(app.document, "activeElement", "get").mockReturnValue(cancelButton);
    const focusConfirm = vi.spyOn(confirmButton, "focus");
    const focusCancel = vi.spyOn(cancelButton, "focus");
    const tab = new app.window.KeyboardEvent("keydown", { key: "Tab", cancelable: true });
    modalElement.dispatchEvent(tab);
    expect(tab.defaultPrevented).toBe(true);
    expect(focusConfirm).toHaveBeenCalledOnce();
    focused.mockReturnValue(confirmButton);
    modalElement.dispatchEvent(new app.window.KeyboardEvent("keydown", { key: "Tab", shiftKey: true, cancelable: true }));
    expect(focusCancel).toHaveBeenCalledOnce();
    const otherKey = new app.window.KeyboardEvent("keydown", { key: "ArrowRight", cancelable: true });
    modalElement.dispatchEvent(otherKey);
    expect(otherKey.defaultPrevented).toBe(false);
    focused.mockRestore();
    app.document.querySelector("#admin-modal").dispatchEvent(new app.window.Event("cancel", { cancelable: true }));
    await expect(escaped).resolves.toBe(false);
    expect(app.document.querySelector("#admin-modal").open).toBe(false);
    expect(app.document.querySelector("#materia-nome").value).toBe("Alterada");
    const confirmation = ui.modalController(app.document.querySelector("#admin-modal")).confirm({
      title: "Confirmar", text: "Continuar",
    });
    app.document.querySelector("#admin-modal-confirmar").click();
    await expect(confirmation).resolves.toBe(true);
    delete globalThis.AdminUI;
    delete globalThis.apiRequest;
  });

  it("apresenta falhas no carregamento inicial das duas telas", async () => {
    const cases = [
      [adminMatterHtmlPath, "../js/admin-materias.js", "#materia-mensagem"],
      [adminSubjectHtmlPath, "../js/admin-assuntos.js", "#assunto-mensagem"],
    ];
    for (const [html, script, selector] of cases) {
      const api = vi.fn(async (path) => {
        if (path === "/areas-enem") throw new Error("Catalogo indisponivel");
        if (path === "/materias?status=todos") return [];
        if (path.startsWith("/admin/")) return envelope([]);
        throw new Error(path);
      });
      const app = await setupAdmin(html, script, api);
      expect(app.document.querySelector(selector).textContent).toContain("indisponivel");
      delete globalThis.AdminUI;
      delete globalThis.apiRequest;
    }
  });

  it("cobre estados, validacao, filtros e exclusao sem vinculos", async () => {
    const subjectItems = [
      { id: 6, nome: "Brasil Colonia", descricao: null, materia_id: 11, materia: matters[1], area_enem: areas[0], status: "inativa", questoes: 0 },
      { id: 7, nome: "Termologia", descricao: "", materia_id: 10, materia: matters[0], area_enem: areas[1], status: "arquivada", questoes: 0 },
      { id: 8, nome: "Ondulatoria", descricao: "Som", materia_id: 10, materia: matters[0], area_enem: areas[1], status: "ativa", questoes: 0 },
    ];
    let failList = false;
    const api = vi.fn(async (path, options = {}) => {
      if (path === "/areas-enem") return areas;
      if (path === "/materias?status=todos") return matters;
      if (path.startsWith("/admin/assuntos")) {
        if (failList) throw new Error("Falha nos assuntos");
        return { ...envelope(subjectItems), pagina: 2, total_paginas: 3 };
      }
      if (path === "/assuntos" && options.method === "POST") return { id: 20 };
      if (path === "/assuntos/6/reativar") return subjectItems[0];
      if (path === "/assuntos/8/impacto-exclusao") return { impacto: { questoes: 0, transferencias: 0 } };
      if (path === "/assuntos/8" && options.method === "DELETE") return null;
      if (path === "/assuntos/6/arquivar") throw new Error("Falha ao arquivar");
      throw new Error(`chamada inesperada ${path}`);
    });
    const app = await setupAdmin(adminSubjectHtmlPath, "../js/admin-assuntos.js", api);

    expect(app.document.querySelector('[data-id="6"][data-action="reativar"]')).not.toBeNull();
    expect(app.document.querySelector('[data-id="7"][data-action="arquivar"]')).toBeNull();
    app.document.querySelector("#assunto-form").dispatchEvent(new app.window.Event("submit", { bubbles: true, cancelable: true }));
    expect(app.document.querySelector("#assunto-mensagem").textContent).toContain("Preencha");
    app.document.querySelector("#assunto-nome").value = "Mecanica";
    app.document.querySelector("#assunto-materia").value = "10";
    app.document.querySelector("#assunto-form").dispatchEvent(new app.window.Event("submit", { bubbles: true, cancelable: true }));
    await settle(); await settle();
    expect(api).toHaveBeenCalledWith("/assuntos", expect.objectContaining({ method: "POST" }));

    app.document.querySelector('[data-id="6"][data-action="reativar"]').click();
    await settle();
    app.document.querySelector("#admin-modal-cancelar").click();
    await settle();
    app.document.querySelector('[data-id="6"][data-action="reativar"]').click();
    await settle();
    app.document.querySelector("#admin-modal-confirmar").click();
    await settle(); await settle();
    expect(api.mock.calls.some(([path]) => path === "/assuntos/6/reativar")).toBe(true);

    app.document.querySelector('[data-id="6"][data-action="arquivar"]').click();
    await settle();
    app.document.querySelector("#admin-modal-confirmar").click();
    await settle(); await settle();
    expect(app.document.querySelector("#assunto-contexto").textContent).toContain("Falha");

    app.document.querySelector('[data-id="8"][data-action="delete"]').click();
    await settle();
    app.document.querySelector("#admin-modal-cancelar").click();
    await settle();
    app.document.querySelector('[data-id="8"][data-action="delete"]').click();
    await settle();
    app.document.querySelector("#admin-modal-confirmar").click();
    await settle(); await settle();
    expect(api).toHaveBeenCalledWith("/assuntos/8", { method: "DELETE" });

    app.document.querySelector("#assuntos-area-filtro").value = "3";
    app.document.querySelector("#assuntos-area-filtro").dispatchEvent(new app.window.Event("change", { bubbles: true }));
    app.document.querySelector("#assuntos-materia-filtro").value = "10";
    app.document.querySelector("#assuntos-materia-filtro").dispatchEvent(new app.window.Event("change", { bubbles: true }));
    app.document.querySelector("#assuntos-status").value = "inativa";
    app.document.querySelector("#assuntos-status").dispatchEvent(new app.window.Event("change", { bubbles: true }));
    app.document.querySelector("#assuntos-anterior").click();
    app.document.querySelector("#assuntos-proxima").click();
    app.document.querySelector("#assuntos-limpar").click();
    failList = true;
    app.document.querySelector("#assuntos-status").value = "arquivada";
    app.document.querySelector("#assuntos-status").dispatchEvent(new app.window.Event("change", { bubbles: true }));
    await settle();
    expect(app.document.querySelector("#assuntos-estado").textContent).toContain("Falha");
    delete globalThis.AdminUI;
    delete globalThis.apiRequest;
  });
});

describe("ADM-CON-001", () => {
  it("lista, filtra, edita, cria e apresenta bloqueio de exclusao", async () => {
    const items = [{
      id: 1, nome: "<Matemática>", descricao: "Raciocínio", area_enem_id: 3,
      area_enem: areas[1], status: "ativa", assuntos: 2, questoes: 7,
      atualizado_em: "2026-09-08T12:00:00",
    }];
    const api = vi.fn(async (path, options = {}) => {
      if (path === "/areas-enem") return areas;
      if (path.startsWith("/api/never")) return null;
      if (path.startsWith("/admin/materias")) return envelope(items);
      if (path === "/materias/1" && !options.method) return items[0];
      if (path === "/materias/1" && options.method === "PUT") {
        const payload = JSON.parse(options.body);
        if (payload.nome === "Duplicada") throw Object.assign(new Error("Nome duplicado"), { status: 409 });
        if (payload.nome === "Falha") throw new Error("Falha ao salvar");
        return items[0];
      }
      if (path === "/materias" && options.method === "POST") return { id: 2 };
      if (path === "/materias/1/impacto-exclusao") {
        return { impacto: { assuntos: 2, questoes: 7, transferencias: 0 } };
      }
      if (path === "/materias/1/inativar") return { ...items[0], status: "inativa" };
      throw new Error(`chamada inesperada ${path}`);
    });
    const app = await setupAdmin(adminMatterHtmlPath, "../js/admin-materias.js", api);
    await settle();
    expect(app.document.querySelector("#materias-corpo").textContent).toContain("<Matemática>");
    expect(app.document.querySelector("#materias-corpo").innerHTML).not.toContain("<matemática>");

    app.document.querySelector("#materias-status").value = "ativa";
    app.document.querySelector("#materias-status").dispatchEvent(new app.window.Event("change", { bubbles: true }));
    await settle();
    expect(api.mock.calls.some(([path]) => path.includes("status=ativa"))).toBe(true);

    app.document.querySelector('[data-action="edit"]').click();
    await settle();
    expect(app.document.querySelector("#materia-id").value).toBe("1");
    app.document.querySelector("#materia-nome").value = "Matemática";
    app.document.querySelector("#materia-form").dispatchEvent(new app.window.Event("submit", { bubbles: true, cancelable: true }));
    await settle();
    expect(api).toHaveBeenCalledWith("/materias/1", expect.objectContaining({ method: "PUT" }));

    app.document.querySelector('[data-action="edit"]').click();
    await settle();
    app.document.querySelector("#materia-nome").value = "Duplicada";
    app.document.querySelector("#materia-form").dispatchEvent(new app.window.Event("submit", { bubbles: true, cancelable: true }));
    await settle();
    expect(app.document.querySelector("#materia-nome-erro").textContent).toContain("duplicado");
    app.document.querySelector("#materia-nome").value = "Falha";
    app.document.querySelector("#materia-form").dispatchEvent(new app.window.Event("submit", { bubbles: true, cancelable: true }));
    await settle();
    expect(app.document.querySelector("#materia-mensagem").textContent).toContain("Falha");

    app.document.querySelector('[data-action="delete"]').click();
    await settle();
    expect(app.document.querySelector("#admin-modal-titulo").textContent).toContain("bloqueada");
    app.document.querySelector("#admin-modal-confirmar").click();
    await settle();
    expect(api.mock.calls.some(([path, options]) => path === "/materias/1" && options?.method === "DELETE")).toBe(false);
    delete globalThis.AdminUI;
    delete globalThis.apiRequest;
  });
  it("cobre estados, criacao, descarte e exclusao sem vinculos", async () => {
    const items = [
      { id: 2, nome: "Historia", descricao: null, area_enem_id: 2, area_enem: areas[0], status: "inativa", assuntos: 0, questoes: 0, atualizado_em: null },
      { id: 3, nome: "Quimica", descricao: "", area_enem_id: 3, area_enem: areas[1], status: "arquivada", assuntos: 0, questoes: 0, atualizado_em: null },
      { id: 4, nome: "Biologia", descricao: "Vida", area_enem_id: 3, area_enem: areas[1], status: "ativa", assuntos: 0, questoes: 0, atualizado_em: null },
    ];
    let failList = false;
    const api = vi.fn(async (path, options = {}) => {
      if (path === "/areas-enem") return areas;
      if (path.startsWith("/admin/materias")) {
        if (failList) throw new Error("Falha na listagem");
        return { ...envelope(items), pagina: 2, total_paginas: 3 };
      }
      if (path === "/materias" && options.method === "POST") return { id: 9 };
      if (path === "/materias/2/reativar") return items[0];
      if (path === "/materias/4/impacto-exclusao") return { impacto: { assuntos: 0, questoes: 0, transferencias: 0 } };
      if (path === "/materias/4" && options.method === "DELETE") return null;
      if (path === "/materias/2/impacto-exclusao") return { impacto: { assuntos: 0, questoes: 0, transferencias: 0 } };
      if (path === "/materias/2/arquivar") throw new Error("Arquivamento indisponivel");
      throw new Error(`chamada inesperada ${path}`);
    });
    const app = await setupAdmin(adminMatterHtmlPath, "../js/admin-materias.js", api);

    expect(app.document.querySelector('[data-id="2"][data-action="reativar"]')).not.toBeNull();
    expect(app.document.querySelector('[data-id="3"][data-action="arquivar"]')).toBeNull();
    app.document.querySelector("#materias-corpo").dispatchEvent(new app.window.Event("click", { bubbles: true }));

    app.document.querySelector("#materia-form").dispatchEvent(new app.window.Event("submit", { bubbles: true, cancelable: true }));
    expect(app.document.querySelector("#materia-mensagem").textContent).toContain("Preencha");
    app.document.querySelector("#materia-nome").value = "Geografia";
    app.document.querySelector("#materia-area").value = "2";
    app.document.querySelector("#materia-form").dispatchEvent(new app.window.Event("submit", { bubbles: true, cancelable: true }));
    await settle(); await settle();
    expect(api).toHaveBeenCalledWith("/materias", expect.objectContaining({ method: "POST" }));

    app.document.querySelector('[data-id="2"][data-action="reativar"]').click();
    await settle();
    app.document.querySelector("#admin-modal-cancelar").click();
    await settle();
    expect(api.mock.calls.some(([path]) => path === "/materias/2/reativar")).toBe(false);
    app.document.querySelector('[data-id="2"][data-action="reativar"]').click();
    await settle();
    app.document.querySelector("#admin-modal-confirmar").click();
    await settle(); await settle();
    expect(api.mock.calls.some(([path]) => path === "/materias/2/reativar")).toBe(true);

    app.document.querySelector('[data-id="2"][data-action="arquivar"]').click();
    await settle();
    app.document.querySelector("#admin-modal-confirmar").click();
    await settle(); await settle();
    expect(app.document.querySelector("#materia-contexto").textContent).toContain("indisponivel");

    app.document.querySelector('[data-id="4"][data-action="delete"]').click();
    await settle();
    app.document.querySelector("#admin-modal-cancelar").click();
    await settle();
    app.document.querySelector('[data-id="4"][data-action="delete"]').click();
    await settle();
    app.document.querySelector("#admin-modal-confirmar").click();
    await settle(); await settle();
    expect(api).toHaveBeenCalledWith("/materias/4", { method: "DELETE" });

    app.document.querySelector("#materias-anterior").click();
    app.document.querySelector("#materias-proxima").click();
    app.document.querySelector("#materias-limpar").click();
    failList = true;
    app.document.querySelector("#materias-status").value = "arquivada";
    app.document.querySelector("#materias-status").dispatchEvent(new app.window.Event("change", { bubbles: true }));
    await settle();
    expect(app.document.querySelector("#materias-estado").textContent).toContain("Falha");
    delete globalThis.AdminUI;
    delete globalThis.apiRequest;
  });
});

describe("ADM-CON-002", () => {
  it("combina filtros, marca resumos e transfere somente apos confirmacao", async () => {
    const subject = {
      id: 5, nome: "Eletricidade", descricao: "Circuitos", materia_id: 10,
      materia: matters[0], area_enem: areas[1], status: "ativa", questoes: 38, resumos: null,
    };
    const preview = {
      assunto_id: 5, materia_origem: matters[0], materia_destino: { ...matters[1], status: "ativa" },
      impacto: { questoes: 38 },
    };
    let transferAttempts = 0;
    const api = vi.fn(async (path, options = {}) => {
      if (path === "/areas-enem") return areas;
      if (path === "/materias?status=todos") return [
        ...matters.map((item) => ({ ...item, status: "ativa" })),
        { id: 12, nome: "Quimica", area_enem_id: 3, status: "ativa" },
      ];
      if (path.startsWith("/admin/assuntos")) return envelope([subject]);
      if (path === "/assuntos/5" && !options.method) return subject;
      if (path.includes("materia_destino_id=12")) throw new Error("Destino indisponivel");
      if (path.startsWith("/assuntos/5/impacto-transferencia")) return preview;
      if (path === "/assuntos/5/transferir" && options.method === "POST") {
        transferAttempts += 1;
        if (transferAttempts === 1) {
          throw Object.assign(new Error("Impacto alterado"), {
            status: 409,
            details: { previa: { ...preview, impacto: { questoes: 39 } } },
          });
        }
        return { ...subject, materia_id: 11 };
      }
      if (path === "/assuntos/5/impacto-exclusao") return { impacto: { questoes: 38, transferencias: 0 } };
      throw new Error(`chamada inesperada ${path}`);
    });
    const app = await setupAdmin(adminSubjectHtmlPath, "../js/admin-assuntos.js", api);
    await settle();
    const summary = app.document.querySelector('td[aria-label*="Resumos"]');
    expect(summary.textContent).toBe("—");

    app.document.querySelector("#assuntos-area-filtro").value = "3";
    app.document.querySelector("#assuntos-area-filtro").dispatchEvent(new app.window.Event("change", { bubbles: true }));
    await settle();
    expect(app.document.querySelector("#assuntos-filtros-aplicados").textContent).toContain("Natureza");

    app.document.querySelector("#assunto-materia").dispatchEvent(new app.window.Event("change", { bubbles: true }));
    await settle();
    app.document.querySelector('[data-action="edit"]').click();
    await settle();
    app.document.querySelector("#assunto-materia").dispatchEvent(new app.window.Event("change", { bubbles: true }));
    await settle();
    app.document.querySelector("#assunto-materia").value = "12";
    app.document.querySelector("#assunto-materia").dispatchEvent(new app.window.Event("change", { bubbles: true }));
    await settle();
    expect(app.document.querySelector("#assunto-impacto").textContent).toContain("indisponivel");
    app.document.querySelector("#assunto-materia").value = "11";
    app.document.querySelector("#assunto-materia").dispatchEvent(new app.window.Event("change", { bubbles: true }));
    await settle();
    expect(app.document.querySelector("#assunto-impacto").textContent).toContain("38");
    app.document.querySelector("#assunto-form").dispatchEvent(new app.window.Event("submit", { bubbles: true, cancelable: true }));
    await settle();
    expect(app.document.querySelector("#admin-modal").open).toBe(true);
    expect(api.mock.calls.some(([path]) => path === "/assuntos/5/transferir")).toBe(false);
    const restoreFocus = vi.spyOn(app.document.querySelector("#assunto-salvar"), "focus");
    app.document.querySelector("#admin-modal").dispatchEvent(new app.window.Event("cancel", { cancelable: true }));
    await settle();
    expect(restoreFocus).toHaveBeenCalledOnce();
    expect(app.document.querySelector("#assunto-materia").value).toBe("11");
    expect(api.mock.calls.some(([path]) => path === "/assuntos/5/transferir")).toBe(false);
    app.document.querySelector("#assunto-form").dispatchEvent(new app.window.Event("submit", { bubbles: true, cancelable: true }));
    await settle();
    app.document.querySelector("#admin-modal-confirmar").click();
    await settle(); await settle();
    expect(app.document.querySelector("#admin-modal").open).toBe(true);
    expect(app.document.querySelector("#admin-modal-texto").textContent).toContain("39");
    app.document.querySelector("#admin-modal-confirmar").click();
    await settle(); await settle();
    expect(api).toHaveBeenCalledWith("/assuntos/5/transferir", expect.objectContaining({ method: "POST" }));
    expect(transferAttempts).toBe(2);

    app.document.querySelector('[data-id="5"][data-action="delete"]').click();
    await settle();
    expect(app.document.querySelector("#admin-modal-titulo").textContent).toContain("bloqueada");
    app.document.querySelector("#admin-modal-confirmar").click();
    await settle();
    delete globalThis.AdminUI;
    delete globalThis.apiRequest;
  });

  it("preserva formulario e aponta duplicidade", async () => {
    const conflict = Object.assign(new Error("Nome duplicado"), { status: 409 });
    const api = vi.fn(async (path, options = {}) => {
      if (path === "/areas-enem") return areas;
      if (path === "/materias?status=todos") return matters;
      if (path.startsWith("/admin/assuntos")) return envelope([]);
      if (path === "/assuntos" && options.method === "POST") throw conflict;
      throw new Error(path);
    });
    const app = await setupAdmin(adminSubjectHtmlPath, "../js/admin-assuntos.js", api);
    await settle();
    app.document.querySelector("#assunto-nome").value = "Duplicado";
    app.document.querySelector("#assunto-materia").value = "10";
    app.document.querySelector("#assunto-form").dispatchEvent(new app.window.Event("submit", { bubbles: true, cancelable: true }));
    await settle();
    expect(app.document.querySelector("#assunto-nome").value).toBe("Duplicado");
    expect(app.document.querySelector("#assunto-nome-erro").textContent).toBe("Nome duplicado");
    delete globalThis.AdminUI;
    delete globalThis.apiRequest;
  });
});
