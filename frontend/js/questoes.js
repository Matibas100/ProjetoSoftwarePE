(async () => {
  if (globalThis.AuthUI && !(await globalThis.AuthUI.ready)) return;
  const form = document.querySelector("#questao-form");
  let persistedForm = "";
  const formSnapshot = () => JSON.stringify(Object.fromEntries(new FormData(form)));
  globalThis.AuthUI?.registerGuard(() => formSnapshot() !== persistedForm);
  form.addEventListener("reset", () => queueMicrotask(() => { persistedForm = formSnapshot(); }));
  const assuntoSelect = document.querySelector("#questao-assunto-id");
  const enunciadoInput = document.querySelector("#questao-enunciado");
  const respostaSelect = document.querySelector("#resposta-correta");
  const dificuldadeSelect = document.querySelector("#questao-dificuldade");
  const explicacaoInput = document.querySelector("#questao-explicacao");
  const salvarButton = document.querySelector("#questao-salvar-button");
  const mensagemElement = document.querySelector("#questao-mensagem");
  const buscaForm = document.querySelector("#busca-questoes-form");
  const buscaAssuntoSelect = document.querySelector("#busca-assunto-id");
  const buscarButton = document.querySelector("#buscar-questoes-button");
  const listaStatusElement = document.querySelector("#questoes-lista-status");
  const listaElement = document.querySelector("#questoes-lista");

  const alternativaInputs = {
    A: document.querySelector("#alternativa-a"),
    B: document.querySelector("#alternativa-b"),
    C: document.querySelector("#alternativa-c"),
    D: document.querySelector("#alternativa-d"),
    E: document.querySelector("#alternativa-e"),
  };

  let assuntosDisponiveis = [];

  function mostrarMensagem(texto, tipo) {
    mensagemElement.textContent = texto;
    mensagemElement.className = `mensagem mensagem--${tipo}`;
    mensagemElement.hidden = false;
  }

  function escaparHtml(valor) {
    const elemento = document.createElement("div");
    elemento.textContent = valor ?? "";
    return elemento.innerHTML;
  }

  function preencherSelect(select, assuntos, valorAtual) {
    select.replaceChildren();
    const opcaoInicial = document.createElement("option");
    opcaoInicial.value = "";
    opcaoInicial.textContent = assuntos.length
      ? "Selecione um assunto"
      : "Cadastre um assunto primeiro";
    select.appendChild(opcaoInicial);

    assuntos.forEach((assunto) => {
      const opcao = document.createElement("option");
      opcao.value = assunto.id;
      opcao.textContent = assunto.nome;
      select.appendChild(opcao);
    });

    select.disabled = assuntos.length === 0;
    if (assuntos.some((assunto) => String(assunto.id) === valorAtual)) {
      select.value = valorAtual;
    }
  }

  function atualizarAssuntos(assuntos) {
    const valorCadastro = assuntoSelect.value;
    const valorBusca = buscaAssuntoSelect.value;
    assuntosDisponiveis = assuntos;
    preencherSelect(assuntoSelect, assuntos, valorCadastro);
    preencherSelect(buscaAssuntoSelect, assuntos, valorBusca);
    salvarButton.disabled = assuntos.length === 0;
    buscarButton.disabled = assuntos.length === 0;
  }

  async function carregarAssuntos() {
    try {
      atualizarAssuntos(await apiRequest("/assuntos"));
    } catch (erro) {
      atualizarAssuntos([]);
      mostrarMensagem(`Não foi possível carregar os assuntos: ${erro.message}`, "erro");
    }
  }

  function nomeAssunto(assuntoId) {
    const assunto = assuntosDisponiveis.find((item) => item.id === assuntoId);
    return assunto ? assunto.nome : `Assunto #${assuntoId}`;
  }

  function renderizarQuestoes(questoes) {
    listaElement.replaceChildren();

    if (questoes.length === 0) {
      listaStatusElement.textContent = "Nenhuma questão encontrada para este assunto.";
      listaStatusElement.hidden = false;
      return;
    }

    listaStatusElement.hidden = true;
    questoes.forEach((questao) => {
      const artigo = document.createElement("article");
      artigo.className = "questao-card";
      artigo.innerHTML = `
        <div class="questao-meta">
          <span class="vinculo">${escaparHtml(nomeAssunto(questao.assunto_id))}</span>
          <span class="dificuldade">${escaparHtml(questao.dificuldade)}</span>
        </div>
        <h3>${escaparHtml(questao.enunciado)}</h3>
        <ol class="alternativas" type="A">
          <li>${escaparHtml(questao.alternativa_a)}</li>
          <li>${escaparHtml(questao.alternativa_b)}</li>
          <li>${escaparHtml(questao.alternativa_c)}</li>
          <li>${escaparHtml(questao.alternativa_d)}</li>
          <li>${escaparHtml(questao.alternativa_e)}</li>
        </ol>
        <p><strong>Resposta correta:</strong> ${escaparHtml(questao.resposta_correta)}</p>
        ${questao.explicacao ? `<p><strong>Explicação:</strong> ${escaparHtml(questao.explicacao)}</p>` : ""}
      `;
      listaElement.appendChild(artigo);
    });
  }

  async function buscarQuestoes(evento) {
    if (evento) {
      evento.preventDefault();
    }

    const assuntoId = buscaAssuntoSelect.value;
    if (!assuntoId) {
      listaStatusElement.textContent = "Selecione um assunto para realizar a busca.";
      listaStatusElement.hidden = false;
      return;
    }

    buscarButton.disabled = true;
    listaStatusElement.textContent = "Buscando questões...";
    listaStatusElement.hidden = false;
    try {
      const questoes = await apiRequest(
        `/questoes/por-assunto?assunto_id=${encodeURIComponent(assuntoId)}`,
      );
      renderizarQuestoes(questoes);
    } catch (erro) {
      listaStatusElement.textContent = erro.message;
    } finally {
      buscarButton.disabled = assuntosDisponiveis.length === 0;
    }
  }

  async function cadastrarQuestao(evento) {
    evento.preventDefault();
    salvarButton.disabled = true;

    const assuntoId = Number(assuntoSelect.value);
    const dados = {
      assunto_id: assuntoId,
      enunciado: enunciadoInput.value,
      alternativa_a: alternativaInputs.A.value,
      alternativa_b: alternativaInputs.B.value,
      alternativa_c: alternativaInputs.C.value,
      alternativa_d: alternativaInputs.D.value,
      alternativa_e: alternativaInputs.E.value,
      resposta_correta: respostaSelect.value,
      explicacao: explicacaoInput.value,
      dificuldade: dificuldadeSelect.value,
    };

    try {
      await apiRequest("/questoes", {
        method: "POST",
        body: JSON.stringify(dados),
      });
      mostrarMensagem("Questão cadastrada com sucesso.", "sucesso");
      form.reset();
      assuntoSelect.value = assuntoId;
      buscaAssuntoSelect.value = assuntoId;
      await buscarQuestoes();
    } catch (erro) {
      mostrarMensagem(erro.message, "erro");
    } finally {
      salvarButton.disabled = assuntosDisponiveis.length === 0;
    }
  }

  form.addEventListener("submit", cadastrarQuestao);
  buscaForm.addEventListener("submit", buscarQuestoes);
  document.addEventListener("assuntos:atualizados", (evento) => {
    atualizarAssuntos(evento.detail);
  });

  carregarAssuntos().then(() => { persistedForm = formSnapshot(); });
})();
