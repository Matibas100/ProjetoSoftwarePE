import fs from "node:fs";
import path from "node:path";
import { afterEach, expect, it, vi } from "vitest";
import { root, settle } from "./helpers/classic-app.js";

const $ = (id) => document.getElementById(id);
const deferred = () => {
  let resolve, reject;
  const promise = new Promise((a, b) => {
    resolve = a;
    reject = b;
  });
  return { promise, resolve, reject };
};
const aluno = { id: 1, nome: "Aluno", email: "aluno@teste.local", perfil: "aluno" };
const item = (id = 9) => ({
  id,
  posicao: 1,
  assunto_id: 2,
  materia_id: 1,
  estado: "pendente",
  concluido_em: null,
  disponivel_para_pratica: true,
  snapshot: {
    materia_nome: "Matemática <script>",
    assunto_nome: "Álgebra",
    percentual_acerto: 40,
    limiar_amostra: 5,
    justificativa: "2 acertos em 5 respostas nos últimos 30 dias UTC."
  }
});
const plan = (id = 7) => ({
  id,
  geracao: id === 7 ? 1 : 2,
  atual: true,
  periodo: { inicio: "2026-09-25", fim: "2026-10-24" },
  gerado_em: "2026-10-24T10:00:00Z",
  itens: [item()]
});
const response = (plano = plan()) => ({ estado: plano ? "disponivel" : "sem_plano", plano });
async function setup(override = () => undefined) {
  globalThis.PlanoUI?.destroy();
  globalThis.AuthUI?.destroy();
  vi.resetModules();
  history.replaceState(null, "", "/aluno/plano.html");
  document.open();
  document.write(fs.readFileSync(path.join(root, "frontend/aluno/plano.html"), "utf8").replace(/<script\s+src="[^"]+"><\/script>/g, ""));
  document.close();
  HTMLDialogElement.prototype.showModal = function () {
    this.open = true;
  };
  HTMLDialogElement.prototype.close = function () {
    this.open = false;
  };
  globalThis.resetCsrf = vi.fn();
  const api = vi.fn(async (route, options) => {
    const custom = override(route, options);
    if (custom !== undefined) return custom;
    if (route.startsWith("/auth/")) return { usuario: aluno };
    if (route === "/aluno/privacidade") return { plano_liberado: true };
    if (route.includes("/concluir")) return { ...item(), estado: "concluido", concluido_em: "2026-10-24T11:00:00Z" };
    return response();
  });
  globalThis.apiRequest = api;
  await import("../js/navigation.js");
  await import("../js/auth-session.js");
  AuthUI.navigate = vi.fn();
  await import("../js/aluno-plano.js");
  await settle();
  return api;
}
const mutations = (api) => api.mock.calls.filter(([, o]) => o?.method === "POST");
const confirm = async () => {
  $("plano-recalcular").click();
  $("plano-confirmar").click();
  await settle();
};
afterEach(() => {
  globalThis.PlanoUI?.destroy();
  globalThis.AuthUI?.destroy();
  delete globalThis.PlanoUI;
  delete globalThis.AuthUI;
  delete globalThis.apiRequest;
  vi.restoreAllMocks();
});

it("não consulta plano sem consentimento e continua oferecendo prática livre", async () => {
  const api = await setup(r => r === "/aluno/privacidade"?{plano_liberado: false}: undefined);
  expect(api.mock.calls.some(([r]) => r === "/aluno/plano")).toBe(false);
  expect($("plano-privacidade").hidden).toBe(false);
  expect($("plano-lista").children).toHaveLength(0);
  expect($("plano-gerar").hidden).toBe(true);
  expect(PlanoUI.state.pending).toBeNull();
});
it("revogação em outra aba retira plano, intenção e ignora resposta atrasada", async () => {
  let allowed = true;
  const pending = deferred();
  const api = await setup((r, o) => r === "/aluno/privacidade"?{plano_liberado: allowed}: o?.method?pending.promise: undefined);
  await confirm();
  allowed = false;
  window.dispatchEvent(new Event("focus"));
  expect($("plano-lista").children).toHaveLength(0);
  await settle();
  expect(PlanoUI.state.pending).toBeNull();
  pending.resolve(response());
  await settle();
  expect($("plano-lista").children).toHaveLength(0);
  expect($("plano-privacidade").hidden).toBe(false);
  expect(mutations(api)).toHaveLength(1);
});
it("perda de permissão após POST ou erro 403 limpa dados e não reenvia intenção", async () => {
  let allowed = true;
  const api = await setup((r, o) => r === "/aluno/privacidade"?{plano_liberado: allowed}: o?.method?(() => {
    allowed = false;
    return response();
  })(): undefined);
  await confirm();
  expect(PlanoUI.state.plan).toBeNull();
  expect(PlanoUI.state.pending).toBeNull();
  expect(mutations(api)).toHaveLength(1);
  allowed = true;
  await PlanoUI.load();
  api.mockImplementationOnce(async() => ({usuario: aluno}));
  allowed = false;
  document.dispatchEvent(new Event("visibilitychange"));
  await settle();
  expect(PlanoUI.state.plan).toBeNull();
});

it("consulta plano real sem gerar, renderiza texto seguro e liga ao assunto", async () => {
  const api = await setup();
  expect(mutations(api)).toHaveLength(0);
  expect($("plano-lista").textContent).toContain("Matemática <script>");
  expect($("plano-lista").querySelector("script")).toBeNull();
  expect($("plano-lista").textContent).toContain("2 acertos em 5 respostas");
  expect($("plano-meta").textContent).toContain("UTC");
  expect($("plano-lista").querySelector("a").getAttribute("href")).toBe("/aluno/questoes.html?assunto_id=2");
  expect($("plano-recalcular").hidden).toBe(false);
  expect($("plano-gerar").hidden).toBe(true);
  expect(document.querySelector('a[href="/aluno/plano.html"][aria-current="page"]')).not.toBeNull();
  // O menu de todas as páginas é verificado após renderização em navigation.test.js.
});
it("gera com UUID, comunica base insuficiente e permite prática livre", async () => {
  let noBase = true;
  const api = await setup((r, o) => r === "/aluno/plano" ? response(null) : o?.method ? noBase ? {estado: "sem_base_suficiente", plano: null} : response() : undefined);
  expect($("plano-gerar").hidden).toBe(false);
  $("plano-gerar").click();
  await settle();
  expect(JSON.parse(mutations(api)[0][1].body).chave_envio).toMatch(/^[a-f0-9-]{36}$/);
  expect($("plano-status").textContent).toContain("Base insuficiente");
  expect($("plano-lista").children).toHaveLength(0);
  expect(document.querySelector('a[href="/aluno/questoes.html"]')).not.toBeNull();
  noBase = false;
  $("plano-gerar").click();
  await settle();
  expect($("plano-lista").children).toHaveLength(1);
  expect(document.activeElement).toBe($("plano-status"));
});
it("conclui manualmente com confirmação explícita no corpo e conserva data", async () => {
  const api = await setup();
  $("plano-lista").querySelector("button").click();
  await settle();
  expect(mutations(api)[0]).toEqual(["/aluno/plano/itens/9/concluir", {method: "POST", body: '{"confirmar":true}'}]);
  expect($("plano-lista").textContent).toContain("Concluído em");
  expect($("plano-lista").querySelector("button")).toBeNull();
  expect($("plano-status").textContent).toContain("desempenho foram preservados");
});
it("marca indisponibilidade sem perder justificativa ou impedir conclusão manual", async () => {
  const p = plan();
  p.itens[0].disponivel_para_pratica = false;
  await setup((r) => r === "/aluno/plano" ? response(p) : undefined);
  expect($("plano-lista").querySelector("a")).toBeNull();
  expect($("plano-lista").textContent).toContain("Conteúdo indisponível");
  expect($("plano-lista").textContent).toContain("2 acertos em 5 respostas");
  expect($("plano-lista").querySelector("button")).not.toBeNull();
});
it("confirma substituição, cancela por botão/Escape e devolve foco", async () => {
  const api = await setup();
  $("plano-recalcular").click();
  expect($("plano-confirmacao").open).toBe(true);
  expect(document.activeElement).toBe($("plano-cancelar"));
  $("plano-cancelar").click();
  expect($("plano-confirmacao").open).toBe(false);
  expect(document.activeElement).toBe($("plano-recalcular"));
  $("plano-recalcular").click();
  $("plano-confirmacao").dispatchEvent(new Event("cancel", {cancelable: true}));
  expect(mutations(api)).toHaveLength(0);
  await confirm();
  const body = JSON.parse(mutations(api)[0][1].body);
  expect(body).toMatchObject({confirmar: true, plano_atual_id: 7});
  expect(body.chave_envio).toBeDefined();
});
it("preserva plano após recálculo sem base e após falha de rede, sem replay automático", async () => {
  let fault = true;
  const api = await setup((r) => r.endsWith("/recalcular") ? fault ? Promise.reject(new Error("Sem rede")) : {estado: "sem_base_suficiente", plano: plan()} : undefined);
  await confirm();
  expect($("plano-lista").children).toHaveLength(0);
  expect($("plano-status").textContent).toContain("Sem rede");
  const first = mutations(api)[0][1].body;
  await settle();
  expect(mutations(api)).toHaveLength(1);
  fault = false;
  $("plano-retentar").click();
  await settle();
  expect(mutations(api)[1][1].body).toBe(first);
  expect($("plano-status").textContent).toContain("anterior foi preservado");
});
it("bloqueia troca de ação pendente e descarta chave após conflito conhecido", async () => {
  let code = 500;
  const api = await setup((r, o) => o?.method ? Promise.reject(Object.assign(new Error("Falha"), {status: code})) : undefined);
  await confirm();
  await PlanoUI.load();
  $("plano-lista").querySelector("button").click();
  await settle();
  expect(mutations(api)).toHaveLength(1);
  expect($("plano-status").textContent).toContain("ação pendente");
  code = 409;
  $("plano-retentar").click();
  await settle();
  expect(PlanoUI.state.pending).toBeNull();
  await PlanoUI.load();
  $("plano-lista").querySelector("button").click();
  await settle();
  expect(mutations(api)).toHaveLength(3);
});
it("consulta após falha retira snapshots e permite tentar novamente", async () => {
  let fail = false;
  const api = await setup((r) => r === "/aluno/plano" && fail ? Promise.reject(new Error("Consulta falhou")) : undefined);
  fail = true;
  $("plano-recarregar").click();
  await settle();
  expect($("plano-lista").children).toHaveLength(0);
  expect($("plano-status").textContent).toContain("Consulta falhou");
  fail = false;
  $("plano-recarregar").click();
  await settle();
  expect(api.mock.calls.filter(([r]) => r === "/aluno/plano")).toHaveLength(3);
});
it("não duplica mutações durante loading", async () => {
  const pending = deferred();
  const api = await setup((r) => r.endsWith("/concluir") ? pending.promise : undefined);
  $("plano-lista").querySelector("button").click();
  $("plano-lista").querySelector("button").click();
  await settle();
  expect(mutations(api)).toHaveLength(1);
  expect($("plano-conteudo").getAttribute("aria-busy")).toBe("true");
  await PlanoUI.load();
  expect(mutations(api)).toHaveLength(1);
  pending.resolve({...item(), estado: "concluido", concluido_em: "2026-10-24T11:00:00Z"});
  await settle();
  expect(PlanoUI.state.busy).toBe(false);
});
it("recupera mesma sessão sem reenviar a ação e exige novo clique", async () => {
  let fail = true;
  const api = await setup((r) => r.endsWith("/concluir") && fail ? (() => {
    document.dispatchEvent(new CustomEvent("auth-required", {detail: "sessao_invalida"}));
    return Promise.reject(Object.assign(new Error("Sessão expirada"), {status: 401}));
  })() : undefined);
  $("plano-lista").querySelector("button").click();
  await settle();
  expect(AuthUI.blocked).toBe(true);
  expect(PlanoUI.state.plan).toBeNull();
  $("auth-recovery-password").value = "Senha de teste";
  $("auth-recovery-form").dispatchEvent(new Event("submit", {bubbles: true, cancelable: true}));
  await settle();
  expect(AuthUI.blocked).toBe(false);
  expect(mutations(api)).toHaveLength(1);
  expect($("plano-lista").children).toHaveLength(0);
  fail = false;
  $("plano-retentar").click();
  await settle();
  expect(mutations(api)).toHaveLength(2);
});
it("limpa plano/chave na troca de conta e descarta resposta atrasada", async () => {
  const pending = deferred();
  const api = await setup((r) => r.endsWith("/recalcular") ? pending.promise : undefined);
  await confirm();
  AuthUI.changedAccount = true;
  document.dispatchEvent(new Event("auth-identity-changed"));
  expect(PlanoUI.state.pending).toBeNull();
  expect(PlanoUI.state.plan).toBeNull();
  expect($("plano-lista").children).toHaveLength(0);
  pending.resolve(response());
  await settle();
  expect($("plano-lista").children).toHaveLength(0);
  await PlanoUI.load();
  expect(mutations(api)).toHaveLength(1);
});
it("descarta consulta atrasada após mudança de identidade e erro atrasado", async () => {
  let next;
  const api = await setup((r) => r === "/aluno/plano" ? next?.promise : undefined);
  next = deferred();
  $("plano-recarregar").click();
  await settle();
  AuthUI.changedAccount = true;
  document.dispatchEvent(new Event("auth-identity-changed"));
  next.reject(new Error("Atrasado"));
  await settle();
  expect($("plano-status").textContent).toContain("A conta mudou");
  expect($("plano-lista").children).toHaveLength(0);
  expect(mutations(api)).toHaveLength(0);
});
it("replay de plano histórico consulta o atual sem reenviar mutação", async () => {
  let query = 0;
  const api = await setup((r, o) => r.endsWith("/recalcular") ? response({...plan(), atual: false}) : r === "/aluno/plano" ? response(++query === 1?plan(): plan(8)) : undefined);
  await confirm();
  expect(PlanoUI.state.plan.id).toBe(8);
  expect(mutations(api)).toHaveLength(1);
});
it("recupera geração salva com resposta perdida mesmo depois de consultar o plano", async () => {
  let saved = false, fail = true;
  const api = await setup((r, o) => {
    if (r === "/aluno/plano") return response(saved?plan(): null);
    if (o?.method) {
      saved = true;
      return fail ? Promise.reject(new Error("Resposta perdida")) : response();
    }
  });
  $("plano-gerar").click();
  await settle();
  const body = mutations(api)[0][1].body;
  $("plano-recarregar").click();
  await settle();
  expect($("plano-gerar").hidden).toBe(true);
  expect($("plano-retentar").hidden).toBe(false);
  fail = false;
  $("plano-retentar").click();
  await settle();
  expect(mutations(api)[1][1].body).toBe(body);
  expect($("plano-retentar").hidden).toBe(true);
  expect(PlanoUI.state.pending).toBeNull();
});
it("recupera conclusão salva após consulta ocultar o botão de concluir", async () => {
  let saved = false, fail = true;
  const completed = {...item(), estado: "concluido", concluido_em: "2026-10-24T11:00:00Z"};
  const api = await setup((r, o) => {
    if (r === "/aluno/plano") return response({...plan(), itens: [saved?completed: item()]});
    if (o?.method) {
      saved = true;
      return fail ? Promise.reject(new Error("Resposta perdida")) : completed;
    }
  });
  $("plano-lista").querySelector("button").click();
  await settle();
  $("plano-recarregar").click();
  await settle();
  expect($("plano-lista").querySelector("button")).toBeNull();
  expect($("plano-retentar").hidden).toBe(false);
  fail = false;
  $("plano-retentar").click();
  await settle();
  expect(mutations(api)).toHaveLength(2);
  expect(PlanoUI.state.pending).toBeNull();
  expect($("plano-retentar").hidden).toBe(true);
});
it("não inicia consultas quando sessão inicial é inválida", async () => {
  const api = await setup((r) => r === "/auth/sessao" ? Promise.reject(Object.assign(new Error("Sem sessão"), {code: "sessao_invalida"})) : undefined);
  expect(api.mock.calls.some(([r]) => r.startsWith("/aluno/"))).toBe(false);
});
