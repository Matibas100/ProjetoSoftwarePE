(() => {
  globalThis.AuthUI?.destroy?.();
  const mode = document.body.dataset.auth;
  const ui = { blocked: true, user: null, ready: null, guards: [], navigate: (path) => location.replace(path) };
  const destination = (user) => user.perfil === "administrador" ? "/admin/materias.html" : "/aluno/inicio.html";
  const panel = document.querySelector("#auth-loading");
  const content = document.querySelector("#auth-content");
  let recovery;

  function status(message, retry = null) {
    if (!panel) return;
    panel.hidden = false;
    panel.replaceChildren();
    const text = document.createElement("p");
    text.setAttribute("role", "status"); text.textContent = message; panel.append(text);
    if (retry) {
      const button = document.createElement("button");
      button.className = "auth-primary"; button.textContent = "Tentar novamente";
      button.addEventListener("click", retry); panel.append(button);
    }
  }

  async function start() {
    try {
      const data = await apiRequest("/auth/sessao");
      ui.user = data.usuario;
      if (mode === "publico") { ui.navigate(destination(ui.user)); return false; }
      if (mode === "administrador" && ui.user.perfil !== "administrador") {
        status("Você não tem acesso à gestão administrativa.");
        const link = document.createElement("a"); link.href = "/aluno/inicio.html";
        link.textContent = "Voltar ao meu início"; panel?.append(link); return false;
      }
      if (mode === "aluno" && ui.user.perfil !== "aluno") {
        status("Esta área exige uma conta de aluno.");
        return false;
      }
      ui.blocked = false;
      if (panel) panel.hidden = true;
      if (content) content.hidden = false;
      document.querySelectorAll("[data-auth-name]").forEach((node) => { node.textContent = ui.user.nome; });
      return true;
    } catch (error) {
      if (error.code === "sessao_invalida") {
        if (mode !== "publico") ui.navigate("/login");
        else ui.blocked = false;
      } else {
        return new Promise((resolve) => {
          status(error.message, async () => resolve(await start()));
        });
      }
      return false;
    }
  }

  ui.registerGuard = (guard) => ui.guards.push(guard);
  ui.logout = async () => {
    if (ui.guards.some((guard) => guard()) && !window.confirm("Descartar alterações não salvas e sair?")) return;
    try { await apiRequest("/auth/logout", { method: "POST" }); ui.navigate("/login"); }
    catch (error) { status(error.message); }
  };
  document.querySelectorAll("[data-auth-exit]").forEach((button) => button.addEventListener("click", ui.logout));

  function recover(code) {
    if (!["administrador", "aluno"].includes(mode) || !ui.user || recovery || ui.changedAccount) return;
    ui.blocked = true;
    if (mode === "aluno" && content) content.hidden = true;
    ui.reason = code;
    const oldId = ui.user.id;
    const sensitive = code === "reautenticacao_necessaria";
    const previousFocus = document.activeElement;
    const dialog = document.createElement("dialog"); dialog.className = "auth-dialog";
    dialog.setAttribute("aria-labelledby", "auth-dialog-title");
    dialog.innerHTML = `<h2 id="auth-dialog-title">${sensitive ? "Confirme sua senha" : "Entre novamente"}</h2>
      <p>Suas alterações continuam aqui. Depois de entrar, confirme a ação novamente.</p>
      <form id="auth-recovery-form"><div class="auth-field" ${sensitive ? "hidden" : ""}><label for="auth-recovery-email">E-mail</label><input id="auth-recovery-email" type="email" autocomplete="username"></div>
      <div class="auth-field"><label for="auth-recovery-password">Senha</label><input id="auth-recovery-password" type="password" autocomplete="current-password" required maxlength="128"></div>
      <p id="auth-recovery-status" class="auth-status" role="status" aria-live="polite"></p>
      <div class="auth-dialog-actions"><button class="auth-secondary" type="button" id="auth-recovery-close">Fechar</button><button class="auth-primary" type="submit">Continuar</button></div></form>`;
    document.body.append(dialog); recovery = dialog;
    const email = dialog.querySelector("#auth-recovery-email"); email.value = ui.user.email;
    const password = dialog.querySelector("#auth-recovery-password");
    const message = dialog.querySelector("#auth-recovery-status");
    const close = () => { dialog.close(); dialog.remove(); recovery = null; previousFocus?.focus(); };
    dialog.querySelector("#auth-recovery-close").addEventListener("click", close);
    dialog.addEventListener("cancel", (event) => { event.preventDefault(); close(); });
    dialog.querySelector("form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const button = dialog.querySelector('[type="submit"]'); button.disabled = true;
      message.textContent = "Verificando...";
      try {
        if (sensitive) await apiRequest("/auth/reautenticar", { method: "POST", body: JSON.stringify({ senha: password.value }) });
        else {
          resetCsrf();
          // Outra aba pode ter trocado apenas CSRF; primeiro conferir a identidade atual.
          try { await apiRequest("/auth/sessao"); }
          catch (error) {
            if (error.code !== "sessao_invalida") throw error;
            await apiRequest("/auth/login", { method: "POST", body: JSON.stringify({ email: email.value, senha: password.value }) });
          }
        }
        const data = await apiRequest("/auth/sessao");
        password.value = "";
        if (data.usuario.id !== oldId) {
          ui.changedAccount = true;
          document.dispatchEvent(new Event("auth-identity-changed"));
          message.textContent = mode === "aluno" ? "A conta mudou. O contexto anterior foi removido. Recarregue para continuar." : "A conta mudou. Copie os dados que precisar e recarregue a página para continuar.";
          const reload = document.createElement("button"); reload.type = "button"; reload.className = "auth-secondary";
          reload.textContent = "Descartar e recarregar"; reload.addEventListener("click", () => location.reload());
          button.replaceWith(reload); return;
        }
        ui.user = data.usuario; ui.blocked = false;
        if (mode === "aluno" && content) content.hidden = false;
        close();
      } catch (error) { message.textContent = error.message; }
      finally { button.disabled = false; }
    });
    dialog.showModal(); password.focus();
  }

  const onRequired = (event) => recover(event.detail);
  document.addEventListener("auth-required", onRequired);
  ui.destroy = () => {
    document.removeEventListener("auth-required", onRequired);
    window.removeEventListener("focus", onReturn);
    document.removeEventListener("visibilitychange", onReturn);
  };
  ui.recover = recover;
  ui.checkIdentity = async () => {
    const data = await apiRequest("/auth/sessao");
    if (data.usuario.id !== ui.user?.id || data.usuario.perfil !== ui.user?.perfil) {
      ui.blocked = true; ui.changedAccount = true;
      document.dispatchEvent(new Event("auth-identity-changed"));
      if (content) content.hidden = true;
      status("A conta mudou. Recarregue a página para continuar.");
      return false;
    }
    return !ui.blocked;
  };
  async function onReturn() {
    if (!["aluno", "administrador"].includes(mode) || !ui.user || ui.blocked || document.visibilityState === "hidden") return;
    // Ao voltar de outra aba, conferir identidade antes de reexibir conteúdo privado.
    if (content) content.hidden = true;
    try {
      if (await ui.checkIdentity()) {
        if (content) content.hidden = false;
        if (panel) panel.hidden = true;
      }
    } catch (error) {
      if (!recovery) status(error.message, onReturn);
    }
  }
  window.addEventListener("focus", onReturn);
  document.addEventListener("visibilitychange", onReturn);
  ui.ready = start();
  globalThis.AuthUI = ui;
})();
