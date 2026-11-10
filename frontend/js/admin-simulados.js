(() => {
  globalThis.SimuladosAdminUI?.destroy();
  const $ = (id) => document.getElementById(id), ui = AdminUI;
  const editor = document.body.dataset.simulado === "admin-editor";
  const state = {
    generation: 0,
    busy: false,
    detail: null,
    selected: [],
    bank: [],
    page: 1,
    pages: 0,
    bankPage: 1,
    bankPages: 0,
    saved: "",
    ready: false
  };
  const param = new URLSearchParams(location.search).get("id");
  const available = () => !AuthUI.blocked && !AuthUI.changedAccount;
  const valid = (g, user) => g === state.generation && available() && AuthUI.user.id === user;
  const element = ui.element;
  const snapshot = () => JSON.stringify([$("titulo")?.value, state.selected.map((q) => q.questao_versao_id)]);
  const dirty = () => editor && state.ready && snapshot() !== state.saved;
  const persisted = () => {
    state.saved = snapshot();
    $("sim-unsaved").hidden = true;
  };
  function message(text, error = false) {
    $("sim-status").textContent = text;
    $("sim-status").dataset.erro = error;
  }
  function busy(value) {
    state.busy = value;
    document.querySelectorAll('main input, main button, main select, main textarea').forEach((n) => {
      n.disabled = value;
    });
    if (editor) {
      const frozen = state.detail && state.detail.estado !== "rascunho";
      $("titulo").disabled = value || frozen;
      $("sim-salvar").disabled = value || frozen || !state.ready;
      $("sim-publicar").disabled = value || frozen;
      $("sim-arquivar").disabled = value || state.detail?.estado === "arquivado";
      $("sim-banco-anterior").disabled = value || state.bankPage <= 1;
      $("sim-banco-proxima").disabled = value || state.bankPage >= state.bankPages;
    } else {
      $("sim-anterior").disabled = value || state.page <= 1;
      $("sim-proxima").disabled = value || state.page >= state.pages;
    }
    document.querySelectorAll('[data-sim-limite="true"]').forEach((n) => {
      n.disabled = true;
    });
  }
  function clearIdentity() {
    state.generation++;
    state.detail = null;
    state.selected = [];
    state.bank = [];
    state.ready = false;
    $("sim-form")?.reset();
    $("sim-motivo") && ($("sim-motivo").value = "");
    document.querySelectorAll('[data-sim-private]').forEach((n) => n.replaceChildren());
    message("A conta mudou. Recarregue a página para continuar.", true);
  }
  document.addEventListener("auth-identity-changed", clearIdentity);
  AuthUI.registerGuard(dirty);
  function beforeUnload(e) {
    if (dirty()) {
      e.preventDefault();
      e.returnValue = "";
    }
  }
  window.addEventListener("beforeunload", beforeUnload);
  function leave(e) {
    if (e.target.closest('a[href]') && dirty()) {
      if (!window.confirm("Descartar alterações não salvas e sair?")) e.preventDefault(); else persisted();
    }
  }
  document.addEventListener("click", leave);
  async function identity() {
    return available() && await AuthUI.checkIdentity();
  }
  const modal = ui.modalController($("admin-modal"));
  function renderSelected() {
    $("sim-selecao").replaceChildren();
    state.selected.forEach((q, index) => {
      const li = element("li", `Questão ${q.questao_id || ""} · versão ${q.questao_versao_id} · ${q.enunciado || "Conteúdo preservado"}`);
      if (!state.detail || state.detail.estado === "rascunho") {
        for (const [text, action] of [["Subir", -1], ["Descer", 1], ["Remover", 0]]) {
          const b = element("button", text);
          b.type = "button";
          b.setAttribute("aria-label", `${text} Questão na posição ${index + 1}`);
          b.disabled = Boolean(action && (index + action < 0 || index + action >= state.selected.length));
          b.dataset.simLimite = b.disabled;
          b.onclick = () => {
            if (state.busy || !available() || (action && (index + action < 0 || index + action >= state.selected.length))) return;
            if (action) [state.selected[index], state.selected[index + action]] = [state.selected[index + action], state.selected[index]];
            else state.selected.splice(index, 1);
            renderSelected();
            $("sim-unsaved").hidden = !dirty();
          };
          li.append(b);
        }
      }
      $("sim-selecao").append(li);
    });
  }
  function fillDetail(d) {
    state.detail = d;
    $("titulo").value = d.titulo;
    state.selected = d.itens.map((i) => ({ ...i, ...state.bank.find((q) => q.questao_versao_id === i.questao_versao_id) }));
    $("sim-revisao").textContent = `Simulado ${d.id} · ${d.estado} · revisão ${d.revisao}`;
    $("sim-publicacao").hidden = d.estado === "arquivado";
    $("sim-banco").hidden = d.estado !== "rascunho";
    renderSelected();
    persisted();
  }
  async function loadBank() {
    if (!available()) return;
    const g = state.generation, user = AuthUI.user.id;
    $("sim-questoes").replaceChildren();
    const busca = $("busca").value.trim();
    const data = await apiRequest(`/admin/questoes?status=publicada&pagina=${state.bankPage}&por_pagina=20&busca=${encodeURIComponent(busca)}`);
    if (!valid(g, user) || !await identity() || !valid(g, user)) return;
    state.bankPages = data.total_paginas;
    state.bank = data.itens.filter((q) => q.versao_publicada_id && q.assunto.status === "ativa" && q.materia.status === "ativa")
    .map((q) => ({ questao_id: q.id, questao_versao_id: q.versao_publicada_id, enunciado: q.enunciado }));
    for (const q of state.bank) {
      const li = element("li", `${q.questao_id} · ${q.enunciado}`), b = element("button", "Adicionar");
      b.type = "button";
      b.onclick = () => {
        if (state.busy || !available() || (state.detail && state.detail.estado !== "rascunho")) return;
        if (state.selected.length >= 180 || state.selected.some((i) => i.questao_versao_id === q.questao_versao_id || i.questao_id === q.questao_id)) {
          message("Selecione até 180 Questões sem repetição.", true);
          return;
        }
        state.selected.push(q);
        renderSelected();
        $("sim-unsaved").hidden = !dirty();
      };
      li.append(b);
      $("sim-questoes").append(li);
    }
    if (!state.bank.length) $("sim-questoes").append(element("li", "Nenhuma Questão publicada disponível neste filtro."));
    $("sim-banco-pagina").textContent = `Página ${state.bankPage} de ${Math.max(1, state.bankPages)}`;
  }
  async function load() {
    if (!available() || state.busy) return;
    if (dirty() && !window.confirm("Descartar alterações não salvas e recarregar?")) return;
    const g = ++state.generation, user = AuthUI.user.id;
    busy(true);
    message("Carregando...");
    try {
      if (!await identity()) return;
      if (editor) {
        if (param !== null && !/^[1-9]\d*$/.test(param)) throw new Error("Identificador de simulado inválido.");
        const d = state.detail ? await apiRequest(`/admin/simulados/${state.detail.id}`) : param ? await apiRequest(`/admin/simulados/${param}`) : null;
        if (!valid(g, user)) return;
        await loadBank();
        if (!valid(g, user) || !await identity() || !valid(g, user)) return;
        state.ready = true;
        if (d) fillDetail(d); else {
          renderSelected();
          persisted();
        }
        message("Selecione Questões e salve o rascunho antes de revisar/publicar.");
      } else {
        $("sim-lista").replaceChildren();
        const status = $("status").value;
        const data = await apiRequest(`/admin/simulados?pagina=${state.page}&por_pagina=20${status ? `&status=${status}` : ""}`);
        if (!valid(g, user) || !await identity() || !valid(g, user)) return;
        state.pages = data.total_paginas;
        for (const s of data.itens) {
          const li = element("li", "");
          li.append(element("strong", s.titulo), element("p", `${s.estado} · ${s.itens.length} Questões · revisão ${s.revisao}`));
          const a = element("a", "Abrir composição");
          a.href = `simulado.html?id=${s.id}`;
          li.append(a);
          $("sim-lista").append(li);
        }
        $("sim-pagina").textContent = `Página ${state.page} de ${Math.max(1, state.pages)}`;
        message(data.itens.length ? `${data.total_itens} simulado(s).` : "Nenhum simulado neste filtro.");
      }
    } catch (e) {
      if (g === state.generation) message(e.message, true);
    }
    finally {
      if (g === state.generation) busy(false);
    }
  }
  async function save(e) {
    e.preventDefault();
    if (state.busy || !state.ready || !available()) return;
    if (!state.selected.length) {
      message("Selecione ao menos uma Questão.", true);
      return;
    }
    const g = state.generation, user = AuthUI.user.id;
    busy(true);
    try {
      if (!await identity()) return;
      const d = state.detail;
      const body = {
        titulo: $("titulo").value,
        questao_versao_ids: state.selected.map((q) => q.questao_versao_id),
        ...(d ? { revisao: d.revisao } : {})
      };
      const r = await apiRequest(`/admin/simulados${d ? `/${d.id}` : ""}`, { method: d ? "PUT" : "POST", body: JSON.stringify(body) });
      if (!valid(g, user) || !await identity() || !valid(g, user)) return;
      history.replaceState(null, "", `simulado.html?id=${r.id}`);
      fillDetail(r);
      message("Rascunho salvo. Revise a composição antes de publicar.");
    } catch (e) {
      if (g === state.generation) message(e.message, true);
    }
    finally {
      if (g === state.generation) busy(false);
    }
  }
  async function action(name) {
    if (state.busy || !available() || !state.detail) return;
    if (dirty()) {
      message("Salve o rascunho antes desta ação.", true);
      return;
    }
    const motivo = $("sim-motivo").value.trim();
    if (motivo.length < 3 || motivo.length > 500) {
      message("Informe motivo de 3 a 500 caracteres.", true);
      $("sim-motivo").focus();
      return;
    }
    const g = state.generation, user = AuthUI.user.id;
    busy(true);
    try {
      const confirm = await modal.confirm({ title: name === "publicar" ? "Revisar e publicar simulado" : "Arquivar simulado",
        text: `${state.detail.titulo}: ${state.selected.length} Questões na ordem exibida. ${name === "publicar" ? "Confirme a revisão do conteúdo. A versão será imutável." : "Novos inícios serão impedidos e o histórico preservado."} Motivo: ${motivo}` });
      if (!confirm || !valid(g, user) || !await identity()) return;
      const r = await apiRequest(`/admin/simulados/${state.detail.id}/${name}`, { method: "POST", body: JSON.stringify({ revisao: state.detail.revisao, confirmar: true, motivo }) });
      if (!valid(g, user) || !await identity() || !valid(g, user)) return;
      fillDetail(r);
      message(name === "publicar" ? "Simulado publicado após revisão." : "Simulado arquivado. Histórico preservado.");
    } catch (e) {
      if (g === state.generation) message(e.message, true);
    }
    finally {
      if (g === state.generation) {
        busy(false);
        $("sim-status").focus();
      }
    }
  }
  if (editor) {
    $("sim-form").onsubmit = save;
    $("titulo").oninput = () => {
      $("sim-unsaved").hidden = !dirty();
    };
    $("sim-publicar").onclick = () => action("publicar");
    $("sim-arquivar").onclick = () => action("arquivar");
    async function bank() {
      if (state.busy || !available()) return;
      busy(true);
      try {
        if (await identity()) await loadBank();
      } catch (e) {
        message(e.message, true);
      } finally {
        busy(false);
      }
    }
    $("sim-busca-form").onsubmit = (e) => {
      e.preventDefault();
      state.bankPage = 1;
      bank();
    };
    $("sim-banco-anterior").onclick = () => {
      state.bankPage--;
      bank();
    };
    $("sim-banco-proxima").onclick = () => {
      state.bankPage++;
      bank();
    };
  } else {
    $("sim-filtros").onsubmit = (e) => {
      e.preventDefault();
      state.page = 1;
      load();
    };
    $("sim-anterior").onclick = () => {
      state.page--;
      load();
    };
    $("sim-proxima").onclick = () => {
      state.page++;
      load();
    };
  }
  $("sim-recarregar").onclick = load;
  globalThis.SimuladosAdminUI = {
    state,
    load,
    dirty,
    destroy() {
      state.generation++;
      document.removeEventListener("auth-identity-changed", clearIdentity);
      document.removeEventListener("click", leave);
      window.removeEventListener("beforeunload", beforeUnload);
    }
  };
  AuthUI.ready.then((ready) => {
    if (ready && available()) load();
  });
})();
