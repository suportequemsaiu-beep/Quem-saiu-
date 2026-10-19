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

/* A Central de Ajuda fica escrita direto no index.html (<details>), para qualquer leitor, inclusive robôs, ver as respostas. */

/* ===== FERRAMENTA DE IMPORTAÇÃO ===== */
var CHAVE = "quemsaiu_exportacoes";
var CHAVE_IGNORADAS = "quemsaiu_ignoradas";

var memoria = {};
function lerDados() {
  if (memoria[CHAVE]) return memoria[CHAVE];
  try { return JSON.parse(localStorage.getItem(CHAVE)) || []; }
  catch (e) { return []; }
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
  try { return JSON.parse(localStorage.getItem(CHAVE_IGNORADAS)) || []; }
  catch (e) { return []; }
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
  else if (json && typeof json === "object") {
    /* só vale uma lista cujos itens parecem contas; se houver mais de uma, só a de nome conhecido */
    var candidatas = Object.keys(json).filter(function (k) {
      return Array.isArray(json[k]) && json[k].some(pareceItemDeConta);
    });
    if (candidatas.length === 1) itens = json[candidatas[0]];
    else if (candidatas.length > 1) {
      var conhecidas = candidatas.filter(function (k) { return CHAVES_CONHECIDAS.indexOf(k) !== -1; });
      if (conhecidas.length !== 1) throw formatoDiferente(nome);
      itens = json[conhecidas[0]];
    }
  }
  if (!itens) return [];
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

function ehArquivoSeguidores(n) { return /^followers(_\d+)?\.json$/i.test(n); }
function ehArquivoSeguindo(n) { return /^following\.json$/i.test(n); }

/* confere a assinatura do arquivo (ZIP começa com PK) */
async function pareceZip(arquivo) {
  try {
    var buf = new Uint8Array(await arquivo.slice(0, 4).arrayBuffer());
    return buf[0] === 0x50 && buf[1] === 0x4b && (buf[2] === 3 || buf[2] === 5 || buf[2] === 7);
  } catch (e) { return false; }
}

async function processarArquivos(arquivos) {
  var seguidores = [], seguindo = [], achouAlgo = false, temHtml = false, dataArquivo = null;

  for (var a = 0; a < arquivos.length; a++) {
    var arquivo = arquivos[a];
    var nome = arquivo.name.toLowerCase();
    if (!dataArquivo) dataArquivo = dataNoNome(nome);
    var ehZip = nome.endsWith(".zip") || (!nome.endsWith(".json") && await pareceZip(arquivo));

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
  var nova = { data: new Date().toISOString(), seguidores: unicos(seguidores), seguindo: unicos(seguindo) };
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
function guardarNova(nova) {
  var dados = lerDados();
  var ultima = dados.length ? dados[dados.length - 1] : null;
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
    listaResultado.innerHTML = '<p style="text-align:center; font-size:12px; color:#475569; padding:14px 0;">' + textoVazio + "</p>" + rodape;
    ligarBotoesLista();
    return;
  }

  listaResultado.innerHTML = '<ul class="lista-usuarios">' + visiveis.map(function (u) {
    return '<li class="item-usuario item-' + tipo + '">' +
      '<span class="avatar" style="background:' + corDoUsuario(u) + '">' + escapar(u.slice(0, 2).toUpperCase()) + "</span>" +
      '<span class="usuario-nome"><a href="https://www.instagram.com/' + encodeURIComponent(u) + '/" target="_blank" rel="noopener">@' + escapar(u) + "</a></span>" +
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

  cardResultado.style.display = "block";

  var abas = [];
  if (anterior) {
    abas.push({ id: "saiu", rotulo: "Deixaram de te seguir · " + saiu.length, texto: "deixaram de te seguir", n: saiu.length });
    abas.push({ id: "entrou", rotulo: "Começaram a te seguir · " + entrou.length, texto: "começaram a te seguir", n: entrou.length });
  }
  if (seguindoSet.size > 0) {
    abas.push({ id: "naoSegue", rotulo: "Não te seguem de volta · " + naoSeguemVolta.length, texto: "não te seguem de volta", n: naoSeguemVolta.length });
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
    explicaAba = "Estavam na lista anterior e não estão na atual. O arquivo não diz o motivo: a pessoa pode ter deixado de seguir ou desativado ou excluído a conta.";
  } else if (abaAtual === "entrou") {
    renderizarLista(entrou, "entrou", seguindoSet, "Nenhum seguidor novo entre as duas listas.");
    explicaAba = "Estão na lista atual e não estavam na anterior.";
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
  if (!marca) return;

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
