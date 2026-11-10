(async () => {
  if (globalThis.AuthUI && !(await globalThis.AuthUI.ready)) return;
  const ui = globalThis.AdminUI;
  const form = document.querySelector("#assunto-form");
  const idInput = document.querySelector("#assunto-id");
  const nameInput = document.querySelector("#assunto-nome");
  const matterSelect = document.querySelector("#assunto-materia");
  const descriptionInput = document.querySelector("#assunto-descricao");
  const message = document.querySelector("#assunto-mensagem");
  const impactNotice = document.querySelector("#assunto-impacto");
  const nameError = document.querySelector("#assunto-nome-erro");
  const body = document.querySelector("#assuntos-corpo");
  const tableState = document.querySelector("#assuntos-estado");
  const search = document.querySelector("#assuntos-busca");
  const areaFilter = document.querySelector("#assuntos-area-filtro");
  const matterFilter = document.querySelector("#assuntos-materia-filtro");
  const statusFilter = document.querySelector("#assuntos-status");
  const modal = ui.modalController(document.querySelector("#admin-modal"));
  const guard = ui.createUnsavedGuard(form, document.querySelector("#assunto-unsaved"));
  const state = { areas: [], matters: [], items: [], page: 1, pages: 0, editing: null };
  let searchTimer;

  let detailToken = 0;
  let detailController;
  let detailLoading = false;
  let saving = false;
  const saveButton = document.querySelector("#assunto-salvar");
  const available = () => !AuthUI.blocked && !AuthUI.changedAccount && AuthUI.user?.perfil === "administrador";
  const identity = () => `${AuthUI.user?.id}:${AuthUI.user?.perfil}`;

  function invalidateDetail() {
    detailToken += 1;
    detailController?.abort();
    detailController = null;
    if (detailLoading) ui.hideMessage(message);
    detailLoading = false;
    saveButton.disabled = saving;
    form.removeAttribute("aria-busy");
    return detailToken;
  }

  function validDetail(item, id) {
    return item && !Array.isArray(item) && typeof item === "object" && item.id === id
    && typeof item.nome === "string" && item.nome.trim()
    && ["ativa", "inativa", "arquivada"].includes(item.status)
    && Number.isInteger(item.materia_id) && item.materia_id > 0
    && (item.descricao === null || typeof item.descricao === "string");
  }

  async function selectDetail(id) {
    const token = invalidateDetail();
    const user = identity();
    const current = () => token === detailToken && available() && user === identity();
    if (!available() || saving || !await discardIfNeeded() || !current()) return;
    const controller = new AbortController();
    detailController = controller;
    detailLoading = true;
    saveButton.disabled = true;
    form.setAttribute("aria-busy", "true");
    ui.showMessage(message, "Carregando assunto...", "info");
    try {
      const [item] = await Promise.all([
        apiRequest(`/assuntos/${id}`, { signal: controller.signal }),
        optionsReady,
      ]);
      if (!current()) return;
      if (!validDetail(item, id)) throw new Error("Resposta inválida do servidor. Selecione Editar para tentar novamente.");
      const matters = await apiRequest("/materias?status=todos", { signal: controller.signal });
      if (!current()) return;
      if (!Array.isArray(matters) || !matters.every((matter) => matter && Number.isInteger(matter.id)
        && typeof matter.nome === "string" && ["ativa", "inativa", "arquivada"].includes(matter.status))
        || !matters.some((matter) => matter.id === item.materia_id)) {
        throw new Error("Matérias indisponíveis. Atualize a página e selecione Editar novamente.");
      }
      if (!current() || !await AuthUI.checkIdentity() || !current()) return;
      state.matters = matters;
      edit(item);
    } catch (error) {
      if (current()) ui.showMessage(message, error.message, "error");
    } finally {
      if (token === detailToken) {
        detailController = null;
        detailLoading = false;
        saveButton.disabled = saving;
        form.removeAttribute("aria-busy");
      }
    }
  }

  async function startForm(focus = false) {
    const token = invalidateDetail();
    if (await discardIfNeeded() && token === detailToken) resetForm(focus);
  }

  form.addEventListener("input", invalidateDetail);
  form.addEventListener("change", invalidateDetail);
  document.addEventListener("auth-required", invalidateDetail);
  document.addEventListener("auth-identity-changed", invalidateDetail);
  guard.markPersisted();


  function activeMatters(currentId = null) {
    return state.matters.filter((item) => item.status === "ativa" || item.id === currentId);
  }

  function refreshMatterFilters() {
    const areaId = Number(areaFilter.value);
    const currentFilter = matterFilter.value;
    const filtered = state.matters.filter((item) => !areaId || item.area_enem_id === areaId);
    ui.fillSelect(matterFilter, filtered, "Todas", currentFilter);
    const labels = [];
    if (areaFilter.value) labels.push(state.areas.find((area) => area.id === areaId)?.nome);
    if (matterFilter.value) labels.push(state.matters.find((item) => item.id === Number(matterFilter.value))?.nome);
    document.querySelector("#assuntos-filtros-aplicados").textContent = labels.length
    ? `Filtros aplicados: ${labels.filter(Boolean).join(" · ")}`
    : "Nenhum filtro aplicado";
  }

  function resetForm(focus = false) {
    invalidateDetail();
    form.reset();
    state.editing = null;
    idInput.value = "";
    ui.fillSelect(matterSelect, activeMatters(), "Selecione");
    document.querySelector("#assunto-editor-titulo").firstChild.textContent = "Criar assunto ";
    document.querySelector("#assunto-salvar").textContent = "Salvar assunto";
    nameError.textContent = "";
    impactNotice.hidden = true;
    ui.hideMessage(message);
    guard.markPersisted();
    if (focus) nameInput.focus();
  }

  async function discardIfNeeded() {
    return !guard.dirty() || modal.confirm({
      title: "Descartar alterações?",
      text: "As alterações não salvas serão perdidas.",
      confirmLabel: "Descartar",
      danger: true,
    });
  }

  function edit(item) {
    state.editing = item;
    idInput.value = item.id;
    nameInput.value = item.nome;
    ui.fillSelect(matterSelect, activeMatters(item.materia_id), "Selecione", item.materia_id);
    descriptionInput.value = item.descricao || "";
    document.querySelector("#assunto-editor-titulo").firstChild.textContent = `Editar assunto · ${item.nome} `;
    document.querySelector("#assunto-salvar").textContent = "Salvar assunto";
    nameError.textContent = "";
    impactNotice.hidden = true;
    ui.hideMessage(message);
    guard.markPersisted();
    document.querySelector("#assunto-editor").scrollIntoView({ behavior: "smooth" });
    nameInput.focus();
  }

  function actionsFor(item) {
    const actions = [{ action: "edit", label: "Editar" }];
    if (item.status === "ativa") actions.push({ action: "inativar", label: "Inativar" });
    if (item.status !== "arquivada") actions.push({ action: "arquivar", label: "Arquivar" });
    if (item.status !== "ativa") actions.push({ action: "reativar", label: "Reativar" });
    actions.push({ action: "delete", label: "Excluir", danger: true });
    return actions;
  }

  function render() {
    body.replaceChildren();
    state.items.forEach((item) => {
      const row = document.createElement("tr");
      row.append(
        ui.cell(item.nome), ui.cell(item.area_enem.nome), ui.cell(item.materia.nome),
        ui.cell(item.descricao || "—"), ui.cell(item.questoes),
      );
      const summaryCell = ui.cell("—");
      summaryCell.title = "Indisponível nesta versão";
      summaryCell.setAttribute("aria-label", "Resumos indisponíveis nesta versão");
      const statusCell = ui.cell();
      statusCell.replaceChildren(ui.statusPill(item.status));
      const actionCell = ui.cell(null, "actions-cell");
      actionCell.replaceChildren(ui.actionMenu(item.id, actionsFor(item)));
      row.append(summaryCell, statusCell, actionCell);
      body.appendChild(row);
    });
    tableState.hidden = state.items.length > 0;
    tableState.textContent = state.items.length ? "" : search.value.trim() || areaFilter.value || matterFilter.value || statusFilter.value
    ? "Nenhum assunto encontrado para os filtros aplicados."
    : "Nenhum assunto cadastrado. Use Novo assunto para começar.";
    document.querySelector("#assuntos-total").textContent = `${state.total || 0} ${state.total === 1 ? "assunto" : "assuntos"}`;
    document.querySelector("#assuntos-pagina").textContent = `Página ${state.page}${state.pages ? ` de ${state.pages}` : ""}`;
    document.querySelector("#assuntos-anterior").disabled = state.page <= 1;
    document.querySelector("#assuntos-proxima").disabled = state.page >= state.pages;
  }

  async function load() {
    tableState.hidden = false;
    tableState.textContent = "Carregando assuntos...";
    const filters = {};
    if (search.value.trim()) filters.busca = search.value.trim();
    if (areaFilter.value) filters.area_enem_id = areaFilter.value;
    if (matterFilter.value) filters.materia_id = matterFilter.value;
    if (statusFilter.value) filters.status = statusFilter.value;
    const query = ui.adminQuery(state.page, filters);
    try {
      const data = await apiRequest(`/admin/assuntos?${query}`);
      ui.applyPage(state, data);
      render();
    } catch (error) {
      state.items = [];
      render();
      tableState.hidden = false;
      tableState.textContent = error.message;
    }
  }

  async function previewTransfer(subjectId, destinationId) {
    return apiRequest(`/assuntos/${subjectId}/impacto-transferencia?materia_destino_id=${destinationId}`);
  }

  async function confirmTransfer(preview) {
    const origin = preview.materia_origem.nome;
    const destination = preview.materia_destino.nome;
    const count = preview.impacto.questoes;
    return modal.confirm({
      title: "Confirmar transferência",
      text: `Origem: ${origin}. Destino: ${destination}. Questões vinculadas: ${count}. Os vínculos serão preservados.`,
      confirmLabel: "Transferir assunto",
    });
  }

  async function transfer(preview, data, retry = true) {
    try {
      return await apiRequest(`/assuntos/${preview.assunto_id}/transferir`, {
        method: "POST",
        body: JSON.stringify({
          materia_destino_id: data.materia_id,
          impacto_esperado: preview.impacto,
          nome: data.nome,
          descricao: data.descricao,
        }),
      });
    } catch (error) {
      const current = error.details?.previa;
      if (retry && error.status === 409 && current && await confirmTransfer(current)) {
        return transfer(current, data, false);
      }
      throw error;
    }
  }

  async function save(event) {
    event.preventDefault();
    const wasLoading = detailLoading;
    invalidateDetail();
    if (wasLoading || saving || !available()) return;
    nameError.textContent = "";
    ui.hideMessage(message);
    if (!nameInput.value.trim() || !matterSelect.value) {
      ui.showMessage(message, "Preencha nome e matéria.", "error");
      return;
    }
    const data = { nome: nameInput.value, descricao: descriptionInput.value, materia_id: Number(matterSelect.value) };
    const id = idInput.value;
    const isTransfer = id && state.editing.materia_id !== data.materia_id;
    const button = document.querySelector("#assunto-salvar");
    saving = true;
    button.disabled = true;
    try {
      if (isTransfer) {
        const preview = await previewTransfer(Number(id), data.materia_id);
        impactNotice.textContent = `Origem: ${preview.materia_origem.nome}. Destino: ${preview.materia_destino.nome}. Questões vinculadas: ${preview.impacto.questoes}. Os vínculos serão preservados.`;
        impactNotice.hidden = false;
        if (!await confirmTransfer(preview)) return;
        await transfer(preview, data);
      } else {
        await apiRequest(id ? `/assuntos/${id}` : "/assuntos", {
          method: id ? "PUT" : "POST",
          body: JSON.stringify(data),
        });
      }
      resetForm();
      ui.showMessage(message, id ? "Assunto atualizado com sucesso." : "Assunto criado com sucesso.");
      await load();
    } catch (error) {
      if (error.status === 409) nameError.textContent = error.message;
      ui.showMessage(message, error.message, "error");
    } finally {
      saving = false;
      button.disabled = detailLoading;
      if (isTransfer) button.focus();
    }
  }

  async function changeStatus(item, action) {
    const confirmed = await modal.confirm({
      title: `${action[0].toUpperCase()}${action.slice(1)} assunto?`,
      text: `${item.nome}. ${item.questoes} questões permanecerão vinculadas.`,
      confirmLabel: action[0].toUpperCase() + action.slice(1),
      danger: action === "arquivar",
    });
    if (!confirmed) return;
    try {
      await apiRequest(`/assuntos/${item.id}/${action}`, { method: "POST" });
      await load();
    } catch (error) {
      document.querySelector("#assunto-contexto").textContent = error.message;
    }
  }

  async function remove(item) {
    try {
      const data = await apiRequest(`/assuntos/${item.id}/impacto-exclusao`);
      if (data.impacto.questoes || data.impacto.transferencias) {
        await modal.confirm({
          title: "Exclusão bloqueada",
          text: `Este assunto possui ${data.impacto.questoes} questões ou histórico de transferência. Arquive-o para preservar os vínculos.`,
          confirmLabel: "Entendi",
        });
        return;
      }
      if (!await modal.confirm({ title: "Excluir assunto?", text: item.nome, confirmLabel: "Excluir", danger: true })) return;
      await apiRequest(`/assuntos/${item.id}`, { method: "DELETE" });
      if (idInput.value === String(item.id)) resetForm();
      await load();
    } catch (error) {
      document.querySelector("#assunto-contexto").textContent = error.message;
    }
  }

  body.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) return;
    const item = state.items.find((current) => current.id === Number(button.dataset.id));
    if (!item) return;
    if (button.dataset.action === "edit") {
      await selectDetail(item.id);
    } else if (button.dataset.action === "delete") {
      await remove(item);
    } else {
      await changeStatus(item, button.dataset.action);
    }
  });

  matterSelect.addEventListener("change", async () => {
    if (!state.editing || Number(matterSelect.value) === state.editing.materia_id || !matterSelect.value) {
      impactNotice.hidden = true;
      return;
    }
    try {
      const preview = await previewTransfer(state.editing.id, Number(matterSelect.value));
      impactNotice.textContent = `Origem: ${preview.materia_origem.nome}. Destino: ${preview.materia_destino.nome}. Questões vinculadas: ${preview.impacto.questoes}. Os vínculos serão preservados.`;
      impactNotice.hidden = false;
    } catch (error) {
      impactNotice.textContent = error.message;
      impactNotice.hidden = false;
    }
  });
  form.addEventListener("submit", save);
  document.querySelector("#novo-assunto").addEventListener("click", () => startForm(true));
  document.querySelector("#assunto-cancelar").addEventListener("click", () => startForm(false));
  document.querySelector("#assuntos-limpar").addEventListener("click", () => {
    search.value = "";
    areaFilter.value = "";
    matterFilter.value = "";
    statusFilter.value = "";
    refreshMatterFilters();
    state.page = 1;
    load();
  });
  areaFilter.addEventListener("change", () => {
    matterFilter.value = "";
    refreshMatterFilters();
    state.page = 1;
    load();
  });
  matterFilter.addEventListener("change", () => {
    refreshMatterFilters();
    state.page = 1;
    load();
  });
  statusFilter.addEventListener("change", () => {
    state.page = 1;
    load();
  });
  search.addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(async () => {
      if (globalThis.AuthUI && !(await globalThis.AuthUI.ready)) return;
      state.page = 1;
      load();
    }, 250);
  });
  document.querySelector("#assuntos-anterior").addEventListener("click", () => {
    state.page -= 1;
    load();
  });
  document.querySelector("#assuntos-proxima").addEventListener("click", () => {
    state.page += 1;
    load();
  });

  const optionsReady = Promise.all([apiRequest("/areas-enem"), apiRequest("/materias?status=todos")])
  .then(([areas, matters]) => {
    const pristine = !guard.dirty();
    state.areas = areas;
    state.matters = matters;
    ui.fillSelect(areaFilter, areas, "Todas", areaFilter.value);
    refreshMatterFilters();
    ui.fillSelect(matterSelect, activeMatters(), "Selecione", matterSelect.value);
    if (pristine) guard.markPersisted();
  });
  optionsReady.catch((error) => ui.showMessage(message, error.message, "error"));
  load();
})();
