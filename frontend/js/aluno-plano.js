(() => {
  globalThis.PlanoUI?.destroy();
  const $ = (id) => document.getElementById(id);
  const state = { generation: 0, busy: false, loaded: false, plan: null, pending: null };
  const dialog = $("plano-confirmacao");
  const available = () => !AuthUI.blocked && !AuthUI.changedAccount;
  const valid = (generation, user) => generation === state.generation && available() && AuthUI.user.id === user;
  const element = (tag, text) => {
    const n = document.createElement(tag);
    n.textContent = text;
    return n;
  };
  function message(text, error = false, focus = false) {
    $("plano-status").textContent = text;
    $("plano-status").dataset.erro = error;
    if (focus) $("plano-status").focus();
  }
  function busy(value) {
    state.busy = value;
    $("plano-conteudo").setAttribute("aria-busy", String(value));
    $("plano-retentar").hidden = !state.pending;
    document.querySelectorAll('[data-plano-action]').forEach((n) => {
      n.disabled = value;
    });
  }
  function clearIdentity() {
    state.generation++;
    state.plan = null;
    state.pending = null;
    state.loaded = false;
    document.querySelectorAll('[data-plano-private]').forEach((n) => n.replaceChildren());
    $("plano-gerar").hidden = true;
    $("plano-recalcular").hidden = true;
    $("plano-retentar").hidden = true;
    if (dialog.open) dialog.close();
    message("A conta mudou. Recarregue a página para continuar.", true);
  }
  document.addEventListener("auth-identity-changed", clearIdentity);
  function clearPlan(discard = false) {
    state.plan = null;
    state.loaded = false;
    if (discard) state.pending = null;
    document.querySelectorAll('[data-plano-private]').forEach(n => n.replaceChildren());
    $("plano-gerar").hidden = true;
    $("plano-recalcular").hidden = true;
    if (dialog.open) dialog.close();
  }
  async function checkPermission(generation, user) {
    const privacy = await apiRequest("/aluno/privacidade");
    if (!valid(generation, user)) return false;
    $("plano-privacidade").hidden = privacy.plano_liberado;
    if (!privacy.plano_liberado) {
      clearPlan(true);
      message("O plano depende da sua escolha de privacidade. Questões, simulados e desempenho continuam disponíveis.");
      return false;
    }
    return true;
  }
  function render(plan) {
    state.plan = plan;
    state.loaded = true;
    $("plano-gerar").hidden = !!plan;
    $("plano-recalcular").hidden = !plan;
    $("plano-meta").textContent = plan ? `Geração ${plan.geracao} · criada em ${new Date(plan.gerado_em).toLocaleString("pt-BR", { timeZone: "UTC" })} UTC · base de ${plan.periodo.inicio} a ${plan.periodo.fim} (UTC).` : "";
    $("plano-vazio").textContent = plan ? "" : "Plano não criado. Gere suas prioridades a partir das respostas que você já concluiu.";
    $("plano-lista").replaceChildren();
    for (const item of plan?.itens || []) {
      const s = item.snapshot, li = element("li", "");
      li.className = "plano-item";
      li.dataset.concluido = item.estado === "concluido";
      li.append(element("span", `Prioridade ${item.posicao}`));
      li.firstChild.className = "plano-ordem";
      li.append(element("h3", `${s.materia_nome} · ${s.assunto_nome}`));
      li.append(element("p", `${s.percentual_acerto.toLocaleString("pt-BR")}% de acerto · mínimo de ${s.limiar_amostra} respostas por assunto.`));
      li.append(element("p", s.justificativa));
      const actions = element("div", "");
      actions.className = "pratica-acoes";
      if (item.disponivel_para_pratica) {
        const a = element("a", "Iniciar prática →");
        a.href = `/aluno/questoes.html?assunto_id=${encodeURIComponent(item.assunto_id)}`;
        actions.append(a);
      } else actions.append(element("span", "Conteúdo indisponível para prática no momento."));
      if (item.estado === "concluido") {
        actions.append(element("span", `Concluído em ${new Date(item.concluido_em).toLocaleString("pt-BR", { timeZone: "UTC" })} UTC.`));
      } else {
        const b = element("button", "Marcar como concluído");
        b.type = "button";
        b.className = "auth-secondary";
        b.dataset.planoAction = "";
        b.addEventListener("click", () => mutate("concluir", item.id));
        actions.append(b);
      }
      li.append(actions);
      $("plano-lista").append(li);
    }
  }
  async function load() {
    if (!available() || state.busy) return;
    const generation = ++state.generation, user = AuthUI.user.id;
    clearPlan();
    busy(true);
    message("Consultando plano...");
    try {
      if (!await AuthUI.checkIdentity() || !valid(generation, user)) return;
      if (!await checkPermission(generation, user)) return;
      const data = await apiRequest("/aluno/plano");
      if (!valid(generation, user) || !await AuthUI.checkIdentity() || !valid(generation, user)) return;
      if (!await checkPermission(generation, user)) return;
      render(data.plano);
      message(data.plano ? "Plano consultado. Novas respostas só entram após um recálculo confirmado." : "Gere seu plano ou pratique questões para formar a base do diagnóstico.");
    } catch (e) {
      if (generation === state.generation) {
        clearPlan(e.status === 403);
        message(e.message, true);
      }
    }
    finally {
      if (generation === state.generation) busy(false);
    }
  }
  async function mutate(action, itemId = null) {
    if (state.busy || !state.loaded || !available()) return;
    if (state.pending && (state.pending.action !== action || state.pending.itemId !== itemId)) {
      message("Tente novamente a ação pendente para recuperar seu resultado antes de escolher outra ação.", true, true);
      return;
    }
    state.pending ||= {
      action,
      itemId,
      body: action === "concluir" ? { confirmar: true } :
      {
        chave_envio: crypto.randomUUID(),
        ...(action === "recalcular" ? { plano_atual_id: state.plan.id, confirmar: true } : {})
      }
    };
    const generation = state.generation, user = AuthUI.user.id, pending = state.pending;
    busy(true);
    message("Salvando...");
    try {
      if (!await AuthUI.checkIdentity() || !valid(generation, user)) return;
      if (!await checkPermission(generation, user)) return;
      const route = action === "concluir" ? `itens/${itemId}/concluir` : action;
      let data = await apiRequest(`/aluno/plano/${route}`, { method: "POST", body: JSON.stringify(pending.body) });
      if (!valid(generation, user) || !await AuthUI.checkIdentity() || !valid(generation, user)) return;
      if (!await checkPermission(generation, user)) return;
      if (action === "concluir") {
        state.plan.itens = state.plan.itens.map((i) => i.id === data.id ? data : i);
        render(state.plan);
      } else {
        // Replay pode apontar para geração histórica; exibir sempre o plano atual.
        if (data.plano && !data.plano.atual) {
          data = await apiRequest("/aluno/plano");
          if (!valid(generation, user) || !await AuthUI.checkIdentity() || !valid(generation, user)) return;
        }
        render(data.plano);
      }
      state.pending = null;
      message(data.estado === "sem_base_suficiente" ? "Base insuficiente: pratique pelo menos cinco respostas por assunto com conteúdo publicado. Seu plano anterior foi preservado, se existir." :
        action === "concluir" ? "Item concluído manualmente. Suas respostas e seu desempenho foram preservados." : "Plano salvo. As prioridades ficam preservadas até você confirmar outro recálculo.", false, true);
    } catch (e) {
      if (generation === state.generation) {
        if ([400, 404, 409].includes(e.status)) state.pending = null;
        clearPlan(e.status === 403);
        message(`${e.message} Confirme a ação novamente para tentar.`, true, true);
      }
    } finally {
      if (generation === state.generation) busy(false);
    }
  }
  function closeDialog() {
    dialog.close();
    $("plano-recalcular").focus();
  }
  $("plano-gerar").addEventListener("click", () => mutate("gerar"));
  $("plano-recarregar").addEventListener("click", load);
  $("plano-retentar").addEventListener("click", async () => {
    if (!state.loaded) await load();
    if (state.pending) mutate(state.pending.action, state.pending.itemId);
  });
  $("plano-recalcular").addEventListener("click", () => {
    if (!available() || state.busy || !state.plan) return;
    dialog.showModal();
    $("plano-cancelar").focus();
  });
  $("plano-cancelar").addEventListener("click", closeDialog);
  dialog.addEventListener("cancel", (e) => {
    e.preventDefault();
    closeDialog();
  });
  $("plano-confirmar").addEventListener("click", () => {
    closeDialog();
    mutate("recalcular");
  });
  function onReturn() {
    if (document.visibilityState === "hidden" || !available()) return;
    state.generation++;
    clearPlan();
    busy(false);
    load();
  }
  function onSessionRequired() {
    state.generation++;
    clearPlan();
    busy(false);
  }
  window.addEventListener("focus", onReturn);
  document.addEventListener("visibilitychange", onReturn);
  document.addEventListener("auth-required", onSessionRequired);
  globalThis.PlanoUI = {
    state,
    load,
    destroy() {
      state.generation++;
      document.removeEventListener("auth-identity-changed", clearIdentity);
      window.removeEventListener("focus", onReturn);
      document.removeEventListener("visibilitychange", onReturn);
      document.removeEventListener("auth-required", onSessionRequired);
    }
  };
  AuthUI.ready.then((ready) => {
    if (ready && available()) load();
  });
})();
