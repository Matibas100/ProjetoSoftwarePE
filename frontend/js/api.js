const API_URL = window.ENEM_API_URL || `http://${location.hostname === "localhost" ? "localhost" : "127.0.0.1"}:5000/api`;
let csrfToken = null;
let csrfPromise = null;

class ApiError extends Error {
  constructor(message, status, details = null, code = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
    this.code = code;
  }
}

async function apiRequest(caminho, opcoes = {}) {
  const mutation = opcoes.method && !["GET", "HEAD", "OPTIONS"].includes(opcoes.method.toUpperCase());
  if (mutation && globalThis.AuthUI?.blocked && !caminho.startsWith("/auth/")) {
    globalThis.AuthUI.recover(globalThis.AuthUI.reason || "sessao_invalida");
    throw new ApiError("Recupere sua sessão e confirme a ação novamente.", 403, null, "acesso_bloqueado");
  }
  if (mutation && !csrfToken) {
    csrfPromise ||= apiRequest("/auth/csrf").finally(() => { csrfPromise = null; });
    await csrfPromise;
  }
  let resposta;
  try {
    resposta = await fetch(`${API_URL}${caminho}`, {
      ...opcoes,
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...opcoes.headers,
        ...(mutation ? { "X-CSRF-Token": csrfToken } : {}),
      },
    });
  } catch {
    throw new ApiError("Não foi possível conectar ao servidor. Verifique a conexão e tente novamente.", 0);
  }

  if (resposta.status === 204) {
    return null;
  }

  const dados = await resposta.json().catch(() => ({}));
  if (dados.csrf_token) csrfToken = dados.csrf_token;
  if (!resposta.ok) {
    if (["sessao_invalida", "csrf_invalido", "reautenticacao_necessaria"].includes(dados.codigo)) {
      csrfToken = null;
      document.dispatchEvent(new CustomEvent("auth-required", { detail: dados.codigo }));
    }
    throw new ApiError(
      dados.erro || "Não foi possível concluir a operação.",
      resposta.status,
      dados.detalhes || null,
      dados.codigo || null,
    );
  }

  return dados;
}

// Mantem o script classico e permite que o mesmo contrato seja exercitado
// pelo transformador de cobertura do ambiente de testes.
globalThis.ApiError = ApiError;
globalThis.apiRequest = apiRequest;
globalThis.resetCsrf = () => { csrfToken = null; };
