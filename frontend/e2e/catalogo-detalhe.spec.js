import { test, expect } from "@playwright/test";

test.beforeAll(() => {
  if (process.env.RUN_MYSQL_E2E !== "1" || !/^plataforma_enem_e2e_test_[a-f0-9]{12}$/.test(process.env.E2E_SCHEMA || "")) {
    throw new Error("Use o runner E2E com MySQL descartável real.");
  }
});

async function response(page, path, method, action, status = 200) {
  const pending = page.waitForResponse(r => new URL(r.url()).pathname === `/api${path}` && r.request().method() === method);
  await action();
  const result = await pending;
  expect(result.status()).toBe(status);
  return result.json();
}

async function open(page, path) {
  await page.goto(path);
  await expect(page.locator("#auth-content")).toBeVisible();
}

async function edit(page, resource, id) {
  const button = page.locator(`#${resource}-corpo button[data-action="edit"][data-id="${id}"]`);
  await button.locator("xpath=ancestor::details").locator("summary").click();
  return response(page, `/${resource}/${id}`, "GET", () => button.click());
}

async function createMatter(page, name) {
  await open(page, "/admin/materias.html");
  await page.locator("#materia-nome").fill(name);
  await page.locator("#materia-area").selectOption("4");
  return response(page, "/materias", "POST", () => page.locator("#materia-salvar").click(), 201);
}

async function filter(page, resource, name) {
  const pending = page.waitForResponse(r => new URL(r.url()).pathname === `/api/admin/${resource}`);
  await page.locator(`#${resource}-busca`).fill(name);
  await pending;
  await expect(page.locator(`#${resource}-corpo tr`)).toHaveCount(1);
}

test("Editar consulta Matéria e Assunto atuais após alterações em segunda aba", async ({ page, context }, info) => {
  await context.addInitScript(url => { window.ENEM_API_URL = url; }, process.env.E2E_API_URL);
  await page.goto("/login");
  await page.locator("#auth-email").fill(process.env.E2E_ADMIN_EMAIL);
  await page.locator("#auth-password").fill(process.env.E2E_ADMIN_PASSWORD);
  await page.locator('#auth-form button[type="submit"]').click();
  await expect(page.locator("#auth-content")).toBeVisible();
  const tag = `Detalhe ${Date.now().toString(36)}`;
  const writes = [];
  page.on("request", request => {
    if (["POST", "PUT", "DELETE"].includes(request.method()) && /\/api\/(materias|assuntos)/.test(request.url())) writes.push(request.url());
  });
  const matter = await createMatter(page, `${tag} origem`);
  await filter(page, "materias", matter.nome);
  const second = await context.newPage();
  try {
    await test.step("Matéria: GET substitui cópia antiga sem escrita automática", async () => {
      await open(second, "/admin/materias.html");
      await filter(second, "materias", matter.nome);
      await edit(second, "materias", matter.id);
      await expect(second.locator("#materia-id")).toHaveValue(String(matter.id));
      await second.locator("#materia-nome").fill(`${tag} atual`);
      await second.locator("#materia-descricao").fill("Descrição atualizada em outra aba");
      await second.locator("#materia-area").selectOption("3");
      await response(second, `/materias/${matter.id}`, "PUT", () => second.locator("#materia-salvar").click());
      await expect(page.locator("#materias-corpo")).toContainText(matter.nome);
      const before = writes.length;
      const detail = await edit(page, "materias", matter.id);
      expect(detail.nome).toBe(`${tag} atual`);
      await expect(page.locator("#materia-nome")).toHaveValue(detail.nome);
      await expect(page.locator("#materia-descricao")).toHaveValue("Descrição atualizada em outra aba");
      await expect(page.locator("#materia-area")).toHaveValue("3");
      await expect(page.locator("#materia-nome")).toBeFocused();
      expect(writes).toHaveLength(before);
      await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
      await page.screenshot({ path: info.outputPath("materia-detalhe-atual.png"), fullPage: true });
      await response(page, `/materias/${matter.id}`, "PUT", () => page.locator("#materia-salvar").click());
    });

    let subject, destination;
    await test.step("Assunto: lista antiga e transferência explícita na segunda aba", async () => {
      await open(page, "/admin/assuntos.html");
      await page.locator("#assunto-nome").fill(`${tag} assunto`);
      await page.locator("#assunto-materia").selectOption(String(matter.id));
      subject = await response(page, "/assuntos", "POST", () => page.locator("#assunto-salvar").click(), 201);
      await filter(page, "assuntos", subject.nome);
      destination = await createMatter(second, `${tag} destino novo`);
      await open(second, "/admin/assuntos.html");
      await filter(second, "assuntos", subject.nome);
      await edit(second, "assuntos", subject.id);
      await expect(second.locator("#assunto-id")).toHaveValue(String(subject.id));
      await second.locator("#assunto-nome").fill(`${tag} assunto atual`);
      await second.locator("#assunto-descricao").fill("Assunto transferido em outra aba");
      await second.locator("#assunto-materia").selectOption(String(destination.id));
      await second.locator("#assunto-salvar").click();
      await expect(second.locator("#admin-modal")).toBeVisible();
      await response(second, `/assuntos/${subject.id}/transferir`, "POST", () => second.locator("#admin-modal-confirmar").click());
      await open(second, "/admin/materias.html");
      await filter(second, "materias", destination.nome);
      await edit(second, "materias", destination.id);
      await expect(second.locator("#materia-id")).toHaveValue(String(destination.id));
      await second.locator("#materia-status-form").selectOption("inativa");
      await response(second, `/materias/${destination.id}`, "PUT", () => second.locator("#materia-salvar").click());
    });

    await test.step("Assunto: detalhe e opções atuais mantêm origem correta no PUT", async () => {
      await expect(page.locator("#assuntos-corpo")).toContainText(subject.nome);
      const before = writes.length;
      const detail = await edit(page, "assuntos", subject.id);
      expect(detail.materia_id).toBe(destination.id);
      await expect(page.locator("#assunto-nome")).toHaveValue(`${tag} assunto atual`);
      await expect(page.locator("#assunto-descricao")).toHaveValue("Assunto transferido em outra aba");
      await expect(page.locator("#assunto-materia")).toHaveValue(String(destination.id));
      await expect(page.locator("#assunto-materia option:checked")).toHaveText(destination.nome);
      await expect(page.locator("#assunto-nome")).toBeFocused();
      expect(writes).toHaveLength(before);
      await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
      await page.screenshot({ path: info.outputPath("assunto-vinculo-atual.png"), fullPage: true });
      const saved = await response(page, `/assuntos/${subject.id}`, "PUT", () => page.locator("#assunto-salvar").click());
      expect(saved.materia_id).toBe(destination.id);
      expect(writes.slice(before).some(path => path.includes("transferir"))).toBe(false);
      await expect(page.locator("#admin-modal")).not.toBeVisible();
    });
  } finally { await second.close(); }
});
