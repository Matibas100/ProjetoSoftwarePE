import { afterEach, describe, expect, it, vi } from "vitest";
import { adminMatterHtmlPath, adminSubjectHtmlPath, settle } from "./helpers/classic-app.js";
import { prepareAdminGlobalDom } from "./helpers/global-app.js";

const areas = [{ id: 4, nome: "Matemática" }, { id: 3, nome: "Natureza" }];
const matters = [{ id: 10, nome: "Origem", area_enem_id: 4, status: "ativa" }];
const deferred = () => { let resolve, reject; const promise = new Promise((a, b) => { resolve = a; reject = b; }); return { promise, resolve, reject }; };
const flush = async () => { await settle(); await settle(); };
const $ = (id) => document.querySelector(`#${id}`);
const event = (id, type) => $(id).dispatchEvent(new Event(type, { bubbles: true, cancelable: true }));
const resources = [
  { plural: "materias", one: "materia", html: adminMatterHtmlPath, select: "area", link: "area_enem_id", newId: "nova-materia" },
  { plural: "assuntos", one: "assunto", html: adminSubjectHtmlPath, select: "materia", link: "materia_id", newId: "novo-assunto" },
];

async function setup(r, handler = () => undefined) {
  vi.resetModules();
  prepareAdminGlobalDom(r.html);
  Object.assign(AuthUI, { user: { id: 1, perfil: "administrador" }, blocked: false, checkIdentity: vi.fn(async () => true) });
  const detail = (id, extra = {}) => ({ id, nome: `Atual ${id}`, descricao: null, status: "ativa", [r.link]: r.one === "materia" ? 4 : 10, ...extra });
  const items = [1, 2].map((id) => ({ ...detail(id, { nome: `Linha ${id}` }), area_enem: areas[0], materia: matters[0], questoes: 0, assuntos: 0 }));
  const api = vi.fn(async (path, options = {}) => {
    const result = handler(path, options, detail);
    if (result !== undefined) return result;
    if (path === "/areas-enem") return areas;
    if (path === "/materias?status=todos") return matters;
    if (path.startsWith(`/admin/${r.plural}?`)) return { itens: items, pagina: 2, total_paginas: 3, total_itens: 41 };
    const match = path.match(new RegExp(`^/${r.plural}/(\\d+)$`));
    if (match) return detail(Number(match[1]));
    throw new Error(`Chamada inesperada: ${path}`);
  });
  globalThis.apiRequest = api;
  await import("../js/admin-common.js");
  await import(`../js/admin-${r.plural}.js`);
  await flush();
  const edit = async (id = 1) => { document.querySelector(`[data-id="${id}"][data-action="edit"]`).click(); await flush(); };
  return { api, detail, edit };
}

afterEach(() => { delete globalThis.apiRequest; delete globalThis.AdminUI; });

describe.each(resources)("consulta administrativa de $one", (r) => {
  const field = (name) => `${r.one}-${name}`;
  const reads = (api) => api.mock.calls.filter(([path, options]) => new RegExp(`^/${r.plural}/\\d+$`).test(path) && !options.method);

  it("usa detalhe atual, mantém filtros/página e só faz PUT após Salvar", async () => {
    const { api, edit } = await setup(r);
    $(`${r.plural}-busca`).value = "Filtro";
    $(`${r.plural}-status`).value = "inativa";
    await edit();
    expect($(field("nome")).value).toBe("Atual 1");
    expect($(field("descricao")).value).toBe("");
    expect($(field("id")).value).toBe("1");
    expect($(`${r.plural}-busca`).value).toBe("Filtro");
    expect($(`${r.plural}-status`).value).toBe("inativa");
    expect($(`${r.plural}-pagina`).textContent).toContain("2 de 3");
    expect(AuthUI.checkIdentity).toHaveBeenCalledOnce();
    expect(api.mock.calls.some(([, o]) => o?.method)).toBe(false);
    expect($(field("unsaved")).hidden).toBe(true);
    $(field("nome")).value = "Edição explícita";
    event(field("form"), "submit"); await flush();
    expect(api).toHaveBeenCalledWith(`/${r.plural}/1`, expect.objectContaining({ method: "PUT" }));
    expect(api.mock.calls.find(([, o]) => o?.method === "PUT")[1].body).toContain("Edição explícita");
  });

  it.each(["404", "rede", "500", "null", "lista", "id", "nome", "status", "vinculo", "descricao"])("preserva ID, rascunho e guard após falha %s, sem fallback/retry", async (failure) => {
    const { api, edit } = await setup(r, (path, options, detail) => {
      if (path !== `/${r.plural}/2` || options.method) return;
      if (["404", "rede", "500"].includes(failure)) return Promise.reject(new Error(`Falha ${failure}`));
      return Promise.resolve(({ null: null, lista: [], id: detail(99), nome: detail(2, { nome: 7 }),
        status: detail(2, { status: "apagada" }), vinculo: detail(2, { [r.link]: "4" }),
        descricao: detail(2, { descricao: {} }) })[failure]);
    });
    await edit();
    $(field("nome")).value = "Rascunho"; event(field("nome"), "input");
    await edit(2);
    expect(reads(api)).toHaveLength(1);
    $("admin-modal-confirmar").click(); await flush();
    expect($(field("nome")).value).toBe("Rascunho");
    expect($(field("id")).value).toBe("1");
    expect($(field("unsaved")).hidden).toBe(false);
    expect($(field("mensagem")).hidden).toBe(false);
    expect($(field("salvar")).disabled).toBe(false);
    expect(reads(api)).toHaveLength(2);
  });

  it("cancelar descarte não consulta; confirmação antiga não inicia GET", async () => {
    const { api, edit } = await setup(r);
    $(field("nome")).value = "Rascunho"; event(field("nome"), "input");
    await edit(); $("admin-modal-cancelar").click(); await flush();
    expect(reads(api)).toHaveLength(0);
    await edit();
    event(field("nome"), "input");
    $("admin-modal-confirmar").click(); await flush();
    expect(reads(api)).toHaveLength(0);
    expect($(field("nome")).value).toBe("Rascunho");
  });

  it.each([false, true])("ignora resultado/erro antigo fora de ordem (erro=%s)", async (oldError) => {
    const a = deferred(), b = deferred();
    const { api, edit, detail } = await setup(r, (path) => path === `/${r.plural}/1` ? a.promise : path === `/${r.plural}/2` ? b.promise : undefined);
    await edit(1); await edit(2);
    expect(reads(api)[0][1].signal.aborted).toBe(true);
    b.resolve(detail(2)); await flush();
    if (oldError) a.reject(new Error("Erro antigo")); else a.resolve(detail(1));
    await flush();
    expect($(field("id")).value).toBe("2");
    expect($(field("nome")).value).toBe("Atual 2");
    expect($(field("mensagem")).hidden).toBe(true);
    expect($(field("salvar")).disabled).toBe(false);
  });

  it("finally antigo não libera Salvar nem troca anúncio da leitura atual", async () => {
    const a = deferred(), b = deferred();
    const { edit, detail } = await setup(r, path => path === `/${r.plural}/1` ? a.promise : path === `/${r.plural}/2` ? b.promise : undefined);
    await edit(1); await edit(2); a.resolve(detail(1)); await flush();
    expect($(field("salvar")).disabled).toBe(true);
    expect($(field("mensagem")).textContent).toContain("Carregando");
    b.resolve(detail(2)); await flush();
    expect($(field("salvar")).disabled).toBe(false);
  });

  it.each(["input", "change", "novo", "cancelar", "salvar"])("invalida leitura ao executar %s e preserva intenção", async (action) => {
    const pending = deferred();
    const { api, edit, detail } = await setup(r, path => path === `/${r.plural}/1` ? pending.promise : undefined);
    await edit();
    expect($(field("form")).getAttribute("aria-busy")).toBe("true");
    expect($(field("mensagem")).getAttribute("aria-live")).toBe("polite");
    if (["input", "change"].includes(action)) { $(field("nome")).value = "Digitado"; event(field("nome"), action); }
    else if (action === "novo") $(r.newId).click();
    else if (action === "cancelar") $(field("cancelar")).click();
    else event(field("form"), "submit");
    await flush();
    expect(reads(api)[0][1].signal.aborted).toBe(true);
    expect($(field("salvar")).disabled).toBe(false);
    pending.resolve(detail(1)); await flush();
    expect($(field("id")).value).toBe("");
    expect($(field("nome")).value).toBe(["input", "change"].includes(action) ? "Digitado" : "");
    expect(api.mock.calls.some(([, o]) => o?.method)).toBe(false);
  });

  it.each(["auth-required", "auth-identity-changed", "blocked", "changedAccount", "id", "perfil", "check-false", "check-error"])("rejeita detalhe em perda/troca de identidade: %s", async (action) => {
    const pending = deferred();
    const { api, edit, detail } = await setup(r, path => path === `/${r.plural}/1` ? pending.promise : undefined);
    await edit();
    if (action.startsWith("auth-")) document.dispatchEvent(new Event(action));
    if (["blocked", "changedAccount"].includes(action)) AuthUI[action] = true;
    if (action === "id") AuthUI.user.id = 2;
    if (action === "perfil") AuthUI.user.perfil = "aluno";
    if (action === "check-false") AuthUI.checkIdentity.mockResolvedValue(false);
    if (action === "check-error") AuthUI.checkIdentity.mockRejectedValue(new Error("Sessão indisponível"));
    pending.resolve(detail(1)); await flush();
    expect($(field("id")).value).toBe("");
    expect(reads(api)).toHaveLength(1);
    AuthUI.blocked = false; AuthUI.changedAccount = false;
    await flush();
    expect(reads(api)).toHaveLength(1);
  });

  it("confere token e identidade também depois da revalidação assíncrona", async () => {
    const check = deferred();
    const { edit } = await setup(r);
    AuthUI.checkIdentity.mockReturnValue(check.promise);
    await edit(); $(field("nome")).value = "Nova intenção"; event(field("nome"), "input");
    check.resolve(true); await flush();
    expect($(field("nome")).value).toBe("Nova intenção");
    expect($(field("id")).value).toBe("");
  });
});

describe("dependências do detalhe", () => {
  it("Matéria aguarda Áreas sem marcar rascunho como persistido", async () => {
    const pending = deferred(), r = resources[0];
    const { edit } = await setup(r, path => path === "/areas-enem" ? pending.promise : undefined);
    await edit(); expect($("materia-id").value).toBe("");
    $("materia-nome").value = "Rascunho durante opções"; event("materia-nome", "input");
    pending.resolve(areas); await flush();
    expect($("materia-nome").value).toContain("Rascunho");
    expect($("materia-unsaved").hidden).toBe(false);
  });

  it("não aplica Matéria com Área ausente", async () => {
    const { edit } = await setup(resources[0], (path, o, detail) => path === "/materias/1" ? detail(1, { area_enem_id: 99 }) : undefined);
    await edit(); expect($("materia-id").value).toBe("");
    expect($("materia-mensagem").textContent).toContain("Área indisponível");
  });

  it.each(["ativa", "inativa", "arquivada"])("Assunto usa Matéria atual %s criada depois da abertura e Salvar não transfere", async (status) => {
    let calls = 0;
    const r = resources[1];
    const { api, edit } = await setup(r, (path, o, detail) => {
      if (path === "/materias?status=todos") return ++calls === 1 ? matters : [...matters, { id: 20, nome: "Nova corrente", status }, { id: 21, nome: "Outra inativa", status: "inativa" }];
      if (path === "/assuntos/1") return detail(1, { materia_id: 20 });
    });
    $("assuntos-area-filtro").value = "4"; event("assuntos-area-filtro", "change"); await flush();
    $("assuntos-materia-filtro").value = "10";
    await edit();
    expect($("assunto-materia").value).toBe("20");
    expect($("assunto-materia").textContent).toContain("Nova corrente");
    expect($("assunto-materia").textContent).not.toContain("Outra inativa");
    expect($("assuntos-materia-filtro").value).toBe("10");
    event("assunto-form", "submit"); await flush();
    expect(api).toHaveBeenCalledWith("/assuntos/1", expect.objectContaining({ method: "PUT" }));
    expect(api.mock.calls.some(([p]) => p.includes("transfer"))).toBe(false);
  });

  it.each(["rede", "ausente", "invalida"])("falha %s das opções de Assunto não aplica campos parciais", async (failure) => {
    let calls = 0;
    const { edit } = await setup(resources[1], path => {
      if (path !== "/materias?status=todos") return;
      if (++calls === 1) return matters;
      if (failure === "rede") return Promise.reject(new Error("Falha das opções"));
      return failure === "ausente" ? [] : {};
    });
    await edit(); expect($("assunto-id").value).toBe("");
    expect($("assunto-nome").value).toBe("");
    expect($("assunto-materia").value).toBe("");
    expect($("assunto-mensagem").hidden).toBe(false);
    expect($("assunto-salvar").disabled).toBe(false);
  });
});
