(() => {
  globalThis.DesempenhoUI?.destroy();
  const $ = (id) => document.getElementById(id), mode = document.body.dataset.desempenho;
  const state = { generation: 0, filters: {}, data: null };
  const blocks = [...document.querySelectorAll('[data-dash-block]')];
  const available = () => !AuthUI.blocked && !AuthUI.changedAccount;
  const valid = (g, user) => state.generation === g && available() && AuthUI.user.id === user;
  const element = (tag, text) => {
    const n = document.createElement(tag);
    n.textContent = text;
    return n;
  };
  const names = {
    sem_dados: "Sem dados",
    amostra_pequena: "Amostra pequena",
    dados_disponiveis: "Dados disponíveis"
  };
  const percentage = (value) => value === null ? "Indisponível" : `${Number(value).toLocaleString("pt-BR", { maximumFractionDigits: 2 })}%`;
  function clear(estado, mensagem) {
    state.data = null;
    document.querySelectorAll('[data-dash-private]').forEach((n) => n.replaceChildren());
    for (const block of blocks) {
      block.dataset.estado = estado;
      block.setAttribute("aria-busy", estado === "carregando");
      block.querySelector('[data-dash-message]').textContent = mensagem;
      block.querySelector('[data-dash-retry]').hidden = estado !== "erro";
    }
  }
  function identityChanged() {
    state.generation++;
    state.filters = {};
    $("dash-filtros")?.reset();
    clear("erro", "A conta mudou. Recarregue a página para continuar.");
  }
  document.addEventListener("auth-identity-changed", identityChanged);
  function body(id, estado, mensagem) {
    const b = $(id);
    b.dataset.estado = estado;
    b.setAttribute("aria-busy", "false");
    b.querySelector('[data-dash-message]').textContent = mensagem;
    b.querySelector('[data-dash-retry]').hidden = true;
    return b.querySelector('[data-dash-body]');
  }
  function cards(target, valores) {
    const grid = element("div", "");
    grid.className = "dash-cards";
    for (const [titulo, valor] of valores) {
      const card = element("article", "");
      card.className = "dash-card";
      card.append(element("p", titulo), element("strong", valor));
      grid.append(card);
    }
    target.append(grid);
  }
  function table(id, linhas, assunto) {
    const target = body(id, linhas.length ? "dados_disponiveis" : "sem_dados", linhas.length ?
      "Base: somente respostas concluídas no período. Grupos sem resposta não são exibidos como 0%." : "Sem respostas neste período. Pratique uma Questão ou finalize um simulado com respostas.");
    if (!linhas.length) return;
    const scroll = element("div", "");
    scroll.className = "dash-scroll";
    scroll.tabIndex = 0;
    scroll.setAttribute("role", "region");
    scroll.setAttribute("aria-label", assunto ? "Tabela de Assuntos" : "Tabela de Matérias");
    const t = element("table", "");
    t.className = "dash-table";
    const head = element("thead", ""), hr = element("tr", "");
    for (const title of [
      assunto ? "Assunto / Matéria" : "Matéria",
      "Respostas",
      "Acertos",
      "Erros",
      "Acerto",
      "Amostra / base"
    ]) {
      const th = element("th", title);
      th.scope = "col";
      hr.append(th);
    }
    head.append(hr);
    t.append(head);
    const tbody = element("tbody", "");
    for (const r of linhas) {
      const tr = element("tr", "");
      for (const value of [
        assunto ? `${r.assunto_nome} · ${r.materia_nome}` : r.materia_nome,
        r.total_respostas,
        r.acertos,
        r.erros,
        percentage(r.percentual_acerto)
      ]) tr.append(element("td", value));
      const td = element("td", names[r.estado_amostra]);
      td.append(element("small", `${r.base.pratica} de práticas · ${r.base.simulado} de simulados`));
      tr.append(td);
      tbody.append(tr);
    }
    t.append(tbody);
    scroll.append(t);
    target.append(scroll);
  }
  function renderAluno(data) {
    const d = mode === "dashboard" ? data.desempenho : data, g = d.geral;
    $("dash-meta").textContent = `${d.periodo.inicio} a ${d.periodo.fim} · ${d.periodo.timezone} · calculado em ${new Date(d.calculado_em).toLocaleString("pt-BR", { timeZone: "UTC" })} UTC · base: ${d.base.pratica} respostas de práticas e ${d.base.simulado} de simulados · limiar operacional: ${d.limiar_amostra} respostas.`;
    const target = body("dash-geral", g.estado_amostra, g.estado_amostra === "sem_dados" ?
      "Sem dados: ausência de respostas não significa desempenho zero." : g.estado_amostra === "amostra_pequena" ?
      "Amostra pequena: menos de cinco respostas. As contagens não comprovam domínio ou significância estatística." : "Dados disponíveis. O limiar de cinco respostas é apenas operacional.");
    cards(target, [
      ["Respostas concluídas", g.total_respostas],
      ["Acertos", g.acertos],
      ["Erros", g.erros],
      ["Percentual de acerto", percentage(g.percentual_acerto)]
    ]);
    table("dash-materias", d.materias, false);
    table("dash-assuntos", d.assuntos, true);
    if (mode === "dashboard") {
      const a = data.ultimas_atividades;
      const node = body("dash-atividades", a.length ? "dados_disponiveis" : "sem_dados", a.length ? "Até cinco tentativas concluídas neste mesmo período. Atividades não equivalem à quantidade de respostas." : "Nenhuma atividade concluída neste período.");
      const list = element("ul", "");
      list.className = "dash-atividades";
      for (const item of a) {
        const li = element("li", ""), link = element("a", item.titulo);
        const destino = item.tipo === "pratica" ? "questao" : "simulado";
        link.href = `/aluno/${destino}.html?tentativa_id=${encodeURIComponent(item.id)}`;
        li.append(link, element("small", `${item.tipo === "pratica" ? "Prática" : "Simulado"} · ${new Date(item.ocorrido_em).toLocaleString("pt-BR")}`));
        list.append(li);
      }
      node.append(list);
    }
  }
  function renderAdmin(d) {
    $("dash-meta").textContent = `Contagens atuais · calculado em ${new Date(d.calculado_em).toLocaleString("pt-BR", { timeZone: "UTC" })} UTC.`;
    const labels = {
      materias_ativas: "Matérias ativas",
      assuntos_ativos: "Assuntos ativos",
      rascunhos: "Rascunhos",
      publicadas: "Publicadas",
      arquivadas: "Arquivadas",
      publicados: "Publicados",
      arquivados: "Arquivados"
    };
    for (const grupo of ["catalogo", "questoes", "simulados"]) {
      const valores = Object.entries(d[grupo]);
      const temDados = valores.some(([, v]) => v > 0);
      cards(body(`dash-${grupo}`, temDados ? "dados_disponiveis" : "sem_dados", temDados ? "Contagens globais atuais." : "Nenhum registro neste grupo."), valores.map(([k, v]) => [labels[k], v]));
    }
    const total = d.tentativas_simulado_finalizadas;
    cards(body("dash-tentativas", total ? "dados_disponiveis" : "sem_dados", total ? "Total global, sem dados individuais de estudantes." : "Nenhuma tentativa de simulado finalizada."), [["Tentativas finalizadas", total]]);
  }
  async function load() {
    if (!available()) return;
    const g = ++state.generation, user = AuthUI.user.id, filters = { ...state.filters };
    clear("carregando", "Carregando dados do período...");
    try {
      if (!await AuthUI.checkIdentity() || !valid(g, user)) return;
      const query = new URLSearchParams(filters).toString();
      const rota = mode === "admin" ? "/admin/dashboard" : `/aluno/${mode === "dashboard" ? "dashboard" : "desempenho"}`;
      const data = await apiRequest(rota + (query ? `?${query}` : ""));
      if (!valid(g, user) || !await AuthUI.checkIdentity() || !valid(g, user)) return;
      if (mode === "admin") renderAdmin(data); else renderAluno(data);
      state.data = data;
    } catch (e) {
      if (g === state.generation && !AuthUI.changedAccount) clear("erro", `${e.message} Recarregue todos os blocos para tentar novamente.`);
    }
  }
  $("dash-filtros")?.addEventListener("submit", (e) => {
    e.preventDefault();
    state.filters = {};
    for (const [key, value] of new FormData(e.currentTarget)) if (value) state.filters[key] = value;
    load();
  });
  $("dash-padrao")?.addEventListener("click", () => {
    $("dash-filtros").reset();
    state.filters = {};
    load();
  });
  $("dash-recarregar").addEventListener("click", load);
  for (const button of document.querySelectorAll('[data-dash-retry]')) button.addEventListener("click", load);
  globalThis.DesempenhoUI = {
    state,
    load,
    destroy() {
      state.generation++;
      document.removeEventListener("auth-identity-changed", identityChanged);
    }
  };
  AuthUI.ready.then((ready) => {
    if (ready && available()) load();
  });
})();
