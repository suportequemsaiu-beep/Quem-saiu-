/* ===== navegação ===== */
function irParaAba(id) {
  document.querySelectorAll("nav .abas button").forEach(function (b) {
    var ativo = b.dataset.tab === id;
    b.classList.toggle("ativo", ativo);
    if (ativo) b.setAttribute("aria-current", "page"); else b.removeAttribute("aria-current");
  });
  document.querySelectorAll("section").forEach(function (s) { s.classList.toggle("ativa", s.id === id); });
  window.scrollTo(0, 0);
}
document.querySelectorAll("nav .abas button").forEach(function (btn) {
  btn.addEventListener("click", function () { irParaAba(btn.dataset.tab); });
});
document.getElementById("marca").addEventListener("click", function () { irParaAba("inicio"); });
document.getElementById("marca").addEventListener("keydown", function (e) {
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); irParaAba("inicio"); }
});

/* ===== gancho -> prova ===== */
document.getElementById("btnDescobrir").addEventListener("click", function () {
  var r = document.getElementById("revelado");
  r.classList.add("on");
  setTimeout(function () { r.scrollIntoView({ behavior: "smooth", block: "start" }); }, 60);
});

/* ===== compartilhar o site ===== */
document.getElementById("btnCompartilhar").addEventListener("click", function () {
  var botao = this;
  /* Depois do menu de compartilhar fechar, o navegador devolve o foco ao botão e
     desenha a borda azul de teclado. Tirar o foco evita que ela fique ali. */
  function soltarFoco() { botao.blur(); }
  var dados = {
    title: "Quem Saiu",
    text: "Descubra quem deixou de te seguir no Instagram — sem login e sem senha.",
    url: "https://quemsaiu.com.br"
  };
  var rotulo = document.getElementById("txtCompartilhar");
  function avisar(msg) {
    rotulo.textContent = msg;
    setTimeout(function () { rotulo.textContent = "Compartilhar"; }, 2000);
  }
  if (navigator.share) {
    navigator.share(dados).catch(function () {}).then(function () { soltarFoco(); setTimeout(soltarFoco, 150); });
    soltarFoco();
  } else if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(dados.url).then(function () { avisar("Link copiado"); }, function () { avisar("Não foi possível copiar"); }).then(soltarFoco);
  } else {
    avisar("Copie: quemsaiu.com.br");
    soltarFoco();
  }
});

/* ===== prova interativa ===== */
var LISTAS = {
  saiu: {
    explica: "Quem te seguia antes e não te segue mais.",
    classe: "",
    itens: [
      { cor: "#f97316", nome: "@bruno_costa", selo: "Você segue", seloClasse: "selo-fake" },
      { cor: "#8b5cf6" }, { cor: "#10b981" }
    ]
  },
  entrou: {
    explica: "Quem passou a te seguir desde a sua última lista.",
    classe: "entrou",
    itens: [
      { cor: "#0ea5e9", nome: "@paula.mendes", selo: "Você segue de volta", seloClasse: "selo-fake selo-verde" },
      { cor: "#ec4899" }, { cor: "#14b8a6" }
    ]
  },
  naoSegue: {
    explica: "Quem você segue e não te segue de volta.",
    classe: "naoSegue",
    itens: [
      { cor: "#6366f1", nome: "@yuri22" },
      { cor: "#f59e0b" }, { cor: "#84cc16" }
    ]
  }
};

function pintarLista(chave) {
  var d = LISTAS[chave];
  document.getElementById("explica").textContent = d.explica;
  document.getElementById("listaProva").innerHTML = d.itens.map(function (i) {
    return '<div class="linha ' + d.classe + '">' +
      '<span class="av" style="background:' + i.cor + '"></span>' +
      (i.nome ? '<span class="nome-claro">' + i.nome + "</span>" : '<span class="nome-borrado"></span>') +
      (i.selo ? '<span class="' + i.seloClasse + '">' + i.selo + "</span>" : "") +
      "</div>";
  }).join("");
}

function trocarAbaProva(chave) {
  document.querySelectorAll(".aba-prova").forEach(function (x) {
    x.classList.remove("ativa", "ativa-verde", "ativa-roxa");
    if (x.dataset.lista === "entrou") x.classList.add("verde");
    if (x.dataset.lista === "naoSegue") x.classList.add("roxa");
  });
  document.querySelectorAll(".aba-prova").forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
  var alvo = document.querySelector('.aba-prova[data-lista="' + chave + '"]');
  alvo.classList.remove("verde", "roxa");
  alvo.classList.add("ativa");
  alvo.setAttribute("aria-pressed", "true");
  if (chave === "entrou") alvo.classList.add("ativa-verde");
  if (chave === "naoSegue") alvo.classList.add("ativa-roxa");
  pintarLista(chave);
}

document.querySelectorAll(".aba-prova").forEach(function (b) {
  b.addEventListener("click", function () { trocarAbaProva(b.dataset.lista); });
});
pintarLista("saiu");

/* ===== abrir a ferramenta ===== */
document.getElementById("btnComecar").addEventListener("click", function () {
  var f = document.getElementById("ferramenta");
  f.style.display = "block";
  setTimeout(function () { f.scrollIntoView({ behavior: "smooth", block: "start" }); }, 60);
});

/* ===== passo a passo expansível ===== */
document.getElementById("togglePasso").addEventListener("click", function () {
  var c = document.getElementById("corpoPasso");
  var aberto = c.style.display !== "none";
  c.style.display = aberto ? "none" : "block";
  document.getElementById("setaPasso").textContent = aberto ? "▼" : "▲";
  this.setAttribute("aria-expanded", aberto ? "false" : "true");
});

/* ===== passo a passo: um passo por vez =====
   Os passos ficam escritos no index.html (assim qualquer leitor, inclusive robôs, vê o texto).
   Aqui só se monta a barra de progresso, os botões e os desenhos. Se algo falhar, a lista inteira continua visível. */
(function () {
  var corpo = document.getElementById("corpoPasso");
  var lista = document.getElementById("listaEtapas");
  if (!corpo || !lista) return;

  /* Desenhos genéricos de telas de celular: sem logo e sem as cores de nenhum aplicativo. */
  function moldura(inner) {
    return '<svg viewBox="0 0 200 240" aria-hidden="true" focusable="false">' +
      '<rect x="3" y="3" width="194" height="234" rx="24" fill="#fff" stroke="#94a3b8" stroke-width="3"/>' +
      '<rect x="80" y="11" width="40" height="5" rx="2.5" fill="#cbd5e1"/>' + inner + '</svg>';
  }
  function barra(x, y, w, cor) {
    return '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="7" rx="3.5" fill="' + (cor || "#e2e8f0") + '"/>';
  }
  function anel(x, y, w, h, r) {
    return '<rect class="alvo-anel" x="' + (x - 4) + '" y="' + (y - 4) + '" width="' + (w + 8) + '" height="' + (h + 8) +
      '" rx="' + (r + 4) + '" fill="none" stroke="#0369a1" stroke-width="2.5"/>';
  }
  /* linha da lista; opcoes: alvo (destacada), apagada (opção errada), valor (texto à direita) */
  function linha(y, texto, o) {
    o = o || {};
    var h = 30, fundo = o.alvo ? "#e0f2fe" : "#f1f5f9";
    var out = '<rect x="16" y="' + y + '" width="168" height="' + h + '" rx="10" fill="' + fundo + '"' +
      (o.alvo ? ' stroke="#0369a1" stroke-width="1.5"' : "") + '/>';
    if (texto) {
      out += '<text x="27" y="' + (y + 19) + '" font-size="10" font-family="sans-serif" font-weight="' + (o.alvo ? 700 : 500) +
        '" fill="' + (o.alvo ? "#0c4a6e" : (o.apagada ? "#94a3b8" : "#64748b")) + '">' + texto + '</text>';
    } else {
      out += barra(27, y + 12, 70 + (y % 5) * 9);
    }
    if (o.valor) {
      out += '<text x="174" y="' + (y + 19) + '" font-size="9.5" font-family="sans-serif" font-weight="700" text-anchor="end" fill="#0369a1">' + o.valor + '</text>';
    }
    return out + (o.alvo ? anel(16, y, 168, h, 10) : "");
  }
  function botao(y, texto, ring) {
    return '<rect x="16" y="' + y + '" width="168" height="34" rx="12" fill="#0369a1"/>' +
      '<text x="100" y="' + (y + 21) + '" font-size="11" font-family="sans-serif" font-weight="800" text-anchor="middle" fill="#fff">' + texto + '</text>' +
      (ring ? anel(16, y, 168, 34, 12) : "");
  }
  function titulo(txt) {
    return '<text x="100" y="42" font-size="10" font-family="sans-serif" font-weight="800" text-anchor="middle" fill="#475569">' + txt + '</text>';
  }
  var cinzaIcone = '#475569';
  var DESENHOS = {
    perfil: function () {
      return moldura(barra(18, 34, 64, "#cbd5e1") +
        '<rect x="165" y="32" width="20" height="3" rx="1.5" fill="' + cinzaIcone + '"/><rect x="165" y="38" width="20" height="3" rx="1.5" fill="' + cinzaIcone + '"/><rect x="165" y="44" width="20" height="3" rx="1.5" fill="' + cinzaIcone + '"/>' +
        anel(161, 27, 28, 24, 8) +
        '<circle cx="42" cy="88" r="22" fill="#e2e8f0"/>' + barra(78, 76, 28) + barra(112, 76, 28) + barra(146, 76, 28) +
        barra(78, 94, 96) + barra(18, 126, 90, "#cbd5e1") +
        '<rect x="16" y="146" width="168" height="26" rx="9" fill="#f1f5f9"/>' +
        '<rect x="16" y="184" width="52" height="42" rx="6" fill="#f1f5f9"/><rect x="74" y="184" width="52" height="42" rx="6" fill="#f1f5f9"/><rect x="132" y="184" width="52" height="42" rx="6" fill="#f1f5f9"/>');
    },
    menu: function () {
      return moldura(titulo("Menu") + linha(58, null) + linha(94, null) + linha(130, "Central de Contas", { alvo: true }) + linha(166, null) + linha(202, null));
    },
    central: function () {
      return moldura(titulo("Central de Contas") + linha(58, null) +
        linha(94, "Suas informações e permissões", { alvo: true }) +
        '<text x="100" y="142" font-size="13" text-anchor="middle" font-family="sans-serif" font-weight="800" fill="#0369a1">↓</text>' +
        linha(150, "Exportar suas informações", { alvo: true }) + linha(194, null));
    },
    criar: function () {
      return moldura(titulo("Exportar informações") +
        '<rect x="16" y="58" width="168" height="54" rx="12" fill="#f1f5f9"/><circle cx="42" cy="85" r="14" fill="#e2e8f0"/>' + barra(66, 77, 80) + barra(66, 91, 50) +
        botao(138, "Criar exportação", true));
    },
    destino: function () {
      return moldura(titulo("Para onde exportar") +
        linha(62, "Exportar para dispositivo", { alvo: true }) +
        linha(112, "Exportar para serviço externo", { apagada: true }) +
        '<circle cx="182" cy="112" r="9" fill="#e11d48"/><text x="182" y="116" font-size="11" font-family="sans-serif" font-weight="800" text-anchor="middle" fill="#fff">✕</text>');
    },
    notificar: function () {
      return moldura(titulo("Exportar informações") +
        linha(62, "Notificar", { alvo: true, valor: "E-mail" }) +
        linha(102, "Personalizar informações") + linha(142, "Formato") + botao(190, "Iniciar exportação", false));
    },
    personalizar: function () {
      function opcao(y, marcada, texto) {
        return '<rect x="16" y="' + y + '" width="168" height="30" rx="10" fill="' + (marcada ? "#e0f2fe" : "#f1f5f9") + '"' + (marcada ? ' stroke="#0369a1" stroke-width="1.5"' : "") + '/>' +
          '<rect x="26" y="' + (y + 8) + '" width="14" height="14" rx="4" fill="' + (marcada ? "#0369a1" : "#fff") + '" stroke="' + (marcada ? "#0369a1" : "#cbd5e1") + '" stroke-width="1.5"/>' +
          (marcada ? '<path d="M29 ' + (y + 15.5) + ' l3 3 l5 -6" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>' : "") +
          (texto ? '<text x="48" y="' + (y + 19) + '" font-size="10" font-family="sans-serif" font-weight="700" fill="#0c4a6e">' + texto + '</text>' : barra(48, y + 12, 60)) +
          (marcada ? anel(16, y, 168, 30, 10) : "");
      }
      return moldura(titulo("Personalizar informações") + opcao(58, true, "Seguidores e seguindo") + opcao(94, false) + opcao(130, false) + botao(184, "Salvar", false));
    },
    formato: function () {
      function radio(y, marcada, texto) {
        return '<rect x="16" y="' + y + '" width="168" height="30" rx="10" fill="' + (marcada ? "#e0f2fe" : "#f1f5f9") + '"' + (marcada ? ' stroke="#0369a1" stroke-width="1.5"' : "") + '/>' +
          '<circle cx="33" cy="' + (y + 15) + '" r="7" fill="#fff" stroke="' + (marcada ? "#0369a1" : "#cbd5e1") + '" stroke-width="1.5"/>' +
          (marcada ? '<circle cx="33" cy="' + (y + 15) + '" r="3.5" fill="#0369a1"/>' : "") +
          '<text x="48" y="' + (y + 19) + '" font-size="10" font-family="sans-serif" font-weight="' + (marcada ? 700 : 500) + '" fill="' + (marcada ? "#0c4a6e" : "#64748b") + '">' + texto + '</text>' +
          (marcada ? anel(16, y, 168, 30, 10) : "");
      }
      return moldura(titulo("Formato") + radio(62, false, "HTML") + radio(102, true, "JSON") + botao(184, "Salvar", false));
    },
    iniciar: function () {
      return moldura(titulo("Exportar informações") +
        linha(62, "Notificar", { valor: "E-mail" }) + linha(102, "Personalizar informações") + linha(142, "Formato", { valor: "JSON" }) +
        botao(190, "Iniciar exportação", true));
    },
    email: function () {
      return moldura(
        '<rect x="30" y="78" width="140" height="94" rx="12" fill="#f0fdf4" stroke="#16a34a" stroke-width="3"/>' +
        '<path d="M34 86 L100 134 L166 86" fill="none" stroke="#16a34a" stroke-width="3" stroke-linejoin="round"/>' +
        '<circle cx="168" cy="78" r="13" fill="#16a34a"/><path d="M161 78 l5 5 l9 -10" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>' +
        barra(52, 196, 96));
    },
    baixar: function () {
      return moldura(
        '<circle cx="100" cy="92" r="44" fill="#f3e8ff"/>' +
        '<path d="M100 68 V104 M84 92 L100 108 L116 92" fill="none" stroke="#7e22ce" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>' +
        '<path d="M82 120 H118" stroke="#7e22ce" stroke-width="5" stroke-linecap="round"/>' +
        '<rect x="16" y="168" width="168" height="34" rx="11" fill="#f1f5f9"/>' +
        '<text x="28" y="189" font-size="10" font-family="sans-serif" font-weight="700" fill="#475569">instagram-….zip</text>');
    },
    compartilhar: function () {
      function app(x, nome, alvo) {
        return '<rect x="' + x + '" y="148" width="32" height="32" rx="9" fill="' + (alvo ? "#0369a1" : "#cbd5e1") + '"/>' +
          '<text x="' + (x + 16) + '" y="196" font-size="7.5" font-family="sans-serif" font-weight="' + (alvo ? 800 : 500) + '" text-anchor="middle" fill="' + (alvo ? "#0c4a6e" : "#94a3b8") + '">' + nome + '</text>' +
          (alvo ? anel(x, 148, 32, 32, 9) : "");
      }
      return moldura(
        '<rect x="16" y="34" width="168" height="40" rx="11" fill="#f1f5f9"/>' +
        '<text x="26" y="58" font-size="10" font-family="sans-serif" font-weight="700" fill="#475569">instagram-….zip</text>' +
        '<circle cx="170" cy="48" r="1.8" fill="#475569"/><circle cx="170" cy="54" r="1.8" fill="#475569"/><circle cx="170" cy="60" r="1.8" fill="#475569"/>' +
        '<text x="100" y="112" font-size="10" font-family="sans-serif" font-weight="800" text-anchor="middle" fill="#475569">Compartilhar</text>' +
        '<rect x="12" y="122" width="176" height="96" rx="16" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.5"/>' +
        app(22, "", false) + app(62, "", false) + app(102, "", false) + app(142, "Quem Saiu", true));
    },
    pc: function () {
      return '<svg viewBox="0 0 200 240" aria-hidden="true" focusable="false">' +
        '<rect x="8" y="46" width="184" height="128" rx="12" fill="#fff" stroke="#94a3b8" stroke-width="3"/>' +
        '<rect x="8" y="46" width="184" height="18" rx="12" fill="#e2e8f0"/><rect x="8" y="56" width="184" height="8" fill="#e2e8f0"/>' +
        '<circle cx="22" cy="55" r="3" fill="#cbd5e1"/><circle cx="33" cy="55" r="3" fill="#cbd5e1"/><circle cx="44" cy="55" r="3" fill="#cbd5e1"/>' +
        '<rect x="30" y="88" width="140" height="34" rx="11" fill="#0369a1"/>' +
        '<text x="100" y="109" font-size="11" font-family="sans-serif" font-weight="800" text-anchor="middle" fill="#fff">Ver a minha lista</text>' +
        anel(30, 88, 140, 34, 11) + barra(48, 142, 104) +
        '<path d="M70 174 L64 200 H136 L130 174" fill="#e2e8f0" stroke="#94a3b8" stroke-width="3" stroke-linejoin="round"/></svg>';
    }
  };
  var FASES = { pedir: "Pedir ao Instagram", esperar: "Esperar o e-mail", enviar: "Enviar para cá" };

  var todas = Array.prototype.slice.call(lista.children);
  var larga = window.matchMedia ? window.matchMedia("(min-width: 900px)") : null;
  var pos = 0;

  try {
    todas.forEach(function (li) {
      var f = DESENHOS[li.getAttribute("data-tela")];
      if (!f) return;
      var d = document.createElement("div");
      d.className = "etapa-desenho";
      d.innerHTML = f();
      li.insertBefore(d, li.firstChild);
    });

    var topo = document.createElement("div");
    topo.className = "passo-topo";
    var chip = document.createElement("span");
    chip.className = "passo-fase";
    var cont = document.createElement("span");
    cont.className = "passo-contagem";
    topo.appendChild(chip);
    topo.appendChild(cont);
    var trilha = document.createElement("div");
    trilha.className = "passo-trilha";
    trilha.setAttribute("role", "progressbar");
    trilha.setAttribute("aria-label", "Progresso do passo a passo");
    var fill = document.createElement("div");
    fill.className = "passo-trilha-fill";
    trilha.appendChild(fill);
    var nav = document.createElement("div");
    nav.className = "passo-nav";
    var voltar = document.createElement("button");
    voltar.type = "button";
    voltar.className = "passo-voltar";
    voltar.textContent = "Voltar";
    var prox = document.createElement("button");
    prox.type = "button";
    prox.className = "passo-proximo";
    nav.appendChild(voltar);
    nav.appendChild(prox);
    var aviso = document.createElement("p");
    aviso.className = "so-leitor";
    aviso.setAttribute("aria-live", "polite");

    corpo.insertBefore(topo, lista);
    corpo.insertBefore(trilha, lista);
    topo.appendChild(aviso);
    lista.parentNode.insertBefore(nav, lista.nextSibling);
    corpo.classList.add("com-passos");

    var visiveis = function () {
      var w = !!(larga && larga.matches);
      return todas.filter(function (li) {
        return !(li.classList.contains(w ? "so-celular" : "so-computador"));
      });
    };
    var mostrar = function (i, volta) {
      var v = visiveis();
      pos = Math.max(0, Math.min(i, v.length - 1));
      todas.forEach(function (li) { li.classList.remove("atual", "voltando"); });
      var li = v[pos];
      li.classList.add("atual");
      if (volta) li.classList.add("voltando");
      var fase = li.getAttribute("data-fase");
      corpo.setAttribute("data-fase", fase);
      chip.textContent = FASES[fase] || "";
      cont.textContent = "Passo " + (pos + 1) + " de " + v.length;
      fill.style.width = ((pos + 1) / v.length * 100) + "%";
      trilha.setAttribute("aria-valuemin", "1");
      trilha.setAttribute("aria-valuemax", String(v.length));
      trilha.setAttribute("aria-valuenow", String(pos + 1));
      voltar.hidden = pos === 0;
      prox.textContent = pos === v.length - 1 ? "Já tenho o arquivo" : "Próximo";
      var h = li.querySelector("h3");
      aviso.textContent = "Passo " + (pos + 1) + " de " + v.length + (h ? ": " + h.textContent : "");
    };

    voltar.addEventListener("click", function () { mostrar(pos - 1, true); });
    prox.addEventListener("click", function () {
      if (pos < visiveis().length - 1) { mostrar(pos + 1, false); return; }
      /* último passo: fecha o passo a passo e leva até o botão de escolher o arquivo */
      mostrar(0, false);
      document.getElementById("togglePasso").click();
      var b = document.getElementById("btnImportar");
      if (b) {
        b.scrollIntoView({ behavior: "smooth", block: "center" });
        try { b.focus({ preventScroll: true }); } catch (e) { b.focus(); }
      }
    });
    if (larga) {
      var aoMudar = function () { mostrar(pos, false); };
      if (larga.addEventListener) larga.addEventListener("change", aoMudar);
      else if (larga.addListener) larga.addListener(aoMudar);
    }
    mostrar(0, false);
  } catch (e) {
    /* se algo der errado, volta a mostrar a lista inteira, como no HTML */
    corpo.classList.remove("com-passos");
  }
})();

/* A Central de Ajuda fica escrita direto no index.html (<details>), para qualquer leitor, inclusive robôs, ver as respostas. */

/* ===== FERRAMENTA DE IMPORTAÇÃO ===== */
var CHAVE = "quemsaiu_exportacoes";
var CHAVE_IGNORADAS = "quemsaiu_ignoradas";

var memoria = {};
/* versão do formato das listas guardadas (campo "v"); se o formato mudar um dia, é por ela que se migra */
var VERSAO_DADOS = 1;
function soTextos(l) { return Array.isArray(l) && l.every(function (u) { return typeof u === "string"; }); }
/* só entra no app o que tem cara de lista guardada; qualquer outra coisa no armazenamento (dado antigo,
   de versão futura ou mexido à mão) é ignorada em vez de quebrar a página inteira */
function listaValida(x) {
  return !!x && typeof x === "object" && typeof x.data === "string" && soTextos(x.seguidores) &&
    (x.seguindo === undefined || soTextos(x.seguindo));
}
function lerDados() {
  if (memoria[CHAVE]) return memoria[CHAVE];
  try {
    var v = JSON.parse(localStorage.getItem(CHAVE));
    return Array.isArray(v) ? v.filter(listaValida) : [];
  } catch (e) { return []; }
}
/* devolve true se gravou no aparelho; false se só ficou na memória desta página */
function gravarDados(v) {
  try { localStorage.setItem(CHAVE, JSON.stringify(v)); delete memoria[CHAVE]; return true; }
  catch (e) { memoria[CHAVE] = v; return false; }
}
function apagarDadosLocais() {
  try { localStorage.removeItem(CHAVE); localStorage.removeItem(CHAVE_IGNORADAS); } catch (e) {}
  delete memoria[CHAVE];
  delete memoria[CHAVE_IGNORADAS];
}
function lerIgnoradas() {
  if (memoria[CHAVE_IGNORADAS]) return memoria[CHAVE_IGNORADAS];
  try {
    var v = JSON.parse(localStorage.getItem(CHAVE_IGNORADAS));
    return Array.isArray(v) ? v.filter(function (u) { return typeof u === "string"; }) : [];
  } catch (e) { return []; }
}
function gravarIgnoradas(v) {
  try { localStorage.setItem(CHAVE_IGNORADAS, JSON.stringify(v)); delete memoria[CHAVE_IGNORADAS]; }
  catch (e) { memoria[CHAVE_IGNORADAS] = v; }
}
function ignorarConta(u) {
  var a = lerIgnoradas();
  if (a.indexOf(u) === -1) { a.push(u); gravarIgnoradas(a); }
}
function restaurarIgnoradas() { gravarIgnoradas([]); }
function restaurarConta(u) {
  gravarIgnoradas(lerIgnoradas().filter(function (x) { return x !== u; }));
}
var painelEscondidasAberto = false;

var inputArquivo = document.getElementById("inputArquivo");
var btnImportar = document.getElementById("btnImportar");
var btnComparar = document.getElementById("btnComparar");
var erroImport = document.getElementById("erroImport");
var statusImport = document.getElementById("statusImport");
var cardResultado = document.getElementById("cardResultado");
var tituloResultado = document.getElementById("tituloResultado");
var abasResultado = document.getElementById("abasResultado");
var listaResultado = document.getElementById("listaResultado");

var abaAtual = "saiu";

function formatarData(iso) {
  return new Date(iso).toLocaleString("pt-BR", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}
var progresso = document.getElementById("progresso");
var progressoBarra = document.getElementById("progressoBarra");
var progressoTexto = document.getElementById("progressoTexto");

function mostrarProgresso(pct, texto) {
  if (!progresso) return;
  progresso.style.display = "block";
  progressoBarra.style.width = pct + "%";
  if (texto) progressoTexto.textContent = texto;
}
function esconderProgresso() {
  if (!progresso) return;
  progresso.style.display = "none";
  progressoBarra.style.width = "0%";
}

/* nomes de usuário vêm do arquivo do Instagram: nunca entram na tela como HTML cru */
function escapar(t) {
  return String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
/* erro com texto nosso (pode ter <b>); qualquer outro erro mostra uma mensagem padrão */
function erroAmigavel(html) { var e = new Error(html); e.amigavel = true; return e; }
function mostrarErro(msg) { erroImport.innerHTML = '<div class="aviso-erro">' + msg + "</div>"; }
function limparErro() { erroImport.innerHTML = ""; }
/* aviso que não é erro (ex.: "nada mudou"); só texto nosso, nunca nomes do arquivo sem escapar */
function mostrarAviso(msg) { erroImport.innerHTML = '<div class="aviso-erro aviso-info">' + msg + "</div>"; }

/* Hoje o Instagram entrega os seguidores como uma lista direta e quem você segue dentro de um
   objeto ({"relationships_following": [...]}). Se o formato mudar, é melhor parar com um aviso
   do que adivinhar e mostrar uma lista errada. */
var CHAVES_CONHECIDAS = ["relationships_following", "relationships_followers"];
function pareceItemDeConta(item) {
  return !!item && typeof item === "object" && (Array.isArray(item.string_list_data) || typeof item.title === "string");
}
function formatoDiferente(nome) {
  return erroAmigavel('O formato do arquivo <b>' + escapar(nome || "enviado") + '</b> é diferente do que o Quem Saiu espera (o Instagram pode ter mudado a exportação). Para não mostrar uma lista errada, a leitura foi interrompida. Escreva para o suporte contando o nome do arquivo.');
}

function extrairUsuarios(json, nome) {
  var itens = null;
  if (Array.isArray(json)) itens = json;
  else if (!json || typeof json !== "object") throw formatoDiferente(nome);
  else {
    /* só vale uma lista cujos itens parecem contas; se houver mais de uma, só a de nome conhecido */
    var candidatas = Object.keys(json).filter(function (k) {
      return Array.isArray(json[k]) && json[k].some(pareceItemDeConta);
    });
    if (candidatas.length === 1) itens = json[candidatas[0]];
    else if (candidatas.length > 1) {
      var conhecidas = candidatas.filter(function (k) { return CHAVES_CONHECIDAS.indexOf(k) !== -1; });
      if (conhecidas.length !== 1) throw formatoDiferente(nome);
      itens = json[conhecidas[0]];
    } else {
      /* nenhuma lista com cara de conta: só vale se for uma lista de nome conhecido (por exemplo, vazia,
         de quem não segue ninguém); qualquer outra coisa é formato desconhecido, não "lista vazia" */
      var vazias = CHAVES_CONHECIDAS.filter(function (k) { return Array.isArray(json[k]); });
      if (vazias.length !== 1) throw formatoDiferente(nome);
      itens = json[vazias[0]];
    }
  }
  var usuarios = [];
  itens.forEach(function (item) {
    var sld = item && item.string_list_data;
    if (Array.isArray(sld) && sld.length > 0) {
      sld.forEach(function (s) {
        if (!s) return;
        if (s.value) { usuarios.push(String(s.value)); return; }
        if (item.title) { usuarios.push(String(item.title)); return; }
        if (s.href) {
          var m = String(s.href).match(/instagram\.com\/(?:_u\/)?([A-Za-z0-9._]+)/);
          if (m) usuarios.push(m[1]);
        }
      });
    } else if (item && item.title) {
      usuarios.push(String(item.title));
    }
  });
  /* uma lista cheia que não rendeu nenhum nome, ou em que mais de 10% dos nomes não parecem usuários
     do Instagram (letras, números, ponto e sublinhado), é sinal de que a lista lida não é a de contas.
     Até 10% de nomes estranhos passam e aparecem como estão (nunca são descartados em silêncio,
     para não criar "saídas" ou "entradas" que não existem). */
  if (itens.length > 0 && usuarios.length === 0) throw formatoDiferente(nome);
  var validos = usuarios.filter(function (u) { return /^[A-Za-z0-9._]{1,30}$/.test(u); }).length;
  if (usuarios.length > 0 && validos < usuarios.length * 0.9) throw formatoDiferente(nome);
  return usuarios;
}

/* o Android renomeia downloads repetidos para "nome (1).json": também vale */
function ehArquivoSeguidores(n) { return /^followers(_\d+)?( \(\d+\))?\.json$/i.test(n); }
function ehArquivoSeguindo(n) { return /^following( \(\d+\))?\.json$/i.test(n); }

/* confere a assinatura do arquivo (ZIP começa com PK) */
async function pareceZip(arquivo) {
  try {
    var buf = new Uint8Array(await arquivo.slice(0, 4).arrayBuffer());
    return buf[0] === 0x50 && buf[1] === 0x4b && (buf[2] === 3 || buf[2] === 5 || buf[2] === 7);
  } catch (e) { return false; }
}

async function processarArquivos(arquivos) {
  var seguidores = [], seguindo = [], achouAlgo = false, temHtml = false, dataArquivo = null;

  /* misturar dois .zip, ou o mesmo arquivo duas vezes, juntaria listas de datas diferentes numa só e
     mostraria um resultado falso: só vale um .zip sozinho, ou arquivos .json de nomes diferentes */
  var tipos = [], zips = 0, vistos = new Set();
  for (var q = 0; q < arquivos.length; q++) {
    var nq = arquivos[q].name.toLowerCase();
    var zq = nq.endsWith(".zip") || (!nq.endsWith(".json") && await pareceZip(arquivos[q]));
    tipos.push(zq);
    if (zq) { zips++; continue; }
    var bq = nq.split("/").pop();
    var chaveq = bq.replace(/ \(\d+\)(?=\.json$)/, "");
    if (vistos.has(chaveq)) throw erroAmigavel('O arquivo <b>' + escapar(bq) + '</b> foi escolhido mais de uma vez. Escolha cada arquivo uma vez só.');
    vistos.add(chaveq);
  }
  if (zips > 1 || (zips === 1 && arquivos.length > 1)) {
    throw erroAmigavel('Escolha só <b>um arquivo .zip</b> por vez (o mais novo), sem outros arquivos junto. Com vários, listas de datas diferentes se misturam e o resultado fica errado.');
  }

  for (var a = 0; a < arquivos.length; a++) {
    var arquivo = arquivos[a];
    var nome = arquivo.name.toLowerCase();
    if (!dataArquivo) dataArquivo = dataNoNome(nome);
    var ehZip = tipos[a];

    if (ehZip) {
      mostrarProgresso(15, "Abrindo o arquivo…");
      if (typeof JSZip === "undefined") throw erroAmigavel('Não consegui carregar o leitor de arquivos .zip. Recarregue a página e tente de novo — ou escolha direto os arquivos <b>followers_1.json</b> e <b>following.json</b>.');
      var zip = await JSZip.loadAsync(arquivo);
      var entradas = Object.keys(zip.files);
      for (var e = 0; e < entradas.length; e++) {
        var caminho = entradas[e];
        var base = caminho.split("/").pop().toLowerCase();
        if (ehArquivoSeguidores(base)) {
          mostrarProgresso(45, "Lendo seus seguidores…");
          var t1 = await zip.files[caminho].async("string");
          seguidores = seguidores.concat(extrairUsuarios(JSON.parse(t1), base));
          achouAlgo = true;
        } else if (ehArquivoSeguindo(base)) {
          mostrarProgresso(75, "Lendo quem você segue…");
          var t2 = await zip.files[caminho].async("string");
          seguindo = seguindo.concat(extrairUsuarios(JSON.parse(t2), base));
          achouAlgo = true;
        } else if (/^followers.*\.html$|^following\.html$/i.test(base)) {
          temHtml = true;
        }
      }
    } else if (nome.endsWith(".json")) {
      var texto = await arquivo.text();
      var b = nome.split("/").pop();
      if (ehArquivoSeguidores(b)) {
        seguidores = seguidores.concat(extrairUsuarios(JSON.parse(texto), b));
        achouAlgo = true;
      } else if (ehArquivoSeguindo(b)) {
        seguindo = seguindo.concat(extrairUsuarios(JSON.parse(texto), b));
        achouAlgo = true;
      }
    }
  }

  if (!achouAlgo && temHtml) throw erroAmigavel("Esta exportação está em HTML. Refaça a exportação no Instagram escolhendo o formato JSON.");
  if (!achouAlgo) throw erroAmigavel('Não encontrei os dados de seguidores neste arquivo. Selecione o <b>.zip que você baixou do Instagram</b> — o nome começa com "instagram-". Se preferir, pode selecionar os arquivos "followers_1.json" e "following.json" de dentro dele.');

  if (seguidores.length === 0) throw erroAmigavel('Não encontrei a lista de <b>seguidores</b> (followers_1.json). Se você escolheu só o following.json, escolha também o followers_1.json — ou use o .zip inteiro. Confira se a exportação inclui "Seguidores e seguindo".');

  mostrarProgresso(95, "Organizando a sua lista…");

  function unicos(l) {
    var v = new Set();
    return l.filter(function (u) { if (v.has(u)) return false; v.add(u); return true; });
  }
  var nova = { v: VERSAO_DADOS, data: new Date().toISOString(), seguidores: unicos(seguidores), seguindo: unicos(seguindo) };
  if (dataArquivo) nova.dataArquivo = dataArquivo;
  return nova;
}

/* o .zip do Instagram costuma trazer a data no nome (instagram-usuario-2026-10-14-xxxx.zip);
   se não trouxer, simplesmente não há como conferir e nada é avisado */
function dataNoNome(nome) {
  var m = String(nome).match(/(20\d{2})-(\d{2})-(\d{2})/);
  if (!m) return null;
  var mes = Number(m[2]), dia = Number(m[3]);
  if (mes < 1 || mes > 12 || dia < 1 || dia > 31) return null;
  return m[1] + "-" + m[2] + "-" + m[3];
}
function dataBr(iso) { var p = iso.split("-"); return p[2] + "/" + p[1] + "/" + p[0]; }

/* confere a lista nova e guarda; devolve false se a pessoa desistir */
function mesmaLista(a, b) {
  if (!Array.isArray(a) || !Array.isArray(b) || a.length !== b.length) return false;
  var conj = new Set(a);
  return b.every(function (u) { return conj.has(u); });
}

function guardarNova(nova) {
  var dados = lerDados();
  var ultima = dados.length ? dados[dados.length - 1] : null;
  /* seguidores iguais aos da última lista (ex.: o mesmo arquivo importado duas vezes): não vira lista
     nova, senão a comparação passaria a ser dessa lista com ela mesma e a anterior de verdade
     deixaria de aparecer */
  if (ultima && mesmaLista(ultima.seguidores, nova.seguidores)) {
    var aviso = "Nada mudou nos seus seguidores desde a última lista guardada (ninguém saiu nem entrou), por isso esta não foi guardada de novo.";
    if (nova.seguindo.length > 0 && !mesmaLista(ultima.seguindo || [], nova.seguindo)) {
      ultima.seguindo = nova.seguindo;
      aviso += " A lista de quem você segue foi atualizada.";
      if (!gravarDados(dados)) aviso += " Não deu para gravar neste navegador: ela vale só até fechar esta página.";
    }
    mostrarAviso(aviso);
    return true;
  }
  if (ultima && ultima.dataArquivo && nova.dataArquivo && nova.dataArquivo < ultima.dataArquivo) {
    var okData = window.confirm("Este arquivo parece mais antigo (" + dataBr(nova.dataArquivo) + ") do que a última lista guardada (" + dataBr(ultima.dataArquivo) +
      "). Se você guardar assim, as saídas e as entradas aparecem trocadas.\n\nGuardar assim mesmo?");
    if (!okData) return false;
  }
  if (ultima && ultima.seguidores && ultima.seguidores.length >= 20 &&
      nova.seguidores.length < ultima.seguidores.length * 0.5) {
    var ok = window.confirm("Esta lista tem " + nova.seguidores.length + " seguidores e a anterior tinha " + ultima.seguidores.length +
      ". Pode ser um arquivo incompleto (por exemplo, faltando o followers_2.json).\n\nGuardar assim mesmo?");
    if (!ok) return false;
  }
  dados.push(nova);
  /* o navegador deixa guardar só uns 5 milhões de caracteres: se não couberem 10 listas,
     descarta as mais antigas, mas mantém sempre as 2 mais recentes (as que são comparadas) */
  var cheio = dados.slice(-10), cabe = cheio, gravou = false;
  while (true) {
    if (gravarDados(cabe)) { gravou = true; break; }
    if (cabe.length <= 2) break;
    cabe = cabe.slice(1);
  }
  if (!gravou) {
    memoria[CHAVE] = cheio;
    mostrarErro("Não consegui guardar a sua lista neste navegador (pode ser aba anônima, falta de espaço ou uma conta com muitos seguidores). Ela fica aqui só até você fechar esta página.");
  }
  return true;
}

function atualizarStatus() {
  var dados = lerDados();
  if (dados.length === 0) {
    statusImport.textContent = "Nenhuma lista guardada ainda.";
    btnComparar.disabled = true;
    return;
  }
  var u = dados[dados.length - 1];
  statusImport.textContent = dados.length + (dados.length === 1 ? " lista guardada" : " listas guardadas") +
    " · última: " + formatarData(u.data) + " (" + u.seguidores.length + " seguidores)" +
    (dados.length === 1 ? " · importe um arquivo mais novo para comparar" : "") +
    (memoria[CHAVE] ? " · só enquanto esta página estiver aberta" : "");
  btnComparar.disabled = dados.length < 2;
}
var PALETA_AVATAR = ["#0369a1","#c2410c","#047857","#7c3aed","#db2777","#b45309","#0f766e","#4f46e5","#dc2626","#4d7c0f"];
function corDoUsuario(u) {
  var s = 0;
  for (var i = 0; i < u.length; i++) s = (s + u.charCodeAt(i) * (i + 1)) % 9973;
  return PALETA_AVATAR[s % PALETA_AVATAR.length];
}

function seloPara(u, seguindoSet, tipo) {
  if (!seguindoSet || seguindoSet.size === 0) return "";
  if (tipo === "saiu") {
    return seguindoSet.has(u) ? '<span class="selo selo-segue">Você segue</span>' : '<span class="selo selo-nao-segue">Você não segue</span>';
  }
  if (tipo === "entrou") {
    return seguindoSet.has(u) ? '<span class="selo selo-segue-volta">Você segue de volta</span>' : '<span class="selo selo-nao-segue">Você não segue</span>';
  }
  return "";
}

function renderizarLista(usuarios, tipo, seguindoSet, textoVazio) {
  var ignoradas = lerIgnoradas();
  var visiveis = usuarios.filter(function (u) { return ignoradas.indexOf(u) === -1; });
  var escondidas = usuarios.length - visiveis.length;
  var podeIgnorar = true;

  var rodape = "";
  if (podeIgnorar && escondidas > 0) {
    var nomesEscondidos = usuarios.filter(function (u) { return ignoradas.indexOf(u) !== -1; });
    rodape = '<div class="rodape-lista">' +
      '<button class="link-escondidas" id="btnVerEscondidas">' + escondidas +
      (escondidas === 1 ? " conta escondida" : " contas escondidas") +
      (painelEscondidasAberto ? " ▲" : " ▼") + "</button>" +
      '<button class="link-restaurar" id="btnRestaurar">Mostrar todas</button></div>';
    if (painelEscondidasAberto) {
      rodape += '<div class="painel-escondidas">' + nomesEscondidos.map(function (u) {
        return '<div class="item-escondido">' +
          '<span class="avatar" style="background:' + corDoUsuario(u) + '">' + escapar(u.slice(0, 2).toUpperCase()) + "</span>" +
          '<span class="usuario-nome">@' + escapar(u) + "</span>" +
          '<button class="btn-restaurar-um" data-restaurar="' + escapar(u) + '">Restaurar</button></div>';
      }).join("") + "</div>";
    }
  }

  if (visiveis.length === 0) {
    /* se há contas escondidas, a lista não está vazia: está toda escondida */
    var msgVazio = escondidas > 0 ? "Todas as contas desta lista estão escondidas." : textoVazio;
    listaResultado.innerHTML = '<p style="text-align:center; font-size:12px; color:#475569; padding:14px 0;">' + msgVazio + "</p>" + rodape;
    ligarBotoesLista();
    return;
  }

  listaResultado.innerHTML = '<ul class="lista-usuarios">' + visiveis.map(function (u) {
    return '<li class="item-usuario item-' + tipo + '">' +
      '<span class="avatar" style="background:' + corDoUsuario(u) + '">' + escapar(u.slice(0, 2).toUpperCase()) + "</span>" +
      '<span class="usuario-nome"><a href="https://www.instagram.com/' + encodeURIComponent(u) + '/" target="_blank" rel="noopener noreferrer">@' + escapar(u) + "</a></span>" +
      seloPara(u, seguindoSet, tipo) +
      (podeIgnorar ? '<button class="btn-ignorar" data-ignorar="' + escapar(u) + '" title="Esconder esta conta da lista" aria-label="Esconder conta @' + escapar(u) + '">&times;</button>' : "") +
      "</li>";
  }).join("") + "</ul>" + rodape;

  ligarBotoesLista();
}

function ligarBotoesLista() {
  listaResultado.querySelectorAll("[data-ignorar]").forEach(function (b) {
    b.addEventListener("click", function () {
      var linha = b.closest("li");
      if (linha) linha.classList.add("saindo");
      setTimeout(function () { ignorarConta(b.dataset.ignorar); renderizarResultado(); }, 180);
    });
  });
  var btnRest = document.getElementById("btnRestaurar");
  if (btnRest) btnRest.addEventListener("click", function () {
    restaurarIgnoradas(); painelEscondidasAberto = false; renderizarResultado();
  });
  var btnVer = document.getElementById("btnVerEscondidas");
  if (btnVer) btnVer.addEventListener("click", function () {
    painelEscondidasAberto = !painelEscondidasAberto; renderizarResultado();
  });
  listaResultado.querySelectorAll("[data-restaurar]").forEach(function (b) {
    b.addEventListener("click", function () { restaurarConta(b.dataset.restaurar); renderizarResultado(); });
  });
}

function renderizarResultado() {
  var dados = lerDados();
  if (dados.length === 0) { cardResultado.style.display = "none"; return; }

  var atual = dados[dados.length - 1];
  var anterior = dados.length >= 2 ? dados[dados.length - 2] : null;
  var seguindoSet = new Set(atual.seguindo || []);
  var seguidoresSet = new Set(atual.seguidores || []);

  var anteriorSet = anterior ? new Set(anterior.seguidores) : null;
  var saiu = anterior ? anterior.seguidores.filter(function (u) { return !seguidoresSet.has(u); }) : [];
  var entrou = anterior ? atual.seguidores.filter(function (u) { return !anteriorSet.has(u); }) : [];
  var naoSeguemVolta = (atual.seguindo || []).filter(function (u) { return !seguidoresSet.has(u); });
  /* os números das abas contam só as contas que estão visíveis (as escondidas aparecem no rodapé da lista) */
  var escondidasSet = new Set(lerIgnoradas());
  function contarVisiveis(l) { return l.filter(function (u) { return !escondidasSet.has(u); }).length; }

  cardResultado.style.display = "block";

  var abas = [];
  if (anterior) {
    abas.push({ id: "saiu", rotulo: "Deixaram de te seguir · " + contarVisiveis(saiu), texto: "deixaram de te seguir", n: contarVisiveis(saiu) });
    abas.push({ id: "entrou", rotulo: "Começaram a te seguir · " + contarVisiveis(entrou), texto: "começaram a te seguir", n: contarVisiveis(entrou) });
  }
  if (seguindoSet.size > 0) {
    abas.push({ id: "naoSegue", rotulo: "Não te seguem de volta · " + contarVisiveis(naoSeguemVolta), texto: "não te seguem de volta", n: contarVisiveis(naoSeguemVolta) });
  }

  if (!anterior) {
    tituloResultado.textContent = "Sua lista está guardada";
    if (abaAtual === "saiu" || abaAtual === "entrou") abaAtual = "naoSegue";
  } else {
    tituloResultado.textContent = "Comparando " + formatarData(anterior.data) + " → " + formatarData(atual.data);
  }
  var existe = abas.some(function (x) { return x.id === abaAtual; });
  if (abas.length > 0 && !existe) abaAtual = abas[0].id;

  abasResultado.innerHTML = abas.map(function (x) {
    return '<button class="aba-res ' + x.id + (x.id === abaAtual ? " ativa" : "") + '" data-res="' + x.id + '" aria-pressed="' + (x.id === abaAtual) + '"><span class="bolha">' + x.n + '</span>' + x.texto + "</button>";
  }).join("");
  abasResultado.querySelectorAll("button").forEach(function (b) {
    b.addEventListener("click", function () { abaAtual = b.dataset.res; renderizarResultado(); });
  });

  if (abas.length === 0) {
    listaResultado.innerHTML = '<p style="text-align:center; font-size:12px; color:#475569; padding:14px 0;">Lista guardada. Quando notar mudança nos seguidores, peça um novo arquivo ao Instagram e traga aqui para comparar.</p>';
    return;
  }

  var aviso = document.getElementById("avisoLeitor");
  if (aviso) {
    var rotuloAtivo = "";
    abas.forEach(function (x) { if (x.id === abaAtual) rotuloAtivo = x.rotulo; });
    aviso.textContent = "Lista pronta. " + rotuloAtivo + ".";
  }

  var explicaAba = "";
  if (abaAtual === "saiu") {
    renderizarLista(saiu, "saiu", seguindoSet, "Ninguém deixou de te seguir entre as duas listas.");
    explicaAba = "Estavam na lista anterior e não estão na atual. O arquivo não diz o motivo: a pessoa pode ter deixado de seguir, desativado ou excluído a conta, ou trocado de nome de usuário (nesse caso o nome novo aparece em \"Começaram a te seguir\").";
  } else if (abaAtual === "entrou") {
    renderizarLista(entrou, "entrou", seguindoSet, "Nenhum seguidor novo entre as duas listas.");
    explicaAba = "Estão na lista atual e não estavam na anterior (pode ser uma conta nova ou alguém que trocou de nome de usuário).";
  } else {
    renderizarLista(naoSeguemVolta, "naoSegue", null, "Todo mundo que você segue também te segue.");
    explicaAba = "Quem você segue e não te segue de volta.";
    var dica = document.createElement("p");
    dica.style.cssText = "font-size:11px; color:#475569; margin:10px 0 0; line-height:1.5;";
    dica.innerHTML = 'Toque no nome para abrir o perfil. Se abrir uma página em branco, a conta não existe mais — use o <b>&times;</b> para escondê-la desta lista.';
    listaResultado.appendChild(dica);
  }
  listaResultado.insertAdjacentHTML("afterbegin", '<p class="explica-aba">' + explicaAba + "</p>");
}

btnImportar.addEventListener("click", function () { inputArquivo.click(); });

inputArquivo.addEventListener("change", async function () {
  limparErro();
  var arquivos = Array.prototype.slice.call(inputArquivo.files || []);
  if (arquivos.length === 0) return;
  btnImportar.disabled = true;
  btnImportar.textContent = "Lendo arquivo…";
  mostrarProgresso(5, "Abrindo o arquivo…");
  try {
    var nova = await processarArquivos(arquivos);
    if (!guardarNova(nova)) { esconderProgresso(); return; }
    mostrarProgresso(100, "Pronto!");
    atualizarStatus();
    renderizarResultado();
    setTimeout(esconderProgresso, 700);
  } catch (erro) {
    esconderProgresso();
    mostrarErro(erro && erro.amigavel ? erro.message : "Não consegui ler este arquivo. Confira se é a exportação do Instagram em formato JSON (não HTML).");
  } finally {
    btnImportar.disabled = false;
    btnImportar.textContent = "📄 Ver a minha lista";
    inputArquivo.value = "";
  }
});

btnComparar.addEventListener("click", function () { abaAtual = "saiu"; renderizarResultado(); });

document.getElementById("btnApagar").addEventListener("click", function () {
  if (!window.confirm("Apagar a sua lista e o histórico guardados neste aparelho? Depois não dá para voltar.")) return;
  apagarDadosLocais();
  if (window.caches) caches.delete("quemsaiu-compartilhado").catch(function () {});
  atualizarStatus();
  cardResultado.style.display = "none";
});

/* se já houver dados salvos, abre a ferramenta direto */
if (lerDados().length > 0) {
  document.getElementById("ferramenta").style.display = "block";
}
atualizarStatus();
renderizarResultado();

/* ===== PWA: instalação e recebimento por compartilhamento ===== */
if ("serviceWorker" in navigator) {
  window.addEventListener("load", function () {
    navigator.serviceWorker.register("service-worker.js").catch(function () {});
  });
}

/* ===== instalação do PWA: seção dedicada + faixa fixa + convite pós-resultado ===== */
var eventoInstalacao = null;
var secaoApp = document.getElementById("secaoApp");
var faixaApp = document.getElementById("faixaApp");
var espacoFaixa = document.getElementById("espacoFaixa");
var convitePos = document.getElementById("convitePos");
var faixaFechadaNestaLeitura = false;
var LIMITE_ROLAGEM_FAIXA = 320;

function estaInstalado() {
  return window.matchMedia && window.matchMedia("(display-mode: standalone)").matches;
}

function atualizarFaixaVisivel() {
  if (!faixaApp || !eventoInstalacao || estaInstalado()) return;
  var mostrar = window.scrollY > LIMITE_ROLAGEM_FAIXA && !faixaFechadaNestaLeitura;
  faixaApp.style.display = mostrar ? "flex" : "none";
  if (espacoFaixa) espacoFaixa.style.display = mostrar ? "block" : "none";
}

window.addEventListener("beforeinstallprompt", function (e) {
  e.preventDefault();
  eventoInstalacao = e;
  if (secaoApp) secaoApp.style.display = "block";
  if (convitePos) convitePos.style.display = "flex";
  window.addEventListener("scroll", atualizarFaixaVisivel);
  atualizarFaixaVisivel();
});

async function instalarApp() {
  if (!eventoInstalacao) return;
  eventoInstalacao.prompt();
  try { await eventoInstalacao.userChoice; } catch (e) {}
  eventoInstalacao = null;
}

["btnInstalar", "btnInstalarFaixa", "btnInstalarPos"].forEach(function (id) {
  var b = document.getElementById(id);
  if (b) b.addEventListener("click", instalarApp);
});

var btnDispensar = document.getElementById("btnDispensar");
if (btnDispensar) btnDispensar.addEventListener("click", function () {
  if (secaoApp) secaoApp.style.display = "none";
});

var btnDispensarPos = document.getElementById("btnDispensarPos");
if (btnDispensarPos) btnDispensarPos.addEventListener("click", function () {
  if (convitePos) convitePos.style.display = "none";
});

var btnFecharFaixa = document.getElementById("btnFecharFaixa");
if (btnFecharFaixa) btnFecharFaixa.addEventListener("click", function () {
  faixaFechadaNestaLeitura = true;
  atualizarFaixaVisivel();
});

/* ao voltar ao topo, a faixa pode aparecer de novo na próxima descida */
window.addEventListener("scroll", function () {
  if (window.scrollY < 40 && faixaFechadaNestaLeitura) faixaFechadaNestaLeitura = false;
});

window.addEventListener("appinstalled", function () {
  if (secaoApp) secaoApp.style.display = "none";
  if (faixaApp) faixaApp.style.display = "none";
  if (espacoFaixa) espacoFaixa.style.display = "none";
  if (convitePos) convitePos.style.display = "none";
  eventoInstalacao = null;
});

/* se o app foi aberto por compartilhamento, pega o arquivo e processa */
async function verificarArquivoCompartilhado() {
  var params = new URLSearchParams(location.search);
  var marca = params.get("compartilhado");
  if (!marca) {
    /* abriu sem ter vindo do Compartilhar: se sobrou uma cópia temporária de um envio que ninguém leu, apaga */
    if (window.caches) caches.delete("quemsaiu-compartilhado").catch(function () {});
    return;
  }

  history.replaceState(null, "", location.pathname);
  document.getElementById("ferramenta").style.display = "block";

  if (marca === "erro" || marca === "vazio") {
    mostrarErro("Não consegui receber o arquivo compartilhado. Tente pelo botão de importar.");
    return;
  }

  try {
    var cache = await caches.open("quemsaiu-compartilhado");
    var resposta = await cache.match("arquivo-compartilhado");
    if (!resposta) return;

    var nome = "instagram.zip";
    var cabecalho = resposta.headers.get("x-nome-arquivo");
    if (cabecalho) { try { nome = decodeURIComponent(cabecalho); } catch (e) {} }

    var blob = await resposta.blob();
    await cache.delete("arquivo-compartilhado");

    var arquivo = new File([blob], nome, { type: blob.type || "application/zip" });

    btnImportar.disabled = true;
    btnImportar.textContent = "Lendo arquivo…";
    mostrarProgresso(5, "Abrindo o arquivo…");
    try {
      var nova = await processarArquivos([arquivo]);
      if (!guardarNova(nova)) { esconderProgresso(); return; }
      mostrarProgresso(100, "Pronto!");
      atualizarStatus();
      renderizarResultado();
      setTimeout(esconderProgresso, 700);
    } catch (erro) {
      esconderProgresso();
      mostrarErro(erro && erro.amigavel ? erro.message : "Não consegui ler o arquivo compartilhado. Confira se é a exportação do Instagram em formato JSON (não HTML).");
    } finally {
      btnImportar.disabled = false;
      btnImportar.textContent = "📄 Ver a minha lista";
    }
  } catch (e) {
    mostrarErro("Não consegui abrir o arquivo compartilhado. Tente pelo botão de importar.");
  }
}
verificarArquivoCompartilhado();
