(() => {
  const aluno = [
    ["inicio", "/aluno/inicio.html", "Meu início", "home"],
    ["grupo", "ESTUDAR"],
    ["questoes", "/aluno/questoes.html", "Praticar questões", "clipboard"],
    ["historico", "/aluno/historico.html", "Meu histórico", "history"],
    ["simulados", "/aluno/simulados.html", "Simulados", "file"],
    ["tutor", "/aluno/tutor.html", "Tutor IA", "tutor"],
    ["grupo", "MINHA EVOLUÇÃO"],
    ["desempenho", "/aluno/desempenho.html", "Desempenho", "chart"],
    ["plano", "/aluno/plano.html", "Plano de Estudos", "calendar"],
    ["grupo", "MINHA CONTA"],
    ["privacidade", "/aluno/privacidade.html", "Privacidade e termos", "shield"],
    ["grupo", "EM BREVE"],
    ["indisponivel", "Resumos · indisponível", "book"],
  ];
  const admin = [
    ["grupo", "Administração"],
    ["dashboard", "dashboard.html", "Dashboard", "grid"],
    ["grupo", "Conteúdo"],
    ["materias", "materias.html", "Matérias", "book"],
    ["assuntos", "assuntos.html", "Assuntos", "list"],
    ["questoes", "questoes.html", "Questões", "file"],
    ["indisponivel", "Resumos", "book"],
    ["grupo", "Avaliações"],
    ["simulados", "simulados.html", "Simulados", "file"],
    ["indisponivel", "Temas de Redação", "pencil"],
    ["indisponivel", "Redações", "pencil"],
    ["grupo", "Gestão"],
    ["usuarios", "usuarios.html", "Usuários", "user"],
    ["grupo", "Minha conta"],
    ["indisponivel", "Perfil", "user"],
    ["indisponivel", "Área do aluno", "arrow"],
  ];
  function icon(name, administrative = true) {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("class", administrative ? "nav-icon" : "aluno-nav-icon");
    svg.setAttribute("aria-hidden", "true");
    svg.setAttribute("focusable", "false");
    const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
    use.setAttribute("href", `../assets/${administrative ? "admin" : "aluno"}-icons.svg#${name}`);
    svg.append(use);
    return svg;
  }
  for (const slot of document.querySelectorAll("[data-navigation]")) {
    const administrative = slot.dataset.navigation === "admin";
    if (!administrative && slot.dataset.navigation !== "aluno") continue;
    slot.replaceChildren();
    for (const [key, target, label, symbol] of administrative ? admin : aluno) {
      const group = key === "grupo", disabled = key === "indisponivel";
      const node = document.createElement(group ? administrative ? "p" : "small" : disabled ? "span" : "a");
      if (administrative) node.className = group ? "nav-label" : "nav-link";
      else node.className = group ? "aluno-nav-label" : "aluno-nav-link";
      node.textContent = group || disabled ? target : label;
      if (disabled) node.setAttribute("aria-disabled", "true");
      else if (!group) {
        node.setAttribute("href", target);
        if (key === slot.dataset.current) node.setAttribute("aria-current", "page");
      }
      if (!group) node.prepend(icon(disabled ? label : symbol, administrative));
      slot.append(node);
    }
  }
})();
