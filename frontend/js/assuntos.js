(() => {
  const form = document.querySelector("#assunto-form");
  const assuntoIdInput = document.querySelector("#assunto-id");
  const nomeInput = document.querySelector("#assunto-nome");
  const materiaSelect = document.querySelector("#assunto-materia-id");
  const descricaoInput = document.querySelector("#assunto-descricao");
  const salvarButton = document.querySelector("#assunto-salvar-button");
  const cancelarButton = document.querySelector("#assunto-cancelar-button");
  const recarregarButton = document.querySelector("#assuntos-recarregar-button");
  const mensagemElement = document.querySelector("#assunto-mensagem");
  const listaStatusElement = document.querySelector("#assuntos-lista-status");
  const listaElement = document.querySelector("#assuntos-lista");

  let assuntos = [];
  let materiasDisponiveis = [];

  function mostrarMensagem(texto, tipo) {
    mensagemElement.textContent = texto;
    mensagemElement.className = `mensagem mensagem--${tipo}`;
    mensagemElement.hidden = false;
  }

  function limparMensagem() {
    mensagemElement.hidden = true;
  }

  function escaparHtml(valor) {
    const elemento = document.createElement("div");
    elemento.textContent = valor ?? "";
    return elemento.innerHTML;
  }

  function atualizarSeletorMaterias(materias) {
    const valorAtual = materiaSelect.value;
    materiasDisponiveis = materias;
    materiaSelect.replaceChildren();

    const opcaoInicial = document.createElement("option");
    opcaoInicial.value = "";
    opcaoInicial.textContent = materias.length
      ? "Selecione uma matéria"
      : "Cadastre uma matéria primeiro";
    materiaSelect.appendChild(opcaoInicial);

    materias.forEach((materia) => {
      const opcao = document.createElement("option");
      opcao.value = materia.id;
      opcao.textContent = materia.nome;
      materiaSelect.appendChild(opcao);
    });

    materiaSelect.disabled = materias.length === 0;
    salvarButton.disabled = materias.length === 0;
    if (materias.some((materia) => String(materia.id) === valorAtual)) {
      materiaSelect.value = valorAtual;
    }
  }

  async function carregarMaterias() {
    try {
      atualizarSeletorMaterias(await apiRequest("/materias"));
      renderizarAssuntos();
    } catch (erro) {
      atualizarSeletorMaterias([]);
      mostrarMensagem(`Não foi possível carregar as matérias: ${erro.message}`, "erro");
    }
  }

  function nomeMateria(materiaId) {
    const materia = materiasDisponiveis.find((item) => item.id === materiaId);
    return materia ? materia.nome : `Matéria #${materiaId}`;
  }

  function renderizarAssuntos() {
    listaElement.replaceChildren();

    if (assuntos.length === 0) {
      listaStatusElement.textContent = "Nenhum assunto cadastrado.";
      listaStatusElement.hidden = false;
      return;
    }

    listaStatusElement.hidden = true;
    assuntos.forEach((assunto) => {
      const artigo = document.createElement("article");
      artigo.className = "assunto-card";
      artigo.innerHTML = `
        <div>
          <span class="vinculo">${escaparHtml(nomeMateria(assunto.materia_id))}</span>
          <h3>${escaparHtml(assunto.nome)}</h3>
          <p>${escaparHtml(assunto.descricao || "Sem descrição.")}</p>
        </div>
        <div class="assunto-acoes">
          <button class="button button--secundario" type="button" data-acao="editar" data-id="${assunto.id}">
            Editar
          </button>
          <button class="button button--perigo" type="button" data-acao="excluir" data-id="${assunto.id}">
            Excluir
          </button>
        </div>
      `;
      listaElement.appendChild(artigo);
    });
  }

  async function carregarAssuntos() {
    listaStatusElement.textContent = "Carregando assuntos...";
    listaStatusElement.hidden = false;
    recarregarButton.disabled = true;

    try {
      assuntos = await apiRequest("/assuntos");
      renderizarAssuntos();
      document.dispatchEvent(
        new CustomEvent("assuntos:atualizados", { detail: assuntos }),
      );
    } catch (erro) {
      listaStatusElement.textContent = erro.message;
      mostrarMensagem(erro.message, "erro");
    } finally {
      recarregarButton.disabled = false;
    }
  }

  function iniciarEdicao(assunto) {
    assuntoIdInput.value = assunto.id;
    nomeInput.value = assunto.nome;
    materiaSelect.value = assunto.materia_id;
    descricaoInput.value = assunto.descricao || "";
    document.querySelector("#titulo-assunto-formulario").textContent =
      "Editar assunto";
    salvarButton.textContent = "Salvar alterações";
    cancelarButton.hidden = false;
    nomeInput.focus();
    form.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  function limparFormulario() {
    form.reset();
    assuntoIdInput.value = "";
    document.querySelector("#titulo-assunto-formulario").textContent =
      "Novo assunto";
    salvarButton.textContent = "Cadastrar assunto";
    cancelarButton.hidden = true;
  }

  async function salvarAssunto(evento) {
    evento.preventDefault();
    limparMensagem();

    const assuntoId = assuntoIdInput.value;
    const editando = Boolean(assuntoId);
    const dados = {
      nome: nomeInput.value,
      descricao: descricaoInput.value,
      materia_id: Number(materiaSelect.value),
    };

    salvarButton.disabled = true;
    try {
      await apiRequest(editando ? `/assuntos/${assuntoId}` : "/assuntos", {
        method: editando ? "PUT" : "POST",
        body: JSON.stringify(dados),
      });
      mostrarMensagem(
        editando ? "Assunto atualizado com sucesso." : "Assunto cadastrado com sucesso.",
        "sucesso",
      );
      limparFormulario();
      await carregarAssuntos();
    } catch (erro) {
      mostrarMensagem(erro.message, "erro");
    } finally {
      salvarButton.disabled = materiasDisponiveis.length === 0;
    }
  }

  async function excluirAssunto(assunto) {
    if (!window.confirm(`Excluir o assunto "${assunto.nome}"?`)) {
      return;
    }

    limparMensagem();
    try {
      await apiRequest(`/assuntos/${assunto.id}`, { method: "DELETE" });
      mostrarMensagem("Assunto excluído com sucesso.", "sucesso");
      if (assuntoIdInput.value === String(assunto.id)) {
        limparFormulario();
      }
      await carregarAssuntos();
    } catch (erro) {
      mostrarMensagem(erro.message, "erro");
    }
  }

  listaElement.addEventListener("click", (evento) => {
    const botao = evento.target.closest("button[data-acao]");
    if (!botao) {
      return;
    }

    const assunto = assuntos.find((item) => item.id === Number(botao.dataset.id));
    if (!assunto) {
      mostrarMensagem("Assunto não encontrado na lista atual.", "erro");
      return;
    }

    if (botao.dataset.acao === "editar") {
      iniciarEdicao(assunto);
    } else if (botao.dataset.acao === "excluir") {
      excluirAssunto(assunto);
    }
  });

  form.addEventListener("submit", salvarAssunto);
  cancelarButton.addEventListener("click", limparFormulario);
  recarregarButton.addEventListener("click", carregarAssuntos);
  document.addEventListener("materias:atualizadas", (evento) => {
    atualizarSeletorMaterias(evento.detail);
    carregarAssuntos();
  });

  carregarMaterias();
  carregarAssuntos();
})();
