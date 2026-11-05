/* Quem Saiu — contagem anônima de uso (leia: é curto de propósito).

   O que este arquivo faz: pede ao PRÓPRIO site alguns arquivos vazios da pasta /m/.
   Quem conta quantas vezes cada um foi pedido são as estatísticas da hospedagem
   (Cloudflare → Análise → Solicitações → Principais caminhos).

   O que NÃO faz: não envia lista, arquivo, nome de usuário, identificador, cookie nem
   nada que ligue o pedido a uma pessoa. Não carrega nada de terceiros.
   Se o navegador pediu "Não rastrear" (DNT) ou Global Privacy Control, não faz nada.

   Pedidos possíveis:
     /m/visita.txt        abriu o site (uma vez por sessão do navegador)
     /m/app-aberto.txt    abriu pelo app instalado (uma vez por sessão)
     /m/ficou-10s.txt ... /m/ficou-300s.txt   ficou esse tempo com a página aberta e visível
     /m/instalou.txt      o navegador avisou que o app foi instalado
     (mais os três do funil de lembretes, listados mais abaixo) */
(function () {
  "use strict";

  try {
    if (navigator.doNotTrack === "1" || window.doNotTrack === "1" || navigator.msDoNotTrack === "1") return;
    if (navigator.globalPrivacyControl === true) return;
    /* em testes locais (localhost) não conta, a não ser que o teste peça */
    if (!window.__QS_CONTAGEM_TESTE && /^(localhost|127\.|\[::1\])/.test(location.hostname)) return;
  } catch (e) { return; }

  function marcar(nome) {
    try {
      fetch("/m/" + nome + ".txt", { cache: "no-store", credentials: "omit", referrerPolicy: "no-referrer", keepalive: true })
        .catch(function () {});
    } catch (e) { /* sem contagem não quebra nada */ }
  }

  function umaVezPorSessao(nome) {
    try {
      var chave = "qs_m_" + nome;
      if (sessionStorage.getItem(chave)) return false;
      sessionStorage.setItem(chave, "1");
    } catch (e) { /* sem sessionStorage: conta de qualquer jeito, uma vez por carregamento */ }
    return true;
  }

  var standalone = false;
  try { standalone = !!(window.matchMedia && window.matchMedia("(display-mode: standalone)").matches); } catch (e) {}

  if (umaVezPorSessao("visita")) marcar("visita");
  if (standalone && umaVezPorSessao("app-aberto")) marcar("app-aberto");

  /* tempo com a página aberta E visível (o relógio para quando a aba vai para segundo plano) */
  var MARCOS = [10, 30, 60, 120, 300];
  var segundos = 0;
  var proximo = 0;
  var relogio = setInterval(function () {
    if (document.visibilityState !== "visible") return;
    segundos += 1;
    if (proximo < MARCOS.length && segundos >= MARCOS[proximo]) {
      marcar("ficou-" + MARCOS[proximo] + "s");
      proximo += 1;
      if (proximo >= MARCOS.length) clearInterval(relogio);
    }
  }, 1000);

  window.addEventListener("appinstalled", function () { marcar("instalou"); });

  /* eventos do funil de lembretes (só o site chama, e só quando os avisos estão ligados):
       /m/pediu.txt         tocou em "Já pedi"
       /m/voltou.txt        abriu o site com um pedido anotado (uma vez por sessão)
       /m/mandou-lista.txt  mandou uma lista
     Sem identificar ninguém: é só um arquivo vazio pedido ao próprio site. */
  var FUNIL = ["pediu", "voltou", "mandou-lista"];
  window.qsContar = function (nome, umaVez) {
    if (FUNIL.indexOf(nome) === -1) return;
    if (umaVez && !umaVezPorSessao(nome)) return;
    marcar(nome);
  };
})();
