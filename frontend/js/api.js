const API_URL = "http://127.0.0.1:5000/api";

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function apiRequest(caminho, opcoes = {}) {
  const resposta = await fetch(`${API_URL}${caminho}`, {
    ...opcoes,
    headers: {
      "Content-Type": "application/json",
      ...opcoes.headers,
    },
  });

  if (resposta.status === 204) {
    return null;
  }

  const dados = await resposta.json().catch(() => ({}));
  if (!resposta.ok) {
    throw new ApiError(
      dados.erro || "Não foi possível concluir a operação.",
      resposta.status,
    );
  }

  return dados;
}

// Mantem o script classico e permite que o mesmo contrato seja exercitado
// pelo transformador de cobertura do ambiente de testes.
globalThis.ApiError = ApiError;
globalThis.apiRequest = apiRequest;
