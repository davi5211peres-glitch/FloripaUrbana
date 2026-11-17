document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.mensagem').forEach((mensagem) => {
    window.setTimeout(() => mensagem.remove(), 6000);
  });
});
