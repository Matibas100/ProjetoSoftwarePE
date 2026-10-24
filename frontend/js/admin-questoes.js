(() => {
  const ui = AdminUI;
  const $ = (id) => document.getElementById(id);
  const editor = document.body.dataset.questaoView === "editor";
  const fields = ["enunciado", "alternativa_a", "alternativa_b", "alternativa_c", "alternativa_d", "alternativa_e", "resposta_correta", "dificuldade", "assunto_id", "explicacao"];
  const filters = ["busca", "area_enem_id", "materia_id", "assunto_id", "dificuldade", "status"];
  const state = { page: 1, pages: 0, detail: null, areas: [], materias: [], assuntos: [], ready: false, busy: false, generation: 0 };
  const form = $(editor ? "questao-form" : "questoes-filtros");
  function unsavedGuard() {
    // A comparação inclui campos desabilitados durante envio/carregamento.
    const snapshot = () => JSON.stringify([...form.querySelectorAll("[name]")].map((node) => [node.name, node.value]));
    let saved = snapshot();
    const dirty = () => saved !== snapshot();
    const update = () => { $("questao-unsaved").hidden = !dirty(); };
    form.addEventListener("input", update); form.addEventListener("change", update);
    AuthUI.registerGuard(dirty);
    window.addEventListener("beforeunload", (event) => { if (dirty()) { event.preventDefault(); event.returnValue = ""; } });
    return { dirty, markPersisted: () => { saved = snapshot(); update(); } };
  }
  const guard = editor ? unsavedGuard() : null;
  guard?.markPersisted();
  const modal = ui.modalController($("admin-modal"));
  const params = new URLSearchParams(location.search);
  const idParam = params.get("id");
  const id = idParam === null ? null : (/^[1-9]\d*$/.test(idParam) ? Number(idParam) : NaN);

  function available() { return !AuthUI.blocked && !AuthUI.changedAccount; }
  function setBusy(busy) {
    state.busy = busy;
    if (editor) {
      const disabled = busy || !state.ready || state.detail?.status === "arquivada";
      form.querySelectorAll("input,textarea,select,button[type=submit]").forEach((node) => { node.disabled = disabled; });
      for (const name of ["questao-publicar", "questao-arquivar"]) $(name).disabled = disabled;
    } else {
      $("questoes-anterior").disabled = busy || state.page <= 1;
      $("questoes-proxima").disabled = busy || state.page >= state.pages;
    }
  }

  function classification(selected = {}) {
    const area = String(selected.area ?? $("area_enem_id").value);
    const materia = String(selected.materia ?? $("materia_id").value);
    const assunto = String(selected.assunto ?? $("assunto_id").value);
    ui.fillSelect($("area_enem_id"), state.areas, editor ? "Selecione" : "Todas", area);
    ui.fillSelect($("materia_id"), state.materias.filter((item) => !area || String(item.area_enem_id) === area), editor ? "Selecione" : "Todas", materia);
    const current = $("materia_id").value;
    ui.fillSelect($("assunto_id"), state.assuntos.filter((item) => (!current || String(item.materia_id) === current) &&
      (!area || state.materias.some((m) => m.id === item.materia_id && String(m.area_enem_id) === area))), editor ? "Selecione" : "Todos", assunto);
  }

  for (const name of ["area_enem_id", "materia_id"]) {
    $(name).addEventListener("change", () => classification({ materia: name === "area_enem_id" ? "" : $("materia_id").value, assunto: "" }));
  }

  async function catalog() {
    const [areas, materias, assuntos] = await Promise.all([
      apiRequest("/areas-enem"), apiRequest("/materias?status=todos"), apiRequest("/assuntos?status=todos"),
    ]);
    Object.assign(state, { areas, materias, assuntos });
  }

  function filterParams() {
    const query = new URLSearchParams();
    for (const field of filters) if ($(field).value.trim()) query.set(field, $(field).value.trim());
    query.set("pagina", String(state.page));
    return query;
  }

  function editLink(questaoId) {
    return `questao.html?id=${questaoId}&retorno=${encodeURIComponent(filterParams().toString())}`;
  }

  async function loadList() {
    if (!available()) return;
    const generation = ++state.generation;
    setBusy(true);
    $("questoes-estado").textContent = "Carregando questões...";
    $("questoes-corpo").replaceChildren();
    try {
      const query = filterParams(); query.set("por_pagina", "20");
      const data = await apiRequest(`/admin/questoes?${query}`);
      if (generation !== state.generation || !available()) return;
      state.pages = data.total_paginas;
      for (const item of data.itens) {
        const row = ui.element("tr");
        for (const value of [item.enunciado, item.area_enem.nome, item.materia.nome, item.assunto.nome, item.dificuldade]) row.append(ui.cell(value));
        const status = ui.cell(""); status.append(ui.statusPill(item.status)); row.append(status);
        const action = ui.cell(""); const link = ui.element("a", "Abrir questão", "button button--text");
        link.href = editLink(item.id); link.setAttribute("aria-label", `Abrir questão ${item.id}`); action.append(link); row.append(action);
        $("questoes-corpo").append(row);
      }
      $("questoes-total").textContent = `${data.total_itens} ${data.total_itens === 1 ? "questão" : "questões"}`;
      $("questoes-pagina").textContent = `Página ${state.page}`;
      $("questoes-estado").textContent = data.itens.length ? "" : (filters.some((f) => $(f).value) ? "Nenhuma questão corresponde aos filtros." : "Nenhuma questão cadastrada. Cadastre a primeira questão.");
      history.replaceState(null, "", `?${filterParams()}`);
      $("questao-nova").href = `questao.html?retorno=${encodeURIComponent(filterParams().toString())}`;
    } catch (error) {
      if (generation === state.generation) $("questoes-estado").textContent = error.message;
    } finally { if (generation === state.generation) setBusy(false); }
  }

  function fillDetail(detail) {
    state.detail = detail;
    if (detail) {
      for (const field of fields) $(field).value = detail.questao[field] ?? "";
      const assunto = state.assuntos.find((item) => item.id === detail.questao.assunto_id);
      const materia = state.materias.find((item) => item.id === assunto?.materia_id);
      classification({ area: materia?.area_enem_id || "", materia: materia?.id || "", assunto: detail.questao.assunto_id });
      $("questao-titulo").textContent = `Editar questão ${detail.questao.id}`;
      $("questao-status").textContent = `Status: ${detail.status}`;
      $("questao-revisao").textContent = `Revisão ${detail.revisao} · ${detail.versao_publicada_id ? "Versão publicada preservada" : "Ainda não publicada"}`;
      $("questao-versoes").replaceChildren(...detail.versoes.map((v) => ui.element("li", `Versão ${v.numero} · ${v.estado}`)));
      $("questao-acoes").hidden = detail.status === "arquivada";
    } else classification();
    guard.markPersisted();
  }

  async function loadEditor() {
    if (!available()) return;
    if (guard.dirty() && !window.confirm("Descartar alterações não salvas e recarregar?")) return;
    const generation = ++state.generation;
    state.ready = false; setBusy(true);
    $("questao-carregando").textContent = "Carregando catálogo e questão...";
    try {
      if (Number.isNaN(id)) throw new Error("Identificador de questão inválido.");
      await catalog();
      const currentId = state.detail?.questao.id ?? id;
      const detail = currentId === null ? null : await apiRequest(`/questoes/${currentId}`);
      if (generation !== state.generation || !available()) return;
      fillDetail(detail); state.ready = true;
      $("questao-carregando").textContent = "";
    } catch (error) { $("questao-carregando").textContent = error.message; }
    finally { if (generation === state.generation) setBusy(false); }
  }

  function content() {
    const data = {};
    for (const field of fields) data[field] = $(field).value.trim();
    for (const field of fields.filter((f) => f !== "explicacao")) {
      if (!data[field]) { $(field).focus(); throw new Error("Preencha o conteúdo, a classificação e a resposta correta."); }
    }
    data.assunto_id = Number(data.assunto_id);
    data.explicacao ||= null;
    return data;
  }

  async function save(event) {
    event.preventDefault();
    if (state.busy || !state.ready || !available()) return;
    let data;
    try { data = content(); }
    catch (error) { ui.showMessage($("questao-mensagem"), error.message, "error"); return; }
    setBusy(true);
    const userId = AuthUI.user.id;
    try {
      let detail;
      if (state.detail) {
        data.revisao = state.detail.revisao;
        detail = await apiRequest(`/questoes/${state.detail.questao.id}`, { method: "PUT", body: JSON.stringify(data) });
      } else {
        const created = await apiRequest("/questoes", { method: "POST", body: JSON.stringify(data) });
        // Guarda a identidade confirmada antes da leitura: falha no GET não duplica cadastro.
        if (!available() || AuthUI.user.id !== userId) return;
        state.detail = { questao: created, status: "rascunho", revisao: 1, versao_publicada_id: null, versoes: [] };
        history.replaceState(null, "", `?id=${created.id}&retorno=${encodeURIComponent(params.get("retorno") || "")}`);
        detail = state.detail;
      }
      if (!available() || AuthUI.user.id !== userId) return;
      fillDetail(detail);
      ui.showMessage($("questao-mensagem"), "Rascunho salvo. A publicação exige revisão e confirmação.");
    } catch (error) { ui.showMessage($("questao-mensagem"), error.message, "error"); }
    finally { setBusy(false); }
  }

  async function action(name) {
    if (state.busy || !state.detail || !available()) return;
    if (guard.dirty()) { ui.showMessage($("questao-mensagem"), "Salve o rascunho antes desta ação.", "error"); return; }
    const reason = $("questao-motivo").value.trim();
    if (reason.length < 3 || reason.length > 500) {
      ui.showMessage($("questao-mensagem"), "Informe um motivo com 3 a 500 caracteres.", "error"); $("questao-motivo").focus(); return;
    }
    const detail = state.detail;
    const userId = AuthUI.user.id;
    setBusy(true);
    try {
      const confirmed = await modal.confirm({ title: name === "publicar" ? "Revisar e publicar questão" : "Arquivar questão",
        text: `Questão ${detail.questao.id}, revisão ${detail.revisao}. ${name === "publicar" ? "Confirme a revisão do conteúdo, gabarito e classificação; será publicada uma versão imutável." : "Novos usos serão bloqueados; versões históricas serão preservadas."} Motivo: ${reason}`,
        danger: name === "arquivar" });
      if (!confirmed || !available() || AuthUI.user.id !== userId) return;
      const result = await apiRequest(`/questoes/${detail.questao.id}/${name}`, { method: "POST",
        body: JSON.stringify({ revisao: detail.revisao, confirmar: true, motivo: reason }) });
      if (!available() || AuthUI.user.id !== userId) return;
      fillDetail(result);
      ui.showMessage($("questao-mensagem"), name === "publicar" ? "Versão publicada após revisão." : "Questão arquivada; histórico preservado.");
    } catch (error) { ui.showMessage($("questao-mensagem"), error.message, "error"); }
    finally { setBusy(false); $("questao-mensagem").focus(); }
  }

  if (editor) {
    $("questao-mensagem").tabIndex = -1;
    const returnQuery = new URLSearchParams(params.get("retorno") || "");
    const safe = new URLSearchParams();
    for (const field of [...filters, "pagina"]) if (returnQuery.has(field)) safe.set(field, returnQuery.get(field));
    $("questao-voltar").href = `questoes.html?${safe}`;
    form.addEventListener("submit", save);
    $("questao-recarregar").addEventListener("click", loadEditor);
    $("questao-cancelar").addEventListener("click", () => $("questao-voltar").click());
    $("questao-publicar").addEventListener("click", () => action("publicar"));
    $("questao-arquivar").addEventListener("click", () => action("arquivar"));
    document.addEventListener("click", (event) => {
      if (!event.target.closest("a[href]") || !guard.dirty()) return;
      if (!window.confirm("Descartar alterações não salvas e sair?")) event.preventDefault();
      else guard.markPersisted();
    });
  } else {
    for (const field of filters) if (params.has(field)) $(field).value = params.get(field);
    state.page = Math.max(1, Number(params.get("pagina")) || 1);
    form.addEventListener("submit", (event) => { event.preventDefault(); state.page = 1; loadList(); });
    $("questoes-limpar").addEventListener("click", () => { form.reset(); classification({ area: "", materia: "", assunto: "" }); state.page = 1; loadList(); });
    $("questoes-recarregar").addEventListener("click", loadList);
    $("questoes-anterior").addEventListener("click", () => { if (state.page > 1) { state.page--; loadList(); } });
    $("questoes-proxima").addEventListener("click", () => { if (state.page < state.pages) { state.page++; loadList(); } });
  }

  (async () => {
    if (!(await AuthUI.ready)) return;
    if (editor) await loadEditor();
    else {
      try { await catalog(); classification({ area: params.get("area_enem_id") || "", materia: params.get("materia_id") || "", assunto: params.get("assunto_id") || "" }); await loadList(); }
      catch (error) { $("questoes-estado").textContent = error.message; }
    }
  })();
})();
