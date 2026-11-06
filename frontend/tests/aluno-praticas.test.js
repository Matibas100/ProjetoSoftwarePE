import fs from "node:fs";
import path from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { root, settle } from "./helpers/classic-app.js";

const aluno = { id: 7, nome: "Estudante", email: "aluno@teste.local", perfil: "aluno" };
const questao = { questao_id: 12, questao_versao_id: 14, enunciado: "Quanto é 2 + 2? <script>", dificuldade: "media",
  materia: { id: 1, nome: "Matemática" }, assunto: { id: 2, nome: "Álgebra" },
  alternativa_a: "4", alternativa_b: "5", alternativa_c: "6", alternativa_d: "7", alternativa_e: "8" };
const envelope = (itens = [questao], pages = 1) => ({ itens, pagina: 1, por_pagina: 20, total_itens: itens.length, total_paginas: pages });
const detalhe = (respondida = false, correta = true, explicacao = null) => ({ id: 21, estado: respondida ? "respondida" : "em_andamento", questao: { ...questao },
  ...(respondida ? { resposta_escolhida: correta ? "A" : "B", correta, gabarito: "A", explicacao, respondida_em: "2026-10-20T12:00:00Z", materia: questao.materia, assunto: questao.assunto } : {}) });
const submit = (id) => document.getElementById(id).dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
const click = (id) => document.getElementById(id).click();

async function setup(mode = "questoes", override = () => undefined, search = "?tentativa_id=21") {
  globalThis.PraticasUI?.destroy?.(); globalThis.AuthUI?.destroy?.(); vi.resetModules();
  history.replaceState(null, "", `/aluno/${mode}.html${search}`);
  const html = fs.readFileSync(path.join(root, "frontend/aluno", `${mode}.html`), "utf8").replace(/<script\s+src="[^"]+"><\/script>/g, "");
  document.open(); document.write(html); document.close();
  HTMLDialogElement.prototype.showModal = function () { this.open = true; };
  HTMLDialogElement.prototype.close = function () { this.open = false; };
  globalThis.resetCsrf = vi.fn();
  vi.stubGlobal("localStorage", { setItem: vi.fn(), getItem: vi.fn().mockReturnValue(null) });
  const api = vi.fn(async (route, options) => {
    const result = override(route, options);
    if (result !== undefined) return result;
    if (route === "/auth/sessao") return { usuario: aluno };
    if (route === "/materias") return [{ id: 1, nome: "Matemática" }, { id: 3, nome: "História" }];
    if (route === "/assuntos") return [{ id: 2, nome: "Álgebra", materia_id: 1 }];
    if (route === "/aluno/praticas/21/resposta") return detalhe(true);
    if (route === "/aluno/praticas/21") return detalhe();
    if (route === "/aluno/praticas") return detalhe();
    return envelope();
  });
  globalThis.apiRequest = api;
  await import("../js/navigation.js"); await import("../js/auth-session.js");
  AuthUI.navigate = vi.fn();
  await import("../js/aluno-praticas.js");
  await settle();
  return api;
}

afterEach(() => { globalThis.PraticasUI?.destroy(); globalThis.AuthUI?.destroy(); delete globalThis.PraticasUI; delete globalThis.AuthUI; delete globalThis.apiRequest; vi.unstubAllGlobals(); });

describe("seleção e início de prática", () => {
  it("abre a prática filtrada pelo assunto do plano e recusa indisponível sem ampliar seleção", async () => {
    let api = await setup("questoes", () => undefined, "?assunto_id=2");
    expect(document.getElementById("assunto_id").value).toBe("2");
    expect(api.mock.calls.some(([r]) => r.includes("assunto_id=2"))).toBe(true);
    for (const search of ["?assunto_id=999", "?assunto_id=abc", "?assunto_id=2&assunto_id=2"]) {
      api = await setup("questoes", () => undefined, search);
      expect(api.mock.calls.some(([r]) => r.startsWith("/aluno/questoes?"))).toBe(false);
      expect(document.getElementById("pratica-status").textContent).toContain("indisponível ou inválido");
    }
  });
  it("oferece entrada para prática e histórico no destino existente de login", () => {
    const html = fs.readFileSync(path.join(root, "frontend/aluno/inicio.html"), "utf8");
    const dom = new DOMParser().parseFromString(html, "text/html");
    expect(dom.querySelector('a[href="/aluno/questoes.html"]')?.textContent).toBe("Praticar questões");
    expect(dom.querySelector('a[href="/aluno/historico.html"]')?.textContent).toBe("Meu histórico");
  });
  it("renderiza DTO seguro como texto, filtra e pagina", async () => {
    const api = await setup("questoes", (r) => r.startsWith("/aluno/questoes?") ? envelope([questao], 2) : undefined);
    expect(document.querySelector("#pratica-lista h2").textContent).toContain("<script>");
    expect(document.querySelector("#pratica-lista script")).toBeNull();
    expect(document.body.textContent).not.toContain("Alternativa correta");
    document.getElementById("materia_id").value = "1";
    document.getElementById("materia_id").dispatchEvent(new Event("change"));
    document.getElementById("assunto_id").value = "2";
    submit("pratica-filtros"); await settle();
    expect(api.mock.calls.some(([r]) => r.includes("materia_id=1") && r.includes("assunto_id=2"))).toBe(true);
    click("pratica-proxima"); await settle(); expect(PraticasUI.state.page).toBe(2);
    click("pratica-anterior"); await settle(); expect(PraticasUI.state.page).toBe(1);
    document.querySelector("#pratica-lista button").click(); await settle();
    expect(AuthUI.navigate).toHaveBeenCalledWith("/aluno/questao.html?tentativa_id=21");
    const body = JSON.parse(api.mock.calls.find(([r]) => r === "/aluno/praticas")[1].body);
    expect(body.questao_versao_id).toBe(14); expect(body.chave_envio).toMatch(/^[a-f0-9-]{36}$/);
    expect(localStorage.setItem).not.toHaveBeenCalled();
  });

  it("mantém a mesma chave na falha e exige recuperação do início pendente", async () => {
    let failed = true;
    const outra = { ...questao, questao_id: 13, questao_versao_id: 15 };
    const api = await setup("questoes", (r) => {
      if (r.startsWith("/aluno/questoes?")) return envelope([questao, outra]);
      if (r === "/aluno/praticas" && failed) return Promise.reject(new Error("Sem rede"));
    });
    document.querySelector("#pratica-lista button").click(); await settle();
    const key = PraticasUI.state.pending.chave_envio;
    document.querySelectorAll("#pratica-lista button")[1].click(); await settle();
    expect(document.getElementById("pratica-status").textContent).toContain("mesma questão");
    failed = false; document.querySelector("#pratica-lista button").click(); await settle();
    const calls = api.mock.calls.filter(([r]) => r === "/aluno/praticas");
    expect(calls).toHaveLength(2); expect(JSON.parse(calls[1][1].body).chave_envio).toBe(key);
  });

  it("libera chave após rejeição definitiva de início", async () => {
    await setup("questoes", (r) => r === "/aluno/praticas" ? Promise.reject(Object.assign(new Error("Versão retirada"), { status: 409 })) : undefined);
    document.querySelector("#pratica-lista button").click(); await settle();
    expect(PraticasUI.state.pending).toBeNull();
    expect(document.getElementById("pratica-status").textContent).toContain("retirada");
  });

  it("mostra vazio e recupera erro de catálogo com recarga explícita", async () => {
    let failed = true;
    await setup("questoes", (r) => {
      if (r === "/materias" && failed) return Promise.reject(new Error("Catálogo indisponível"));
      if (r.startsWith("/aluno/questoes?")) return envelope([], 0);
    });
    expect(document.getElementById("pratica-status").textContent).toContain("indisponível");
    failed = false; click("pratica-recarregar"); await settle();
    expect(document.getElementById("pratica-status").textContent).toContain("Nenhuma questão");
    expect(document.getElementById("pratica-proxima").disabled).toBe(true);
  });

  it("remove lista anterior em erro e descarta consulta atrasada", async () => {
    let release;
    let phase = 0;
    await setup("questoes", (r) => {
      if (r.startsWith("/aluno/questoes?")) {
        if (phase === 1) return new Promise((resolve) => { release = resolve; });
        if (phase === 2) return Promise.reject(new Error("Sem rede"));
      }
    });
    phase = 1; submit("pratica-filtros"); await settle();
    expect(document.querySelectorAll("#pratica-lista li")).toHaveLength(0);
    phase = 2; submit("pratica-filtros"); await settle();
    release(envelope()); await settle();
    expect(document.querySelectorAll("#pratica-lista li")).toHaveLength(0);
    expect(document.getElementById("pratica-status").textContent).toContain("Sem rede");
    expect(document.querySelector('a[href="/aluno/inicio.html"]')).not.toBeNull();
  });
});

describe("resolução e histórico", () => {
  it("envia somente alternativa, usa correção do servidor e anuncia resultado", async () => {
    const api = await setup("questao");
    expect(document.body.textContent).not.toContain("Alternativa correta: A");
    submit("pratica-resposta"); expect(document.getElementById("pratica-status").textContent).toContain("Selecione");
    document.querySelector('input[value="A"]').checked = true; submit("pratica-resposta"); await settle();
    const call = api.mock.calls.find(([r]) => r.endsWith("/resposta"));
    expect(JSON.parse(call[1].body)).toEqual({ alternativa: "A" });
    expect(document.getElementById("pratica-feedback").textContent).toBe("Correto");
    expect(document.getElementById("pratica-explicacao").textContent).toContain("indisponível");
    expect(document.activeElement.id).toBe("pratica-feedback");
    expect(document.getElementById("pratica-enviar").hidden).toBe(true);
    submit("pratica-resposta"); await settle();
    expect(api.mock.calls.filter(([r]) => r.endsWith("/resposta"))).toHaveLength(1);
  });

  it("preserva seleção em falha de rede e recupera detalhe salvo por recarga", async () => {
    let answered = false;
    await setup("questao", (r) => {
      if (r.endsWith("/resposta")) return Promise.reject(new Error("Sem rede"));
      if (r === "/aluno/praticas/21" && answered) return detalhe(true, false, "A soma resulta em 4.");
    });
    document.querySelector('input[value="B"]').checked = true;
    submit("pratica-resposta"); await settle();
    expect(document.querySelector('input[value="B"]').checked).toBe(true);
    expect(document.getElementById("pratica-resultado").hidden).toBe(true);
    answered = true; click("pratica-recarregar"); await settle();
    expect(document.getElementById("pratica-feedback").textContent).toBe("Incorreto");
    expect(document.getElementById("pratica-explicacao").textContent).toBe("A soma resulta em 4.");
  });

  it("trata ID inválido e recurso ausente sem revelar conteúdo", async () => {
    let api = await setup("questao", () => undefined, "?tentativa_id=x");
    expect(document.getElementById("pratica-status").textContent).toContain("inválido");
    expect(api.mock.calls.some(([r]) => r.startsWith("/aluno/praticas/"))).toBe(false);
    await setup("questao", (r) => r === "/aluno/praticas/21" ? Promise.reject(new Error("Tentativa não encontrada")) : undefined);
    expect(document.getElementById("pratica-conteudo").hidden).toBe(true);
    expect(document.getElementById("pratica-status").textContent).toContain("não encontrada");
  });

  it("mostra histórico corrigido e vazio sem inventar desempenho", async () => {
    let empty = false;
    await setup("historico", (r) => r.startsWith("/aluno/praticas?") ? envelope(empty ? [] : [detalhe(true), detalhe(true, false)]) : undefined);
    expect(document.querySelectorAll("#pratica-lista li")).toHaveLength(2);
    expect(document.body.textContent).toContain("Resposta incorreta");
    expect(document.querySelector('#pratica-lista a').getAttribute("href")).toBe("/aluno/questao.html?tentativa_id=21");
    empty = true; click("pratica-recarregar"); await settle();
    expect(document.getElementById("pratica-status").textContent).toContain("Nenhuma resposta");
  });
});

describe("sessão e identidade", () => {
  it("preserva alternativa na expiração e exige novo envio após recuperar mesma conta", async () => {
    let expired = false;
    const api = await setup("questao", (r) => {
      if (r.endsWith("/resposta") && !expired) {
        expired = true;
        document.dispatchEvent(new CustomEvent("auth-required", { detail: "sessao_invalida" }));
        return Promise.reject(new Error("Entre novamente"));
      }
    });
    document.querySelector('input[value="C"]').checked = true; submit("pratica-resposta"); await settle();
    expect(AuthUI.blocked).toBe(true); expect(document.getElementById("auth-content").hidden).toBe(true);
    document.getElementById("auth-recovery-password").value = "Senha";
    submit("auth-recovery-form"); await settle();
    expect(AuthUI.blocked).toBe(false); expect(document.querySelector('input[value="C"]').checked).toBe(true);
    expect(api.mock.calls.filter(([r]) => r.endsWith("/resposta"))).toHaveLength(1);
    submit("pratica-resposta"); await settle();
    expect(api.mock.calls.filter(([r]) => r.endsWith("/resposta"))).toHaveLength(2);
  });

  it("limpa conteúdo e seleção se outra conta assume a sessão", async () => {
    let changed = false;
    await setup("questao", (r) => r === "/auth/sessao" && changed ? { usuario: { ...aluno, id: 8 } } : undefined);
    document.querySelector('input[value="B"]').checked = true;
    changed = true; click("pratica-recarregar"); await settle();
    expect(AuthUI.changedAccount).toBe(true);
    expect(document.getElementById("pratica-enunciado").textContent).toBe("");
    expect(document.querySelector('input[name="alternativa"]')).toBeNull();
    expect(document.getElementById("auth-content").hidden).toBe(true);
  });

  it("confere identidade ao voltar de outra aba e recupera falha sem exibir dados antigos", async () => {
    let phase = 0;
    await setup("questao", (r) => {
      if (r === "/auth/sessao" && phase === 1) return Promise.reject(new Error("Sem rede"));
      if (r === "/auth/sessao" && phase === 2) return { usuario: { ...aluno, id: 8 } };
    });
    phase = 1; window.dispatchEvent(new Event("focus")); await settle();
    expect(document.getElementById("auth-content").hidden).toBe(true);
    expect(document.getElementById("auth-loading").textContent).toContain("Sem rede");
    phase = 0; document.querySelector("#auth-loading button").click(); await settle();
    expect(document.getElementById("auth-content").hidden).toBe(false);
    phase = 2; window.dispatchEvent(new Event("focus")); await settle();
    expect(AuthUI.changedAccount).toBe(true);
    expect(document.getElementById("pratica-enunciado").textContent).toBe("");
  });

  it("limpa contexto quando conta muda durante recuperação", async () => {
    let changed = false;
    await setup("questao", (r) => r === "/auth/sessao" && changed ? { usuario: { ...aluno, id: 9 } } : undefined);
    AuthUI.recover("csrf_invalido"); changed = true;
    submit("auth-recovery-form"); await settle();
    expect(document.getElementById("auth-recovery-status").textContent).toContain("contexto anterior foi removido");
    expect(PraticasUI.state.detail).toBeNull();
    expect(document.getElementById("pratica-enunciado").textContent).toBe("");
  });

  it("descarta resultado de início atrasado após mudança de identidade", async () => {
    let release;
    const api = await setup("questoes", (r) => r === "/aluno/praticas" ? new Promise((resolve) => { release = resolve; }) : undefined);
    document.querySelector("#pratica-lista button").click(); await settle();
    document.dispatchEvent(new Event("auth-identity-changed"));
    release(detalhe()); await settle();
    expect(AuthUI.navigate).not.toHaveBeenCalled(); expect(PraticasUI.state.pending).toBeNull();
    expect(api.mock.calls.filter(([r]) => r === "/aluno/praticas")).toHaveLength(1);
  });

  it("bloqueia administrador antes de carregar conteúdo acadêmico", async () => {
    const api = await setup("questoes", (r) => r === "/auth/sessao" ? { usuario: { ...aluno, perfil: "administrador" } } : undefined);
    expect(AuthUI.blocked).toBe(true); expect(api).toHaveBeenCalledTimes(1);
    expect(document.getElementById("auth-loading").textContent).toContain("conta de aluno");
  });
});
