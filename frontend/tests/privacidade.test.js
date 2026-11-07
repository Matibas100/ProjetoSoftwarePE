import fs from "node:fs";
import path from "node:path";
import { afterEach, expect, it, vi } from "vitest";
import { root, settle } from "./helpers/classic-app.js";

const $ = id => document.getElementById(id);
const user = { id: 1, nome: "Aluno", email: "aluno@teste.local", perfil: "aluno" };
const record = (id = 1, acao = "aceitar") => ({ id, acao, versao: "1.0", documento_sha256: "a".repeat(64), registrado_em: "2026-11-06T12:00:00Z" });
const privacy = (estado = "nao_informado", uso = true) => ({ termos_uso: { versao_vigente: "1.0", documento_url: "/legal/termo-de-uso-v1.html", aceite_vigente: uso, registro: uso ? record() : null },
  consentimento_plano: { versao_vigente: "1.0", documento_url: "/legal/termo-de-consentimento-plano-v1.html", estado,
    registro: estado === "nao_informado" ? null : record(2, ({ recusado: "recusar", revogado: "revogar" })[estado] || "aceitar") }, plano_liberado: estado === "aceito" && uso });
async function setup(override = () => undefined) {
  globalThis.PrivacidadeUI?.destroy?.(); globalThis.AuthUI?.destroy?.(); vi.resetModules();
  document.open(); document.write(fs.readFileSync(path.join(root, "frontend/aluno/privacidade.html"), "utf8").replace(/<script\s+src="[^"]+"><\/script>/g, "")); document.close();
  HTMLDialogElement.prototype.showModal = function () { this.open = true; };
  HTMLDialogElement.prototype.close = function () { this.open = false; };
  globalThis.resetCsrf = vi.fn();
  const api = vi.fn(async (route, options) => {
    const custom = override(route, options); if (custom !== undefined) return custom;
    if (route.startsWith("/auth/")) return { usuario: user };
    return options?.method ? { registro: record(2), privacidade: privacy("aceito") } : privacy();
  });
  globalThis.apiRequest = api;
  await import("../js/navigation.js"); await import("../js/auth-session.js"); AuthUI.navigate = vi.fn();
  await import("../js/aluno-privacidade.js"); await settle(); return api;
}
const mutations = api => api.mock.calls.filter(([,o]) => o?.method === "POST");
afterEach(() => { globalThis.PrivacidadeUI?.destroy(); globalThis.AuthUI?.destroy(); delete globalThis.PrivacidadeUI; delete globalThis.AuthUI; delete globalThis.apiRequest; vi.restoreAllMocks(); });

it("mostra evidências, uso pendente e escolhas opcionais com mesmo estilo", async () => {
  await setup(r => r === "/aluno/privacidade" ? privacy("nao_informado", false) : undefined);
  expect($("privacidade-uso").textContent).toContain("pendente");
  expect($("privacidade-aceitar-uso").hidden).toBe(false);
  expect($("privacidade-aceitar").hidden).toBe(true); expect($("privacidade-recusar").hidden).toBe(false);
  expect($("privacidade-recusar").className).toBe($("privacidade-aceitar").className);
  $("privacidade-aceitar-uso").click(); await settle(); expect($("privacidade-uso").textContent).toContain("SHA-256");
  expect($("privacidade-status").textContent).toContain("registrada");
});
it("aceita explicitamente com revisão do tipo e não gera plano", async () => {
  const api = await setup(); $("privacidade-aceitar").click(); await settle();
  expect(mutations(api)).toHaveLength(1);
  const [url, options] = mutations(api)[0]; expect(url).toBe("/aluno/privacidade/consentimento-plano/aceitar");
  expect(JSON.parse(options.body)).toMatchObject({ revisao: 0, versao: "1.0" });
  expect(JSON.parse(options.body).chave_envio).toMatch(/^[a-f0-9-]{36}$/);
  expect($("privacidade-revogar").hidden).toBe(false); expect($("privacidade-recusar").hidden).toBe(true);
});
it("cancela por botão/Escape sem POST; confirmação negativa elimina e mostra estado atual do replay", async () => {
  const api = await setup(); $("privacidade-recusar").click();
  expect(document.activeElement).toBe($("privacidade-cancelar")); $("privacidade-cancelar").click();
  expect(document.activeElement).toBe($("privacidade-recusar"));
  $("privacidade-recusar").click(); $("privacidade-confirmacao").dispatchEvent(new Event("cancel", { cancelable: true }));
  expect(mutations(api)).toHaveLength(0);
  $("privacidade-recusar").click(); $("privacidade-confirmar").click(); await settle();
  expect(JSON.parse(mutations(api)[0][1].body).confirmar).toBe(true);
  // Replay de negativa pode retornar autorização posterior: exibir estado atual.
  expect($("privacidade-plano").textContent).toContain("Plano liberado");
});
it("permite revogar aceitação antiga e recuperar retry com a mesma chave sem envio automático", async () => {
  let fail = true;
  const api = await setup((r,o) => r === "/aluno/privacidade" ? privacy("desatualizado") : o?.method && fail ? Promise.reject(new Error("Sem rede")) : undefined);
  $("privacidade-revogar").click(); $("privacidade-confirmar").click(); await settle();
  expect($("privacidade-status").textContent).toContain("Sem rede"); expect(mutations(api)).toHaveLength(1);
  const first = mutations(api)[0][1].body; expect(JSON.parse(first).revisao).toBe(2);
  fail = false; $("privacidade-retentar").click(); await settle(); expect(mutations(api)[1][1].body).toBe(first);
});
it("conflito exige consulta e descarta intenção; não confunde revisão de uso e de plano", async () => {
  const api = await setup((r,o) => o?.method ? Promise.reject(Object.assign(new Error("Mudou"), { status: 409 })) : undefined);
  $("privacidade-aceitar").click(); await settle(); expect(PrivacidadeUI.state.pending).toBeNull();
  expect($("privacidade-aceitar").hidden).toBe(true); $("privacidade-consultar").click(); await settle();
  expect($("privacidade-aceitar").hidden).toBe(false); expect(mutations(api)).toHaveLength(1);
});
it("bloqueia ação diferente e duplicada durante erro/loading; permite nova consulta", async () => {
  let resolve;
  const api = await setup((r,o) => o?.method ? new Promise(a => { resolve = a; }) : undefined);
  $("privacidade-aceitar").click(); $("privacidade-aceitar").click(); await settle(); expect(mutations(api)).toHaveLength(1);
  resolve({ registro: record(), privacidade: privacy("aceito") }); await settle();
  expect(PrivacidadeUI.state.busy).toBe(false);
});
it("retira dados e ignora resposta atrasada após troca de conta", async () => {
  let finish;
  const api = await setup(); api.mockImplementationOnce(() => new Promise(r => { finish = r; }));
  $("privacidade-consultar").click(); await settle();
  document.dispatchEvent(new Event("auth-identity-changed")); finish({ usuario: user }); await settle();
  expect($("privacidade-uso").textContent).toBe(""); expect(PrivacidadeUI.state.pending).toBeNull();
  expect($("privacidade-status").textContent).toContain("conta mudou");
});
it("revalida no retorno de outra aba e trata falha da consulta sem evidência residual", async () => {
  let fail = false;
  await setup(r => r === "/aluno/privacidade" && fail ? Promise.reject(new Error("Indisponível")) : undefined);
  expect($("privacidade-uso").textContent).toContain("Registro");
  fail = true; window.dispatchEvent(new Event("focus")); await settle();
  expect($("privacidade-uso").textContent).toBe(""); expect($("privacidade-status").textContent).toContain("Indisponível");
});

it("sessão expirada retira evidências; mesma conta recupera a intenção sem POST automático", async () => {
  let fail = true;
  const api = await setup((r,o) => o?.method && r.includes("consentimento-plano") && fail ? (() => {
    document.dispatchEvent(new CustomEvent("auth-required", { detail: "sessao_invalida" }));
    return Promise.reject(Object.assign(new Error("Expirou"), { status: 401 }));
  })() : undefined);
  $("privacidade-aceitar").click(); await settle();
  const first = mutations(api)[0][1].body;
  expect(AuthUI.blocked).toBe(true); expect($("privacidade-uso").textContent).toBe("");
  $("auth-recovery-password").value = "Senha de teste";
  $("auth-recovery-form").dispatchEvent(new Event("submit", { cancelable: true })); await settle();
  expect(AuthUI.blocked).toBe(false); expect(mutations(api)).toHaveLength(1);
  fail = false; $("privacidade-retentar").click(); await settle();
  expect(mutations(api)).toHaveLength(2); expect(mutations(api)[1][1].body).toBe(first);
});

it("decisão pendente exige recuperar seu resultado antes de outra escolha", async () => {
  const api = await setup((r,o) => o?.method ? Promise.reject(new Error("Sem rede")) : undefined);
  $("privacidade-aceitar").click(); await settle();
  $("privacidade-recusar").click(); $("privacidade-confirmar").click(); await settle();
  expect($("privacidade-status").textContent).toContain("decisão pendente"); expect(mutations(api)).toHaveLength(1);
});

it("oferece o documento vigente atualizado e revoga a versão da aceitação antiga", async () => {
  const data = privacy("desatualizado"); data.consentimento_plano.versao_vigente = "2.0";
  data.consentimento_plano.documento_url = "/legal/termo-de-consentimento-plano-v2.html";
  const api = await setup(r => r === "/aluno/privacidade" ? data : undefined);
  expect($("privacidade-plano-link").getAttribute("href")).toBe(data.consentimento_plano.documento_url);
  $("privacidade-revogar").click(); $("privacidade-confirmar").click(); await settle();
  expect(JSON.parse(mutations(api)[0][1].body).versao).toBe("1.0");
});
