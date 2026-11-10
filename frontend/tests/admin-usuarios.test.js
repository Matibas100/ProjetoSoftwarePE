import path from 'node:path';
import { afterEach, expect, it, vi } from 'vitest';
import { root, settle } from './helpers/classic-app.js';
import { prepareAdminGlobalDom } from './helpers/global-app.js';

const $ = id => document.getElementById(id);
const flush = async () => {
  await settle();
  await settle();
};
const fire = (id, type = 'click') => $(id).dispatchEvent(new Event(type, {bubbles: true, cancelable: true}));
const item = (id = 9, extra = {}) => ({
  id,
  nome: 'Aluno atual',
  email: 'aluno@teste.local',
  perfil: 'aluno',
  ativo: true,
  criado_em: '2026-11-09T12:00:00Z',
  ...extra
});
const pending = () => {
  let resolve;
  const promise = new Promise(r => {
    resolve = r;
  });
  return {promise, resolve};
};
async function setup({list = false, id = null, handler, allowed = true} = {}) {
  vi.resetModules();
  prepareAdminGlobalDom(path.join(root, 'frontend/admin', list?'usuarios.html': 'usuario.html'));
  history.replaceState(null, '', list?'/admin/usuarios.html': `/admin/usuario.html${id === null?'': `?id=${id}`}`);
  Object.assign(AuthUI, {
    ready: Promise.resolve(allowed),
    user: {id: 1, perfil: 'administrador'},
    blocked: false,
    changedAccount: false,
    checkIdentity: vi.fn(async() => true),
    recover: vi.fn(),
    navigate: vi.fn()
  });
  globalThis.apiRequest = vi.fn(async(url, options = {}) => {
    const custom = handler?.(url, options);
    if(custom !== undefined)return custom;
    if(options.method === 'DELETE')return null;
    if(options.method)return item(9, {...JSON.parse(options.body)});
    if(url.startsWith('/admin/usuarios?'))return {itens: [{...item(), email_mascarado: 'a***@teste.local'}], pagina: 1, total_paginas: 2, total_itens: 21};
    return item(Number(url.split('/').at(-1)));
  });
  await import('../js/admin-common.js');
  await import('../js/admin-usuarios.js');
  await flush();
  return apiRequest;
}
afterEach(() => {
  document.body.replaceChildren();
  vi.restoreAllMocks();
});

it('aguarda autorização antes de consultar ou registrar ações', async() => {
  const api = await setup({list: true, allowed: false});
  expect(api).not.toHaveBeenCalled();
});
it('lista com máscara, perfil fixo e navegação de detalhe; filtros e paginação reais', async() => {
  const api = await setup({list: true});
  expect($('usuarios-corpo').textContent).toContain('a***@teste.local');
  expect($('usuarios-corpo').querySelector('a').getAttribute('href')).toBe('usuario.html?id=9');
  fire('usuarios-proxima');
  await flush();
  expect(api.mock.calls.at(-1)[0]).toContain('pagina=2');
  fire('usuarios-anterior');
  await flush();
  $('usuarios-busca').value = '%_\\';
  fire('usuarios-filtros', 'submit');
  await flush();
  expect(api.mock.calls.at(-1)[0]).toContain('busca=%25_');
  $('usuarios-status').value = 'inativo';
  fire('usuarios-status', 'change');
  await flush();
  expect(api.mock.calls.at(-1)[0]).toContain('status=inativo');
  fire('usuarios-limpar');
  await flush();
  expect($('usuarios-busca').value).toBe('');
  AuthUI.blocked = true;
  fire('usuarios-recarregar');
  await flush();
  expect(AuthUI.recover).toHaveBeenCalled();
});
it('mostra vazio, sem resultado, falha de rede e permite atualização explícita', async() => {
  let mode = 'empty';
  await setup({
    list: true,
    handler: () => mode === 'error'?Promise.reject(new Error('Rede indisponível')):
    mode === 'invalid'?{}: {itens: [], pagina: 1, total_itens: 0, total_paginas: 0}
  });
  expect($('usuarios-estado').textContent).toContain('Nenhum Aluno');
  $('usuarios-busca').value = 'Ausente';
  fire('usuarios-filtros', 'submit');
  await flush();
  expect($('usuarios-estado').textContent).toContain('estes filtros');
  mode = 'error';
  fire('usuarios-recarregar');
  await flush();
  expect($('usuarios-mensagem').textContent).toContain('Rede');
  mode = 'invalid';
  fire('usuarios-recarregar');
  await flush();
  expect($('usuarios-mensagem').textContent).toContain('Resposta inválida');
});
it('descarta consulta atrasada após filtros, bloqueio e troca de identidade', async() => {
  const delay = pending();
  let first = true;
  await setup({list: true, handler: () => {
    if(first){
      first = false;
      return delay.promise;
    }
  }});
  fire('usuarios-recarregar');
  await flush();
  delay.resolve({itens: [item(55)], pagina: 1, total_itens: 1, total_paginas: 1});
  await flush();
  expect($('usuarios-corpo').textContent).toContain('Aluno atual');
  document.dispatchEvent(new Event('auth-identity-changed'));
  expect($('usuarios-corpo').childElementCount).toBe(0);
});
it('cria com quatro campos, limpa senha e muda para PUT na URL de detalhe', async() => {
  const storage = vi.spyOn(Storage.prototype, 'setItem');
  const api = await setup();
  $('usuario-nome').value = 'Aluno';
  $('usuario-email').value = 'aluno@teste.local';
  $('usuario-senha').value = 'Segredo inicial';
  $('usuario-confirmacao').value = 'Segredo inicial';
  fire('usuario-form', 'submit');
  await flush();
  const post = api.mock.calls.find(([, o]) => o.method === 'POST');
  expect(Object.keys(JSON.parse(post[1].body))).toEqual(['nome', 'email', 'senha', 'senha_confirmacao']);
  expect(location.search).toBe('?id=9');
  expect($('usuario-senha').value).toBe('');
  expect($('usuario-senhas').hidden).toBe(true);
  expect($('usuario-unsaved').hidden).toBe(true);
  fire('usuario-form', 'submit');
  await flush();
  expect(api.mock.calls.filter(([, o]) => o.method === 'POST')).toHaveLength(1);
  expect(api.mock.calls.at(-1)[1].method).toBe('PUT');
  expect(Object.keys(JSON.parse(api.mock.calls.at(-1)[1].body))).toEqual(['nome', 'email']);
  expect(storage).not.toHaveBeenCalled();
});
it('lê detalhe atual, trata XSS como texto e troca e-mail somente após confirmação', async() => {
  const api = await setup({id: 9, handler: (url, o) => !o.method?item(9, {nome: '<img src=x onerror=alert(1)>'}): undefined});
  expect($('usuario-nome').value).toContain('<img');
  expect(document.querySelector('img[src="x"]')).toBeNull();
  $('usuario-email').value = 'novo@teste.local';
  fire('usuario-email', 'input');
  fire('usuario-form', 'submit');
  await flush();
  expect($('admin-modal').open).toBe(true);
  fire('admin-modal-cancelar');
  await flush();
  expect(api.mock.calls.filter(([, o]) => o.method)).toHaveLength(0);
  fire('usuario-form', 'submit');
  await flush();
  fire('admin-modal-confirmar');
  await flush();
  expect(api.mock.calls.at(-1)[1].method).toBe('PUT');
});
it('status e exclusão são ações distintas; 409 mantém conta e rascunho sem fallback', async() => {
  const api = await setup({
    id: 9,
    handler: (_url, o) => o.method === 'DELETE'?Promise.reject(new Error('A conta possui vínculos. Considere desativá-la.')): undefined
  });
  fire('usuario-excluir');
  await flush();
  fire('admin-modal-confirmar');
  await flush();
  expect($('usuarios-mensagem').textContent).toContain('vínculos');
  expect(api.mock.calls.filter(([url]) => url.endsWith('/desativar'))).toHaveLength(0);
  fire('usuario-status-acao');
  await flush();
  fire('admin-modal-confirmar');
  await flush();
  expect(api.mock.calls.at(-1)[0]).toBe('/admin/usuarios/9/desativar');
  expect(JSON.parse(api.mock.calls.at(-1)[1].body)).toEqual({confirmar: true});
});
it('reativa inativo e exclui sem vínculo com confirmação e navegação', async() => {
  const api = await setup({id: 9, handler: (_url, o) => !o.method?item(9, {ativo: false}): undefined});
  expect($('usuario-status-acao').textContent).toBe('Reativar conta');
  fire('usuario-status-acao');
  await flush();
  fire('admin-modal-confirmar');
  await flush();
  expect(api.mock.calls.at(-1)[0]).toBe('/admin/usuarios/9/reativar');
  fire('usuario-excluir');
  await flush();
  fire('admin-modal-confirmar');
  await flush();
  expect(AuthUI.navigate).toHaveBeenCalledWith('/admin/usuarios.html');
});
it('bloqueia duplo envio, preserva falha e não repete após recuperar sessão', async() => {
  const delay = pending();
  const api = await setup({handler: (_url, o) => o.method?delay.promise: undefined});
  $('usuario-nome').value = 'Rascunho';
  $('usuario-email').value = 'rascunho@teste.local';
  $('usuario-senha').value = 'Segredo';
  fire('usuario-form', 'submit');
  fire('usuario-form', 'submit');
  await flush();
  expect(api.mock.calls.filter(([, o]) => o.method)).toHaveLength(1);
  AuthUI.blocked = true;
  document.dispatchEvent(new CustomEvent('auth-required', {detail: 'sessao_invalida'}));
  expect($('usuario-senha').value).toBe('');
  delay.resolve(item());
  await flush();
  expect($('usuario-nome').value).toBe('Rascunho');
  expect(location.search).toBe('');
  AuthUI.blocked = false;
  await flush();
  expect(api.mock.calls.filter(([, o]) => o.method)).toHaveLength(1);
});
it('rascunho e falhas de corpo não geram replay; nova confirmação após reauth', async() => {
  let fail = true;
  const api = await setup({id: 9, handler: (_url, o) => o.method && fail?Promise.reject(new Error('Resposta inválida')): undefined});
  $('usuario-nome').value = 'Rascunho';
  fire('usuario-nome', 'input');
  fire('usuario-form', 'submit');
  await flush();
  expect($('usuario-nome').value).toBe('Rascunho');
  expect($('usuarios-mensagem').textContent).toContain('inválida');
  fire('usuario-excluir');
  await flush();
  expect($('admin-modal-titulo').textContent).toContain('Descartar');
  fire('admin-modal-confirmar');
  await flush();
  document.dispatchEvent(new CustomEvent('auth-required', {detail: 'reautenticacao_necessaria'}));
  await flush();
  expect($('admin-modal').open).toBe(false);
  expect(api.mock.calls.filter(([, o]) => o.method === 'DELETE')).toHaveLength(0);
  fail = false;
  fire('usuario-excluir');
  await flush();
  fire('admin-modal-cancelar');
  await flush();
  expect(api.mock.calls.filter(([, o]) => o.method === 'DELETE')).toHaveLength(0);
});
it('cancelamento e links confirmam descarte e limpam senha', async() => {
  await setup();
  $('usuario-nome').value = 'Rascunho';
  $('usuario-senha').value = 'Segredo';
  fire('usuario-nome', 'input');
  fire('usuario-cancelar');
  await flush();
  fire('admin-modal-cancelar');
  await flush();
  expect($('usuario-senha').value).toBe('Segredo');
  expect(AuthUI.navigate).not.toHaveBeenCalled();
  fire('usuario-voltar');
  await flush();
  fire('admin-modal-confirmar');
  await flush();
  expect($('usuario-senha').value).toBe('');
  expect(AuthUI.navigate).toHaveBeenCalledWith('usuarios.html');
});
it('nega ID inválido, detalhe inconsistente e leitura falha, sem habilitar escrita', async() => {
  for(const id of ['0', 'x', '2147483648']){
    const api = await setup({id});
    expect(api).not.toHaveBeenCalled();
    expect($('usuario-salvar').disabled).toBe(true);
  }
  await setup({id: 9, handler: () => item(8)});
  expect($('usuarios-mensagem').textContent).toContain('inválida');
  expect($('usuario-salvar').disabled).toBe(true);
  await setup({id: 9, handler: () => Promise.reject(new Error('Não encontrado'))});
  expect($('usuarios-mensagem').textContent).toContain('Não encontrado');
});
it('invalida detalhe atrasado ao bloquear identidade e limpa dados ao trocar de conta', async() => {
  const delay = pending();
  await setup({id: 9, handler: () => delay.promise});
  document.dispatchEvent(new Event('auth-required'));
  delay.resolve(item());
  await flush();
  expect($('usuario-nome').value).toBe('');
  document.dispatchEvent(new Event('auth-identity-changed'));
  expect($('usuario-form').hidden).toBe(true);
});
it('bloqueio de sessão exige recuperação explícita e troca de conta impede envio', async() => {
  const api = await setup();
  AuthUI.blocked = true;
  fire('usuario-form', 'submit');
  await flush();
  expect(AuthUI.recover).toHaveBeenCalled();
  expect(api).not.toHaveBeenCalled();
  AuthUI.changedAccount = true;
  fire('usuario-form', 'submit');
  await flush();
  expect(api).not.toHaveBeenCalled();
});
