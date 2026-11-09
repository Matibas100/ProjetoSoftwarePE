import { randomUUID } from 'node:crypto';
import { test,expect } from '@playwright/test';

const base='/admin/usuarios';
test.beforeAll(()=>{
  if(process.env.RUN_MYSQL_E2E!=='1'||!/^plataforma_enem_e2e_test_[a-f0-9]{12}$/.test(process.env.E2E_SCHEMA||'')) throw new Error('Use o runner MySQL descartável.');
});
async function response(page,path,method,action,status=200){
  const pending=page.waitForResponse(r=>new URL(r.url()).pathname===`/api${path}`&&r.request().method()===method)
    .then(async r=>({status:r.status(),data:status===204||path==='/auth/login'?null:await r.json()}));
  await action();const r=await pending;expect(r.status).toBe(status);return r.data;
}
async function open(page,path){await page.goto(path);await expect(page.locator('#auth-content')).toBeVisible();}
async function login(page,email,password){
  await page.goto('/login');await page.locator('#auth-email').fill(email);await page.locator('#auth-password').fill(password);
  await response(page,'/auth/login','POST',()=>page.locator('#auth-form button[type="submit"]').click());
  await expect(page.locator('#auth-content')).toBeVisible();
}
async function create(page,email,name){
  await open(page,'/admin/usuario.html');
  await page.locator('#usuario-nome').fill(name);await page.locator('#usuario-email').fill(email);
  await page.locator('#usuario-senha').fill(process.env.E2E_STUDENT_PASSWORD);
  await page.locator('#usuario-confirmacao').fill(process.env.E2E_STUDENT_PASSWORD);
  const data=await response(page,base,'POST',()=>page.locator('#usuario-salvar').click(),201);
  await expect(page).toHaveURL(new RegExp(`usuario.html\\?id=${data.id}$`));
  await expect(page.locator('#usuario-senha')).toHaveValue('');return data;
}
async function confirm(page,path,method,button,status=200){
  await page.locator(button).click();await expect(page.locator('#admin-modal')).toBeVisible();
  return response(page,path,method,()=>page.locator('#admin-modal-confirmar').click(),status);
}
async function get(page,path,status=200){const r=await page.request.get(process.env.E2E_API_URL+path);expect(r.status()).toBe(status);return r.json();}

test('Gestão de Alunos: CRUD permitido, vínculos, sessões e revisão 1440/390',async({browser},info)=>{
  const contexts=[];
  async function newPage(){
    const c=await browser.newContext({baseURL:process.env.E2E_BASE_URL,viewport:{width:1440,height:1000}});contexts.push(c);
    await c.addInitScript(url=>{window.ENEM_API_URL=url;},process.env.E2E_API_URL);return c.newPage();
  }
  try{
    const admin=await newPage();await login(admin,process.env.E2E_ADMIN_EMAIL,process.env.E2E_ADMIN_PASSWORD);
    const tag=randomUUID().slice(0,8);const email=`gestao-${tag}@teste.local`;
    let fresh,used;
    await test.step('Criar, listar com máscara, detalhe atual, editar e excluir sem vínculos',async()=>{
      fresh=await create(admin,email,`Aluno CRUD ${tag}`);
      expect(Object.keys(fresh).sort()).toEqual(['ativo','criado_em','email','id','nome','perfil']);
      await open(admin,'/admin/usuarios.html');
      await admin.locator('#usuarios-busca').fill(email);
      const filtered=admin.waitForResponse(r=>new URL(r.url()).pathname===`/api${base}`&&new URL(r.url()).searchParams.get('busca')===email);
      await admin.locator('#usuarios-filtros button[type="submit"]').click();
      const list=await (await filtered).json();
      expect(list.total_itens).toBe(1);expect(list.itens[0].email_mascarado).toBe('g***@teste.local');
      await expect(admin.locator('#usuarios-corpo tr')).toHaveCount(1);
      for(const width of [1440,390]){
        await admin.setViewportSize({width,height:1000});
        expect(await admin.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
        await admin.screenshot({path:info.outputPath(`usuarios-lista-${width}.png`),fullPage:true});
      }
      await admin.locator('#usuarios-corpo a').click();await expect(admin.locator('#usuario-email')).toHaveValue(email);
      await admin.locator('#usuario-nome').fill(`Aluno corrigido ${tag}`);
      await response(admin,`${base}/${fresh.id}`,'PUT',()=>admin.locator('#usuario-salvar').click());
      await admin.reload();await expect(admin.locator('#usuario-nome')).toHaveValue(`Aluno corrigido ${tag}`);
      await confirm(admin,`${base}/${fresh.id}`,'DELETE','#usuario-excluir',204);
      await expect(admin).toHaveURL(/\/admin\/usuarios.html$/);
      await get(admin,`${base}/${fresh.id}`,404);
    });
    const student=await newPage(),second=await newPage();
    await test.step('Conta provisionada sem decisões; titular aceita termos e DELETE é bloqueado',async()=>{
      used=await create(admin,`usado-${tag}@teste.local`,`Aluno com histórico ${tag}`);
      await login(student,used.email,process.env.E2E_STUDENT_PASSWORD);
      await login(second,used.email,process.env.E2E_STUDENT_PASSWORD);
      await open(student,'/aluno/privacidade.html');
      const before=await get(student,'/aluno/privacidade');expect(before.termos_uso.registro).toBeNull();
      await response(student,'/aluno/privacidade/termos-uso','POST',()=>student.locator('#privacidade-aceitar-uso').click(),201);
      await expect(student.locator('#privacidade-uso')).toContainText('Aceite vigente');
      const result=await confirm(admin,`${base}/${used.id}`,'DELETE','#usuario-excluir',409);
      expect(result.codigo).toBe('usuario_com_vinculos');
      await expect(admin.locator('#usuarios-mensagem')).toContainText('vínculos');
      expect((await get(student,'/auth/sessao')).usuario.id).toBe(used.id);
    });
    await test.step('Desativar revoga ambas as sessões; reativar preserva decisões sem recuperar cookies',async()=>{
      await confirm(admin,`${base}/${used.id}/desativar`,'POST','#usuario-status-acao');
      await get(student,'/auth/sessao',401);await get(second,'/auth/sessao',401);
      for(const width of [1440,390]){
        await admin.setViewportSize({width,height:1000});
        expect(await admin.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
        await admin.screenshot({path:info.outputPath(`usuario-detalhe-${width}.png`),fullPage:true});
      }
      await confirm(admin,`${base}/${used.id}/reativar`,'POST','#usuario-status-acao');
      await get(student,'/auth/sessao',401);
      await login(student,used.email,process.env.E2E_STUDENT_PASSWORD);
      expect((await get(student,'/aluno/privacidade')).termos_uso.aceite_vigente).toBe(true);
    });
    await test.step('Trocar endereço revoga sessão; novo login usa e-mail atualizado',async()=>{
      const novo=`alterado-${tag}@teste.local`;
      await admin.locator('#usuario-email').fill(novo);await admin.locator('#usuario-salvar').click();
      await expect(admin.locator('#admin-modal-cancelar')).toBeFocused();
      await admin.keyboard.press('Tab');await expect(admin.locator('#admin-modal-confirmar')).toBeFocused();
      await response(admin,`${base}/${used.id}`,'PUT',()=>admin.keyboard.press('Enter'));
      await get(student,'/auth/sessao',401);
      await login(student,novo,process.env.E2E_STUDENT_PASSWORD);
      expect((await get(student,'/auth/sessao')).usuario.email).toBe(novo);
      expect((await get(student,'/aluno/privacidade')).termos_uso.aceite_vigente).toBe(true);
    });
    await info.attach('gestao-alunos-evidencia',{body:Buffer.from(JSON.stringify({
      crudSemVinculos:true,exclusaoComVinculos:409,sessoesRevogadas:true,reativacaoSemCookiesAntigos:true,
      trocaEmailRevoga:true,termosPreservados:true,larguras:[1440,390],interceptacao:false})),contentType:'application/json'});
  }finally{for(const c of contexts)await c.close();}
});
