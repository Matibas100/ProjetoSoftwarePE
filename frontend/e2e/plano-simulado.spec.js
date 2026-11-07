import { randomUUID } from "node:crypto";
import { test, expect } from "@playwright/test";

test.beforeAll(() => {
  if (process.env.RUN_MYSQL_E2E !== "1" || !/^plataforma_enem_e2e_test_[a-f0-9]{12}$/.test(process.env.E2E_SCHEMA || "")
      || !process.env.E2E_BASE_URL || !process.env.E2E_API_URL) {
    throw new Error("Use o runner: RUN_MYSQL_E2E=1 npm run test:e2e, com MySQL real.");
  }
});

async function mutacao(page, path, method, acao, status = 200) {
  const redireciona = ["/auth/login", "/auth/cadastro", "/aluno/praticas", "/aluno/tentativas-simulado"].includes(path);
  const pending = page.waitForResponse((r) => new URL(r.url()).pathname === `/api${path}` && r.request().method() === method)
    .then(async (r) => ({ status: r.status(), data: redireciona ? null : await r.json() }));
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

async function abrir(page, path) {
  await page.goto(path);
  await expect(page.locator("#auth-content")).toBeVisible();
}

async function login(page, email, senha) {
  await page.goto("/login");
  await page.locator("#auth-email").fill(email);
  await page.locator("#auth-password").fill(senha);
  await mutacao(page, "/auth/login", "POST", () => page.locator('#auth-form button[type="submit"]').click());
  await expect(page.locator("#auth-content")).toBeVisible();
}

function conferirDiagnostico(data, total, acertos, percentual, base) {
  const metricas = { total_respostas: total, acertos, erros: total - acertos, percentual_acerto: percentual, base };
  expect(data.base).toEqual(base);
  expect(data.geral).toMatchObject(metricas);
  expect(data.materias).toHaveLength(1);
  expect(data.assuntos).toHaveLength(1);
  expect(data.materias[0]).toMatchObject(metricas);
  expect(data.assuntos[0]).toMatchObject(metricas);
}

test("Plano e Simulado: geração, conclusão, finalização e recálculo persistidos", async ({ browser }) => {
  const tag = randomUUID().replaceAll("-", "");
  const email = `plano-simulado-${tag}@teste.local`;
  const senha = process.env.E2E_STUDENT_PASSWORD;
  let adminContext, alunoContext;
  try {
    adminContext = await browser.newContext({ baseURL: process.env.E2E_BASE_URL });
    alunoContext = await browser.newContext({ baseURL: process.env.E2E_BASE_URL });
    for (const context of [adminContext, alunoContext]) {
      // Somente o destino é configurado; sessão e fatos vêm dos fluxos reais.
      await context.addInitScript((url) => { window.ENEM_API_URL = url; }, process.env.E2E_API_URL);
    }
    const admin = await adminContext.newPage(), aluno = await alunoContext.newPage();
    let materia, assunto, simulado, tentativa, plano1, plano1Concluido, plano2, corpoGeracao;
    const questoes = [];

    await test.step("Preparação pela UI: catálogo próprio, três Questões A e Simulado publicado", async () => {
      await login(admin, process.env.E2E_ADMIN_EMAIL, process.env.E2E_ADMIN_PASSWORD);
      await abrir(admin, "/index.html");
      await admin.locator("#nome").fill(`Matéria plano ${tag}`);
      await admin.locator("#materia-area-enem-id").selectOption("4");
      materia = await mutacao(admin, "/materias", "POST", () => admin.locator("#salvar-button").click(), 201);
      await admin.locator("#assunto-nome").fill(`Assunto plano ${tag}`);
      await admin.locator("#assunto-materia-id").selectOption(String(materia.id));
      assunto = await mutacao(admin, "/assuntos", "POST", () => admin.locator("#assunto-salvar-button").click(), 201);
      for (let i = 1; i <= 3; i++) {
        await abrir(admin, "/index.html");
        await admin.locator("#questao-assunto-id").selectOption(String(assunto.id));
        const enunciado = `Questão plano ${tag} número ${i}`;
        await admin.locator("#questao-enunciado").fill(enunciado);
        for (const letra of "abcde") await admin.locator(`#alternativa-${letra}`).fill(`Alternativa ${letra.toUpperCase()}`);
        await admin.locator("#resposta-correta").selectOption("A");
        await admin.locator("#questao-dificuldade").selectOption("media");
        const q = await mutacao(admin, "/questoes", "POST", () => admin.locator("#questao-salvar-button").click(), 201);
        questoes.push({ id: q.id, enunciado });
        await abrir(admin, `/admin/questao.html?id=${q.id}`);
        await expect(admin.locator("#enunciado")).toHaveValue(enunciado);
        await admin.locator("#questao-motivo").fill("Revisão sintética para Plano e Simulado");
        await admin.locator("#questao-publicar").click();
        await mutacao(admin, `/questoes/${q.id}/publicar`, "POST", () => admin.locator("#admin-modal-confirmar").click());
        await expect(admin.locator("#questao-status")).toContainText("publicada");
      }
      await abrir(admin, "/admin/simulado.html");
      await expect(admin.locator("#sim-salvar")).toBeEnabled();
      await admin.locator("#busca").fill(tag);
      await admin.locator("#sim-busca-form").getByRole("button", { name: "Buscar", exact: true }).click();
      await expect(admin.locator("#sim-questoes li")).toHaveCount(3);
      await admin.locator("#titulo").fill(`Simulado plano ${tag}`);
      for (const q of questoes) {
        await admin.locator("#sim-questoes li").filter({ hasText: q.enunciado }).getByRole("button", { name: "Adicionar" }).click();
      }
      simulado = await mutacao(admin, "/admin/simulados", "POST", () => admin.locator("#sim-salvar").click(), 201);
      await expect(admin.locator("#sim-revisao")).toContainText(`Simulado ${simulado.id}`);
      await admin.locator("#sim-motivo").fill("Composição de três Questões revisada");
      await admin.locator("#sim-publicar").click();
      await mutacao(admin, `/admin/simulados/${simulado.id}/publicar`, "POST", () => admin.locator("#admin-modal-confirmar").click());
      await expect(admin.locator("#sim-revisao")).toContainText("publicado");
      await admin.reload();
      await expect(admin.locator("#sim-selecao li")).toHaveCount(3);
    });

    await test.step("Cadastro e login pela UI: Aluno exclusivo deste teste", async () => {
      await aluno.goto("/cadastro");
      await aluno.locator("#auth-name").fill("Aluno Plano Simulado");
      await aluno.locator("#auth-email").fill(email);
      await aluno.locator("#auth-password").fill(senha);
      await aluno.locator("#auth-confirmation").fill(senha);
      await aluno.locator("#auth-terms").check();
      await mutacao(aluno, "/auth/cadastro", "POST", () => aluno.locator('#auth-form button[type="submit"]').click(), 201);
      await expect(aluno).toHaveURL(/\/login$/);
      await login(aluno, email, senha);
      expect((await consultar(aluno, "/auth/sessao")).usuario.perfil).toBe("aluno");
      await abrir(aluno, "/aluno/privacidade.html");
      await mutacao(aluno, "/aluno/privacidade/consentimento-plano/aceitar", "POST", () => aluno.locator("#privacidade-aceitar").click(), 201);
      await expect(aluno.locator("#privacidade-plano")).toContainText("Plano liberado");
    });

    async function praticar(alternativa) {
      await abrir(aluno, `/aluno/questoes.html?assunto_id=${assunto.id}`);
      const card = aluno.locator("#pratica-lista li").filter({ hasText: questoes[0].enunciado });
      await mutacao(aluno, "/aluno/praticas", "POST", () => card.getByRole("button").click(), 201);
      await expect(aluno).toHaveURL(/tentativa_id=/);
      const id = new URL(aluno.url()).searchParams.get("tentativa_id");
      await aluno.locator(`#pratica-alternativas input[value="${alternativa}"]`).check();
      const resposta = await mutacao(aluno, `/aluno/praticas/${id}/resposta`, "POST", () => aluno.locator("#pratica-enviar").click());
      expect(resposta).toMatchObject({ id: Number(id), estado: "respondida", correta: alternativa === "A" });
      await expect(aluno.locator("#pratica-status")).toHaveText("Resposta salva. Consulte sua correção abaixo.");
    }

    await test.step("Quatro práticas reais: 2/4 e geração sem base, sem plano vazio", async () => {
      for (const alternativa of ["A", "A", "B", "B"]) await praticar(alternativa);
      conferirDiagnostico(await consultar(aluno, "/aluno/desempenho"), 4, 2, 50, { pratica: 4, simulado: 0 });
      await abrir(aluno, "/aluno/plano.html");
      const data = await mutacao(aluno, "/aluno/plano/gerar", "POST", () => aluno.locator("#plano-gerar").click());
      expect(data).toMatchObject({ estado: "sem_base_suficiente", plano: null });
      await expect(aluno.locator("#plano-status")).toContainText("Base insuficiente");
      expect(await consultar(aluno, "/aluno/plano")).toEqual({ estado: "sem_plano", plano: null });
      await aluno.reload();
      await expect(aluno.locator("#plano-gerar")).toBeVisible();
      await expect(aluno.locator("#plano-lista li")).toHaveCount(0);
      expect(await consultar(aluno, "/aluno/plano")).toEqual({ estado: "sem_plano", plano: null });
    });

    await test.step("Quinta prática B e geração 1: snapshot 2/5, 40%, persistido", async () => {
      await praticar("B");
      await abrir(aluno, "/aluno/plano.html");
      const request = aluno.waitForRequest((r) => new URL(r.url()).pathname === "/api/aluno/plano/gerar" && r.method() === "POST");
      const data = await mutacao(aluno, "/aluno/plano/gerar", "POST", () => aluno.locator("#plano-gerar").click(), 201);
      // Corpo/chave permanecem só em memória para o replay auxiliar de histórico.
      corpoGeracao = (await request).postDataJSON();
      plano1 = data.plano;
      expect(plano1).toMatchObject({ geracao: 1, atual: true });
      expect(plano1.itens).toHaveLength(1);
      expect(plano1.itens[0]).toMatchObject({ estado: "pendente", concluido_em: null, assunto_id: assunto.id, materia_id: materia.id,
        snapshot: { acertos: 2, total_respostas: 5, percentual_acerto: 40, limiar_amostra: 5 } });
      expect(plano1.itens[0].snapshot.justificativa).toContain("2 acertos em 5 respostas");
      await expect(aluno.locator("#plano-lista")).toContainText(plano1.itens[0].snapshot.justificativa);
      expect((await consultar(aluno, "/aluno/plano")).plano).toEqual(plano1);
      await aluno.reload();
      await expect(aluno.locator("#plano-meta")).toContainText("Geração 1");
      await expect(aluno.locator("#plano-lista")).toContainText("40% de acerto");
      expect((await consultar(aluno, "/aluno/plano")).plano).toEqual(plano1);
    });

    await test.step("Conclusão manual: estado/data persistidos, diagnóstico continua 2/5", async () => {
      const item = await mutacao(aluno, `/aluno/plano/itens/${plano1.itens[0].id}/concluir`, "POST",
        () => aluno.getByRole("button", { name: "Marcar como concluído" }).click());
      expect(item).toMatchObject({ id: plano1.itens[0].id, estado: "concluido", snapshot: plano1.itens[0].snapshot });
      expect(item.concluido_em).toMatch(/^\d{4}-\d{2}-\d{2}T.+Z$/);
      await expect(aluno.locator("#plano-status")).toContainText("Suas respostas e seu desempenho foram preservados");
      plano1Concluido = { ...plano1, itens: [item] };
      await aluno.reload();
      await expect(aluno.locator('#plano-lista li[data-concluido="true"]')).toHaveCount(1);
      await expect(aluno.locator("#plano-lista")).toContainText("Concluído em");
      await expect(aluno.locator(".plano-explicacao")).toContainText("não comprova dificuldade ou domínio");
      expect((await consultar(aluno, "/aluno/plano")).plano).toEqual(plano1Concluido);
      conferirDiagnostico(await consultar(aluno, "/aluno/desempenho"), 5, 2, 40, { pratica: 5, simulado: 0 });
    });

    await test.step("Simulado: salvar A/B/branco, recarregar e cancelar finalização sem POST", async () => {
      await abrir(aluno, "/aluno/simulados.html");
      const card = aluno.locator("#sim-lista li").filter({ hasText: simulado.titulo });
      await mutacao(aluno, "/aluno/tentativas-simulado", "POST", () => card.getByRole("button", { name: "Iniciar simulado" }).click(), 201);
      await expect(aluno).toHaveURL(/tentativa_id=/);
      const id = new URL(aluno.url()).searchParams.get("tentativa_id");
      tentativa = await consultar(aluno, `/aluno/tentativas-simulado/${id}`);
      expect(tentativa.itens.map((i) => i.questao.enunciado)).toEqual(questoes.map((q) => q.enunciado));
      for (const [index, alternativa] of [[0, "A"], [1, "B"]]) {
        await aluno.locator("#sim-mapa button").nth(index).click();
        await aluno.locator(`#sim-alternativas input[value="${alternativa}"]`).check();
        await mutacao(aluno, `/aluno/tentativas-simulado/${id}/respostas/${tentativa.itens[index].item_id}`, "PUT",
          () => aluno.locator("#sim-salvar").click());
        await expect(aluno.locator("#sim-status")).toHaveText("Resposta salva no servidor.");
      }
      await aluno.reload();
      await expect(aluno.locator('#sim-alternativas input[value="A"]')).toBeChecked();
      await aluno.locator("#sim-mapa button").nth(1).click();
      await expect(aluno.locator('#sim-alternativas input[value="B"]')).toBeChecked();
      await aluno.locator("#sim-mapa button").nth(2).click();
      await expect(aluno.locator("#sim-alternativas input:checked")).toHaveCount(0);
      await expect(aluno.locator("#sim-feedback")).toBeHidden();
      await expect(aluno.locator("#sim-resultado")).toBeHidden();
      const detalhe = await consultar(aluno, `/aluno/tentativas-simulado/${id}`);
      expect(detalhe.estado).toBe("em_andamento");
      expect(detalhe.itens.map((i) => i.alternativa)).toEqual(["A", "B", null]);
      expect(JSON.stringify(detalhe)).not.toMatch(/gabarito|resposta_correta|explicacao|"correta"/);
      conferirDiagnostico(await consultar(aluno, "/aluno/desempenho"), 5, 2, 40, { pratica: 5, simulado: 0 });
      let posts = 0;
      const observar = (r) => { if (r.method() === "POST" && new URL(r.url()).pathname === `/api/aluno/tentativas-simulado/${id}/finalizar`) posts++; };
      aluno.on("request", observar);
      try {
        await aluno.locator("#sim-finalizar").click();
        await expect(aluno.locator("#sim-confirmar-texto")).toContainText("1 Questão(ões) em branco");
        await aluno.locator("#sim-confirmar-cancelar").click();
        await expect(aluno.locator("#sim-confirmacao")).not.toBeVisible();
        await expect(aluno.locator("#sim-finalizar")).toBeFocused();
        expect((await consultar(aluno, `/aluno/tentativas-simulado/${id}`)).estado).toBe("em_andamento");
        expect(posts).toBe(0);
      } finally { aluno.off("request", observar); }
    });

    await test.step("Finalizar pela UI: 1 acerto/1 erro/1 branco, resultado 33,33% e correção bloqueada", async () => {
      const path = `/aluno/tentativas-simulado/${tentativa.id}`;
      await aluno.locator("#sim-finalizar").click();
      const resultado = await mutacao(aluno, `${path}/finalizar`, "POST", () => aluno.locator("#sim-confirmar").click());
      expect(resultado).toMatchObject({ total: 3, respondidas: 2, acertos: 1, erros: 1, em_branco: 1, percentual_acerto: 33.33 });
      await expect(aluno.locator("#sim-resultado-titulo")).toBeFocused();
      await expect(aluno.locator("#sim-totais")).toContainText("33.33% · 1 acertos · 1 erros · 1 em branco · 3 Questões");
      expect((await consultar(aluno, path)).resultado).toEqual(resultado);
      await aluno.reload();
      await expect(aluno.locator("#sim-resultado")).toBeVisible();
      expect((await consultar(aluno, path)).resultado).toEqual(resultado);
      await aluno.locator("#sim-correcao").click();
      await expect(aluno.locator("#sim-titulo")).toHaveText("Correção do simulado");
      for (const [index, feedback] of [[0, "Resposta correta"], [1, "Resposta incorreta"], [2, "Em branco"]]) {
        await aluno.locator("#sim-mapa button").nth(index).click();
        await expect(aluno.locator("#sim-enunciado")).toHaveText(questoes[index].enunciado);
        await expect(aluno.locator("#sim-feedback-titulo")).toHaveText(feedback);
        await expect(aluno.locator("#sim-gabarito")).toHaveText(`Sua resposta: ${["A", "B", "Em branco"][index]} · Gabarito: A`);
        await expect(aluno.locator("#sim-alternativas input:disabled")).toHaveCount(5);
        await expect(aluno.locator("#sim-salvar")).toBeHidden();
        await expect(aluno.locator("#sim-limpar")).toBeHidden();
      }
    });

    await test.step("Desempenho pela tela/API: 3/7, 42,86%, base 5 práticas + 2 respostas do Simulado", async () => {
      await abrir(aluno, "/aluno/desempenho.html");
      const metricas = [["Respostas concluídas", "7"], ["Acertos", "3"], ["Erros", "4"], ["Percentual de acerto", "42,86%"]];
      for (const [titulo, valor] of metricas) {
        await expect(aluno.locator("#dash-geral article").filter({ has: aluno.getByText(titulo, { exact: true }) }).locator("strong")).toHaveText(valor);
      }
      await expect(aluno.locator("#dash-meta")).toContainText("5 respostas de práticas e 2 de simulados");
      await expect(aluno.locator("#dash-assuntos tbody tr")).toContainText(assunto.nome);
      await expect(aluno.locator("#dash-assuntos tbody tr")).toContainText("42,86%");
      conferirDiagnostico(await consultar(aluno, "/aluno/desempenho"), 7, 3, 42.86, { pratica: 5, simulado: 2 });
    });

    await test.step("Plano preservado; cancelar recálculo sem POST e confirmar geração 2 com snapshot 3/7", async () => {
      await abrir(aluno, "/aluno/plano.html");
      await expect(aluno.locator("#plano-meta")).toContainText("Geração 1");
      await expect(aluno.locator('#plano-lista li[data-concluido="true"]')).toContainText("40% de acerto");
      expect((await consultar(aluno, "/aluno/plano")).plano).toEqual(plano1Concluido);
      let posts = 0;
      const observar = (r) => { if (r.method() === "POST" && new URL(r.url()).pathname === "/api/aluno/plano/recalcular") posts++; };
      aluno.on("request", observar);
      try {
        await aluno.locator("#plano-recalcular").click();
        await expect(aluno.locator("#plano-confirmacao")).toBeVisible();
        await aluno.locator("#plano-cancelar").click();
        await expect(aluno.locator("#plano-confirmacao")).not.toBeVisible();
        await expect(aluno.locator("#plano-recalcular")).toBeFocused();
        expect((await consultar(aluno, "/aluno/plano")).plano).toEqual(plano1Concluido);
        expect(posts).toBe(0);
      } finally { aluno.off("request", observar); }
      await aluno.locator("#plano-recalcular").click();
      plano2 = (await mutacao(aluno, "/aluno/plano/recalcular", "POST", () => aluno.locator("#plano-confirmar").click(), 201)).plano;
      expect(plano2.id).not.toBe(plano1.id);
      expect(plano2).toMatchObject({ geracao: 2, atual: true });
      expect(plano2.itens).toHaveLength(1);
      expect(plano2.itens[0]).toMatchObject({ estado: "pendente", concluido_em: null,
        snapshot: { acertos: 3, total_respostas: 7, percentual_acerto: 42.86 } });
      await expect(aluno.locator("#plano-meta")).toContainText("Geração 2");
      await expect(aluno.locator("#plano-lista")).toContainText("42,86% de acerto");
      expect((await consultar(aluno, "/aluno/plano")).plano).toEqual(plano2);
      await aluno.reload();
      await expect(aluno.locator("#plano-meta")).toContainText("Geração 2");
      await expect(aluno.locator('#plano-lista li[data-concluido="false"]')).toHaveCount(1);
      expect((await consultar(aluno, "/aluno/plano")).plano).toEqual(plano2);
    });

    await test.step("Auxiliar técnico de histórico: replay HTTP da geração 1, sem botão e sem trocar geração 2", async () => {
      // Única mutação auxiliar: reutiliza corpo/chave originais via HTTP real e CSRF.
      // Não substitui a geração nem o recálculo realizados pela interface acima.
      const historico = await mutacao(aluno, "/aluno/plano/gerar", "POST",
        () => aluno.evaluate((body) => apiRequest("/aluno/plano/gerar", { method: "POST", body: JSON.stringify(body) }), corpoGeracao));
      expect(historico.plano).toEqual({ ...plano1Concluido, atual: false });
      expect((await consultar(aluno, "/aluno/plano")).plano).toEqual(plano2);
      await expect(aluno.locator("#plano-meta")).toContainText("Geração 2");
    });
  } finally {
    try { await alunoContext?.close(); } finally { await adminContext?.close(); }
  }
});
