import { randomUUID } from "node:crypto";
import { test, expect } from "@playwright/test";

test.beforeAll(() => {
  if (process.env.RUN_MYSQL_E2E !== "1" || !/^plataforma_enem_e2e_test_[a-f0-9]{12}$/.test(process.env.E2E_SCHEMA || "")) throw new Error("Use o runner E2E com MySQL descartável real.");
  if (process.env.GEMINI_API_KEY || process.env.TUTOR_IA_ENABLED !== "false") throw new Error("E2E comum exige Tutor desabilitado e nenhuma chave Gemini.");
});

async function login(page, email, password) {
  await page.goto("/login"); await page.locator("#auth-email").fill(email); await page.locator("#auth-password").fill(password);
  await page.locator('#auth-form button[type="submit"]').click(); await expect(page.locator("#auth-content")).toBeVisible();
}
async function submit(page, path, selector, status) {
  const response = page.waitForResponse(r => new URL(r.url()).pathname === path && r.request().method() === "POST");
  await page.locator(selector).click(); const r = await response; expect(r.status()).toBe(status); return r;
}

test("Tutor: navegação, uso antigo, novo aceite e indisponibilidade real sem Gemini", async ({ browser }, info) => {
  const contexts = [];
  async function page() {
    const context = await browser.newContext({ baseURL: process.env.E2E_BASE_URL }); contexts.push(context);
    await context.addInitScript(url => { window.ENEM_API_URL = url; }, process.env.E2E_API_URL);
    return context.newPage();
  }
  try {
    const admin = await page(), aluno = await page(); const tag = randomUUID().replaceAll("-", "");
    await login(admin, process.env.E2E_ADMIN_EMAIL, process.env.E2E_ADMIN_PASSWORD);
    await admin.goto("/index.html"); await admin.locator("#nome").fill(`Revisão ${tag}`); await admin.locator("#materia-area-enem-id").selectOption("4");
    const materia = await (await submit(admin, "/api/materias", "#salvar-button", 201)).json();
    await admin.locator("#assunto-nome").fill(`Eletricidade ${tag}`); await admin.locator("#assunto-materia-id").selectOption(String(materia.id));
    const assunto = await (await submit(admin, "/api/assuntos", "#assunto-salvar-button", 201)).json();
    await login(aluno, process.env.E2E_TUTOR_EMAIL, process.env.E2E_TUTOR_PASSWORD);
    await aluno.getByRole("link", { name: "Tutor IA", exact: true }).click(); await expect(aluno.locator("h1")).toHaveText("Tutor IA");
    await expect(aluno.locator("#tutor-aviso")).toContainText("Google Gemini");
    await aluno.locator("#tutor-materia").selectOption(String(materia.id)); await aluno.locator("#tutor-assunto").selectOption(String(assunto.id));
    await aluno.locator("#tutor-duvida").fill("Como distinguir corrente elétrica e tensão em um circuito?");
    const pendente = await submit(aluno, "/api/tutoria", "#tutor-enviar", 409);
    expect((await pendente.json()).codigo).toBe("termos_uso_pendentes");
    await aluno.locator("#tutor-termos a").click(); await expect(aluno.locator("#privacidade-uso")).toContainText("1.0");
    await submit(aluno, "/api/aluno/privacidade/termos-uso", "#privacidade-aceitar-uso", 201);
    await expect(aluno.locator("#privacidade-uso")).toContainText("2.0");
    await expect(aluno.locator("#privacidade-plano")).toContainText("Sem decisão");
    await aluno.getByRole("link", { name: "Tutor IA", exact: true }).click();
    await aluno.locator("#tutor-materia").selectOption(String(materia.id)); await aluno.locator("#tutor-assunto").selectOption(String(assunto.id));
    await aluno.locator("#tutor-duvida").fill("Como distinguir corrente elétrica e tensão em um circuito?");
    const indisponivel = await submit(aluno, "/api/tutoria", "#tutor-enviar", 503);
    expect((await indisponivel.json()).codigo).toBe("tutor_indisponivel");
    await expect(aluno.locator("#tutor-status")).toContainText("indisponível");
    await expect(aluno.locator("#tutor-duvida")).toHaveValue(/corrente elétrica/);
    for (const width of [1440, 390]) {
      await aluno.setViewportSize({ width, height: 1000 });
      expect(await aluno.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
      await aluno.locator("#tutor-duvida").focus(); await aluno.keyboard.press("Tab"); await expect(aluno.locator("#tutor-enviar")).toBeFocused();
      await aluno.screenshot({ path: info.outputPath(`tutor-${width}.png`), fullPage: true });
    }
    await aluno.reload(); await expect(aluno.locator("#tutor-duvida")).toHaveValue("");
    await expect(aluno.locator("#tutor-resultado")).toBeHidden();
  } finally { for (const context of contexts) await context.close(); }
});
