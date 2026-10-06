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
      "http://127.0.0.1:5000/api/health",
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
});
