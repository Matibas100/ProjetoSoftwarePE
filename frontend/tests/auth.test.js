import fs from "node:fs";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { root, settle } from "./helpers/classic-app.js";

const aluno = { id: 1, nome: "Aluno <teste>", email: "aluno@teste.local", perfil: "aluno" };
const admin = { ...aluno, perfil: "administrador" };
const expired = () => Object.assign(new Error("Entre novamente"), { code: "sessao_invalida" });

async function setup(file = "login.html", api = vi.fn().mockRejectedValue(expired())) {
  vi.resetModules(); globalThis.AuthUI?.destroy?.();
  const html = fs.readFileSync(path.join(root, "frontend", file), "utf8").replace(/<script\s+src="[^"]+"><\/script>/g, "");
  document.open(); document.write(html); document.close();
  HTMLDialogElement.prototype.showModal = function () { this.open = true; };
  HTMLDialogElement.prototype.close = function () { this.open = false; };
  globalThis.apiRequest = api; globalThis.resetCsrf = vi.fn();
  await import("../js/auth-session.js");
  globalThis.AuthUI.navigate = vi.fn();
  if (["login.html", "cadastro.html"].includes(file)) await import("../js/auth-page.js");
  await settle();
  return api;
}

function fill(signup = false) {
  document.querySelector("#auth-email").value = aluno.email;
  document.querySelector("#auth-password").value = "senha correta";
  if (signup) {
    document.querySelector("#auth-name").value = aluno.nome;
    document.querySelector("#auth-confirmation").value = "senha correta";
  }
}
const submit = () => document.querySelector("#auth-form").dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));

describe("cadastro e login", () => {
  beforeEach(() => { sessionStorage.clear(); });
  afterEach(() => { globalThis.AuthUI?.destroy?.(); delete globalThis.AuthUI; delete globalThis.apiRequest; });

  it("valida campo e coincidencia sem chamar API", async () => {
    const api = await setup("cadastro.html"); submit();
    expect(document.querySelector("#auth-name").getAttribute("aria-invalid")).toBe("true");
    fill(true); document.querySelector("#auth-confirmation").value = "diferente"; submit();
    expect(document.querySelector("#auth-confirmation-error").textContent).toContain("coincidem");
    expect(api).toHaveBeenCalledTimes(1);
    document.querySelector("#auth-form").dispatchEvent(new Event("input"));
    expect(document.querySelector("#auth-length").dataset.valid).toBe("true");
    expect(document.querySelector("#auth-match").dataset.valid).toBe("false");
    document.querySelector("#auth-confirmation").value = "senha correta";
    document.querySelector("#auth-form").dispatchEvent(new Event("input"));
    expect(document.querySelector("#auth-match").dataset.valid).toBe("true");
  });

  it("cadastra sem perfil, preserva email para login e nao salva senha", async () => {
    const api = await setup("cadastro.html");
    api.mockResolvedValueOnce({ usuario: aluno }); fill(true); submit(); await settle();
    const body = JSON.parse(api.mock.calls[1][1].body);
    expect(Object.keys(body).sort()).toEqual(["email", "nome", "senha", "senha_confirmacao"]);
    expect(sessionStorage.getItem("cadastro-email")).toBe(aluno.email);
    expect(sessionStorage.getItem("senha")).toBeNull();
    expect(AuthUI.navigate).toHaveBeenCalledWith("/login.html");
    await setup();
    expect(document.querySelector("#auth-email").value).toBe(aluno.email);
    expect(sessionStorage.getItem("cadastro-email")).toBeNull();
    expect(document.querySelector("#auth-message").textContent).toContain("Conta criada");
  });

  it("associa erro ao nome normalizado e permite corrigir sem perder os demais campos", async () => {
    const api = await setup("cadastro.html"); fill(true);
    const name = document.querySelector("#auth-name");
    for (const value of ["  ", " A ", "a".repeat(101)]) {
      name.value = value; submit();
      expect(name.getAttribute("aria-invalid")).toBe("true");
      expect(document.querySelector("#auth-name-error").textContent).toContain("2 e 100");
      expect(document.activeElement).toBe(name);
      expect(document.querySelector("#auth-email").value).toBe(aluno.email);
      expect(api).toHaveBeenCalledTimes(1);
    }
    name.value = " Ana Silva ";
    api.mockResolvedValueOnce({ usuario: { ...aluno, nome: "Ana Silva" } });
    submit(); await settle();
    expect(name.hasAttribute("aria-invalid")).toBe(false);
    expect(document.querySelector("#auth-name-error").textContent).toBe("");
    expect(AuthUI.navigate).toHaveBeenCalledWith("/login.html");
    expect(api).toHaveBeenCalledTimes(2);
  });

  it("trata duplicidade e rede mantendo campos e habilitando nova tentativa", async () => {
    const api = await setup("cadastro.html"); fill(true);
    api.mockRejectedValueOnce(Object.assign(new Error("Email em uso"), { code: "email_em_uso" }));
    submit(); await settle();
    expect(document.querySelector("#auth-email-error").textContent).toBe("Email em uso");
    expect(document.querySelector("#auth-email").value).toBe(aluno.email);
    api.mockRejectedValueOnce(new Error("Sem rede")); submit(); await settle();
    expect(document.querySelector("#auth-message").textContent).toBe("Sem rede");
    expect(document.querySelector('[type="submit"]').disabled).toBe(false);
  });

  it("mostra e oculta senhas, impede envio duplicado e aplica destinos fixos", async () => {
    const api = await setup(); fill();
    const toggle = document.querySelector("[data-password-toggle]"); toggle.click();
    expect(document.querySelector("#auth-password").type).toBe("text"); toggle.click();
    expect(toggle.getAttribute("aria-pressed")).toBe("false");
    let finish; api.mockImplementationOnce(() => new Promise((resolve) => { finish = resolve; }));
    submit(); submit(); expect(api).toHaveBeenCalledTimes(2);
    finish({ usuario: admin, destino: "https://malicioso.test" }); await settle();
    expect(AuthUI.navigate).toHaveBeenCalledWith("/admin/materias.html");
    api.mockResolvedValueOnce({ usuario: aluno }); fill(); submit(); await settle();
    expect(AuthUI.navigate).toHaveBeenCalledWith("/aluno/inicio.html");
  });
});

describe("sessao e preservacao administrativa", () => {
  afterEach(() => { globalThis.AuthUI?.destroy?.(); delete globalThis.AuthUI; delete globalThis.apiRequest; vi.restoreAllMocks(); });

  it("carrega identidade segura e confirma descarte antes do logout", async () => {
    const api = vi.fn().mockResolvedValue({ usuario: aluno });
    await setup("aluno/inicio.html", api);
    expect(document.querySelector("[data-auth-name]").textContent).toBe(aluno.nome);
    expect(document.querySelector("#auth-content").hidden).toBe(false);
    AuthUI.registerGuard(() => true); vi.spyOn(window, "confirm").mockReturnValue(false);
    await AuthUI.logout(); expect(api).toHaveBeenCalledTimes(1);
    window.confirm.mockReturnValue(true); api.mockRejectedValueOnce(new Error("Sem rede"));
    await AuthUI.logout(); expect(document.querySelector("#auth-loading").textContent).toContain("Sem rede");
    api.mockResolvedValueOnce(null); await AuthUI.logout();
    expect(AuthUI.navigate).toHaveBeenCalledWith("/login.html");
  });

  it("nega aluno na gestao e nao executa consultas de conteudo", async () => {
    const api = vi.fn().mockResolvedValue({ usuario: aluno }); await setup("admin/materias.html", api);
    expect(AuthUI.blocked).toBe(true);
    expect(document.querySelector("#auth-loading").textContent).toContain("não tem acesso");
    expect(document.querySelector("#auth-content").hidden).toBe(true);
    expect(api).toHaveBeenCalledTimes(1);
  });

  it("aguarda recuperacao de rede no guard e depois libera conteudo", async () => {
    const api = vi.fn().mockRejectedValueOnce(new Error("Sem rede")).mockResolvedValue({ usuario: admin });
    await setup("admin/materias.html", api);
    document.querySelector("#auth-loading button").click(); await settle();
    expect(await AuthUI.ready).toBe(true);
    expect(document.querySelector("#auth-content").hidden).toBe(false);
  });

  it("reautentica no contexto sem repetir mutacao ou apagar campos", async () => {
    const api = vi.fn().mockResolvedValue({ usuario: admin }); await setup("admin/materias.html", api);
    const name = document.querySelector("#materia-nome"); name.value = "Edicao local";
    document.dispatchEvent(new CustomEvent("auth-required", { detail: "reautenticacao_necessaria" }));
    expect(AuthUI.blocked).toBe(true);
    AuthUI.recover("reautenticacao_necessaria"); expect(document.querySelectorAll(".auth-dialog")).toHaveLength(1);
    document.querySelector("#auth-recovery-password").value = "senha correta";
    api.mockRejectedValueOnce(new Error("Senha incorreta"));
    document.querySelector("#auth-recovery-form").dispatchEvent(new Event("submit", { cancelable: true })); await settle();
    expect(document.querySelector("#auth-recovery-status").textContent).toBe("Senha incorreta");
    document.querySelector("#auth-recovery-form").dispatchEvent(new Event("submit", { cancelable: true })); await settle();
    expect(AuthUI.blocked).toBe(false); expect(name.value).toBe("Edicao local");
    expect(api.mock.calls.filter(([route]) => !route.startsWith("/auth/"))).toHaveLength(0);
  });

  it("recupera login expirado e exige recarga para conta diferente", async () => {
    const api = vi.fn().mockResolvedValue({ usuario: admin }); await setup("admin/materias.html", api);
    AuthUI.recover("sessao_invalida"); document.querySelector("#auth-recovery-password").value = "senha correta";
    api.mockRejectedValueOnce(expired()).mockResolvedValueOnce({ usuario: admin }).mockResolvedValueOnce({ usuario: { ...admin, id: 2 } });
    document.querySelector("#auth-recovery-form").dispatchEvent(new Event("submit", { cancelable: true })); await settle();
    expect(AuthUI.blocked).toBe(true); expect(AuthUI.changedAccount).toBe(true);
    expect(document.querySelector("#auth-recovery-status").textContent).toContain("A conta mudou");
    document.querySelector("#auth-recovery-close").click(); expect(document.querySelector(".auth-dialog")).toBeNull();
    AuthUI.recover("sessao_invalida"); expect(document.querySelector(".auth-dialog")).toBeNull();
  });

  it("trata troca somente de CSRF e fechamento do dialogo", async () => {
    const api = vi.fn().mockResolvedValue({ usuario: admin }); await setup("admin/materias.html", api);
    AuthUI.recover("csrf_invalido"); document.querySelector("#auth-recovery-password").value = "senha correta";
    document.querySelector("#auth-recovery-form").dispatchEvent(new Event("submit", { cancelable: true })); await settle();
    expect(resetCsrf).toHaveBeenCalled(); expect(AuthUI.blocked).toBe(false);
    AuthUI.recover("sessao_invalida");
    document.querySelector(".auth-dialog").dispatchEvent(new Event("cancel", { cancelable: true }));
    expect(document.querySelector(".auth-dialog")).toBeNull();
    AuthUI.recover("sessao_invalida"); api.mockRejectedValueOnce(new Error("Sem rede"));
    document.querySelector("#auth-recovery-form").dispatchEvent(new Event("submit", { cancelable: true })); await settle();
    expect(document.querySelector("#auth-recovery-status").textContent).toBe("Sem rede");
  });
});
