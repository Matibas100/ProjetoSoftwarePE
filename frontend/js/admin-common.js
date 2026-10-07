(() => {
  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined && text !== null) node.textContent = String(text);
    if (className) node.className = className;
    return node;
  }

  function cell(text, className) {
    return element("td", text ?? "—", className);
  }

  function showMessage(node, message, type = "success") {
    node.textContent = message;
    node.className = `notice notice--${type}`;
    node.hidden = false;
  }

  function hideMessage(node) {
    node.hidden = true;
    node.textContent = "";
  }

  function fillSelect(select, items, initialLabel, selected = "") {
    select.replaceChildren();
    const initial = element("option", initialLabel);
    initial.value = "";
    select.appendChild(initial);
    items.forEach((item) => {
      const option = element("option", item.nome);
      option.value = String(item.id);
      select.appendChild(option);
    });
    select.value = String(selected || "");
  }

  function dateLabel(value) {
    if (!value) return "—";
    return new Intl.DateTimeFormat("pt-BR", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(value));
  }

  function adminQuery(page, filters = {}) {
    return new URLSearchParams({ pagina: page, por_pagina: 20, ...filters });
  }

  function applyPage(state, data) {
    Object.assign(state, {
      items: data.itens,
      page: data.pagina,
      pages: data.total_paginas,
      total: data.total_itens,
    });
  }

  function statusPill(status) {
    return element("span", status, `status-pill status-pill--${status}`);
  }

  function actionMenu(id, actions) {
    const details = element("details", null, "action-menu");
    const summary = element("summary", "Editar ···");
    summary.setAttribute("aria-label", `${summary.textContent}, ações do item ${id}`);
    details.appendChild(summary);
    const menu = element("div");
    actions.forEach(({ action, label, danger }) => {
      const button = element("button", label, danger ? "danger" : "");
      button.type = "button";
      button.dataset.action = action;
      button.dataset.id = String(id);
      menu.appendChild(button);
    });
    details.appendChild(menu);
    return details;
  }

  function createUnsavedGuard(form, indicator) {
    let persisted = "";
    const snapshot = () => JSON.stringify(Object.fromEntries(new FormData(form)));
    const dirty = () => snapshot() !== persisted;
    globalThis.AuthUI?.registerGuard(dirty);
    const update = () => { indicator.hidden = !dirty(); };
    const markPersisted = () => { persisted = snapshot(); update(); };
    form.addEventListener("input", update);
    form.addEventListener("change", update);
    window.addEventListener("beforeunload", (event) => {
      if (dirty()) {
        event.preventDefault();
        event.returnValue = "";
      }
    });
    return { dirty, markPersisted };
  }

  function modalController(dialog) {
    const title = dialog.querySelector("#admin-modal-titulo");
    const text = dialog.querySelector("#admin-modal-texto");
    const cancel = dialog.querySelector("#admin-modal-cancelar");
    const confirm = dialog.querySelector("#admin-modal-confirmar");
    return {
      confirm(options) {
        title.textContent = options.title;
        text.textContent = options.text;
        confirm.textContent = options.confirmLabel || "Confirmar";
        confirm.className = options.danger
          ? "button button--danger"
          : "button button--primary";
        dialog.showModal();
        return new Promise((resolve) => {
          const finish = (result) => {
            dialog.close();
            cancel.removeEventListener("click", onCancel);
            confirm.removeEventListener("click", onConfirm);
            dialog.removeEventListener("cancel", onEscape);
            dialog.removeEventListener("keydown", onKeyDown);
            resolve(result);
          };
          const onCancel = () => finish(false);
          const onConfirm = () => finish(true);
          const onEscape = (event) => {
            event.preventDefault();
            finish(false);
          };
          const onKeyDown = (event) => {
            if (event.key === "Tab") {
              event.preventDefault();
              (document.activeElement === cancel ? confirm : cancel).focus();
            }
          };
          cancel.addEventListener("click", onCancel);
          confirm.addEventListener("click", onConfirm);
          dialog.addEventListener("cancel", onEscape);
          dialog.addEventListener("keydown", onKeyDown);
        });
      },
    };
  }

  globalThis.AdminUI = {
    adminQuery,
    applyPage,
    actionMenu,
    cell,
    createUnsavedGuard,
    dateLabel,
    element,
    fillSelect,
    hideMessage,
    modalController,
    showMessage,
    statusPill,
  };
})();
