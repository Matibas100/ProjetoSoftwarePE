import fs from "node:fs";
import path from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { root, settle } from "./helpers/classic-app.js";

const q = { questao_id: 1, questao_versao_id: 11, enunciado: "Questão <script>", materia: { nome: "Matemática" }, assunto: { nome: "Álgebra" }, alternativa_a: "4", alternativa_b: "5", alternativa_c: "6", alternativa_d: "7", alternativa_e: "8" };
const resultado = { total: 2, respondidas: 1, acertos: 1, erros: 0, em_branco: 1, percentual_acerto: 50, finalizada_em: "2026-10-23T10:00:00Z" };
const tentativa = (done = false, correction = false) => ({ id: 21, titulo: "Prova real", estado: done ? "finalizada" : "em_andamento", revisao: 1, simulado_versao_id: 4,
  itens: [0, 1].map((n) => ({ item_id: n + 1, posicao: n + 1, alternativa: n === 0 ? "A" : null, questao: { ...q }, ...(correction ? { correta: n === 0, gabarito: "A", explicacao: null } : {}) })), ...(done ? { resultado } : {}) });
const simulado = (estado = "rascunho") => ({ id: 10, titulo: "Composição real", estado, revisao: 1, simulado_versao_id: estado === "publicado" ? 4 : null, itens: [{ posicao: 1, questao_versao_id: 11 }] });
const envelope = (itens, pages = 1) => ({ itens, total_itens: itens.length, total_paginas: pages });
const $ = (id) => document.getElementById(id);
const click = (id) => $(id).click();
const submit = (id) => $(id).dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
const input = (id, value) => { $(id).value = value; $(id).dispatchEvent(new Event("input", { bubbles: true })); };
const deferred = () => { let resolve; const promise = new Promise((r) => { resolve = r; }); return { promise, resolve }; };
async function setup(mode, override = () => undefined, search = mode === "aluno-tentativa" ? "?tentativa_id=21" : "") {
  globalThis.SimuladosAlunoUI?.destroy(); globalThis.SimuladosAdminUI?.destroy(); vi.resetModules();
  const admin = mode.startsWith("admin"), editor = mode.endsWith("editor") || mode.endsWith("tentativa");
  const name = editor ? "simulado" : "simulados";
  history.replaceState(null, "", `/${admin ? "admin" : "aluno"}/${name}.html${search}`);
  const html = fs.readFileSync(path.join(root, "frontend", admin ? "admin" : "aluno", name + ".html"), "utf8").replace(/<script\s+src="[^"]+"><\/script>/g, "");
  document.open(); document.write(html); document.close();
  HTMLDialogElement.prototype.showModal = function () { this.open = true; }; HTMLDialogElement.prototype.close = function () { this.open = false; };
  vi.spyOn(window, "confirm").mockReturnValue(true);
  globalThis.AuthUI = { user: { id: 7 }, ready: Promise.resolve(true), blocked: false, changedAccount: false, checkIdentity: vi.fn(async () => true), registerGuard: vi.fn(), navigate: vi.fn() };
  const api = vi.fn(async (r, o) => {
    const custom = override(r, o); if (custom !== undefined) return custom;
    if (r.startsWith("/admin/questoes?")) return envelope([1, 2].map((n) => ({ id: n, versao_publicada_id: n + 10, enunciado: "Conteúdo " + n, assunto: { status: "ativa" }, materia: { status: "ativa" } })));
    if (r === "/admin/simulados/10/publicar") return simulado("publicado");
    if (r === "/admin/simulados/10/arquivar") return simulado("arquivado");
    if (r === "/admin/simulados/10" || r === "/admin/simulados") return simulado();
    if (r.startsWith("/admin/simulados?")) return envelope([simulado()]);
    if (r === "/aluno/tentativas-simulado/21/finalizar") return resultado;
    if (r === "/aluno/tentativas-simulado/21/correcao") return tentativa(true, true);
    if (r.includes("/respostas/")) return { item_id: 1, alternativa: JSON.parse(o.body).alternativa, revisao: 2 };
    if (r === "/aluno/tentativas-simulado/21" || r === "/aluno/tentativas-simulado") return tentativa();
    if (r.startsWith("/aluno/tentativas-simulado?")) return envelope([{ id: 21, titulo: "Prova real", resultado }]);
    return envelope([{ id: 10, titulo: "Prova real", simulado_versao_id: 4, total_questoes: 2, disponivel: true, tentativa_em_andamento_id: null }]);
  });
  globalThis.apiRequest = api;
  if (admin) { await import("../js/admin-common.js"); await import("../js/admin-simulados.js"); }
  else await import("../js/aluno-simulados.js");
  await settle(); return api;
}
afterEach(() => { globalThis.SimuladosAlunoUI?.destroy(); globalThis.SimuladosAdminUI?.destroy(); delete globalThis.SimuladosAlunoUI; delete globalThis.SimuladosAdminUI; delete globalThis.AuthUI; delete globalThis.apiRequest; vi.restoreAllMocks(); });

describe("simulados do aluno", () => {
  it("lista, pagina, inicia e mostra histórico sem correção antecipada", async () => {
    const api = await setup("aluno-lista", (r) => r.startsWith("/aluno/simulados?") ? envelope([{ titulo: "Teste <script>", simulado_versao_id: 4, total_questoes: 2, disponivel: true }], 2) : undefined);
    expect($("sim-lista").textContent).toContain("<script>"); expect($("sim-lista").querySelector("script")).toBeNull();
    click("sim-proxima"); await settle(); click("sim-anterior"); await settle();
    $("sim-lista").querySelector("button").click(); await settle(); expect(AuthUI.navigate).toHaveBeenCalledWith("/aluno/simulado.html?tentativa_id=21");
    $("sim-modo").value = "historico"; submit("sim-filtros"); await settle(); expect($("sim-lista a")).toBeNull();
    expect($("sim-lista").querySelector("a").href).toContain("tentativa_id=21");
    expect(api.mock.calls.some(([r]) => r.includes("pagina=2"))).toBe(true);
  });
  it("mostra retomada, indisponibilidade e lista vazia", async () => {
    let empty = false;
    await setup("aluno-lista", (r) => r.startsWith("/aluno/simulados?") ? envelope(empty ? [] : [{ titulo: "Retomar", total_questoes: 2, disponivel: false, tentativa_em_andamento_id: 21 }, { titulo: "Retirado", total_questoes: 1, disponivel: false }]) : undefined);
    expect($("sim-lista").querySelector("a").textContent).toBe("Continuar tentativa"); expect($("sim-lista").querySelectorAll("button")).toHaveLength(0);
    empty = true; click("sim-recarregar"); await settle(); expect($("sim-status").textContent).toContain("Nenhum");
  });
  it("preserva chave após rede, impede outro início e libera rejeição definitiva", async () => {
    let status = 0;
    const api = await setup("aluno-lista", (r) => {
      if (r.startsWith("/aluno/simulados?")) return envelope([4, 5].map((v) => ({ titulo: "Prova", total_questoes: 2, simulado_versao_id: v, disponivel: true })));
      if (r === "/aluno/tentativas-simulado") return Promise.reject(Object.assign(new Error("Falha"), { status }));
    });
    $("sim-lista").querySelectorAll("button")[0].click(); await settle(); const chave = SimuladosAlunoUI.state.pending.chave_envio;
    $("sim-lista").querySelectorAll("button")[1].click(); await settle(); expect($("sim-status").textContent).toContain("mesmo simulado");
    status = 409; $("sim-lista").querySelectorAll("button")[0].click(); await settle();
    expect(JSON.parse(api.mock.calls.filter(([r]) => r === "/aluno/tentativas-simulado")[1][1].body).chave_envio).toBe(chave);
    expect(SimuladosAlunoUI.state.pending).toBeNull();
  });
  it("salva, altera, limpa e exige salvar antes de finalizar", async () => {
    const api = await setup("aluno-tentativa");
    const radio = document.querySelector('input[value="B"]'); radio.click(); click("sim-finalizar"); expect($("sim-status").textContent).toContain("Salve");
    submit("sim-resposta"); await settle(); expect(SimuladosAlunoUI.state.detail.itens[0].alternativa).toBe("B");
    click("sim-limpar"); await settle(); expect(SimuladosAlunoUI.state.detail.itens[0].alternativa).toBeNull();
    expect(api.mock.calls.filter(([r]) => r.includes("/respostas/")).map(([, o]) => JSON.parse(o.body).alternativa)).toEqual(["B", null]);
    submit("sim-resposta"); expect($("sim-status").textContent).toContain("Selecione");
    expect(document.body.textContent).not.toContain("Gabarito:");
  });
  it("preserva alternativa em falha e recarga e protege navegação", async () => {
    await setup("aluno-tentativa", (r) => r.includes("/respostas/") ? Promise.reject(new Error("Sem rede")) : undefined);
    document.querySelector('input[value="B"]').click(); submit("sim-resposta"); await settle(); expect($("sim-status").textContent).toBe("Sem rede");
    window.confirm.mockReturnValue(false); click("sim-item-proxima"); expect(SimuladosAlunoUI.state.index).toBe(0);
    const e = new Event("beforeunload", { cancelable: true }); window.dispatchEvent(e); expect(e.defaultPrevented).toBe(true);
    const link = document.querySelector('a[href="simulados.html"]'); const event = new MouseEvent("click", { bubbles: true, cancelable: true }); link.dispatchEvent(event); expect(event.defaultPrevented).toBe(true);
    click("sim-recarregar"); await settle(); expect(document.querySelector('input[value="B"]').checked).toBe(true);
    window.confirm.mockReturnValue(true); click("sim-item-proxima"); expect(SimuladosAlunoUI.state.index).toBe(1); click("sim-item-anterior"); expect(SimuladosAlunoUI.state.index).toBe(0);
  });
  it("confirma com brancos, falha sem replay e mostra resultado/correção", async () => {
    let fail = true;
    const api = await setup("aluno-tentativa", (r) => r.endsWith("/finalizar") && fail ? Promise.reject(new Error("Falha ao finalizar")) : undefined);
    click("sim-finalizar"); expect($("sim-confirmar-texto").textContent).toContain("1 Questão(ões) em branco");
    click("sim-confirmar-cancelar"); expect(document.activeElement.id).toBe("sim-finalizar");
    click("sim-finalizar"); click("sim-confirmar"); await settle(); expect($("sim-status").textContent).toBe("Falha ao finalizar");
    expect(api.mock.calls.filter(([r]) => r.endsWith("/finalizar"))).toHaveLength(1);
    fail = false; click("sim-finalizar"); click("sim-confirmar"); await settle(); expect($("sim-totais").textContent).toContain("50%");
    click("sim-correcao"); await settle(); expect($("sim-gabarito").textContent).toContain("Gabarito: A"); expect($("sim-feedback-titulo").textContent).toBe("Resposta correta");
    expect(document.querySelector('input[value="A"]').disabled).toBe(true);
    click("sim-item-proxima"); expect($("sim-feedback-titulo").textContent).toBe("Em branco");
  });
  it("mostra resposta incorreta e explicação preservada", async () => {
    await setup("aluno-tentativa", (r) => { if (r.endsWith("/correcao")) { const d = tentativa(true, true); d.itens[0].correta = false; d.itens[0].explicacao = "Resolução original"; return d; } if (r.endsWith("/21")) return tentativa(true); });
    click("sim-correcao"); await settle(); expect($("sim-feedback-titulo").textContent).toContain("incorreta"); expect($("sim-explicacao").textContent).toBe("Resolução original");
  });
  it("descarta consulta atrasada ao trocar identidade e não envia bloqueado", async () => {
    const pending = deferred(); const api = await setup("aluno-lista", (r) => r.startsWith("/aluno/simulados?") ? pending.promise : undefined);
    AuthUI.changedAccount = true; document.dispatchEvent(new Event("auth-identity-changed")); pending.resolve(envelope([{ titulo: "Conta anterior" }])); await settle();
    expect($("sim-lista").textContent).not.toContain("Conta anterior"); click("sim-recarregar"); expect(api.mock.calls.filter(([r]) => r.startsWith("/aluno/simulados?"))).toHaveLength(1);
  });
  it("limpa detalhe e alternativa na mudança de conta", async () => {
    await setup("aluno-tentativa"); document.querySelector('input[value="B"]').click(); AuthUI.changedAccount = true; document.dispatchEvent(new Event("auth-identity-changed"));
    expect(SimuladosAlunoUI.state.draft).toBeUndefined(); expect($("sim-conteudo").textContent).toBe("");
  });
  it("recupera erro de leitura e rejeita ID inválido", async () => {
    let fail = true;
    await setup("aluno-lista", (r) => r.startsWith("/aluno/simulados?") && fail ? Promise.reject(new Error("Sem rede")) : undefined);
    expect($("sim-status").textContent).toBe("Sem rede"); fail = false; click("sim-recarregar"); await settle(); expect($("sim-lista").children.length).toBe(1);
    await setup("aluno-tentativa", () => undefined, "?tentativa_id=x"); expect($("sim-status").textContent).toContain("inválido");
  });
});

describe("gestão de simulados", () => {
  it("lista e filtra, pagina e distingue vazio/falha", async () => {
    let empty = false, fail = false;
    const api = await setup("admin-lista", (r) => r.startsWith("/admin/simulados?") ? fail ? Promise.reject(new Error("Falha")) : envelope(empty ? [] : [simulado()], 2) : undefined);
    expect($("sim-lista").textContent).toContain("Composição real"); click("sim-proxima"); await settle(); click("sim-anterior"); await settle();
    $("status").value = "publicado"; submit("sim-filtros"); await settle(); expect(api.mock.calls.some(([r]) => r.includes("status=publicado"))).toBe(true);
    empty = true; click("sim-recarregar"); await settle(); expect($("sim-status").textContent).toContain("Nenhum");
    fail = true; click("sim-recarregar"); await settle(); expect($("sim-status").textContent).toBe("Falha");
  });
  it("seleciona sem repetir, ordena, remove, salva e publica após confirmação", async () => {
    const api = await setup("admin-editor");
    submit("sim-form"); expect($("sim-status").textContent).toContain("ao menos");
    input("titulo", "Minha prova"); $("sim-questoes").querySelectorAll("button")[0].click(); $("sim-questoes").querySelectorAll("button")[0].click(); expect($("sim-status").textContent).toContain("sem repetição");
    $("sim-questoes").querySelectorAll("button")[1].click(); $("sim-selecao").querySelectorAll("li")[1].querySelector("button").click(); expect(SimuladosAdminUI.state.selected[0].questao_versao_id).toBe(12);
    $("sim-selecao").querySelectorAll("li")[0].querySelectorAll("button")[1].click();
    $("sim-selecao").querySelectorAll("li")[1].querySelectorAll("button")[2].click();
    submit("sim-form"); await settle(); expect(api.mock.calls.some(([r, o]) => r === "/admin/simulados" && o.method === "POST")).toBe(true);
    expect($("sim-selecao").querySelector("button").disabled).toBe(true);
    click("sim-publicar"); expect($("sim-status").textContent).toContain("motivo"); input("sim-motivo", "Revisado manualmente");
    click("sim-publicar"); await settle(); expect($("admin-modal").open).toBe(true); click("admin-modal-confirmar"); await settle(); expect($("sim-status").textContent).toContain("publicado"); expect($("sim-salvar").disabled).toBe(true);
    click("sim-arquivar"); await settle(); click("admin-modal-confirmar"); await settle(); expect($("sim-status").textContent).toContain("arquivado");
  });
  it("edita revisão existente e protege recarga/saída", async () => {
    const api = await setup("admin-editor", () => undefined, "?id=10"); input("titulo", "Mudou");
    click("sim-publicar"); expect($("sim-status").textContent).toContain("Salve");
    window.confirm.mockReturnValue(false); click("sim-recarregar"); await settle(); expect($("titulo").value).toBe("Mudou");
    const e = new Event("beforeunload", { cancelable: true }); window.dispatchEvent(e); expect(e.defaultPrevented).toBe(true);
    const a = document.querySelector('a[href="simulados.html"]'); const event = new MouseEvent("click", { bubbles: true, cancelable: true }); a.dispatchEvent(event); expect(event.defaultPrevented).toBe(true);
    submit("sim-form"); await settle(); const call = api.mock.calls.find(([r, o]) => r === "/admin/simulados/10" && o?.method === "PUT"); expect(JSON.parse(call[1].body).revisao).toBe(1);
    window.confirm.mockReturnValue(true); click("sim-recarregar"); await settle(); expect($("sim-revisao").textContent).toContain("revisão 1");
  });
  it("preserva seleção e motivo ao falhar gravação/publicação sem replay", async () => {
    let fail = true;
    const api = await setup("admin-editor", (r, o) => o?.method && fail ? Promise.reject(new Error("Recupere a sessão")) : undefined, "?id=10");
    input("titulo", "Rascunho local"); submit("sim-form"); await settle(); expect($("titulo").value).toBe("Rascunho local"); expect(SimuladosAdminUI.state.selected).toHaveLength(1);
    fail = false; submit("sim-form"); await settle(); input("sim-motivo", "Revisado");
    click("sim-publicar"); await settle(); click("admin-modal-cancelar"); await settle(); expect(api.mock.calls.some(([r]) => r.endsWith("/publicar"))).toBe(false);
    fail = true; click("sim-publicar"); await settle(); click("admin-modal-confirmar"); await settle(); expect($("sim-motivo").value).toBe("Revisado"); expect($("sim-status").textContent).toBe("Recupere a sessão");
  });
  it("busca e pagina banco sem perder composição e trata falha/vazio", async () => {
    let fail = false, empty = false;
    const api = await setup("admin-editor", (r) => r.startsWith("/admin/questoes?") ? fail ? Promise.reject(new Error("Falha no banco")) : empty ? envelope([]) : envelope([{ id: 1, versao_publicada_id: 11, enunciado: "Texto", assunto: { status: "ativa" }, materia: { status: "ativa" } }], 2) : undefined);
    $("sim-questoes").querySelector("button").click(); click("sim-banco-proxima"); await settle(); click("sim-banco-anterior"); await settle();
    input("busca", "Álgebra"); submit("sim-busca-form"); await settle(); expect(api.mock.calls.some(([r]) => r.includes(encodeURIComponent("Álgebra")))).toBe(true); expect(SimuladosAdminUI.state.selected).toHaveLength(1);
    empty = true; submit("sim-busca-form"); await settle(); expect($("sim-questoes").textContent).toContain("Nenhuma");
    fail = true; submit("sim-busca-form"); await settle(); expect($("sim-status").textContent).toBe("Falha no banco");
  });
  it("descarta dados atrasados e limpa conta anterior", async () => {
    const pending = deferred(); await setup("admin-editor", (r) => r.startsWith("/admin/questoes?") ? pending.promise : undefined);
    AuthUI.changedAccount = true; document.dispatchEvent(new Event("auth-identity-changed")); pending.resolve(envelope([])); await settle(); expect($("sim-selecao").textContent).toBe(""); expect(SimuladosAdminUI.state.ready).toBe(false);
    await setup("admin-editor", () => undefined, "?id=10"); document.dispatchEvent(new Event("auth-identity-changed")); expect($("titulo").value).toBe("");
  });
  it("rejeita identificador inválido e falha na carga", async () => {
    await setup("admin-editor", () => undefined, "?id=abc"); expect($("sim-status").textContent).toContain("inválido");
    await setup("admin-editor", (r) => r.startsWith("/admin/questoes?") ? Promise.reject(new Error("Banco indisponível")) : undefined); expect($("sim-status").textContent).toBe("Banco indisponível"); expect($("sim-salvar").disabled).toBe(true);
  });
});
