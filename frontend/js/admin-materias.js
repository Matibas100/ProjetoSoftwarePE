(() => {
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

  function resetForm(focus = false) {
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
      button.disabled = false;
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
      if (await discardIfNeeded()) edit(item);
    } else if (button.dataset.action === "delete") {
      await remove(item);
    } else {
      await changeStatus(item, button.dataset.action);
    }
  });

  form.addEventListener("submit", save);
  document.querySelector("#nova-materia").addEventListener("click", async () => { if (await discardIfNeeded()) resetForm(true); });
  document.querySelector("#materia-cancelar").addEventListener("click", async () => { if (await discardIfNeeded()) resetForm(); });
  document.querySelector("#materias-limpar").addEventListener("click", () => { search.value = ""; statusFilter.value = ""; state.page = 1; load(); });
  statusFilter.addEventListener("change", () => { state.page = 1; load(); });
  search.addEventListener("input", () => { clearTimeout(searchTimer); searchTimer = setTimeout(() => { state.page = 1; load(); }, 250); });
  document.querySelector("#materias-anterior").addEventListener("click", () => { state.page -= 1; load(); });
  document.querySelector("#materias-proxima").addEventListener("click", () => { state.page += 1; load(); });

  Promise.all([apiRequest("/areas-enem"), load()]).then(([areas]) => {
    state.areas = areas;
    ui.fillSelect(areaSelect, areas, "Selecione");
    guard.markPersisted();
  }).catch((error) => ui.showMessage(message, error.message, "error"));
})();
