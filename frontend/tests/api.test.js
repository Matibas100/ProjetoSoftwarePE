import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { prepareGlobalDom } from "./helpers/global-app.js";


describe("apiRequest", () => {
  beforeEach(async () => {
    vi.resetModules();
    prepareGlobalDom();
    window.fetch = vi.fn();
    await import("../js/api.js");
  });

  afterEach(() => {
    delete globalThis.apiRequest;
    delete globalThis.ApiError;
    delete globalThis.AuthUI;
    delete window.ENEM_API_URL;
  });

  function request(path = "/health", options) {
    return globalThis.apiRequest(path, options);
  }

  it("retorna JSON e combina cabecalhos", async () => {
    window.fetch.mockResolvedValue({
      status: 200,
      ok: true,
      json: vi.fn().mockResolvedValue({ status: "online" }),
    });
    await expect(request("/health", { headers: { Authorization: "token" } })).resolves.toEqual({ status: "online" });
    expect(window.fetch).toHaveBeenCalledWith(
      "http://localhost:5000/api/health",
      expect.objectContaining({
        headers: { "Content-Type": "application/json", Authorization: "token" },
      }),
    );
  });

  it("retorna null para 204 sem tentar interpretar JSON", async () => {
    const json = vi.fn();
    window.fetch.mockResolvedValue({ status: 204, ok: true, json });
    await expect(request("/materias/1", { method: "DELETE" })).resolves.toBeNull();
    expect(json).not.toHaveBeenCalled();
  });

  it("explica falha de conexao e permite repetir a chamada", async () => {
    window.fetch
      .mockRejectedValueOnce(new TypeError("Failed to fetch"))
      .mockResolvedValueOnce({ status: 200, ok: true, json: vi.fn().mockResolvedValue({ status: "online" }) });
    await expect(request()).rejects.toMatchObject({
      name: "ApiError", status: 0,
      message: "Não foi possível conectar ao servidor. Verifique a conexão e tente novamente.",
    });
    await expect(request()).resolves.toEqual({ status: "online" });
  });

  it("lanca ApiError com mensagem da API", async () => {
    window.fetch.mockResolvedValue({
      status: 409,
      ok: false,
      json: vi.fn().mockResolvedValue({ erro: "Conflito", detalhes: { previa: true } }),
    });
    await expect(request()).rejects.toMatchObject({
      name: "ApiError", message: "Conflito", status: 409, details: { previa: true },
    });
  });

  it("caracteriza JSON invalido em sucesso e erro", async () => {
    window.fetch
      .mockResolvedValueOnce({ status: 200, ok: true, json: vi.fn().mockRejectedValue(new SyntaxError()) })
      .mockResolvedValueOnce({ status: 500, ok: false, json: vi.fn().mockRejectedValue(new SyntaxError()) });
    await expect(request()).resolves.toEqual({});
    const error = await request().catch((received) => received);
    expect(error).toMatchObject({ name: "ApiError", status: 500 });
    expect(error.message).toContain("concluir a opera");
  });

  function response(data, status = 200) {
    return { status, ok: status < 400, json: vi.fn().mockResolvedValue(data) };
  }

  it("compartilha bootstrap CSRF entre envios concorrentes e usa cookie", async () => {
    window.fetch.mockResolvedValueOnce(response({ csrf_token: "temporario" }))
      .mockResolvedValue(response({ id: 1 }));
    await Promise.all([request("/materias", { method: "POST" }), request("/assuntos", { method: "POST" })]);
    expect(window.fetch).toHaveBeenCalledTimes(3);
    expect(window.fetch.mock.calls.filter(([url]) => url.endsWith("/auth/csrf"))).toHaveLength(1);
    for (const [, options] of window.fetch.mock.calls.slice(1)) {
      expect(options.credentials).toBe("include");
      expect(options.headers["X-CSRF-Token"]).toBe("temporario");
    }
  });

  it("usa o token rotacionado pelo login e permite reset explicito", async () => {
    window.fetch.mockResolvedValueOnce(response({ csrf_token: "anonimo" }))
      .mockResolvedValueOnce(response({ csrf_token: "autenticado" }))
      .mockResolvedValueOnce(response({ id: 1 }))
      .mockResolvedValueOnce(response({ csrf_token: "novo" }))
      .mockResolvedValueOnce(response({ id: 2 }));
    await request("/auth/login", { method: "POST" });
    await request("/materias", { method: "PUT" });
    expect(window.fetch.mock.calls[2][1].headers["X-CSRF-Token"]).toBe("autenticado");
    globalThis.resetCsrf();
    await request("/assuntos", { method: "POST" });
    expect(window.fetch.mock.calls[4][1].headers["X-CSRF-Token"]).toBe("novo");
  });

  it("sinaliza expiracao sem repetir mutacao e renova CSRF na nova confirmacao", async () => {
    const listener = vi.fn(); document.addEventListener("auth-required", listener);
    try {
      window.fetch.mockResolvedValueOnce(response({ csrf_token: "antes" }))
        .mockResolvedValueOnce(response({ codigo: "sessao_invalida", erro: "Entre novamente" }, 401))
        .mockResolvedValueOnce(response({ csrf_token: "depois" }))
        .mockResolvedValueOnce(response({ id: 1 }));
      await expect(request("/materias", { method: "POST" })).rejects.toMatchObject({ code: "sessao_invalida" });
      expect(window.fetch).toHaveBeenCalledTimes(2);
      expect(listener.mock.calls[0][0].detail).toBe("sessao_invalida");
      await request("/materias", { method: "POST" });
      expect(window.fetch.mock.calls[3][1].headers["X-CSRF-Token"]).toBe("depois");
    } finally { document.removeEventListener("auth-required", listener); }
  });

  it("bloqueia nova mutacao durante recuperacao sem requisicao de rede", async () => {
    const recover = vi.fn(); globalThis.AuthUI = { blocked: true, recover };
    await expect(request("/materias", { method: "DELETE" })).rejects.toMatchObject({ code: "acesso_bloqueado" });
    expect(recover).toHaveBeenLastCalledWith("sessao_invalida");
    globalThis.AuthUI.reason = "reautenticacao_necessaria";
    await expect(request("/materias", { method: "PUT" })).rejects.toMatchObject({ status: 403 });
    expect(recover).toHaveBeenLastCalledWith("reautenticacao_necessaria");
    expect(window.fetch).not.toHaveBeenCalled();
  });

  it("respeita URL configurada e nao envia CSRF em HEAD", async () => {
    vi.resetModules(); window.ENEM_API_URL = "https://api.escola.test/api";
    await import("../js/api.js");
    window.fetch.mockResolvedValue(response({}));
    await request("/materias", { method: "HEAD" });
    expect(window.fetch.mock.calls[0][0]).toBe("https://api.escola.test/api/materias");
    expect(window.fetch.mock.calls[0][1].headers).not.toHaveProperty("X-CSRF-Token");
  });
});
