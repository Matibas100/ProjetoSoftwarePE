import fs from "node:fs";
import path from "node:path";
import { JSDOM } from "jsdom";

export const root = path.resolve(import.meta.dirname, "../../..");
export const htmlPath = path.join(root, "frontend", "index.html");
export const adminMatterHtmlPath = path.join(root, "frontend", "admin", "materias.html");
export const adminSubjectHtmlPath = path.join(root, "frontend", "admin", "assuntos.html");

export function declaredScripts(html = fs.readFileSync(htmlPath, "utf8")) {
  const dom = new JSDOM(html);
  return [...dom.window.document.querySelectorAll("script[src]")].map((script) =>
    script.getAttribute("src"),
  );
}

export function createClassicApp({ apiRequest, confirm = () => true } = {}) {
  const sourceHtml = fs.readFileSync(htmlPath, "utf8");
  const scripts = declaredScripts(sourceHtml);
  const html = sourceHtml.replace(
    /<script\s+src="[^"]+"><\/script>/g,
    "",
  );
  const dom = new JSDOM(html, {
    runScripts: "dangerously",
    url: "http://127.0.0.1:5500/",
  });
  dom.window.console.error = () => {};
  dom.window.confirm = confirm;
  dom.window.scrollTo = () => {};
  dom.window.HTMLElement.prototype.focus = () => {};
  dom.window.HTMLElement.prototype.scrollIntoView = () => {};

  function execute(relativePath) {
    const absolutePath = path.join(root, relativePath);
    const script = dom.window.document.createElement("script");
    script.textContent = `${fs.readFileSync(absolutePath, "utf8")}\n//# sourceURL=${absolutePath.replaceAll("\\", "/")}`;
    dom.window.document.head.appendChild(script);
    return dom;
  }

  for (const scriptPath of scripts) {
    execute(path.posix.join("frontend", scriptPath));
    if (scriptPath === "js/api.js" && apiRequest) {
      dom.window.__apiRequestMock = (path, ...args) => path === "/auth/sessao"
        ? Promise.resolve({ usuario: { id: 1, nome: "Admin teste", email: "admin@teste.local", perfil: "administrador" }, csrf_token: "unit" })
        : apiRequest(path, ...args);
      dom.window.eval("apiRequest = window.__apiRequestMock");
    }
  }

  return {
    dom,
    window: dom.window,
    document: dom.window.document,
    executedScripts: scripts,
    execute,
    evaluate: (source) => dom.window.eval(source),
    close: () => dom.window.close(),
  };
}

export function createAdminApp(htmlFile, { apiRequest } = {}) {
  const sourceHtml = fs.readFileSync(htmlFile, "utf8");
  const dom = new JSDOM(
    sourceHtml.replace(/<script\s+src="[^"]+"><\/script>/g, ""),
    { runScripts: "dangerously", url: `http://127.0.0.1:5500/admin/${path.basename(htmlFile)}` },
  );
  dom.window.HTMLElement.prototype.focus = () => {};
  dom.window.HTMLElement.prototype.scrollIntoView = () => {};
  dom.window.HTMLDialogElement.prototype.showModal = function showModal() { this.open = true; };
  dom.window.HTMLDialogElement.prototype.close = function close() { this.open = false; };
  const scripts = declaredScripts(sourceHtml);
  for (const scriptPath of scripts) {
    const absolutePath = path.resolve(path.dirname(htmlFile), scriptPath);
    const script = dom.window.document.createElement("script");
    script.textContent = `${fs.readFileSync(absolutePath, "utf8")}\n//# sourceURL=${absolutePath.replaceAll("\\", "/")}`;
    dom.window.document.head.appendChild(script);
    if (scriptPath.endsWith("api.js") && apiRequest) {
      dom.window.__apiRequestMock = (path, ...args) => path === "/auth/sessao"
        ? Promise.resolve({ usuario: { id: 1, nome: "Admin teste", email: "admin@teste.local", perfil: "administrador" }, csrf_token: "unit" })
        : apiRequest(path, ...args);
      dom.window.eval("apiRequest = window.__apiRequestMock");
    }
  }
  return {
    dom,
    window: dom.window,
    document: dom.window.document,
    close: () => dom.window.close(),
  };
}

export async function settle() {
  await Promise.resolve();
  await new Promise((resolve) => setTimeout(resolve, 0));
  await Promise.resolve();
}
