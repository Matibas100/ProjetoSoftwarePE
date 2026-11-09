(() => {
  globalThis.TutorUI?.destroy?.();
  const $ = id => document.getElementById(id);
  const titulos = ["1. Explicação simples", "2. Exemplo", "3. Verifique sua compreensão", "4. Exercício curto"];
  const state = { generation: 0, filter: 0, busy: false, materias: [], assuntos: [], result: null, controller: null, timer: null, destroyed: false };
  const available = () => !state.destroyed && !AuthUI.blocked && !AuthUI.changedAccount;
  const valid = (generation, user) => generation === state.generation && available() && AuthUI.user?.id === user;
  const node = (tag, text) => { const n = document.createElement(tag); n.textContent = text; return n; };
  function message(text, error = false, focus = false) {
    $("tutor-status").textContent = text; $("tutor-status").dataset.erro = error;
    if (focus) $("tutor-status").focus();
  }
  function update() {
    const materia = state.materias.find(m => String(m.id) === $("tutor-materia").value);
    const assunto = state.assuntos.find(a => String(a.id) === $("tutor-assunto").value);
    $("tutor-contexto").textContent = materia ? `${materia.nome} · ${assunto ? assunto.nome : "Escolha o assunto"}` : "Escolha uma matéria e um assunto do catálogo ativo.";
    $("tutor-enviar").disabled = !available() || state.busy || !materia || !assunto;
    $("tutor-enviar").textContent = state.busy ? "Enviando ao Gemini..." : "Enviar dúvida ao Gemini";
    $("tutor-painel")?.setAttribute("aria-busy", String(state.busy));
    $("tutor-form").setAttribute("aria-busy", String(state.busy));
  }
  function clear() {
    state.generation++; state.filter++; state.controller?.abort(); clearTimeout(state.timer);
    state.controller = null; state.timer = null; state.busy = false; state.result = null;
    $("tutor-duvida").value = ""; $("tutor-secoes").replaceChildren();
    $("tutor-pergunta-anterior").textContent = ""; $("tutor-resposta-contexto").textContent = "";
    $("tutor-resultado").hidden = true; $("tutor-termos").hidden = true;
    message("Sessão alterada ou encerrada. Confirme sua identidade para continuar.", true); update();
  }
  function options(select, items, title) { select.replaceChildren(new Option(title, ""), ...items.map(i => new Option(i.nome, i.id))); }
  async function catalogo() {
    if (!available() || state.busy) return;
    const generation = state.generation, user = AuthUI.user.id, filter = ++state.filter;
    state.materias = []; state.assuntos = [];
    options($("tutor-materia"), [], "Carregando catálogo..."); options($("tutor-assunto"), [], "Escolha a matéria");
    $("tutor-materia").disabled = true; $("tutor-assunto").disabled = true; update();
    try {
      const materias = await apiRequest("/materias");
      if (!valid(generation, user) || filter !== state.filter) return;
      if (!Array.isArray(materias)) throw new Error("Catálogo inválido.");
      state.materias = materias;
      options($("tutor-materia"), materias, materias.length ? "Escolha a matéria" : "Nenhuma matéria disponível");
      $("tutor-materia").disabled = !materias.length;
      message(materias.length ? "Escolha matéria e assunto e escreva sua dúvida." : "Catálogo vazio. Não há matérias disponíveis.");
    } catch (error) { if (valid(generation, user) && filter === state.filter) message(`Falha no catálogo. ${error.message}`, true); }
    finally { if (valid(generation, user)) update(); }
  }
  async function assuntos() {
    const generation = state.generation, user = AuthUI.user?.id, filter = ++state.filter, materia = $("tutor-materia").value;
    state.assuntos = []; options($("tutor-assunto"), [], "Escolha o assunto"); $("tutor-assunto").disabled = true; update();
    if (!materia || !available()) return;
    message("Carregando assuntos...");
    try {
      const data = await apiRequest(`/assuntos?materia_id=${encodeURIComponent(materia)}`);
      if (!valid(generation, user) || filter !== state.filter) return;
      if (!Array.isArray(data)) throw new Error("Catálogo inválido.");
      state.assuntos = data.filter(a => String(a.materia_id) === materia);
      options($("tutor-assunto"), state.assuntos, state.assuntos.length ? "Escolha o assunto" : "Nenhum assunto disponível");
      $("tutor-assunto").disabled = !state.assuntos.length;
      message(state.assuntos.length ? "Escolha o assunto e escreva sua dúvida." : "Nenhum assunto disponível nesta matéria.");
    } catch (error) { if (valid(generation, user) && filter === state.filter) message(`Falha nos assuntos. ${error.message}`, true); }
    finally { if (valid(generation, user)) update(); }
  }
  function render(data, pergunta) {
    if (typeof data?.resposta !== "string") throw new Error("Resposta inválida do servidor.");
    const texto = data.resposta.replace(/\r\n?/g, "\n").trim();
    const linhas = texto.split("\n"), posicoes = titulos.map(t => linhas.indexOf(t));
    if (posicoes[0] !== 0 || posicoes.some((p, i) => p < 0 || (i > 0 && p <= posicoes[i - 1])) || texto.length > 12000 ||
        titulos.some(t => linhas.filter(l => l === t).length !== 1)) throw new Error("Resposta incompleta do Tutor.");
    const secoes = titulos.map((t, i) => {
      const conteudo = linhas.slice(posicoes[i] + 1, i < 3 ? posicoes[i + 1] : undefined).join("\n").trim();
      if (!conteudo) throw new Error("Resposta incompleta do Tutor.");
      const section = document.createElement("section"); section.append(node("h3", t), node("p", conteudo)); return section;
    });
    $("tutor-secoes").replaceChildren(...secoes);
    $("tutor-pergunta-anterior").textContent = pergunta.duvida;
    $("tutor-resposta-contexto").textContent = `${pergunta.disciplina} · ${pergunta.assunto} · Pergunta deste envio`;
    state.result = true; $("tutor-resultado").hidden = document.visibilityState === "hidden";
  }
  async function enviar(event) {
    event.preventDefault();
    if (!available() || state.busy || $("tutor-enviar").disabled) return;
    const duvida = $("tutor-duvida").value.trim();
    if (duvida.length < 10 || duvida.length > 2000) { message("Escreva uma dúvida de 10 a 2000 caracteres.", true); $("tutor-duvida").focus(); return; }
    const pergunta = { disciplina: state.materias.find(m => String(m.id) === $("tutor-materia").value).nome,
      nivel: "ensino_medio", assunto: state.assuntos.find(a => String(a.id) === $("tutor-assunto").value).nome, duvida };
    const generation = ++state.generation, user = AuthUI.user.id, controller = new AbortController();
    state.controller = controller; state.busy = true; update(); $("tutor-termos").hidden = true;
    message("Enviando sua dúvida ao Gemini. Aguarde...");
    if (state.result) $("tutor-resposta-contexto").textContent += " · Resposta anterior; novo envio em andamento";
    let timedOut = false;
    try {
      const timeout = new Promise((_, reject) => { state.timer = setTimeout(() => {
        timedOut = true; controller.abort(); reject(new Error("A espera de 45 segundos terminou. Você pode confirmar outra tentativa; o provedor pode continuar processando."));
      }, 45000); });
      const operacao = async () => {
        if (!await AuthUI.checkIdentity() || !valid(generation, user) || controller.signal.aborted) return null;
        const data = await apiRequest("/tutoria", { method: "POST", body: JSON.stringify(pergunta), signal: controller.signal });
        if (!valid(generation, user) || controller.signal.aborted || !await AuthUI.checkIdentity() || !valid(generation, user) || controller.signal.aborted) return null;
        return { data };
      };
      const resultado = await Promise.race([operacao(), timeout]);
      if (!resultado || !valid(generation, user)) return;
      render(resultado.data, pergunta); message("Resposta recebida. Confira o raciocínio antes de usá-lo."); $("tutor-resposta-titulo").focus();
    } catch (error) {
      if (valid(generation, user)) {
        const text = timedOut ? "A espera de 45 segundos terminou. Confirme novo envio se desejar; pode haver consumo no provedor." : error.message;
        message(`${text}${state.result ? " A resposta anterior continua associada à pergunta anterior." : ""}`, true, true);
        if (state.result) $("tutor-resposta-contexto").textContent = $("tutor-resposta-contexto").textContent.replace(/ · Resposta anterior;.*/, "") + " · Resposta anterior; a nova tentativa falhou";
        $("tutor-termos").hidden = error.code !== "termos_uso_pendentes";
      }
    } finally {
      if (generation === state.generation) { clearTimeout(state.timer); state.timer = null; state.controller = null; state.busy = false; update(); }
    }
  }
  async function onReturn() {
    if (document.visibilityState === "hidden") { $("tutor-resultado").hidden = true; return; }
    if (!available()) return;
    const generation = state.generation, user = AuthUI.user.id;
    $("tutor-resultado").hidden = true;
    try { if (await AuthUI.checkIdentity() && valid(generation, user)) $("tutor-resultado").hidden = !state.result; }
    catch { clear(); }
  }
  function onRequired() { clear(); }
  const exit = document.querySelector("[data-auth-exit]");
  $("tutor-form").addEventListener("submit", enviar);
  $("tutor-materia").addEventListener("change", assuntos); $("tutor-assunto").addEventListener("change", update);
  $("tutor-catalogo").addEventListener("click", catalogo);
  exit.addEventListener("click", clear);
  document.addEventListener("auth-required", onRequired); document.addEventListener("auth-identity-changed", clear);
  window.addEventListener("pagehide", clear); window.addEventListener("focus", onReturn); document.addEventListener("visibilitychange", onReturn);
  globalThis.TutorUI = { state, catalogo, destroy() {
    clear(); state.destroyed = true;
    $("tutor-form").removeEventListener("submit", enviar); $("tutor-materia").removeEventListener("change", assuntos);
    $("tutor-assunto").removeEventListener("change", update); $("tutor-catalogo").removeEventListener("click", catalogo); exit.removeEventListener("click", clear);
    document.removeEventListener("auth-required", onRequired); document.removeEventListener("auth-identity-changed", clear);
    window.removeEventListener("pagehide", clear); window.removeEventListener("focus", onReturn); document.removeEventListener("visibilitychange", onReturn);
  } };
  AuthUI.ready.then(ready => { if (ready && available()) catalogo(); });
})();
