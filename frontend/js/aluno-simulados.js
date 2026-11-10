(() => {
  globalThis.SimuladosAlunoUI?.destroy();
  const $ = (id) => document.getElementById(id);
  const tentativa = document.body.dataset.simulado === "aluno-tentativa";
  const state = {
    generation: 0,
    busy: false,
    page: 1,
    pages: 0,
    detail: null,
    index: 0,
    correction: false,
    pending: null,
    draft: undefined
  };
  const id = new URLSearchParams(location.search).get("tentativa_id");
  const endpoint = `/aluno/tentativas-simulado/${id}`;
  const available = () => !AuthUI.blocked && !AuthUI.changedAccount;
  const valid = (g, user) => g === state.generation && available() && AuthUI.user.id === user;
  const element = (tag, text) => {
    const n = document.createElement(tag);
    n.textContent = text;
    return n;
  };
  function message(text, error = false) {
    $("sim-status").textContent = text;
    $("sim-status").dataset.erro = error;
  }
  function busy(value) {
    state.busy = value;
    document.querySelectorAll('main button, main input, main select').forEach((n) => {
      n.disabled = value;
    });
    if (!tentativa) {
      $("sim-anterior").disabled = value || state.page <= 1;
      $("sim-proxima").disabled = value || state.page >= state.pages;
    }
  }
  function clearIdentity() {
    state.generation++;
    state.detail = null;
    state.pending = null;
    state.draft = undefined;
    document.querySelectorAll('[data-sim-private]').forEach((n) => n.replaceChildren());
    message("A conta mudou. Recarregue a página para continuar.", true);
  }
  document.addEventListener("auth-identity-changed", clearIdentity);
  async function identity() {
    return available() && await AuthUI.checkIdentity();
  }
  function dirty() {
    return state.draft !== undefined && state.detail?.estado === "em_andamento";
  }
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
      if (!window.confirm("Descartar a alternativa ainda não salva e sair?")) e.preventDefault();
      else state.draft = undefined;
    }
  }
  document.addEventListener("click", leave);
  async function loadList() {
    if (!available() || state.busy) return;
    const g = ++state.generation, user = AuthUI.user.id;
    $("sim-lista").replaceChildren();
    busy(true);
    message("Carregando simulados...");
    try {
      if (!await identity()) return;
      const history = $("sim-modo").value === "historico";
      const data = await apiRequest(`/aluno/${history ? "tentativas-simulado" : "simulados"}?pagina=${state.page}&por_pagina=20`);
      if (!valid(g, user) || !await identity() || !valid(g, user)) return;
      state.pages = data.total_paginas;
      for (const item of data.itens) {
        const li = element("li", "");
        li.className = "pratica-card";
        li.append(element("h2", item.titulo));
        if (history) {
          li.append(element("p", `${item.resultado.acertos} acertos em ${item.resultado.total} Questões · ${item.resultado.percentual_acerto}% · ${new Date(item.resultado.finalizada_em).toLocaleString("pt-BR")}`));
          const a = element("a", "Ver resultado e correção");
          a.href = `/aluno/simulado.html?tentativa_id=${item.id}`;
          li.append(a);
        } else {
          li.append(element("p", `${item.total_questoes} Questões · ${item.disponivel ? "Disponível" : "Indisponível para novo início"}`));
          if (item.tentativa_em_andamento_id) {
            const a = element("a", "Continuar tentativa");
            a.href = `/aluno/simulado.html?tentativa_id=${item.tentativa_em_andamento_id}`;
            li.append(a);
          } else if (item.disponivel) {
            const b = element("button", "Iniciar simulado");
            b.className = "auth-primary";
            b.type = "button";
            b.onclick = () => start(item);
            li.append(b);
          }
        }
        $("sim-lista").append(li);
      }
      $("sim-pagina").textContent = `Página ${state.page} de ${Math.max(1, state.pages)}`;
      message(data.itens.length ? `${data.total_itens} ${history ? "tentativa(s) finalizada(s)" : "simulado(s) publicado(s)"}.` : "Nenhum simulado neste filtro.");
    } catch (e) {
      if (valid(g, user)) message(e.message, true);
    }
    finally {
      if (g === state.generation) busy(false);
    }
  }
  async function start(item) {
    if (state.busy || !available()) return;
    if (state.pending && state.pending.simulado_versao_id !== item.simulado_versao_id) {
      message("Tente novamente o mesmo simulado para recuperar o início pendente.", true);
      return;
    }
    state.pending ||= { simulado_versao_id: item.simulado_versao_id, chave_envio: crypto.randomUUID() };
    const g = state.generation, user = AuthUI.user.id;
    busy(true);
    try {
      if (!await identity()) return;
      const data = await apiRequest("/aluno/tentativas-simulado", { method: "POST", body: JSON.stringify(state.pending) });
      if (valid(g, user) && await identity() && valid(g, user)) {
        state.pending = null;
        AuthUI.navigate(`/aluno/simulado.html?tentativa_id=${data.id}`);
      }
    } catch (e) {
      if (valid(g, user)) {
        if ([400, 404, 409].includes(e.status)) state.pending = null;
        message(e.message, true);
      }
    }
    finally {
      if (g === state.generation) busy(false);
    }
  }
  function render() {
    const d = state.detail, done = d.estado === "finalizada", item = d.itens[state.index];
    $("sim-conteudo").hidden = false;
    $("sim-nome").textContent = d.titulo;
    $("sim-titulo").textContent = done ? state.correction ? "Correção do simulado" : "Resultado do simulado" : "Realizar simulado";
    const answered = d.itens.filter((i) => i.alternativa !== null).length;
    $("sim-progresso").textContent = `${answered} de ${d.itens.length} respostas salvas · revisão ${d.revisao}`;
    $("sim-barra").max = d.itens.length;
    $("sim-barra").value = answered;
    $("sim-brancos").textContent = `${d.itens.length - answered} Questão(ões) em branco.`;
    $("sim-resultado").hidden = !done;
    $("sim-finalizar").hidden = done;
    $("sim-questao").hidden = done && !state.correction;
    if (done) {
      const r = d.resultado;
      $("sim-totais").textContent = `${r.percentual_acerto}% · ${r.acertos} acertos · ${r.erros} erros · ${r.em_branco} em branco · ${r.total} Questões · ${new Date(r.finalizada_em).toLocaleString("pt-BR")}`;
      $("sim-correcao").hidden = state.correction;
    }
    $("sim-mapa").replaceChildren();
    d.itens.forEach((i, index) => {
      const b = element("button", i.posicao);
      b.type = "button";
      b.dataset.respondida = i.alternativa !== null;
      const label = i.alternativa === null ? "Em branco" : state.correction ? i.correta ? "Correta" : "Incorreta" : "Respondida";
      b.setAttribute("aria-label", `Questão ${i.posicao}: ${label}`);
      b.setAttribute("aria-current", index === state.index);
      if (state.correction) b.dataset.resultado = i.alternativa === null ? "branco" : i.correta ? "correta" : "incorreta";
      b.onclick = () => move(index);
      $("sim-mapa").append(b);
    });
    $("sim-posicao").textContent = `Questão ${item.posicao} de ${d.itens.length}`;
    $("sim-classificacao").textContent = `${item.questao.materia.nome} · ${item.questao.assunto.nome} · versão ${item.questao.questao_versao_id}`;
    $("sim-enunciado").textContent = item.questao.enunciado;
    $("sim-alternativas").replaceChildren();
    for (const letter of "ABCDE") {
      const label = element("label", "");
      label.className = "pratica-opcao";
      const radio = document.createElement("input");
      radio.type = "radio";
      radio.name = "alternativa";
      radio.value = letter;
      radio.checked = letter === (state.draft === undefined ? item.alternativa : state.draft);
      radio.disabled = done;
      radio.onchange = () => {
        state.draft = letter;
        message("Alternativa ainda não salva. Confirme em Salvar resposta.");
      };
      label.append(radio, element("span", `${letter} · ${item.questao[`alternativa_${letter.toLowerCase()}`]}`));
      $("sim-alternativas").append(label);
    }
    $("sim-salvar").hidden = done;
    $("sim-limpar").hidden = done;
    $("sim-feedback").hidden = !state.correction;
    if (state.correction) {
      $("sim-feedback-titulo").textContent = item.alternativa === null ? "Em branco" : item.correta ? "Resposta correta" : "Resposta incorreta";
      $("sim-gabarito").textContent = `Sua resposta: ${item.alternativa || "Em branco"} · Gabarito: ${item.gabarito}`;
      $("sim-explicacao").textContent = item.explicacao || "Explicação indisponível para esta Questão.";
    }
  }
  function move(index) {
    if (state.busy || !state.detail || index < 0 || index >= state.detail.itens.length) return;
    if (dirty() && !window.confirm("Descartar a alternativa ainda não salva e mudar de Questão?")) return;
    state.draft = undefined;
    state.index = index;
    render();
    $("sim-posicao").focus();
  }
  async function loadDetail(correction = state.correction) {
    if (!available() || state.busy) return;
    const g = ++state.generation, user = AuthUI.user.id;
    busy(true);
    $("sim-conteudo").hidden = true;
    message("Carregando tentativa...");
    try {
      if (!id || !/^[1-9]\d*$/.test(id)) throw new Error("Identificador de tentativa inválido.");
      if (!await identity()) return;
      const data = await apiRequest(endpoint + (correction ? "/correcao" : ""));
      if (!valid(g, user) || !await identity() || !valid(g, user)) return;
      state.detail = data;
      state.correction = correction;
      if (data.estado === "finalizada") state.draft = undefined;
      render();
      message(data.estado === "finalizada" ? "Resultado preservado no servidor." : "Selecione e salve cada resposta. Você pode alterar ou limpar antes de finalizar.");
    } catch (e) {
      if (valid(g, user)) message(e.message, true);
    }
    finally {
      if (g === state.generation) {
        busy(false);
        if (state.detail?.estado === "finalizada") document.querySelectorAll('input[name="alternativa"]').forEach((n) => {
          n.disabled = true;
        });
      }
    }
  }
  async function save(alternativa) {
    if (state.busy || !available() || state.detail?.estado !== "em_andamento") return;
    state.draft = alternativa;
    const g = state.generation, user = AuthUI.user.id, d = state.detail, i = d.itens[state.index];
    busy(true);
    try {
      if (!await identity()) return;
      const r = await apiRequest(`${endpoint}/respostas/${i.item_id}`, { method: "PUT", body: JSON.stringify({ alternativa, revisao: d.revisao }) });
      if (!valid(g, user) || !await identity() || !valid(g, user)) return;
      i.alternativa = r.alternativa;
      d.revisao = r.revisao;
      state.draft = undefined;
      render();
      message("Resposta salva no servidor.");
    } catch (e) {
      if (g === state.generation) message(e.message, true);
    }
    finally {
      if (g === state.generation) busy(false);
    }
  }
  function confirmFinish() {
    if (state.busy || !available() || state.detail?.estado !== "em_andamento") return;
    if (dirty()) {
      message("Salve a alternativa selecionada antes de finalizar.", true);
      return;
    }
    const blanks = state.detail.itens.filter((i) => i.alternativa === null).length;
    $("sim-confirmar-texto").textContent = `${blanks} Questão(ões) em branco. Após finalizar, as respostas e o resultado serão definitivos.`;
    $("sim-confirmacao").showModal();
    $("sim-confirmar-cancelar").focus();
  }
  async function finish() {
    $("sim-confirmacao").close();
    if (state.busy || !available() || !state.detail) return;
    const g = state.generation, user = AuthUI.user.id;
    busy(true);
    try {
      if (!await identity()) return;
      const r = await apiRequest(endpoint + "/finalizar", { method: "POST", body: JSON.stringify({ revisao: state.detail.revisao, confirmar: true }) });
      if (!valid(g, user) || !await identity() || !valid(g, user)) return;
      state.detail.resultado = r;
      state.detail.estado = "finalizada";
      state.draft = undefined;
      render();
      message("Simulado finalizado. Resultado salvo.");
      $("sim-resultado-titulo").focus();
    } catch (e) {
      if (g === state.generation) message(e.message, true);
    }
    finally {
      if (g === state.generation) busy(false);
    }
  }
  if (tentativa) {
    $("sim-resposta").onsubmit = (e) => {
      e.preventDefault();
      const value = document.querySelector('input[name="alternativa"]:checked')?.value;
      if (value) save(value); else message("Selecione uma alternativa ou use Limpar resposta.", true);
    };
    $("sim-limpar").onclick = () => save(null);
    $("sim-item-anterior").onclick = () => move(state.index - 1);
    $("sim-item-proxima").onclick = () => move(state.index + 1);
    $("sim-correcao").onclick = () => loadDetail(true);
    $("sim-finalizar").onclick = confirmFinish;
    $("sim-confirmar-cancelar").onclick = () => {
      $("sim-confirmacao").close();
      $("sim-finalizar").focus();
    };
    $("sim-confirmar").onclick = finish;
  } else {
    $("sim-filtros").onsubmit = (e) => {
      e.preventDefault();
      state.page = 1;
      loadList();
    };
    $("sim-anterior").onclick = () => {
      state.page--;
      loadList();
    };
    $("sim-proxima").onclick = () => {
      state.page++;
      loadList();
    };
  }
  $("sim-recarregar").onclick = () => tentativa ? loadDetail() : loadList();
  globalThis.SimuladosAlunoUI = {
    state,
    loadList,
    loadDetail,
    destroy() {
      state.generation++;
      document.removeEventListener("auth-identity-changed", clearIdentity);
      window.removeEventListener("beforeunload", beforeUnload);
      document.removeEventListener("click", leave);
    }
  };
  AuthUI.ready.then((ready) => {
    if (ready && available()) tentativa ? loadDetail() : loadList();
  });
})();
