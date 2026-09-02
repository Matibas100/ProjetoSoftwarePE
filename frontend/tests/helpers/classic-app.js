import fs from "node:fs";
import path from "node:path";
import { JSDOM } from "jsdom";

export const root = path.resolve(import.meta.dirname, "../../..");
export const htmlPath = path.join(root, "frontend", "index.html");

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
      dom.window.__apiRequestMock = apiRequest;
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

export async function settle() {
  await Promise.resolve();
  await new Promise((resolve) => setTimeout(resolve, 0));
  await Promise.resolve();
}
