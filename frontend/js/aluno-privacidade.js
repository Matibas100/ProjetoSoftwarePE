(() => {
  globalThis.PrivacidadeUI?.destroy();
  const $ = (id) => document.getElementById(id);
  const state = { generation: 0, busy: false, data: null, pending: null, confirmation: null };
  const dialog = $("privacidade-confirmacao");
  const available = () => !AuthUI.blocked && !AuthUI.changedAccount;
  const valid = (generation, user) => generation === state.generation && available() && AuthUI.user.id === user;
  function message(text, error = false, focus = false) {
    $("privacidade-status").textContent = text;
    $("privacidade-status").dataset.erro = error;
    if (focus) $("privacidade-status").focus();
  }
  function busy(value) {
    state.busy = value;
    $("privacidade-conteudo").setAttribute("aria-busy", String(value));
    document.querySelectorAll("[data-privacidade-action],#privacidade-consultar,#privacidade-retentar").forEach(n => {
      n.disabled = value;
    });
    $("privacidade-retentar").hidden = !state.pending;
  }
  function clear(discard = false) {
    state.generation++;
    state.data = null;
    state.confirmation = null;
    if (discard) state.pending = null;
    document.querySelectorAll("[data-privacidade-private]").forEach(n => n.replaceChildren());
    document.querySelectorAll("[data-privacidade-action]").forEach(n => {
      n.hidden = true;
    });
    if (dialog.open) dialog.close();
    busy(false);
  }
  function identityChanged() {
    clear(true);
    message("A conta mudou. Recarregue para continuar.", true);
  }
  const labels = {
    nao_informado: "Sem decisão",
    aceito: "Aceito",
    recusado: "Recusado",
    revogado: "Revogado",
    desatualizado: "Aceitação desatualizada"
  };
  function evidence(record) {
    return record ? `Registro ${record.id}: ${record.acao}, versão ${record.versao}, em ${new Date(record.registrado_em).toLocaleString("pt-BR", { timeZone: "UTC" })} UTC. SHA-256: ${record.documento_sha256}.` : "Nenhuma decisão registrada.";
  }
  function render(data) {
    state.data = data;
    $("privacidade-uso-link").href = data.termos_uso.documento_url;
    $("privacidade-plano-link").href = data.consentimento_plano.documento_url;
    $("privacidade-uso").textContent = `${data.termos_uso.aceite_vigente ? "Aceite vigente" : "Aceite pendente"}. Versão vigente: ${data.termos_uso.versao_vigente}. ${evidence(data.termos_uso.registro)}`;
    $("privacidade-plano").textContent = `${labels[data.consentimento_plano.estado]}. Versão vigente: ${data.consentimento_plano.versao_vigente}. ${evidence(data.consentimento_plano.registro)} ${data.plano_liberado ? "Plano liberado." : "Plano bloqueado."}`;
    $("privacidade-aceitar-uso").hidden = data.termos_uso.aceite_vigente;
    const accepted = data.consentimento_plano.registro?.acao === "aceitar";
    $("privacidade-aceitar").hidden = !data.termos_uso.aceite_vigente || data.consentimento_plano.estado === "aceito";
    $("privacidade-recusar").hidden = accepted;
    $("privacidade-revogar").hidden = !accepted;
  }
  async function load() {
    if (!available() || state.busy) return;
    clear();
    const generation = state.generation, user = AuthUI.user.id;
    busy(true);
    message("Consultando privacidade...");
    try {
      if (!await AuthUI.checkIdentity() || !valid(generation, user)) return;
      const data = await apiRequest("/aluno/privacidade");
      if (!valid(generation, user) || !await AuthUI.checkIdentity() || !valid(generation, user)) return;
      render(data);
      message("Decisões consultadas. Você escolhe se deseja utilizar o plano.");
    } catch (e) {
      if (generation === state.generation) message(e.message, true);
    }
    finally {
      if (generation === state.generation) busy(false);
    }
  }
  async function mutate(action) {
    if (!available() || state.busy || !state.data) return;
    if (state.pending && state.pending.action !== action) {
      message("Tente a decisão pendente antes de escolher outra ação.", true, true);
      return;
    }
    const tipo = action === "termos-uso" ? "termos_uso" : "consentimento_plano";
    const current = state.data[tipo];
    state.pending ||= {
      action,
      body: {
        versao: action === "revogar" ? current.registro.versao : current.versao_vigente,
        chave_envio: crypto.randomUUID(),
        revisao: current.registro?.id || 0,
        ...(["recusar", "revogar"].includes(action) ? { confirmar: true } : {})
      }
    };
    const generation = state.generation, user = AuthUI.user.id, pending = state.pending;
    busy(true);
    message("Registrando decisão...");
    try {
      if (!await AuthUI.checkIdentity() || !valid(generation, user)) return;
      const route = action === "termos-uso" ? "termos-uso" : `consentimento-plano/${action}`;
      const data = await apiRequest(`/aluno/privacidade/${route}`, { method: "POST", body: JSON.stringify(pending.body) });
      if (!valid(generation, user) || !await AuthUI.checkIdentity() || !valid(generation, user)) return;
      state.pending = null;
      render(data.privacidade);
      message("Decisão registrada. A tela mostra seu estado atual, inclusive em caso de reenvio.", false, true);
    } catch (e) {
      if (generation === state.generation) {
        if ([400, 404, 409].includes(e.status)) {
          state.pending = null;
          state.data = null;
          document.querySelectorAll("[data-privacidade-action]").forEach(n => {
            n.hidden = true;
          });
        }
        message(`${e.message} Consulte novamente ou tente a decisão pendente explicitamente.`, true, true);
      }
    } finally {
      if (generation === state.generation) busy(false);
    }
  }
  function closeDialog() {
    const action = state.confirmation;
    state.confirmation = null;
    dialog.close();
    if (action) $(`privacidade-${action}`).focus();
  }
  document.querySelectorAll("[data-privacidade-action]").forEach(n => n.addEventListener("click", () => {
    if (!available() || state.busy || !state.data) return;
    const action = n.dataset.privacidadeAction;
    if (["recusar", "revogar"].includes(action)) {
      state.confirmation = action;
      dialog.showModal();
      $("privacidade-cancelar").focus();
    }
    else mutate(action);
  }));
  $("privacidade-cancelar").addEventListener("click", closeDialog);
  dialog.addEventListener("cancel", e => {
    e.preventDefault();
    closeDialog();
  });
  $("privacidade-confirmar").addEventListener("click", () => {
    const action = state.confirmation;
    closeDialog();
    if (action) mutate(action);
  });
  $("privacidade-consultar").addEventListener("click", load);
  $("privacidade-retentar").addEventListener("click", async () => {
    if (!state.pending) return;
    if (!state.data) await load();
    if (state.pending) mutate(state.pending.action);
  });
  function onReturn() {
    if (document.visibilityState !== "hidden" && available()) {
      clear();
      load();
    }
  }
  function onSessionRequired() {
    clear();
    message("Entre novamente e consulte a privacidade antes de continuar.", true);
  }
  document.addEventListener("auth-identity-changed", identityChanged);
  document.addEventListener("auth-required", onSessionRequired);
  window.addEventListener("focus", onReturn);
  document.addEventListener("visibilitychange", onReturn);
  globalThis.PrivacidadeUI = {
    state,
    load,
    destroy() {
      state.generation++;
      document.removeEventListener("auth-identity-changed", identityChanged);
      document.removeEventListener("auth-required", onSessionRequired);
      window.removeEventListener("focus", onReturn);
      document.removeEventListener("visibilitychange", onReturn);
    }
  };
  AuthUI.ready.then(ready => {
    if (ready && available()) load();
  });
})();
