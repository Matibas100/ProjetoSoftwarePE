import fs from "node:fs";

import { htmlPath } from "./classic-app.js";


export function prepareGlobalDom() {
  const html = fs.readFileSync(htmlPath, "utf8").replace(
    /<script\s+src="[^"]+"><\/script>/g,
    "",
  );
  document.open();
  document.write(html);
  document.close();
  window.scrollTo = () => {};
  window.confirm = () => true;
  HTMLElement.prototype.focus = () => {};
  HTMLElement.prototype.scrollIntoView = () => {};
}

export function prepareAdminGlobalDom(sourcePath) {
  const html = fs.readFileSync(sourcePath, "utf8").replace(
    /<script\s+src="[^"]+"><\/script>/g,
    "",
  );
  document.open();
  document.write(html);
  document.close();
  HTMLElement.prototype.focus = () => {};
  HTMLElement.prototype.scrollIntoView = () => {};
  HTMLDialogElement.prototype.showModal = function showModal() { this.open = true; };
  HTMLDialogElement.prototype.close = function close() { this.open = false; };
}
