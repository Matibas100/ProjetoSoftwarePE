import fs from "node:fs";
import path from "node:path";
import { afterEach, expect, it, vi } from "vitest";
import { root, settle } from "./helpers/classic-app.js";

const $ = id => document.getElementById(id);
const titulos = ["1. Explicação simples", "2. Exemplo", "3. Verifique sua compreensão", "4. Exercício curto"];
const resposta = texto => ({ disciplina: "Física", assunto: "Eletricidade", resposta: titulos.map(t => `${t}\n${texto || "Conteúdo de estudo."}`).join("\n") });
const materias = [{ id: 1, nome: "Física" }, { id: 2, nome: "Matemática" }];
const deferred = () => { let resolve, reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no; }); return { promise, resolve, reject }; };
const posts = api => api.mock.calls.filter(([r]) => r === "/tutoria");
const submit = () => $("tutor-form").dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
async function setup(override = () => undefined, ready = true) {
  globalThis.TutorUI?.destroy(); vi.resetModules();
  document.open(); document.write(fs.readFileSync(path.join(root, "frontend/aluno/tutor.html"), "utf8").replace(/<script\s+src="[^"]+"><\/script>/g, "")); document.close();
  globalThis.AuthUI = { ready: Promise.resolve(ready), user: { id: 1, perfil: "aluno" }, blocked: false, checkIdentity: vi.fn(async () => true) };
  const api = vi.fn(async (r, o) => {
    const custom = override(r, o); if (custom !== undefined) return custom;
    if (r === "/materias") return materias;
    if (r.startsWith("/assuntos")) { const id = Number(r.split("=")[1]); return [{ id: id * 10, nome: id === 1 ? "Eletricidade" : "Álgebra", materia_id: id }]; }
    return resposta();
  });
  globalThis.apiRequest = api;
  await import("../js/aluno-tutor.js"); await settle(); return api;
}
async function choose(id = "1") {
  $("tutor-materia").value = id; $("tutor-materia").dispatchEvent(new Event("change")); await settle();
  $("tutor-assunto").value = String(Number(id) * 10); $("tutor-assunto").dispatchEvent(new Event("change"));
  $("tutor-duvida").value = "Qual a diferença entre corrente e tensão?";
}
afterEach(() => { globalThis.TutorUI?.destroy(); delete globalThis.TutorUI; delete globalThis.AuthUI; delete globalThis.apiRequest; vi.useRealTimers(); vi.restoreAllMocks(); });

it("mantém contrato HTML, nível fixo, avisos, teclado e nenhum envio automático", async () => {
  const api = await setup();
  expect($("tutor-materia").disabled).toBe(false); expect($("tutor-enviar").disabled).toBe(true);
  expect(document.querySelector('label[for="tutor-duvida"]')).not.toBeNull();
  expect($("tutor-aviso").textContent).toContain("Google Gemini");
  expect(document.body.textContent).toContain("Ensino médio");
  expect($("tutor-termos").querySelector("a").getAttribute("href")).toBe("/aluno/privacidade.html");
  expect(document.querySelector("[data-current]").dataset.current).toBe("tutor");
  await choose(); expect(posts(api)).toHaveLength(0); expect($("tutor-enviar").disabled).toBe(false);
  $("tutor-duvida").focus(); expect(document.activeElement).toBe($("tutor-duvida"));
  expect(document.querySelectorAll('[id]').length).toBe(new Set([...document.querySelectorAll('[id]')].map(e => e.id)).size);
});
it("envia quatro campos uma vez, renderiza quatro partes como texto e não persiste", async () => {
  const malicious = '<script>window.invadiu=true</script><img src=x onerror=alert(1)> [link](https://externo.test)';
  const storage = vi.spyOn(Storage.prototype, "setItem");
  const api = await setup(r => r === "/tutoria" ? resposta(malicious) : undefined); await choose();
  submit(); submit(); await settle();
  expect(posts(api)).toHaveLength(1);
  const options = posts(api)[0][1];
  expect(JSON.parse(options.body)).toEqual({ disciplina: "Física", nivel: "ensino_medio", assunto: "Eletricidade", duvida: $("tutor-duvida").value });
  expect(options.signal).toBeInstanceOf(AbortSignal);
  expect($("tutor-secoes").querySelectorAll("section")).toHaveLength(4);
  expect($("tutor-secoes").textContent).toContain(malicious);
  expect($("tutor-secoes").querySelector("script,img,a")).toBeNull(); expect(window.invadiu).toBeUndefined();
  expect($("tutor-resultado").hidden).toBe(false); expect(document.activeElement).toBe($("tutor-resposta-titulo"));
  expect(storage).not.toHaveBeenCalled(); expect($("tutor-form").getAttribute("aria-busy")).toBe("false");
});
it.each(["curta", "x".repeat(2001)])("valida tamanho antes de chamar API: %s", async text => {
  const api = await setup(); await choose(); $("tutor-duvida").value = text; submit(); await settle();
  expect(posts(api)).toHaveLength(0); expect($("tutor-status").textContent).toContain("10 a 2000");
  expect(document.activeElement).toBe($("tutor-duvida"));
});
it.each([
  [400, "dados_invalidos", "Dados inválidos"], [409, "termos_uso_pendentes", "Aceite o uso vigente"],
  [429, "limite_tutoria", "Aguarde antes de enviar novamente"], [502, "tutor_timeout", "O Tutor excedeu o tempo de espera"],
  [503, "tutor_indisponivel", "Tutor indisponível"], [500, "erro_interno", "Falha interna"],
])("trata HTTP %s sem reenvio e preserva rascunho", async (status, code, message) => {
  const api = await setup(r => r === "/tutoria" ? Promise.reject(Object.assign(new Error(message), { status, code })) : undefined);
  await choose(); submit(); await settle();
  expect($("tutor-status").textContent).toContain(message); expect(posts(api)).toHaveLength(1);
  expect($("tutor-duvida").value).toContain("corrente"); expect($("tutor-enviar").disabled).toBe(false);
  expect($("tutor-termos").hidden).toBe(code !== "termos_uso_pendentes");
});
it("mantém resposta anterior com sua pergunta e filtros após nova falha", async () => {
  let falhar = false;
  const api = await setup(r => r === "/tutoria" && falhar ? Promise.reject(new Error("Rede falhou")) : undefined);
  await choose(); submit(); await settle(); falhar = true;
  await choose("2"); $("tutor-duvida").value = "Outra pergunta com contexto novo"; submit(); await settle();
  expect($("tutor-resposta-contexto").textContent).toContain("Física · Eletricidade");
  expect($("tutor-resposta-contexto").textContent).toContain("a nova tentativa falhou");
  expect($("tutor-pergunta-anterior").textContent).toContain("corrente");
  expect($("tutor-status").textContent).toContain("resposta anterior"); expect(posts(api)).toHaveLength(2);
});
it.each([null, { resposta: "texto sem títulos" }, { resposta: titulos.join("\n") },
  { resposta: titulos.map(t => t + "\nConteúdo").join("\n") + "\n" + titulos[0] },
  { resposta: "x".repeat(12001) }])("rejeita resposta incompleta ou malformada", async data => {
  const api = await setup(r => r === "/tutoria" ? Promise.resolve(data) : undefined); await choose(); submit(); await settle();
  expect($("tutor-resultado").hidden).toBe(true); expect($("tutor-status").dataset.erro).toBe("true");
  expect(posts(api)).toHaveLength(1);
});
it.each([[], null, new Error("sem rede")])("bloqueia catálogo vazio ou falho", async data => {
  const api = await setup(r => r === "/materias" ? data instanceof Error ? Promise.reject(data) : Promise.resolve(data) : undefined);
  expect($("tutor-enviar").disabled).toBe(true); expect($("tutor-materia").disabled).toBe(true);
  expect($("tutor-status").textContent).toMatch(/vazio|Falha/); submit(); expect(posts(api)).toHaveLength(0);
  api.mockImplementation(async () => materias); $("tutor-catalogo").click(); await settle(); expect($("tutor-materia").disabled).toBe(false);
});
it.each([[], null, new Error("sem rede")])("bloqueia assuntos vazios/falhos e permite limpar filtro", async data => {
  await setup(r => r.startsWith("/assuntos") ? data instanceof Error ? Promise.reject(data) : Promise.resolve(data) : undefined);
  await choose(); expect($("tutor-enviar").disabled).toBe(true); expect($("tutor-assunto").disabled).toBe(true);
  $("tutor-materia").value = ""; $("tutor-materia").dispatchEvent(new Event("change")); await settle();
  expect($("tutor-contexto").textContent).toContain("Escolha uma matéria");
});
it("ignora filtro atrasado depois de selecionar outra matéria", async () => {
  const old = deferred(); await setup(r => r === "/assuntos?materia_id=1" ? old.promise : undefined);
  $("tutor-materia").value = "1"; $("tutor-materia").dispatchEvent(new Event("change"));
  await choose("2"); old.resolve([{ id: 10, nome: "Antigo", materia_id: 1 }]); await settle();
  expect($("tutor-assunto").textContent).toContain("Álgebra"); expect($("tutor-assunto").textContent).not.toContain("Antigo");
});
it("ignora falhas de filtro e catálogo antigos", async () => {
  const old = deferred(), catalog = deferred(); let n = 0;
  await setup(r => r === "/materias" && n++ > 0 ? catalog.promise : r === "/assuntos?materia_id=1" ? old.promise : undefined);
  $("tutor-materia").value = "1"; $("tutor-materia").dispatchEvent(new Event("change")); await choose("2");
  old.reject(new Error("Antigo")); await settle(); expect($("tutor-status").textContent).not.toContain("Antigo");
  $("tutor-catalogo").click(); document.dispatchEvent(new Event("auth-identity-changed")); catalog.reject(new Error("Antigo")); await settle();
  expect($("tutor-status").textContent).not.toContain("Antigo");
});
it("ignora sucesso de catálogo após troca de identidade", async () => {
  const old = deferred(); await setup(r => r === "/materias" ? old.promise : undefined);
  document.dispatchEvent(new Event("auth-identity-changed")); old.resolve(materias); await settle();
  expect(TutorUI.state.materias).toEqual([]);
});
it("cancela em 45 s, libera envio e ignora sucesso tardio sem retry", async () => {
  const old = deferred(); const api = await setup(r => r === "/tutoria" ? old.promise : undefined); await choose();
  vi.useFakeTimers(); submit(); await vi.advanceTimersByTimeAsync(45001);
  expect(posts(api)[0][1].signal.aborted).toBe(true); expect($("tutor-status").textContent).toContain("45 segundos");
  expect($("tutor-enviar").disabled).toBe(false); expect($("tutor-duvida").value).toContain("corrente");
  old.resolve(resposta()); await vi.advanceTimersByTimeAsync(0);
  expect($("tutor-resultado").hidden).toBe(true); expect(posts(api)).toHaveLength(1);
});
it.each(["auth-required", "auth-identity-changed", "pagehide", "logout"])("limpa conteúdo e aborta na saída %s", async type => {
  const old = deferred(); const api = await setup(r => r === "/tutoria" ? old.promise : undefined); await choose(); submit(); await settle();
  if (type === "logout") document.querySelector("[data-auth-exit]").click();
  else (type === "pagehide" ? window : document).dispatchEvent(new Event(type));
  old.resolve(resposta()); await settle();
  expect(posts(api)[0][1].signal.aborted).toBe(true); expect($("tutor-duvida").value).toBe("");
  expect($("tutor-secoes").textContent).toBe(""); expect($("tutor-resultado").hidden).toBe(true);
});
it("não envia quando identidade falha; não envia automaticamente ao recuperá-la", async () => {
  const api = await setup(); await choose(); AuthUI.checkIdentity.mockResolvedValue(false); submit(); await settle();
  expect(posts(api)).toHaveLength(0); AuthUI.checkIdentity.mockResolvedValue(true); window.dispatchEvent(new Event("focus")); await settle();
  expect(posts(api)).toHaveLength(0);
});
it.each(["antes", "depois"])("limita também a espera da identidade %s da chamada externa", async etapa => {
  const api = await setup(); await choose(); const checking = deferred();
  if (etapa === "antes") AuthUI.checkIdentity.mockReturnValue(checking.promise);
  else AuthUI.checkIdentity.mockResolvedValueOnce(true).mockReturnValue(checking.promise);
  vi.useFakeTimers(); submit(); await vi.advanceTimersByTimeAsync(45001);
  expect($("tutor-enviar").disabled).toBe(false); expect($("tutor-status").textContent).toContain("45 segundos");
  checking.resolve(true); await vi.advanceTimersByTimeAsync(0);
  expect(posts(api)).toHaveLength(etapa === "antes" ? 0 : 1); expect($("tutor-resultado").hidden).toBe(true);
});
it("retira resultado ao retornar até verificar identidade e limpa em falha", async () => {
  await setup(); await choose(); submit(); await settle();
  const checking = deferred(); AuthUI.checkIdentity.mockReturnValue(checking.promise); window.dispatchEvent(new Event("focus"));
  expect($("tutor-resultado").hidden).toBe(true); checking.resolve(true); await settle(); expect($("tutor-resultado").hidden).toBe(false);
  AuthUI.checkIdentity.mockRejectedValue(new Error("sessão")); window.dispatchEvent(new Event("focus")); await settle();
  expect($("tutor-duvida").value).toBe(""); expect($("tutor-resultado").hidden).toBe(true);
});
it("ignora resultado se a conta muda na conferência final", async () => {
  await setup(); await choose(); AuthUI.checkIdentity.mockImplementation(async () => {
    if (TutorUI.state.busy && posts(apiRequest).length) { AuthUI.user.id = 2; document.dispatchEvent(new Event("auth-identity-changed")); return false; }
    return true;
  }); submit(); await settle(); expect($("tutor-secoes").textContent).toBe("");
});
it("ignora falha externa tardia após encerrar e retorno em aba oculta", async () => {
  const old = deferred(); await setup(r => r === "/tutoria" ? old.promise : undefined); await choose(); submit(); await settle();
  Object.defineProperty(document, "visibilityState", { configurable: true, value: "hidden" });
  document.dispatchEvent(new Event("visibilitychange")); expect($("tutor-resultado").hidden).toBe(true);
  document.dispatchEvent(new Event("auth-identity-changed")); old.reject(new Error("atrasada")); await settle();
  expect($("tutor-status").textContent).not.toContain("atrasada");
  Object.defineProperty(document, "visibilityState", { configurable: true, value: "visible" });
});
it("não carrega sem autenticação e bloqueia ações durante processamento", async () => {
  const api = await setup(() => undefined, false); expect(api).not.toHaveBeenCalled();
  AuthUI.blocked = true; $("tutor-catalogo").click(); window.dispatchEvent(new Event("focus")); submit(); await settle(); expect(api).not.toHaveBeenCalled();
  AuthUI.blocked = false; await TutorUI.catalogo(); await choose();
  const pending = deferred(); api.mockImplementation(() => pending.promise); submit(); await settle();
  $("tutor-catalogo").click(); submit(); expect(posts(api)).toHaveLength(1); pending.resolve(resposta()); await settle();
});
