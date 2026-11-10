import fs from "node:fs";
import path from "node:path";
import { expect, it, vi } from "vitest";
import { root } from "./helpers/classic-app.js";

for (const area of ["aluno", "admin"]) {
  for (const file of fs.readdirSync(path.join(root, "frontend", area)).filter((name) => name.endsWith(".html"))) {
    it(`renderiza menu ${area}/${file} com destinos, atual único e indisponíveis sem ação`, async () => {
      vi.resetModules();
      const html = fs.readFileSync(path.join(root, "frontend", area, file), "utf8");
      document.open();
      document.write(html.replace(/<script\s+src="[^"]+"><\/script>/g, ""));
      document.close();
      await import("../js/navigation.js");
      const slot = document.querySelector("[data-navigation]");
      expect(slot.querySelectorAll('[aria-current="page"]')).toHaveLength(1);
      const section = { questao: "questoes", simulado: "simulados", usuario: "usuarios" }[file.replace(".html", "")] || file.replace(".html", "");
      expect(slot.querySelector('[aria-current="page"]').getAttribute("href")).toBe(
        area === "aluno" ? `/aluno/${section}.html` : `${section}.html`,
      );
      const expected = area === "aluno" ? ["inicio", "questoes", "historico", "simulados", "tutor", "desempenho", "plano", "privacidade"] : ["dashboard", "materias", "assuntos", "questoes", "simulados", "usuarios"];
      expect([...slot.querySelectorAll("a")].map((a) => a.getAttribute("href"))).toEqual(
        expected.map((key) => area === "aluno" ? `/aluno/${key}.html` : `${key}.html`),
      );
      for (const unavailable of slot.querySelectorAll('[aria-disabled="true"]')) {
        expect(unavailable.tagName).toBe("SPAN");
        expect(unavailable.hasAttribute("href")).toBe(false);
        expect(unavailable.tabIndex).toBe(-1);
      }
      const link = slot.querySelector("a");
      link.focus();
      expect(document.activeElement).toBe(link);
      expect(html.indexOf("js/navigation.js")).toBeLessThan(html.indexOf("js/auth-session.js"));
      expect(document.querySelector("[data-auth-exit]")).not.toBeNull();
      expect(document.querySelector("[data-auth-name]")).not.toBeNull();
      if (area === "aluno") {
        expect([...slot.querySelectorAll("a")].map(a => a.textContent)).toEqual([
          "Meu início",
          "Praticar questões",
          "Meu histórico",
          "Simulados",
          "Tutor IA",
          "Desempenho",
          "Plano de Estudos",
          "Privacidade e termos",
        ]);
      }
      for (const item of slot.querySelectorAll('a,[aria-disabled="true"]')) {
        const icon = item.querySelector("svg");
        expect(icon.getAttribute("aria-hidden")).toBe("true");
        expect(icon.getAttribute("focusable")).toBe("false");
        expect(icon.hasAttribute("tabindex")).toBe(false);
        const href = icon.querySelector("use").getAttribute("href");
        const [sprite, symbol] = href.split("#");
        expect(sprite).toBe(`../assets/${area}-icons.svg`);
        expect(fs.readFileSync(path.join(root, "frontend", "assets", `${area}-icons.svg`), "utf8")).toContain(`id="${symbol}"`);
      }
    });
  }
}

it("preserva slots desconhecidos e ignora página sem slot", async () => {
  vi.resetModules();
  document.body.innerHTML = '<div data-navigation="desconhecido">Preservar</div>';
  await import("../js/navigation.js");
  expect(document.body.textContent).toBe("Preservar");
  vi.resetModules();
  document.body.replaceChildren();
  await import("../js/navigation.js");
  expect(document.body.childElementCount).toBe(0);
});
