(async () => {
  if (globalThis.AuthUI && !(await globalThis.AuthUI.ready)) return;
  const ui = globalThis.AdminUI;
  const form = document.querySelector("#materia-form");
  const idInput = document.querySelector("#materia-id");
  const nameInput = document.querySelector("#materia-nome");
  const areaSelect = document.querySelector("#materia-area");
  const descriptionInput = document.querySelector("#materia-descricao");
  const formStatus = document.querySelector("#materia-status-form");
  const message = document.querySelector("#materia-mensagem");
  const nameError = document.querySelector("#materia-nome-erro");
  const body = document.querySelector("#materias-corpo");
  const tableState = document.querySelector("#materias-estado");
  const search = document.querySelector("#materias-busca");
  const statusFilter = document.querySelector("#materias-status");
  const modal = ui.modalController(document.querySelector("#admin-modal"));
  const guard = ui.createUnsavedGuard(form, document.querySelector("#materia-unsaved"));
  const state = { areas: [], items: [], page: 1, pages: 0 };
  let searchTimer;

  let detailToken = 0;
  let detailController;
  let detailLoading = false;
  let saving = false;
  const saveButton = document.querySelector("#materia-salvar");
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
      && Number.isInteger(item.area_enem_id) && item.area_enem_id > 0
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
    ui.showMessage(message, "Carregando matéria...", "info");
    try {
      const [item] = await Promise.all([
        apiRequest(`/materias/${id}`, { signal: controller.signal }), optionsReady,
      ]);
      if (!current()) return;
      if (!validDetail(item, id)) throw new Error("Resposta inválida do servidor. Selecione Editar para tentar novamente.");
      if (!state.areas.some((area) => area.id === item.area_enem_id)) {
        throw new Error("Área indisponível. Atualize a página e selecione Editar novamente.");
      }
      if (!current() || !await AuthUI.checkIdentity() || !current()) return;

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


  function resetForm(focus = false) {
    invalidateDetail();
    form.reset();
    idInput.value = "";
    formStatus.value = "ativa";
    document.querySelector("#materia-editor-titulo").firstChild.textContent = "Criar matéria ";
    document.querySelector("#materia-salvar").textContent = "Salvar matéria";
    nameError.textContent = "";
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
    idInput.value = item.id;
    nameInput.value = item.nome;
    areaSelect.value = item.area_enem_id;
    descriptionInput.value = item.descricao || "";
    formStatus.value = item.status;
    document.querySelector("#materia-editor-titulo").firstChild.textContent = `Editar matéria · ${item.nome} `;
    document.querySelector("#materia-salvar").textContent = "Salvar alterações";
    nameError.textContent = "";
    ui.hideMessage(message);
    guard.markPersisted();
    document.querySelector("#materia-editor").scrollIntoView({ behavior: "smooth" });
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
        ui.cell(item.nome),
        ui.cell(item.area_enem.nome),
        ui.cell(item.descricao || "—"),
        ui.cell(item.assuntos),
        ui.cell(item.questoes),
      );
      const statusCell = ui.cell();
      statusCell.replaceChildren(ui.statusPill(item.status));
      const actionCell = ui.cell(null, "actions-cell");
      actionCell.replaceChildren(ui.actionMenu(item.id, actionsFor(item)));
      row.append(statusCell, ui.cell(ui.dateLabel(item.atualizado_em)), actionCell);
      body.appendChild(row);
    });
    tableState.hidden = state.items.length > 0;
    tableState.textContent = state.items.length ? "" : search.value.trim() || statusFilter.value
      ? "Nenhuma matéria encontrada para os filtros aplicados."
      : "Nenhuma matéria cadastrada. Use Nova matéria para começar.";
    document.querySelector("#materias-total").textContent = `${state.total || 0} ${state.total === 1 ? "matéria" : "matérias"}`;
    document.querySelector("#materias-pagina").textContent = `Página ${state.page}${state.pages ? ` de ${state.pages}` : ""}`;
    document.querySelector("#materias-anterior").disabled = state.page <= 1;
    document.querySelector("#materias-proxima").disabled = state.page >= state.pages;
  }

  async function load() {
    tableState.hidden = false;
    tableState.textContent = "Carregando matérias...";
    const filters = {};
    if (search.value.trim()) filters.busca = search.value.trim();
    if (statusFilter.value) filters.status = statusFilter.value;
    const query = ui.adminQuery(state.page, filters);
    try {
      const data = await apiRequest(`/admin/materias?${query}`);
      ui.applyPage(state, data);
      render();
    } catch (error) {
      state.items = [];
      render();
      tableState.hidden = false;
      tableState.textContent = error.message;
    }
  }

  async function save(event) {
    event.preventDefault();
    const wasLoading = detailLoading;
    invalidateDetail();
    if (wasLoading || saving || !available()) return;
    nameError.textContent = "";
    ui.hideMessage(message);
    if (!nameInput.value.trim() || !areaSelect.value) {
      ui.showMessage(message, "Preencha nome e Área do ENEM.", "error");
      return;
    }
    const id = idInput.value;
    const data = {
      nome: nameInput.value,
      area_enem_id: Number(areaSelect.value),
      descricao: descriptionInput.value,
      status: formStatus.value,
    };
    const button = document.querySelector("#materia-salvar");
    saving = true;
    button.disabled = true;
    try {
      await apiRequest(id ? `/materias/${id}` : "/materias", {
        method: id ? "PUT" : "POST",
        body: JSON.stringify(data),
      });
      resetForm();
      ui.showMessage(message, id ? "Matéria atualizada com sucesso." : "Matéria criada com sucesso.");
      await load();
    } catch (error) {
      if (error.status === 409) nameError.textContent = error.message;
      ui.showMessage(message, error.message, "error");
    } finally {
      saving = false;
      button.disabled = detailLoading;
    }
  }

  async function changeStatus(item, action) {
    let impact = "";
    if (action === "arquivar") {
      const data = await apiRequest(`/materias/${item.id}/impacto-exclusao`);
      impact = `\nVínculos preservados: ${data.impacto.assuntos} assuntos e ${data.impacto.questoes} questões.`;
    }
    const confirmed = await modal.confirm({
      title: `${action[0].toUpperCase()}${action.slice(1)} matéria?`,
      text: `${item.nome}.${impact}`,
      confirmLabel: action[0].toUpperCase() + action.slice(1),
      danger: action === "arquivar",
    });
    if (!confirmed) return;
    try {
      await apiRequest(`/materias/${item.id}/${action}`, { method: "POST" });
      await load();
    } catch (error) {
      document.querySelector("#materia-contexto").className = "notice notice--warning";
      document.querySelector("#materia-contexto").textContent = error.message;
    }
  }

  async function remove(item) {
    try {
      const data = await apiRequest(`/materias/${item.id}/impacto-exclusao`);
      const impact = data.impacto;
      if (impact.assuntos || impact.transferencias) {
        await modal.confirm({
          title: "Exclusão bloqueada",
          text: `Esta matéria possui ${impact.assuntos} assuntos e ${impact.questoes} questões. Arquive ou transfira os conteúdos.`,
          confirmLabel: "Entendi",
        });
        return;
      }
      if (!await modal.confirm({ title: "Excluir matéria?", text: item.nome, confirmLabel: "Excluir", danger: true })) return;
      await apiRequest(`/materias/${item.id}`, { method: "DELETE" });
      if (idInput.value === String(item.id)) resetForm();
      await load();
    } catch (error) {
      document.querySelector("#materia-contexto").textContent = error.message;
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

  form.addEventListener("submit", save);
  document.querySelector("#nova-materia").addEventListener("click", () => startForm(true));
  document.querySelector("#materia-cancelar").addEventListener("click", () => startForm(false));
  document.querySelector("#materias-limpar").addEventListener("click", () => { search.value = ""; statusFilter.value = ""; state.page = 1; load(); });
  statusFilter.addEventListener("change", () => { state.page = 1; load(); });
  search.addEventListener("input", () => { clearTimeout(searchTimer); searchTimer = setTimeout(async () => {
  if (globalThis.AuthUI && !(await globalThis.AuthUI.ready)) return; state.page = 1; load(); }, 250); });
  document.querySelector("#materias-anterior").addEventListener("click", () => { state.page -= 1; load(); });
  document.querySelector("#materias-proxima").addEventListener("click", () => { state.page += 1; load(); });

  const optionsReady = apiRequest("/areas-enem").then((areas) => {
    const pristine = !guard.dirty();
    state.areas = areas;
    ui.fillSelect(areaSelect, areas, "Selecione", areaSelect.value);
    if (pristine) guard.markPersisted();
  });
  optionsReady.catch((error) => ui.showMessage(message, error.message, "error"));
  load();
})();
