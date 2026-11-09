(async () => {
  if (!(await globalThis.AuthUI?.ready) || AuthUI.user?.perfil !== "administrador") return;
  const ui = globalThis.AdminUI;
  const $ = (id) => document.getElementById(id);
  const message = $("usuarios-mensagem");
  const modal = ui.modalController($("admin-modal"));
  const form = $("usuario-form");
  const base = "/admin/usuarios";
  let version = 0, controller, busy = false;
  const available = () => !AuthUI.blocked && !AuthUI.changedAccount && AuthUI.user?.perfil === "administrador";
  const identity = () => `${AuthUI.user?.id}:${AuthUI.user?.perfil}`;
  const showError = (error) => ui.showMessage(message, error.message, "error");
  function invalidate() { version += 1; controller?.abort(); }
  function clearPasswords() {
    if (form) { $("usuario-senha").value = ""; $("usuario-confirmacao").value = ""; }
  }
  document.addEventListener("auth-required", () => {
    invalidate(); clearPasswords();
    if ($("admin-modal").open) $("admin-modal").dispatchEvent(new Event("cancel", { cancelable: true }));
  });
  document.addEventListener("auth-identity-changed", () => {
    invalidate(); clearPasswords();
    if (form) { form.reset(); form.hidden = true; }
    $("usuarios-corpo")?.replaceChildren();
  });
  function validItem(item, id) {
    return item && item.id === id && Number.isInteger(id) && id > 0 && id <= 2147483647
      && typeof item.nome === "string" && typeof item.email === "string"
      && item.perfil === "aluno" && typeof item.ativo === "boolean"
      && typeof item.criado_em === "string" && Number.isFinite(Date.parse(item.criado_em));
  }

  if (!form) {
    let page = 1, pages = 0;
    async function load() {
      invalidate();
      if (!available()) { AuthUI.recover(AuthUI.reason || "sessao_invalida"); return; }
      const token = version, user = identity();
      controller = new AbortController();
      const current = () => token === version && available() && identity() === user;
      $("usuarios-corpo").replaceChildren();
      $("usuarios-estado").hidden = false;
      $("usuarios-estado").textContent = "Carregando usuários...";
      $("usuarios-anterior").disabled = true; $("usuarios-proxima").disabled = true;
      ui.hideMessage(message);
      try {
        const query = ui.adminQuery(page, { busca: $("usuarios-busca").value.trim(), status: $("usuarios-status").value });
        const data = await apiRequest(`${base}?${query}`, { signal: controller.signal });
        if (!current() || !await AuthUI.checkIdentity() || !current()) return;
        if (!Array.isArray(data.itens) || !Number.isInteger(data.total_itens)) throw new Error("Resposta inválida do servidor.");
        page = data.pagina; pages = data.total_paginas;
        for (const item of data.itens) {
          const row = ui.element("tr");
          const link = ui.element("a", "Abrir detalhe", "button button--text");
          link.href = `usuario.html?id=${Number(item.id)}`;
          const action = ui.cell(); action.append(link);
          row.append(ui.cell(item.nome), ui.cell(item.email_mascarado), ui.cell("Aluno"),
            ui.cell(item.ativo ? "Ativo" : "Inativo"), ui.cell(ui.dateLabel(item.criado_em)), action);
          $("usuarios-corpo").append(row);
        }
        $("usuarios-estado").hidden = data.itens.length > 0;
        $("usuarios-estado").textContent = $("usuarios-busca").value || $("usuarios-status").value
          ? "Nenhum usuário encontrado para estes filtros." : "Nenhum Aluno cadastrado nesta página.";
        $("usuarios-total").textContent = `${data.total_itens} usuários`;
        $("usuarios-pagina").textContent = `Página ${page} de ${pages || 1}`;
        $("usuarios-anterior").disabled = page <= 1;
        $("usuarios-proxima").disabled = page >= pages;
      } catch (error) {
        if (current()) { showError(error); $("usuarios-estado").textContent = "Não foi possível carregar a lista. Atualize para tentar novamente."; }
      }
    }
    $("usuarios-filtros").addEventListener("submit", (event) => { event.preventDefault(); page = 1; load(); });
    $("usuarios-status").addEventListener("change", () => { page = 1; load(); });
    $("usuarios-limpar").addEventListener("click", () => { $("usuarios-filtros").reset(); page = 1; load(); });
    $("usuarios-anterior").addEventListener("click", () => { if (page > 1) { page -= 1; load(); } });
    $("usuarios-proxima").addEventListener("click", () => { if (page < pages) { page += 1; load(); } });
    $("usuarios-recarregar").addEventListener("click", load);
    await load();
    return;
  }

  let item = null;
  const queryId = new URLSearchParams(location.search).get("id");
  let id = queryId === null ? null : Number(queryId);
  const guard = ui.createUnsavedGuard(form, $("usuario-unsaved"));
  guard.markPersisted();
  const setBusy = (value) => {
    busy = value;
    form.querySelectorAll('input').forEach((input) => { input.readOnly = value; });
    for (const name of ["usuario-salvar", "usuario-status-acao", "usuario-excluir", "usuario-recarregar", "usuario-cancelar"]) $(name).disabled = value;
    form.setAttribute("aria-busy", String(value));
  };
  function display(data) {
    item = data; id = data.id;
    clearPasswords();
    $("usuario-nome").value = data.nome; $("usuario-email").value = data.email;
    $("usuario-titulo").textContent = "Detalhe do usuário";
    $("usuario-senhas").hidden = true; $("usuario-aviso-criacao").hidden = true;
    for (const name of ["usuario-senha", "usuario-confirmacao"]) { $(name).required = false; $(name).disabled = true; }
    $("usuario-status").textContent = data.ativo ? "Conta ativa" : "Conta inativa";
    $("usuario-criado").textContent = `Criação: ${ui.dateLabel(data.criado_em)}`;
    $("usuario-status-acao").textContent = data.ativo ? "Desativar conta" : "Reativar conta";
    $("usuario-acoes").hidden = false; $("usuario-recarregar").hidden = false;
    $("usuario-salvar").textContent = "Salvar alterações";
    guard.markPersisted();
  }
  async function discard() {
    return !guard.dirty() || modal.confirm({ title: "Descartar alterações?", text: "As alterações não salvas serão perdidas.", confirmLabel: "Descartar", danger: true });
  }
  async function loadDetail() {
    if (busy || !available() || !await discard()) return;
    invalidate(); const token = version, user = identity(), target = id;
    controller = new AbortController(); setBusy(true);
    $("usuario-carregando").hidden = false;
    const current = () => token === version && available() && user === identity() && target === id;
    try {
      const data = await apiRequest(`${base}/${target}`, { signal: controller.signal });
      if (!current() || !await AuthUI.checkIdentity() || !current()) return;
      if (!validItem(data, target)) throw new Error("Resposta inválida do servidor.");
      display(data); ui.hideMessage(message);
    } catch (error) { if (current()) showError(error); }
    finally { setBusy(false); $("usuario-carregando").hidden = true; if (!item) $("usuario-salvar").disabled = true; }
  }
  form.addEventListener("input", invalidate);
  async function mutate(action) {
    if (busy || AuthUI.changedAccount) return;
    if (id !== null && !item) return;
    if (!available()) { AuthUI.recover(AuthUI.reason || "sessao_invalida"); return; }
    const user = identity(), token = version;
    const current = () => user === identity() && token === version && available();
    setBusy(true); // Inclui o intervalo de confirmação; duplo clique não abre outra ação.
    try {
      if (!await AuthUI.checkIdentity() || !current()) return;
      let method, path, body;
      if (action === "save") {
        body = { nome: $("usuario-nome").value, email: $("usuario-email").value };
        if (item && body.email.trim().toLowerCase() !== item.email) {
          if (!await modal.confirm({ title: "Trocar e-mail?", text: "Todas as sessões do Aluno serão encerradas.", confirmLabel: "Trocar e-mail" }) || !current()) return;
        }
        method = id === null ? "POST" : "PUT"; path = id === null ? base : `${base}/${id}`;
        if (id === null) { body.senha = $("usuario-senha").value; body.senha_confirmacao = $("usuario-confirmacao").value; }
      } else {
        if (!item) return;
        if (!await discard() || !current()) return;
        const deleting = action === "delete";
        const operation = deleting ? "Excluir" : item.ativo ? "Desativar" : "Reativar";
        if (!await modal.confirm({ title: `${operation} conta?`,
          text: deleting ? "A exclusão é permanente e só é permitida sem vínculos. Contas com histórico podem ser desativadas em uma ação separada."
            : item.ativo ? "O acesso será bloqueado e todas as sessões encerradas. Histórico e decisões serão preservados."
              : "O Aluno poderá fazer novo login. Sessões antigas continuarão revogadas.",
          confirmLabel: `${operation} conta`, danger: deleting || item.ativo }) || !current()) return;
        method = deleting ? "DELETE" : "POST";
        path = deleting ? `${base}/${id}` : `${base}/${id}/${item.ativo ? "desativar" : "reativar"}`;
        body = { confirmar: true };
      }
      if (!current() || !await AuthUI.checkIdentity() || !current()) return;
      const result = await apiRequest(path, { method, body: JSON.stringify(body) });
      if (!current()) return;
      if (method === "DELETE") {
        clearPasswords(); form.reset(); guard.markPersisted(); AuthUI.navigate("/admin/usuarios.html"); return;
      }
      if (!validItem(result, id === null ? result?.id : id)) throw new Error("Resposta inválida do servidor. Confira o cadastro antes de tentar novamente.");
      display(result);
      history.replaceState(null, "", `usuario.html?id=${result.id}`);
      ui.showMessage(message, "Operação concluída.");
    } catch (error) { showError(error); }
    finally { setBusy(false); }
  }
  form.addEventListener("submit", (event) => { event.preventDefault(); mutate("save"); });
  $("usuario-status-acao").addEventListener("click", () => mutate("status"));
  $("usuario-excluir").addEventListener("click", () => mutate("delete"));
  $("usuario-recarregar").addEventListener("click", loadDetail);
  async function leave(path) {
    if (busy || !await discard()) return;
    invalidate(); clearPasswords(); form.reset(); guard.markPersisted(); AuthUI.navigate(path);
  }
  $("usuario-cancelar").addEventListener("click", () => leave("/admin/usuarios.html"));
  document.addEventListener("click", (event) => {
    const link = event.target.closest("a[href]");
    if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault(); leave(link.getAttribute("href"));
  });
  if (id !== null) {
    if (!/^\d+$/.test(queryId) || !Number.isInteger(id) || id < 1 || id > 2147483647) {
      showError(new Error("Identificador inválido.")); $("usuario-salvar").disabled = true; return;
    }
    $("usuario-recarregar").hidden = false;
    await loadDetail();
  }
})();
