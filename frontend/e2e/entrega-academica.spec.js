import { test, expect } from "@playwright/test";

test.beforeAll(() => {
  if (process.env.RUN_MYSQL_E2E !== "1" || !/^plataforma_enem_e2e_test_[a-f0-9]{12}$/.test(process.env.E2E_SCHEMA || "")
      || !process.env.E2E_BASE_URL || !process.env.E2E_API_URL) {
    throw new Error("Use o runner: RUN_MYSQL_E2E=1 npm run test:e2e, com MySQL real.");
  }
});
test.beforeEach(async ({ context }) => {
  // Configuração de destino; todas as chamadas continuam usando a API real.
  await context.addInitScript((url) => { window.ENEM_API_URL = url; }, process.env.E2E_API_URL);
});

async function mutacao(page, path, method, acao, status = 200) {
  const redireciona = ["/auth/login", "/auth/cadastro", "/aluno/praticas", "/aluno/tentativas-simulado"].includes(path);
  const pending = page.waitForResponse((r) => new URL(r.url()).pathname === `/api${path}` && r.request().method() === method)
    .then(async (response) => ({ status: response.status(), data: status === 204 || redireciona ? null : await response.json() }));
  await acao();
  const response = await pending;
  expect(response.status).toBe(status);
  return response.data;
}
async function consultar(page, path) {
  const response = await page.request.get(process.env.E2E_API_URL + path);
  expect(response.status()).toBe(200);
  return response.json();
}
async function abrir(page, url) {
  await page.goto(url);
  await expect(page.locator("#auth-content")).toBeVisible();
}
async function login(page, email, senha) {
  await page.goto("/login");
  await page.locator("#auth-email").fill(email);
  await page.locator("#auth-password").fill(senha);
  await mutacao(page, "/auth/login", "POST", () => page.locator('#auth-form button[type="submit"]').click());
  await expect(page.locator("#auth-content")).toBeVisible();
}

test("vinte funcionalidades com persistência e regressões de navegação", async ({ page, browser }, info) => {
  const tag = Date.now().toString(36);
  await login(page, process.env.E2E_ADMIN_EMAIL, process.env.E2E_ADMIN_PASSWORD);
  await abrir(page, "/index.html");
  const materiaCard = (id) => page.locator(`.materia-card:has([data-id="${id}"])`);
  const assuntoCard = (id) => page.locator(`.assunto-card:has([data-id="${id}"])`);
  async function cadastrarMateria(nome) {
    await page.locator("#nome").fill(nome);
    await page.locator("#materia-area-enem-id").selectOption("4");
    return mutacao(page, "/materias", "POST", () => page.locator("#salvar-button").click(), 201);
  }
  async function cadastrarAssunto(materia, nome) {
    await page.locator("#assunto-nome").fill(nome);
    await page.locator("#assunto-materia-id").selectOption(String(materia.id));
    return mutacao(page, "/assuntos", "POST", () => page.locator("#assunto-salvar-button").click(), 201);
  }
  let materia, assunto, questao, tentativa, simulado, execucao;
  await test.step("01 — Cadastrar Matéria", async () => {
    materia = await cadastrarMateria(`Matéria ${tag}`);
    await page.reload(); await expect(materiaCard(materia.id)).toContainText(materia.nome);
  });
  await test.step("02 — Listar Matérias", async () => {
    await page.locator("#recarregar-button").click();
    await expect(materiaCard(materia.id)).toBeVisible();
  });
  await test.step("03 — Atualizar Matéria", async () => {
    await materiaCard(materia.id).getByRole("button", { name: "Editar", exact: true }).click();
    await page.locator("#nome").fill(`Matéria editada ${tag}`);
    await mutacao(page, `/materias/${materia.id}`, "PUT", () => page.locator("#salvar-button").click());
    await page.reload(); await expect(materiaCard(materia.id)).toContainText(`Matéria editada ${tag}`);
  });
  await test.step("04 — Excluir Matéria sem vínculos", async () => {
    page.once("dialog", (d) => d.accept());
    await mutacao(page, `/materias/${materia.id}`, "DELETE", () => materiaCard(materia.id).getByRole("button", { name: "Excluir" }).click(), 204);
    await page.reload(); await expect(materiaCard(materia.id)).toHaveCount(0);
  });
  await test.step("Setup UI: Matéria para os próximos casos", async () => {
    materia = await cadastrarMateria(`Matemática ${tag}`);
  });
  await test.step("05 — Cadastrar Assunto", async () => {
    assunto = await cadastrarAssunto(materia, `Assunto ${tag}`);
    await page.reload(); await expect(assuntoCard(assunto.id)).toContainText(assunto.nome);
  });
  await test.step("06 — Listar Assuntos", async () => {
    await page.locator("#assuntos-recarregar-button").click();
    await expect(assuntoCard(assunto.id)).toBeVisible();
  });
  await test.step("07 — Atualizar Assunto", async () => {
    await assuntoCard(assunto.id).getByRole("button", { name: "Editar", exact: true }).click();
    await page.locator("#assunto-nome").fill(`Assunto editado ${tag}`);
    await mutacao(page, `/assuntos/${assunto.id}`, "PUT", () => page.locator("#assunto-salvar-button").click());
    await page.reload(); await expect(assuntoCard(assunto.id)).toContainText(`Assunto editado ${tag}`);
  });
  await test.step("08 — Excluir Assunto sem vínculos", async () => {
    page.once("dialog", (d) => d.accept());
    await mutacao(page, `/assuntos/${assunto.id}`, "DELETE", () => assuntoCard(assunto.id).getByRole("button", { name: "Excluir" }).click(), 204);
    await page.reload(); await expect(assuntoCard(assunto.id)).toHaveCount(0);
  });
  await test.step("Setup UI: Assunto para a Questão", async () => {
    assunto = await cadastrarAssunto(materia, `Álgebra ${tag}`);
  });
  await test.step("09 — Cadastrar Questão", async () => {
    await page.locator("#questao-assunto-id").selectOption(String(assunto.id));
    await page.locator("#questao-enunciado").fill(`Enunciado ${tag}`);
    for (const letra of ["a", "b", "c", "d", "e"]) await page.locator(`#alternativa-${letra}`).fill(`Alternativa ${letra.toUpperCase()}`);
    await page.locator("#resposta-correta").selectOption("A");
    await page.locator("#questao-dificuldade").selectOption("media");
    questao = await mutacao(page, "/questoes", "POST", () => page.locator("#questao-salvar-button").click(), 201);
  });
  await test.step("10 — Buscar Questões por Assunto", async () => {
    await page.reload();
    await page.locator("#busca-assunto-id").selectOption(String(assunto.id));
    await page.locator("#buscar-questoes-button").click();
    await expect(page.locator("#questoes-lista")).toContainText(`Enunciado ${tag}`);
  });
  await test.step("Exclusões vinculadas bloqueadas", async () => {
    for (const [path, card] of [[`/materias/${materia.id}`, materiaCard(materia.id)], [`/assuntos/${assunto.id}`, assuntoCard(assunto.id)]]) {
      page.once("dialog", (d) => d.accept());
      await mutacao(page, path, "DELETE", () => card.getByRole("button", { name: "Excluir" }).click(), 409);
      await expect(card).toBeVisible();
    }
  });

  const alunoContext = await browser.newContext({ baseURL: process.env.E2E_BASE_URL, viewport: { width: 1440, height: 1000 } });
  await alunoContext.addInitScript((url) => { window.ENEM_API_URL = url; }, process.env.E2E_API_URL);
  const aluno = await alunoContext.newPage();
  try {
    await test.step("11 — Cadastrar Aluno", async () => {
      await aluno.goto("/cadastro");
      await aluno.locator("#auth-name").fill("Aluno sintético");
      await aluno.locator("#auth-email").fill(process.env.E2E_STUDENT_EMAIL);
      await aluno.locator("#auth-password").fill(process.env.E2E_STUDENT_PASSWORD);
      await aluno.locator("#auth-confirmation").fill(process.env.E2E_STUDENT_PASSWORD);
      await mutacao(aluno, "/auth/cadastro", "POST", () => aluno.locator('#auth-form button[type="submit"]').click(), 201);
      await expect(aluno).toHaveURL(/\/login$/);
    });
    await test.step("12 — Fazer login", async () => {
      await login(aluno, process.env.E2E_STUDENT_EMAIL, process.env.E2E_STUDENT_PASSWORD);
      expect((await consultar(aluno, "/auth/sessao")).usuario.perfil).toBe("aluno");
      await aluno.reload(); await expect(aluno.locator("[data-auth-name]")).toHaveText("Aluno sintético");
    });
    await test.step("13 — Editar Questão", async () => {
      await abrir(page, `/admin/questao.html?id=${questao.id}`);
      await expect(page.locator("#questao-salvar")).toBeEnabled();
      await page.locator("#enunciado").fill(`Edição ${tag}`);
      await mutacao(page, `/questoes/${questao.id}`, "PUT", () => page.locator("#questao-salvar").click());
      await page.reload(); await expect(page.locator("#enunciado")).toHaveValue(`Edição ${tag}`);
    });
    await test.step("14 — Publicar Questão", async () => {
      await page.locator("#questao-motivo").fill("Revisão acadêmica sintética");
      await page.locator("#questao-publicar").click();
      await mutacao(page, `/questoes/${questao.id}/publicar`, "POST", () => page.locator("#admin-modal-confirmar").click());
      await page.reload(); await expect(page.locator("#questao-status")).toContainText("publicada");
    });
    await test.step("16 — Iniciar prática sem correção antecipada", async () => {
      await abrir(aluno, "/aluno/questoes.html");
      const card = aluno.locator("#pratica-lista li").filter({ hasText: `Edição ${tag}` });
      await mutacao(aluno, "/aluno/praticas", "POST", () => card.getByRole("button").click(), 201);
      await expect(aluno).toHaveURL(/tentativa_id=/);
      tentativa = await consultar(aluno, `/aluno/praticas/${new URL(aluno.url()).searchParams.get("tentativa_id")}`);
      expect(JSON.stringify(tentativa)).not.toMatch(/resposta_correta|explicacao|gabarito/);
      await expect(aluno).toHaveURL(/tentativa_id=/);
      await aluno.reload(); await expect(aluno.locator("#pratica-enunciado")).toHaveText(`Edição ${tag}`);
      await expect(aluno.locator("#pratica-resultado")).toBeHidden();
    });
    await test.step("17 — Responder com correção persistida", async () => {
      await aluno.locator('input[value="A"]').check();
      await mutacao(aluno, `/aluno/praticas/${tentativa.id}/resposta`, "POST", () => aluno.locator("#pratica-enviar").click());
      await aluno.reload(); await expect(aluno.locator("#pratica-resultado")).toBeVisible();
      await expect(aluno.locator("#pratica-correcao")).toContainText("A");
    });
    await test.step("18 — Consultar histórico", async () => {
      await abrir(aluno, "/aluno/historico.html");
      await expect(aluno.locator("#pratica-lista")).toContainText(assunto.nome);
      await expect(aluno.locator("#pratica-lista")).toContainText("Resposta correta");
      await aluno.reload(); await expect(aluno.locator(`a[href*="tentativa_id=${tentativa.id}"]`)).toBeVisible();
    });
    await test.step("19 — Criar Simulado manual", async () => {
      await abrir(page, "/admin/simulado.html");
      await page.locator("#titulo").fill(`Simulado ${tag}`);
      await page.locator("#sim-questoes li").filter({ hasText: `Edição ${tag}` }).getByRole("button").click();
      simulado = await mutacao(page, "/admin/simulados", "POST", () => page.locator("#sim-salvar").click(), 201);
      await expect(page).toHaveURL(new RegExp(`simulado.html\\?id=${simulado.id}$`));
      await page.reload(); await expect(page.locator("#titulo")).toHaveValue(`Simulado ${tag}`);
      await expect(page.locator("#sim-selecao li")).toHaveCount(1);
    });
    await test.step("20 — Consultar desempenho por Matéria/Assunto", async () => {
      await abrir(aluno, "/aluno/desempenho.html");
      await expect(aluno.locator("#dash-materias")).toContainText(materia.nome);
      await expect(aluno.locator("#dash-assuntos")).toContainText(assunto.nome);
      await aluno.reload(); await expect(aluno.locator("#dash-geral")).toContainText("100%");
    });
    await test.step("Setup UI: publicar/iniciar Simulado para smoke da execução", async () => {
      await page.locator("#sim-motivo").fill("Publicação sintética para regressão");
      await page.locator("#sim-publicar").click();
      await mutacao(page, `/admin/simulados/${simulado.id}/publicar`, "POST", () => page.locator("#admin-modal-confirmar").click());
      await abrir(aluno, "/aluno/simulados.html");
      await mutacao(aluno, "/aluno/tentativas-simulado", "POST", () => aluno.locator("#sim-lista li").filter({ hasText: `Simulado ${tag}` }).getByRole("button").click(), 201);
      await expect(aluno).toHaveURL(/tentativa_id=/);
      execucao = await consultar(aluno, `/aluno/tentativas-simulado/${new URL(aluno.url()).searchParams.get("tentativa_id")}`);
    });
    await test.step("Plano: cancelamento de descarte mantém alternativa local", async () => {
      await expect(aluno.locator('input[value="B"]')).toBeVisible();
      await aluno.locator('input[value="B"]').check();
      const destino = aluno.url();
      aluno.once("dialog", (d) => d.dismiss());
      await aluno.locator('[data-navigation] a[href="/aluno/plano.html"]').click();
      await expect(aluno).toHaveURL(destino); await expect(aluno.locator('input[value="B"]')).toBeChecked();
      aluno.once("dialog", (d) => d.accept());
      await aluno.locator('[data-navigation] a[href="/aluno/plano.html"]').click();
      await expect(aluno).toHaveURL(/\/aluno\/plano.html$/);
    });
    await test.step("15 — Arquivar Questão preservando histórico", async () => {
      await abrir(page, `/admin/questao.html?id=${questao.id}`);
      await page.locator("#questao-motivo").fill("Retirada sintética com histórico preservado");
      await page.locator("#questao-arquivar").click();
      await mutacao(page, `/questoes/${questao.id}/arquivar`, "POST", () => page.locator("#admin-modal-confirmar").click());
      await page.reload(); await expect(page.locator("#questao-status")).toContainText("arquivada");
      await abrir(aluno, `/aluno/questao.html?tentativa_id=${tentativa.id}`);
      await expect(aluno.locator("#pratica-correcao")).toContainText("A");
    });
    await test.step("Smoke de oito páginas, teclado e capturas 1440/390", async () => {
      for (const file of ["inicio", "questoes", `questao?tentativa_id=${tentativa.id}`, "historico", "simulados", `simulado?tentativa_id=${execucao.id}`, "desempenho", "plano"]) {
        const [name, query] = file.split("?");
        await abrir(aluno, `/aluno/${name}.html${query ? "?" + query : ""}`);
        const plano = aluno.locator('[data-navigation] a[href="/aluno/plano.html"]');
        await expect(plano).toBeVisible(); await expect(aluno.locator('[data-navigation] [aria-current="page"]')).toHaveCount(1);
        await plano.focus(); await aluno.keyboard.press("Tab"); await aluno.keyboard.press("Shift+Tab");
        await expect(plano).toBeFocused();
        expect(await plano.evaluate((node) => getComputedStyle(node).outlineStyle)).not.toBe("none");
        await plano.press("Enter"); await expect(aluno).toHaveURL(/\/aluno\/plano.html$/);
      }
      for (const width of [1440, 390]) {
        await aluno.setViewportSize({ width, height: 1000 });
        await expect(aluno.locator("#plano-status")).toContainText("Gere seu plano");
        await expect(aluno.locator("h1")).toBeVisible();
        await aluno.screenshot({ path: info.outputPath(`plano-${width}.png`), fullPage: true });
        await page.setViewportSize({ width, height: 1000 });
        await abrir(page, "/admin/materias.html");
        await expect(page.locator("#materias-corpo")).toContainText(materia.nome);
        await expect(page.locator("h1")).toBeVisible();
        await page.screenshot({ path: info.outputPath(`admin-${width}.png`), fullPage: true });
      }
    });
  } finally {
    await alunoContext.close();
  }
});
