import { randomUUID } from "node:crypto";
import { test, expect } from "@playwright/test";

test.beforeAll(() => {
  if (process.env.RUN_MYSQL_E2E !== "1" || !/^plataforma_enem_e2e_test_[a-f0-9]{12}$/.test(process.env.E2E_SCHEMA || "")) throw new Error("Use o runner E2E com MySQL descartável real.");
});
async function mutate(page, path, method, action, status = 200) {
  const response = page.waitForResponse(r => new URL(r.url()).pathname === `/api${path}` && r.request().method() === method);
  await action(); const r = await response; expect(r.status()).toBe(status);
  if (["/auth/cadastro", "/auth/login", "/aluno/praticas", "/aluno/tentativas-simulado"].includes(path)) return null;
  return r.json();
}
async function get(page, path) {
  const r=await page.request.get(process.env.E2E_API_URL+path); expect(r.status()).toBe(200);return r.json();
}
async function open(page, url) { await page.goto(url);await expect(page.locator("#auth-content")).toBeVisible(); }
async function login(page,email,password) {
  await page.goto("/login");await page.locator("#auth-email").fill(email);await page.locator("#auth-password").fill(password);
  await mutate(page,"/auth/login","POST",()=>page.locator('#auth-form button[type="submit"]').click());
  await expect(page.locator("#auth-content")).toBeVisible();
}

test("Privacidade independente: documentos, recusa, estudo real, autorização, eliminação e nova autorização", async ({ browser }, info) => {
  const contexts=[];
  const tag=randomUUID().replaceAll("-",""); const email=`privacidade-${tag}@teste.local`;
  async function context(options={}) {
    const c=await browser.newContext({baseURL:process.env.E2E_BASE_URL,...options});contexts.push(c);
    await c.addInitScript(url=>{window.ENEM_API_URL=url;},process.env.E2E_API_URL);return c;
  }
  try {
    const publicContext=await context({javaScriptEnabled:false});const publicPage=await publicContext.newPage();
    for(const name of ["termo-de-uso-v1","termo-de-consentimento-plano-v1"]) {
      for(const width of [1440,390]) {
        await publicPage.setViewportSize({width,height:900});
        const r=await publicPage.goto(`/legal/${name}.html`);expect(r.status()).toBe(200);
        await expect(publicPage.locator("h1")).toBeVisible();await publicPage.keyboard.press("Tab");
        await expect(publicPage.locator('a[href="/cadastro"]').first()).toBeFocused();
        await publicPage.screenshot({path:info.outputPath(`${name}-${width}.png`),fullPage:true});
      }
    }
    const admin=await (await context()).newPage();const studentContext=await context();const aluno=await studentContext.newPage();
    let materia,assunto,questao,simulado,attempt,original;
    await test.step("Catálogo sintético pela interface",async()=>{
      await login(admin,process.env.E2E_ADMIN_EMAIL,process.env.E2E_ADMIN_PASSWORD);await open(admin,"/index.html");
      await admin.locator("#nome").fill(`Privacidade ${tag}`);await admin.locator("#materia-area-enem-id").selectOption("4");
      materia=await mutate(admin,"/materias","POST",()=>admin.locator("#salvar-button").click(),201);
      await admin.locator("#assunto-nome").fill(`Assunto ${tag}`);await admin.locator("#assunto-materia-id").selectOption(String(materia.id));
      assunto=await mutate(admin,"/assuntos","POST",()=>admin.locator("#assunto-salvar-button").click(),201);
      await admin.locator("#questao-assunto-id").selectOption(String(assunto.id));await admin.locator("#questao-enunciado").fill(`Questão privacidade ${tag}`);
      for(const letter of "abcde")await admin.locator(`#alternativa-${letter}`).fill(`Alternativa ${letter}`);
      await admin.locator("#resposta-correta").selectOption("A");await admin.locator("#questao-dificuldade").selectOption("media");
      questao=await mutate(admin,"/questoes","POST",()=>admin.locator("#questao-salvar-button").click(),201);
      await open(admin,`/admin/questao.html?id=${questao.id}`);await admin.locator("#questao-motivo").fill("Revisão acadêmica sintética");
      await admin.locator("#questao-publicar").click();await mutate(admin,`/questoes/${questao.id}/publicar`,"POST",()=>admin.locator("#admin-modal-confirmar").click());
      await open(admin,"/admin/simulado.html");await admin.locator("#busca").fill(tag);
      await admin.locator("#sim-busca-form").getByRole("button",{name:"Buscar",exact:true}).click();
      await expect(admin.locator("#sim-questoes li")).toHaveCount(1);await admin.locator("#sim-questoes li").getByRole("button",{name:"Adicionar"}).click();
      await admin.locator("#titulo").fill(`Simulado privacidade ${tag}`);
      simulado=await mutate(admin,"/admin/simulados","POST",()=>admin.locator("#sim-salvar").click(),201);
      await admin.locator("#sim-motivo").fill("Revisão acadêmica sintética");await admin.locator("#sim-publicar").click();
      await mutate(admin,`/admin/simulados/${simulado.id}/publicar`,"POST",()=>admin.locator("#admin-modal-confirmar").click());
    });
    await test.step("Cadastro explícito e recusa por teclado",async()=>{
      await aluno.goto("/cadastro");await expect(aluno.locator("#auth-terms")).not.toBeChecked();
      await aluno.locator("#auth-name").fill("Aluno Privacidade");await aluno.locator("#auth-email").fill(email);
      await aluno.locator("#auth-password").fill(process.env.E2E_STUDENT_PASSWORD);await aluno.locator("#auth-confirmation").fill(process.env.E2E_STUDENT_PASSWORD);
      await aluno.locator("#auth-terms").focus();await aluno.keyboard.press("Space");
      await mutate(aluno,"/auth/cadastro","POST",()=>aluno.locator('#auth-form button[type="submit"]').click(),201);
      await expect(aluno).toHaveURL(/\/login$/);await login(aluno,email,process.env.E2E_STUDENT_PASSWORD);
      await aluno.getByRole("link",{name:"Privacidade e termos",exact:true}).first().click();
      await expect(aluno.locator("#privacidade-plano")).toContainText("Sem decisão");
      await aluno.locator("#privacidade-recusar").focus();await aluno.keyboard.press("Enter");
      await expect(aluno.locator("#privacidade-cancelar")).toBeFocused();await aluno.keyboard.press("Escape");
      expect((await get(aluno,"/aluno/privacidade")).consentimento_plano.estado).toBe("nao_informado");
      await aluno.locator("#privacidade-recusar").click();
      await mutate(aluno,"/aluno/privacidade/consentimento-plano/recusar","POST",()=>aluno.locator("#privacidade-confirmar").click(),201);
      await expect(aluno.locator("#privacidade-plano")).toContainText("Recusado");
      for(const width of [1440,390]) {
        await aluno.setViewportSize({width,height:1000});
        expect(await aluno.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
        await aluno.screenshot({path:info.outputPath(`privacidade-${width}.png`),fullPage:true});
      }
      await aluno.setViewportSize({width:1440,height:1000});
    });
    await test.step("Recusa mantém práticas e simulado; base com respostas reais",async()=>{
      for(let n=0;n<5;n++) {
        await open(aluno,`/aluno/questoes.html?assunto_id=${assunto.id}`);
        await mutate(aluno,"/aluno/praticas","POST",()=>aluno.locator("#pratica-lista li").filter({hasText:tag}).getByRole("button").click(),201);
        await expect(aluno).toHaveURL(/tentativa_id=/);const id=new URL(aluno.url()).searchParams.get("tentativa_id");
        await aluno.locator('#pratica-alternativas input[value="B"]').check();await mutate(aluno,`/aluno/praticas/${id}/resposta`,"POST",()=>aluno.locator("#pratica-enviar").click());
      }
      await open(aluno,"/aluno/simulados.html");await mutate(aluno,"/aluno/tentativas-simulado","POST",()=>aluno.locator("#sim-lista li").filter({hasText:simulado.titulo}).getByRole("button",{name:"Iniciar simulado"}).click(),201);
      await expect(aluno).toHaveURL(/tentativa_id=/);attempt=new URL(aluno.url()).searchParams.get("tentativa_id");
      const detail=await get(aluno,`/aluno/tentativas-simulado/${attempt}`);await aluno.locator('#sim-alternativas input[value="A"]').check();
      await mutate(aluno,`/aluno/tentativas-simulado/${attempt}/respostas/${detail.itens[0].item_id}`,"PUT",()=>aluno.locator("#sim-salvar").click());
      await aluno.locator("#sim-finalizar").click();await mutate(aluno,`/aluno/tentativas-simulado/${attempt}/finalizar`,"POST",()=>aluno.locator("#sim-confirmar").click());
      expect((await get(aluno,"/aluno/desempenho")).geral.total_respostas).toBe(6);
      await open(aluno,"/aluno/plano.html");await expect(aluno.locator("#plano-privacidade")).toBeVisible();await expect(aluno.locator("#plano-lista li")).toHaveCount(0);
    });
    await test.step("Autorizar, gerar, concluir e revogar com plano aberto em outra aba",async()=>{
      await open(aluno,"/aluno/privacidade.html");await mutate(aluno,"/aluno/privacidade/consentimento-plano/aceitar","POST",()=>aluno.locator("#privacidade-aceitar").click(),201);
      await open(aluno,"/aluno/plano.html");original=(await mutate(aluno,"/aluno/plano/gerar","POST",()=>aluno.locator("#plano-gerar").click(),201)).plano;
      await mutate(aluno,`/aluno/plano/itens/${original.itens[0].id}/concluir`,"POST",()=>aluno.locator("#plano-lista button").click());
      await expect(aluno.locator("#plano-lista")).toContainText("Concluído em");
      const aba=await studentContext.newPage();await open(aba,"/aluno/privacidade.html");await aba.bringToFront();
      await aba.locator("#privacidade-revogar").click();await mutate(aba,"/aluno/privacidade/consentimento-plano/revogar","POST",()=>aba.locator("#privacidade-confirmar").click(),201);
      await expect(aba.locator("#privacidade-plano")).toContainText("Revogado");
      await aluno.bringToFront();
      // Headless nem sempre emite foco ao ativar uma aba. Disparar o evento de
      // retorno mantém todas as consultas/decisões na API e no MySQL reais.
      await aluno.evaluate(() => window.dispatchEvent(new Event("focus")));
      await expect(aluno.locator("#plano-privacidade")).toBeVisible();await expect(aluno.locator("#plano-lista li")).toHaveCount(0);
      expect((await get(aluno,`/aluno/tentativas-simulado/${attempt}`)).estado).toBe("finalizada");
      expect((await get(aluno,"/aluno/desempenho")).geral.total_respostas).toBe(6);
      await open(aluno,"/aluno/privacidade.html");await mutate(aluno,"/aluno/privacidade/consentimento-plano/aceitar","POST",()=>aluno.locator("#privacidade-aceitar").click(),201);
      await open(aluno,"/aluno/plano.html");await expect(aluno.locator("#plano-gerar")).toBeVisible();
      const novo=(await mutate(aluno,"/aluno/plano/gerar","POST",()=>aluno.locator("#plano-gerar").click(),201)).plano;
      expect(novo.id).not.toBe(original.id);expect(novo.geracao).toBe(1);expect(novo.itens[0].estado).toBe("pendente");
    });
  } finally {for(const c of contexts.reverse())await c.close();}
});
