(() => {
  globalThis.PraticasUI?.destroy?.();
  const $ = (id) => document.getElementById(id);
  const mode = document.body.dataset.pratica;
  const state = {
    generation: 0,
    busy: false,
    page: 1,
    totalPages: 0,
    items: [],
    assuntos: [],
    detail: null,
    pending: null,
    filtersReady: false
  };
  const form = $("pratica-filtros");
  const list = $("pratica-lista");
  const status = $("pratica-status");
  const available = () => !AuthUI.blocked && !AuthUI.changedAccount;
  const element = (tag, text) => {
    const node = document.createElement(tag);
    node.textContent = text;
    return node;
  };
  function message(text, error = false) {
    status.textContent = text;
    status.dataset.erro = error;
  }
  function busy(value) {
    state.busy = value;
    document.querySelectorAll('[data-pratica-action]').forEach((b) => {
      b.disabled = value;
    });
    if ($("pratica-anterior")) {
      $("pratica-anterior").disabled = value || state.page <= 1;
      $("pratica-proxima").disabled = value || state.page >= state.totalPages;
    }
  }
  function clearIdentity() {
    state.generation++;
    state.items = [];
    state.detail = null;
    state.pending = null;
    document.querySelectorAll('[data-pratica-private]').forEach((node) => node.replaceChildren());
    $("pratica-resposta")?.reset();
    message("A conta mudou. Recarregue a página para continuar.", true);
  }
  document.addEventListener("auth-identity-changed", clearIdentity);
  const valid = (generation, user) => generation === state.generation && available() && AuthUI.user.id === user;
  async function identity() {
    return available() && await AuthUI.checkIdentity();
  }

  function options(select, items, title) {
    select.replaceChildren(new Option(title, ""), ...items.map((item) => new Option(item.nome, item.id)));
  }
  function subjects() {
    const materia = $("materia_id");
    options($("assunto_id"), state.assuntos.filter((a) => !materia || !materia.value || a.materia_id === Number(materia.value)), "Todos os assuntos");
  }
  function renderList(data) {
    state.items = data.itens;
    state.totalPages = data.total_paginas;
    list.replaceChildren();
    for (const item of data.itens) {
      const li = element("li", "");
      li.className = "pratica-card";
      const meta = element("span", `${item.materia.nome} · ${item.assunto.nome}`);
      meta.className = "pratica-meta";
      li.append(meta);
      if (mode === "historico") {
        li.append(element("h2", item.correta ? "Resposta correta" : "Resposta incorreta"));
        li.append(element("p", `Sua resposta: ${item.resposta_escolhida} · ${new Date(item.respondida_em).toLocaleString("pt-BR")}`));
        const link = element("a", "Ver correção");
        link.href = `/aluno/questao.html?tentativa_id=${item.id}`;
        li.append(link);
      } else {
        li.append(element("h2", item.enunciado));
        const button = element("button", "Resolver questão");
        button.type = "button";
        button.className = "auth-primary";
        button.dataset.praticaAction = "";
        button.addEventListener("click", () => start(item));
        li.append(button);
      }
      list.append(li);
    }
    $("pratica-pagina").textContent = `Página ${state.page} de ${Math.max(1, state.totalPages)}`;
    message(data.itens.length ? `${data.total_itens} ${mode === "historico" ? "tentativa(s) respondida(s)" : "questão(ões) disponível(is)"}.` :
      mode === "historico" ? "Nenhuma resposta neste filtro. Pratique uma questão para começar seu histórico." : "Nenhuma questão publicada disponível neste filtro.");
  }
  async function loadList() {
    if (!available()) return;
    const generation = ++state.generation, user = AuthUI.user.id;
    list.replaceChildren();
    state.items = [];
    busy(true);
    message("Carregando...");
    try {
      if (!await identity()) return;
      const query = new URLSearchParams({ pagina: state.page, por_pagina: 20 });
      for (const [key, value] of new FormData(form)) if (value) query.set(key, value);
      const data = await apiRequest(`/aluno/${mode === "historico" ? "praticas" : "questoes"}?${query}`);
      if (valid(generation, user) && await identity() && valid(generation, user)) renderList(data);
    } catch (error) {
      if (generation === state.generation) message(error.message, true);
    }
    finally {
      if (generation === state.generation) busy(false);
    }
  }
  async function start(item) {
    if (state.busy || !available()) return;
    // Não trocar conteúdo/chave enquanto um início tem resultado desconhecido.
    if (state.pending && state.pending.questao_versao_id !== item.questao_versao_id) {
      message("Tente novamente a mesma questão para recuperar o início pendente.", true);
      return;
    }
    state.pending ||= { questao_versao_id: item.questao_versao_id, chave_envio: crypto.randomUUID() };
    const generation = state.generation, user = AuthUI.user.id;
    busy(true);
    message("Iniciando tentativa...");
    try {
      if (!await identity()) return;
      const data = await apiRequest("/aluno/praticas", { method: "POST", body: JSON.stringify(state.pending) });
      if (valid(generation, user) && await identity() && valid(generation, user)) {
        state.pending = null;
        AuthUI.navigate(`/aluno/questao.html?tentativa_id=${data.id}`);
      }
    } catch (error) {
      if (generation === state.generation) {
        if ([400, 404, 409].includes(error.status)) state.pending = null;
        message(error.message, true);
      }
    } finally {
      if (generation === state.generation) busy(false);
    }
  }
  function renderDetail(data) {
    const chosen = document.querySelector('input[name="alternativa"]:checked')?.value;
    state.detail = data;
    $("pratica-classificacao").textContent = `${data.questao.materia.nome} · ${data.questao.assunto.nome} · ${data.questao.dificuldade}`;
    $("pratica-enunciado").textContent = data.questao.enunciado;
    const optionsNode = $("pratica-alternativas");
    optionsNode.replaceChildren();
    for (const letter of "ABCDE") {
      const label = element("label", "");
      label.className = "pratica-opcao";
      const radio = document.createElement("input");
      radio.type = "radio";
      radio.name = "alternativa";
      radio.value = letter;
      radio.required = true;
      radio.checked = letter === (data.resposta_escolhida || chosen);
      radio.disabled = data.estado === "respondida";
      label.append(radio, element("span", `${letter} · ${data.questao[`alternativa_${letter.toLowerCase()}`]}`));
      optionsNode.append(label);
    }
    const answered = data.estado === "respondida";
    $("pratica-enviar").hidden = answered;
    $("pratica-resultado").hidden = !answered;
    $("pratica-titulo").textContent = answered ? "Resultado da questão" : "Resolver questão";
    if (answered) {
      $("pratica-resultado").dataset.correta = data.correta;
      $("pratica-feedback").textContent = data.correta ? "Correto" : "Incorreto";
      $("pratica-correcao").textContent = `Sua resposta: ${data.resposta_escolhida} · Alternativa correta: ${data.gabarito}`;
      $("pratica-explicacao").textContent = data.explicacao || "Explicação indisponível para esta questão.";
      $("pratica-data").textContent = `Resposta salva em ${new Date(data.respondida_em).toLocaleString("pt-BR")}.`;
    }
    $("pratica-conteudo").hidden = false;
  }
  const query = new URLSearchParams(location.search);
  const id = query.get("tentativa_id");
  async function loadDetail() {
    if (!available() || state.busy) return;
    const generation = ++state.generation, user = AuthUI.user.id;
    busy(true);
    $("pratica-conteudo").hidden = true;
    message("Carregando tentativa...");
    try {
      if (!id || !/^[1-9]\d*$/.test(id)) throw new Error("Identificador de tentativa inválido.");
      if (!await identity()) return;
      const data = await apiRequest(`/aluno/praticas/${id}`);
      if (valid(generation, user) && await identity() && valid(generation, user)) {
        renderDetail(data);
        message(data.estado === "respondida" ? "Correção salva no seu histórico." : "Selecione uma alternativa. A resposta enviada será definitiva.");
      }
    } catch (error) {
      if (generation === state.generation) message(error.message, true);
    }
    finally {
      if (generation === state.generation) busy(false);
    }
  }
  async function answer(event) {
    event.preventDefault();
    if (state.busy || !state.detail || state.detail.estado === "respondida" || !available()) return;
    const alternativa = document.querySelector('input[name="alternativa"]:checked')?.value;
    if (!alternativa) {
      message("Selecione uma alternativa.", true);
      return;
    }
    const generation = state.generation, user = AuthUI.user.id;
    busy(true);
    message("Salvando resposta...");
    try {
      if (!await identity()) return;
      const data = await apiRequest(`/aluno/praticas/${id}/resposta`, { method: "POST", body: JSON.stringify({ alternativa }) });
      if (valid(generation, user) && await identity() && valid(generation, user)) {
        renderDetail(data);
        message("Resposta salva. Consulte sua correção abaixo.");
        $("pratica-feedback").focus();
      }
    } catch (error) {
      if (generation === state.generation) message(error.message, true);
    }
    finally {
      if (generation === state.generation) busy(false);
    }
  }
  $("pratica-resposta")?.addEventListener("submit", answer);
  $("pratica-recarregar").addEventListener("click", () => mode === "questao" ? loadDetail() : state.filtersReady ? loadList() : bootstrap());
  form?.addEventListener("submit", (event) => {
    event.preventDefault();
    state.page = 1;
    loadList();
  });
  $("materia_id")?.addEventListener("change", subjects);
  for (const [name, step] of [["pratica-anterior", -1], ["pratica-proxima", 1]]) {
    $(name)?.addEventListener("click", () => {
      if (!state.busy) {
        state.page += step;
        loadList();
      }
    });
  }
  async function bootstrap() {
    if (!await AuthUI.ready || !available()) return;
    if (mode === "questao") {
      await loadDetail();
      return;
    }
    const generation = ++state.generation, user = AuthUI.user.id;
    busy(true);
    message("Carregando filtros...");
    try {
      if (!await identity()) return;
      const [materias, assuntos] = await Promise.all([apiRequest("/materias"), apiRequest("/assuntos")]);
      if (!valid(generation, user)) return;
      state.assuntos = assuntos;
      if ($("materia_id")) options($("materia_id"), materias, "Todas as matérias");
      subjects();
      if (mode === "questoes" && query.has("assunto_id")) {
        const subject = query.get("assunto_id");
        if (query.getAll("assunto_id").length !== 1 || !/^[1-9]\d*$/.test(subject) ||
          !state.assuntos.some((a) => String(a.id) === subject)) {
          throw new Error("Assunto do plano indisponível ou inválido. Selecione um assunto disponível para praticar.");
        }
        $("assunto_id").value = subject;
      }
      state.filtersReady = true;
      // Histórico usa nomes preservados nas linhas mesmo para catálogo arquivado.
      await loadList();
    } catch (error) {
      if (generation === state.generation) message(error.message, true);
    }
    finally {
      if (generation === state.generation) busy(false);
    }
  }
  globalThis.PraticasUI = {
    state,
    bootstrap,
    loadList,
    loadDetail,
    destroy: () => {
      state.generation++;
      document.removeEventListener("auth-identity-changed", clearIdentity);
    }
  };
  bootstrap();
})();
