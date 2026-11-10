import fs from "node:fs";
import path from "node:path";
import { afterEach, expect, it, vi } from "vitest";
import { root, settle } from "./helpers/classic-app.js";

const $ = (id) => document.getElementById(id);
const submit = () => $("dash-filtros").dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
const deferred = () => {
  let resolve, reject;
  const promise = new Promise((a, b) => {
    resolve = a;
    reject = b;
  });
  return { promise, resolve, reject };
};
const metric = (n = 4, acertos = 2) => ({
  total_respostas: n,
  acertos,
  erros: n - acertos,
  percentual_acerto: n ? 100 * acertos / n : null,
  estado_amostra: n === 0 ? "sem_dados" : n < 5 ? "amostra_pequena" : "dados_disponiveis",
  base: { pratica: n, simulado: 0 }
});
const diagnostic = (n = 4) => ({
  periodo: { inicio: "2026-10-01", fim: "2026-10-23", timezone: "UTC" },
  calculado_em: "2026-10-24T00:00:00Z",
  limiar_amostra: 5,
  base: { pratica: n, simulado: 0 },
  geral: metric(n, n ? 2 : 0),
  materias: n ? [{ ...metric(n), materia_id: 1, materia_nome: "Matéria <script>" }] : [],
  assuntos: n ? [
    {
      ...metric(n),
      materia_id: 1,
      materia_nome: "Matéria <script>",
      assunto_id: 2,
      assunto_nome: "Álgebra"
    }
  ] : []
});
const dashboard = (n = 4, atividades = true) => ({
  desempenho: diagnostic(n),
  ultimas_atividades: atividades ? [
    {
      tipo: "pratica",
      id: 7,
      titulo: "Prática <script>",
      ocorrido_em: "2026-10-22T10:00:00Z",
      url: "/aluno/questao.html?tentativa_id=7"
    },
    {
      tipo: "simulado",
      id: 9,
      titulo: "Simulado real",
      ocorrido_em: "2026-10-21T10:00:00Z",
      url: "/aluno/simulado.html?tentativa_id=9"
    }] : []
});
const admin = (n = 2) => ({
  calculado_em: "2026-10-24T00:00:00Z",
  catalogo: { materias_ativas: n, assuntos_ativos: n },
  questoes: { rascunhos: n, publicadas: n, arquivadas: 0 },
  simulados: { rascunhos: 0, publicados: n, arquivados: 0 },
  tentativas_simulado_finalizadas: n
});
async function setup(mode = "dashboard", override = () => undefined, auth = {}) {
  globalThis.DesempenhoUI?.destroy();
  vi.resetModules();
  const file = mode === "admin" ? "admin/dashboard.html" : mode === "dashboard" ? "aluno/inicio.html" : "aluno/desempenho.html";
  history.replaceState(null, "", "/" + file);
  const html = fs.readFileSync(path.join(root, "frontend", file), "utf8").replace(/<script\s+src="[^"]+"><\/script>/g, "");
  document.open();
  document.write(html);
  document.close();
  globalThis.AuthUI = {
    user: { id: 1 },
    blocked: false,
    changedAccount: false,
    ready: Promise.resolve(true),
    checkIdentity: vi.fn(async () => true),
    ...auth
  };
  const api = vi.fn(async (r) => {
    const custom = override(r);
    if (custom !== undefined) return custom;
    return mode === "admin" ? admin() : mode === "dashboard" ? dashboard() : diagnostic();
  });
  globalThis.apiRequest = api;
  await import("../js/navigation.js");
  await import("../js/desempenho.js");
  await settle();
  return api;
}
afterEach(() => {
  globalThis.DesempenhoUI?.destroy();
  delete globalThis.DesempenhoUI;
  delete globalThis.AuthUI;
  delete globalThis.apiRequest;
  vi.restoreAllMocks();
});

it("mostra base/período/amostra, grupos e links próprios como texto seguro", async () => {
  await setup();
  expect($("dash-meta").textContent).toContain("UTC");
  expect($("dash-meta").textContent).toContain("4 respostas de práticas");
  expect($("dash-geral").dataset.estado).toBe("amostra_pequena");
  expect($("dash-geral").textContent).toContain("50%");
  expect($("dash-materias").textContent).toContain("Matéria <script>");
  expect($("dash-materias").querySelector("script")).toBeNull();
  expect($("dash-assuntos").textContent).toContain("Álgebra");
  expect($("dash-atividades").querySelectorAll("a")[0].getAttribute("href")).toBe("/aluno/questao.html?tentativa_id=7");
  expect($("dash-atividades").querySelectorAll("a")[1].getAttribute("href")).toBe("/aluno/simulado.html?tentativa_id=9");
  expect($("dash-atividades").textContent).toContain("Atividades não equivalem");
});

it("distingue zero de percentual zero e mantém grupos/atividades vazios", async () => {
  await setup("dashboard", () => dashboard(0, false));
  expect($("dash-geral").textContent).toContain("Indisponível");
  expect($("dash-geral").textContent).not.toContain("0%");
  expect($("dash-materias").querySelector("table")).toBeNull();
  expect($("dash-atividades").textContent).toContain("Nenhuma atividade");
  expect($("dash-geral").dataset.estado).toBe("sem_dados");
});

it("exibe dados disponíveis e percentuais de amostra válida", async () => {
  await setup("desempenho", () => diagnostic(5));
  expect($("dash-geral").dataset.estado).toBe("dados_disponiveis");
  expect($("dash-geral").textContent).toContain("40%");
  expect($("dash-atividades")).toBeNull();
  expect(document.querySelector('a[href="/aluno/inicio.html"]')).not.toBeNull();
});

it("limpa todos os dados ao recarregar e recarrega blocos juntos após erro", async () => {
  let next;
  const api = await setup("dashboard", () => next?.promise);
  next = deferred();
  $("dash-recarregar").click();
  expect($("dash-geral").querySelector("strong")).toBeNull();
  expect($("dash-meta").textContent).toBe("");
  expect($("dash-atividades").querySelector("a")).toBeNull();
  expect([...document.querySelectorAll('[data-dash-block]')].every((b) => b.dataset.estado === "carregando")).toBe(true);
  await settle();
  next.reject(new Error("Falha na consulta"));
  await settle();
  expect([...document.querySelectorAll('[data-dash-block]')].every((b) => b.dataset.estado === "erro")).toBe(true);
  expect(document.querySelector('a[href="/aluno/questoes.html"]')).not.toBeNull();
  next = undefined;
  document.querySelector('[data-dash-retry]').click();
  await settle();
  expect(api).toHaveBeenCalledTimes(3);
  expect($("dash-geral").textContent).toContain("50%");
});

it("aplica período e descarta resposta tardia do período anterior", async () => {
  const pending = deferred();
  const api = await setup("dashboard", (r) => r.includes("inicio=2026-10-01") ? pending.promise : undefined);
  $("inicio").value = "2026-10-01";
  $("fim").value = "2026-10-10";
  submit();
  await settle();
  expect($("dash-geral").querySelector("strong")).toBeNull();
  $("inicio").value = "2026-10-11";
  $("fim").value = "2026-10-20";
  submit();
  await settle();
  expect(api.mock.calls.some(([r]) => r.includes("inicio=2026-10-11&fim=2026-10-20"))).toBe(true);
  pending.resolve(dashboard(0, false));
  await settle();
  expect($("dash-geral").textContent).toContain("50%");
  $("dash-padrao").click();
  await settle();
  expect($("inicio").value).toBe("");
  expect(api.mock.lastCall[0]).toBe("/aluno/dashboard");
});

it("descarta erro tardio de período anterior", async () => {
  const pending = deferred();
  await setup("dashboard", (r) => r.includes("inicio=") ? pending.promise : undefined);
  $("inicio").value = "2026-10-01";
  $("fim").value = "2026-10-10";
  submit();
  await settle();
  $("dash-padrao").click();
  await settle();
  pending.reject(new Error("Erro antigo"));
  await settle();
  expect($("dash-geral").dataset.estado).toBe("amostra_pequena");
  expect(document.body.textContent).not.toContain("Erro antigo");
});

it("troca de conta limpa dados e impede resposta anterior ou nova consulta", async () => {
  const pending = deferred();
  let wait = false;
  const api = await setup("dashboard", () => wait ? pending.promise : undefined);
  wait = true;
  $("dash-recarregar").click();
  await settle();
  AuthUI.changedAccount = true;
  document.dispatchEvent(new Event("auth-identity-changed"));
  pending.resolve(dashboard());
  await settle();
  expect($("dash-geral").querySelector("strong")).toBeNull();
  expect($("dash-meta").textContent).toBe("");
  expect(DesempenhoUI.state.filters).toEqual({});
  const count = api.mock.calls.length;
  $("dash-recarregar").click();
  expect(api).toHaveBeenCalledTimes(count);
});

it("identidade muda depois da consulta e o payload não é exibido", async () => {
  let calls = 0;
  await setup("dashboard", () => undefined, { checkIdentity: vi.fn(async () => ++calls === 1) });
  expect($("dash-geral").querySelector("strong")).toBeNull();
});

it("falha de sessão e perfil não renderiza dados e exige tentativa explícita", async () => {
  const api = await setup("dashboard", () => undefined, { checkIdentity: vi.fn(async () => false) });
  expect(api).not.toHaveBeenCalled();
  await setup("dashboard", () => Promise.reject(new Error("Entre novamente")));
  expect($("dash-geral").dataset.estado).toBe("erro");
  expect($("dash-geral").querySelector("strong")).toBeNull();
});

it("admin mostra somente contagens atuais globais e estado vazio", async () => {
  let empty = false;
  const api = await setup("admin", () => admin(empty ? 0 : 2));
  expect(api).toHaveBeenCalledExactlyOnceWith("/admin/dashboard");
  expect($("dash-filtros")).toBeNull();
  expect($("dash-catalogo").textContent).toContain("Matérias ativas");
  expect($("dash-tentativas").textContent).toContain("sem dados individuais");
  empty = true;
  $("dash-recarregar").click();
  await settle();
  expect($("dash-catalogo").dataset.estado).toBe("sem_dados");
  expect($("dash-tentativas").dataset.estado).toBe("sem_dados");
  expect(document.querySelector('a[href="simulados.html"]')).not.toBeNull();
});

it("falha parcial de renderização também limpa todos os blocos", async () => {
  await setup("dashboard", () => ({ desempenho: diagnostic(), ultimas_atividades: null }));
  expect([...document.querySelectorAll('[data-dash-block]')].every((b) => b.dataset.estado === "erro")).toBe(true);
  expect($("dash-geral").querySelector("strong")).toBeNull();
});
