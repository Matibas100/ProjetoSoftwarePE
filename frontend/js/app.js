(async () => {
if (globalThis.AuthUI && !(await globalThis.AuthUI.ready)) return;
const statusElement = document.querySelector("#api-status");
const form = document.querySelector("#materia-form");
const materiaIdInput = document.querySelector("#materia-id");
const nomeInput = document.querySelector("#nome");
const descricaoInput = document.querySelector("#descricao");
const areaSelect = document.querySelector("#materia-area-enem-id");
const salvarButton = document.querySelector("#salvar-button");
const cancelarButton = document.querySelector("#cancelar-button");
const recarregarButton = document.querySelector("#recarregar-button");
const mensagemElement = document.querySelector("#mensagem");
const listaStatusElement = document.querySelector("#lista-status");
const listaElement = document.querySelector("#materias-lista");

let materias = [];
let persistedForm = "";
const formSnapshot = () => JSON.stringify(Object.fromEntries(new FormData(form)));
globalThis.AuthUI?.registerGuard(() => formSnapshot() !== persistedForm);
form.addEventListener("reset", () => queueMicrotask(() => { persistedForm = formSnapshot(); }));

async function carregarAreas() {
  try {
    const areas = await apiRequest("/areas-enem");
    areaSelect.replaceChildren();
    const inicial = document.createElement("option");
    inicial.value = "";
    inicial.textContent = "Selecione uma área";
    areaSelect.appendChild(inicial);
    areas.forEach((area) => {
      const option = document.createElement("option");
      option.value = area.id;
      option.textContent = area.nome;
      areaSelect.appendChild(option);
    });
  } catch (erro) {
    areaSelect.replaceChildren();
    const option = document.createElement("option");
    option.textContent = "Não foi possível carregar as áreas";
    areaSelect.appendChild(option);
    areaSelect.disabled = true;
    mostrarMensagem(erro.message, "erro");
  }
}

async function verificarApi() {
  try {
    const dados = await apiRequest("/health");
    statusElement.textContent = `API: ${dados.status}`;
    statusElement.classList.add("status--online");
  } catch (erro) {
    statusElement.textContent = "API indisponivel. Inicie o backend e tente novamente.";
    statusElement.classList.add("status--offline");
    console.error("Falha ao consultar a API:", erro);
  }
}

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

function renderizarMaterias() {
  listaElement.replaceChildren();

  if (materias.length === 0) {
    listaStatusElement.textContent = "Nenhuma matéria cadastrada.";
    listaStatusElement.hidden = false;
    return;
  }

  listaStatusElement.hidden = true;
  materias.forEach((materia) => {
    const artigo = document.createElement("article");
    artigo.className = "materia-card";
    artigo.innerHTML = `
      <div>
        <h3>${escaparHtml(materia.nome)}</h3>
        <p>${escaparHtml(materia.descricao || "Sem descrição.")}</p>
      </div>
      <div class="materia-acoes">
        <button class="button button--secundario" type="button" data-acao="editar" data-id="${materia.id}">
          Editar
        </button>
        <button class="button button--perigo" type="button" data-acao="excluir" data-id="${materia.id}">
          Excluir
        </button>
      </div>
    `;
    listaElement.appendChild(artigo);
  });
}

async function carregarMaterias() {
  listaStatusElement.textContent = "Carregando matérias...";
  listaStatusElement.hidden = false;
  recarregarButton.disabled = true;

  try {
    materias = await apiRequest("/materias");
    renderizarMaterias();
    document.dispatchEvent(
      new CustomEvent("materias:atualizadas", { detail: materias }),
    );
  } catch (erro) {
    listaStatusElement.textContent = erro.message;
    mostrarMensagem(erro.message, "erro");
  } finally {
    recarregarButton.disabled = false;
  }
}

function iniciarEdicao(materia) {
  materiaIdInput.value = materia.id;
  nomeInput.value = materia.nome;
  descricaoInput.value = materia.descricao || "";
  areaSelect.value = materia.area_enem_id;
  persistedForm = formSnapshot();
  document.querySelector("#titulo-formulario").textContent = "Editar matéria";
  salvarButton.textContent = "Salvar alterações";
  cancelarButton.hidden = false;
  nomeInput.focus();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function limparFormulario() {
  form.reset();
  materiaIdInput.value = "";
  document.querySelector("#titulo-formulario").textContent = "Nova matéria";
  salvarButton.textContent = "Cadastrar matéria";
  cancelarButton.hidden = true;
}

async function salvarMateria(evento) {
  evento.preventDefault();
  limparMensagem();

  const materiaId = materiaIdInput.value;
  const dados = {
    nome: nomeInput.value,
    descricao: descricaoInput.value,
    area_enem_id: Number(areaSelect.value),
  };
  const editando = Boolean(materiaId);

  salvarButton.disabled = true;
  try {
    await apiRequest(editando ? `/materias/${materiaId}` : "/materias", {
      method: editando ? "PUT" : "POST",
      body: JSON.stringify(dados),
    });
    mostrarMensagem(
      editando ? "Matéria atualizada com sucesso." : "Matéria cadastrada com sucesso.",
      "sucesso",
    );
    limparFormulario();
    await carregarMaterias();
  } catch (erro) {
    mostrarMensagem(erro.message, "erro");
  } finally {
    salvarButton.disabled = false;
  }
}

async function excluirMateria(materia) {
  const confirmou = window.confirm(`Excluir a matéria "${materia.nome}"?`);
  if (!confirmou) {
    return;
  }

  limparMensagem();
  try {
    await apiRequest(`/materias/${materia.id}`, { method: "DELETE" });
    mostrarMensagem("Matéria excluída com sucesso.", "sucesso");
    if (materiaIdInput.value === String(materia.id)) {
      limparFormulario();
    }
    await carregarMaterias();
  } catch (erro) {
    mostrarMensagem(erro.message, "erro");
  }
}

listaElement.addEventListener("click", (evento) => {
  const botao = evento.target.closest("button[data-acao]");
  if (!botao) {
    return;
  }

  const materia = materias.find((item) => item.id === Number(botao.dataset.id));
  if (!materia) {
    mostrarMensagem("Matéria não encontrada na lista atual.", "erro");
    return;
  }

  if (botao.dataset.acao === "editar") {
    iniciarEdicao(materia);
  } else if (botao.dataset.acao === "excluir") {
    excluirMateria(materia);
  }
});

form.addEventListener("submit", salvarMateria);
cancelarButton.addEventListener("click", limparFormulario);
recarregarButton.addEventListener("click", carregarMaterias);

verificarApi();
carregarAreas().then(() => { persistedForm = formSnapshot(); });
carregarMaterias();

})();
