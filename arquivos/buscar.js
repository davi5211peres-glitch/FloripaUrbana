document.querySelectorAll(".busca-topo").forEach((form, indice) => {
  const input = form.querySelector("input");
  const lista = form.querySelector(".sugestoes-busca");
  lista.id = `sugestoes-busca-${indice}`;
  input.setAttribute("aria-controls", lista.id);
  let timer;
  let resultadosAtuais = [];

  function fecharSugestoes() {
    lista.replaceChildren();
    lista.classList.remove("aberta");
    resultadosAtuais = [];
  }

  input.addEventListener("input", () => {
    clearTimeout(timer);
    resultadosAtuais = [];
    const termo = input.value.trim();
    if (termo.length < 2) {
      fecharSugestoes();
      return;
    }

    timer = setTimeout(async () => {
      try {
        const resposta = await fetch(`${form.dataset.api}?q=${encodeURIComponent(termo)}`);
        resultadosAtuais = await resposta.json();
        lista.replaceChildren();
        resultadosAtuais.forEach((item) => {
          const itemLista = document.createElement("li");
          itemLista.setAttribute("role", "option");
          const link = document.createElement("a");
          link.href = item.url;
          link.textContent = item.nome;
          itemLista.append(link);
          lista.append(itemLista);
        });
        lista.classList.toggle("aberta", resultadosAtuais.length > 0);
      } catch {
        fecharSugestoes();
      }
    }, 180);
  });

  form.addEventListener("submit", (event) => {
    if (input.value.trim() && resultadosAtuais.length) {
      event.preventDefault();
      window.location.href = resultadosAtuais[0].url;
    }
  });

  document.addEventListener("click", (event) => {
    if (!form.contains(event.target)) fecharSugestoes();
  });
});
