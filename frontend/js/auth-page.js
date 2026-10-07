(() => {
  const form = document.querySelector("#auth-form");
  if (!form) return;
  const signup = form.dataset.kind === "cadastro";
  const message = document.querySelector("#auth-message");
  const button = form.querySelector('[type="submit"]');
  const password = form.elements.senha;
  const email = form.elements.email;
  const prefill = sessionStorage.getItem("cadastro-email");
  if (!signup && prefill) {
    email.value = prefill; sessionStorage.removeItem("cadastro-email");
    message.textContent = "Conta criada. Entre com seu e-mail e senha.";
  }
  document.querySelectorAll("[data-password-toggle]").forEach((toggle) => {
    toggle.addEventListener("click", () => {
      const input = document.getElementById(toggle.dataset.passwordToggle);
      const visible = input.type === "password"; input.type = visible ? "text" : "password";
      toggle.setAttribute("aria-label", visible ? "Ocultar senha" : "Mostrar senha");
      toggle.setAttribute("aria-pressed", String(visible));
    });
  });
  function requirements() {
    if (!signup) return;
    document.querySelector("#auth-length").dataset.valid = String(password.value.length >= 8);
    document.querySelector("#auth-match").dataset.valid = String(!!password.value && password.value === form.elements.senha_confirmacao.value);
  }
  form.addEventListener("input", requirements);
  form.addEventListener("submit", async (event) => {
    event.preventDefault(); if (button.disabled) return;
    form.querySelectorAll(".auth-error").forEach((node) => { node.textContent = ""; });
    for (const input of form.querySelectorAll("input")) {
      input.removeAttribute("aria-invalid");
      let error = input.validity.valid ? "" : "Confira este campo.";
      if (signup && input.name === "nome") {
        const length = Array.from(input.value.trim()).length;
        if (length < 2 || length > 100) error = "O nome deve ter entre 2 e 100 caracteres.";
      }
      if (signup && input.name === "senha_confirmacao" && input.value !== password.value) error = "As senhas não coincidem.";
      if (error) {
        input.setAttribute("aria-invalid", "true"); document.getElementById(`${input.id}-error`).textContent = error;
        input.focus(); return;
      }
    }
    button.disabled = true; message.dataset.error = "false"; message.textContent = signup ? "Criando sua conta..." : "Entrando...";
    try {
      const data = await apiRequest(`/auth/${signup ? "cadastro" : "login"}`, {
        method: "POST", body: JSON.stringify(Object.fromEntries(new FormData(form))),
      });
      password.value = "";
      if (signup) {
        form.elements.senha_confirmacao.value = "";
        sessionStorage.setItem("cadastro-email", data.usuario.email); AuthUI.navigate("/login.html");
      } else AuthUI.navigate(data.usuario.perfil === "administrador" ? "/admin/materias.html" : "/aluno/inicio.html");
    } catch (error) {
      message.dataset.error = "true"; message.textContent = error.message;
      if (error.code === "email_em_uso") {
        email.setAttribute("aria-invalid", "true"); document.getElementById(`${email.id}-error`).textContent = error.message;
      }
    } finally { button.disabled = false; }
  });
})();
