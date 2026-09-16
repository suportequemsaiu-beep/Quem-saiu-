/* ===== configuração ===== */
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
      { cor: "#6366f1", nome: "@adamsandler" },
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

/* ===== FAQ ===== */
var PERGUNTAS = [
  { q: "Como o Quem Saiu descobre quem deixou de me seguir?", a: "Comparando a sua lista de seguidores em dois momentos diferentes. Você importa sua lista uma primeira vez e, quando notar que o número de seguidores mudou, importa de novo. Quem estava na primeira lista e não está na segunda, saiu." },
  { q: "Preciso informar minha senha do Instagram?", a: "Não. O Quem Saiu nunca pede login nem senha." },
  { q: "Existe um app de unfollow do Instagram que não pede senha?", a: "Sim — o Quem Saiu nunca pede login ou senha. Aplicativos que exigem essas credenciais violam os Termos de Uso do Instagram, o que pode levar a penalidades na conta. O Quem Saiu usa só a exportação oficial de dados, um caminho que o próprio Instagram disponibiliza para qualquer usuário." },
  { q: "Meus dados ficam salvos em algum servidor?", a: "Não. Tudo fica guardado localmente no seu próprio navegador. Não existe backend, nem envio de dados para fora do seu aparelho." },
  { q: "Apareceu alguém que na verdade me segue. Por quê?", a: "A exportação do Instagram é um retrato do momento em que foi gerada e, de vez em quando, deixa alguém de fora da lista de seguidores. Nesses casos, use o × para esconder a conta da lista." },
  { q: "Aparecem contas que não existem mais. Dá para esconder?", a: "Sim. A exportação não informa quais contas foram desativadas ou excluídas, então o Quem Saiu não tem como saber sozinho. Toque no nome para conferir o perfil e, se ele não existir mais, use o × ao lado. Depois dá para revisar tudo em 'contas escondidas' e restaurar o que quiser." },
  { q: "Por que não aparecem as fotos de perfil?", a: "A exportação do Instagram traz apenas os nomes de usuário, sem fotos. Por isso mostramos as iniciais de cada conta, com uma cor fixa para ajudar a reconhecê-las." },
  { q: "O Instagram deu erro na hora de exportar. O que eu faço?", a: "Acontece — a Central de Contas do Instagram é instável às vezes. Toque em 'Recarregar página'; se não resolver, feche e refaça o caminho desde 'Exportar suas informações'; se ainda assim falhar, tente pelo navegador em accountscenter.instagram.com." },
  { q: "Escolhi o formato HTML em vez de JSON. E agora?", a: "Refaça a exportação escolhendo JSON no campo 'Formato'. O arquivo HTML não funciona para a comparação." },
  { q: "Por quanto tempo consigo baixar o arquivo?", a: "O Instagram avisa quando a exportação fica pronta, e o link para baixar fica disponível por 4 dias." },
  { q: "Como sei se eu ainda sigo quem deixou de me seguir?", a: "A exportação inclui também a sua lista de 'seguindo', então os resultados já mostram os selos 'Você segue' e 'Você não segue' em cada conta." },
  { q: "Existe versão para computador?", a: "Sim. Além de usar esta página no navegador do computador, existe uma extensão para o Chrome que captura a lista direto da página do Instagram." },
];
var faqLista = document.getElementById("faqLista");
PERGUNTAS.forEach(function (item) {
  var div = document.createElement("div");
  div.className = "faq-item";
  var btn = document.createElement("button");
  btn.className = "faq-q";
  btn.setAttribute("aria-expanded", "false");
  btn.innerHTML = item.q + "<span>+</span>";
  var resp = document.createElement("p");
  resp.className = "faq-a";
  resp.textContent = item.a;
  resp.style.display = "none";
  btn.addEventListener("click", function () {
    var aberto = resp.style.display !== "none";
    resp.style.display = aberto ? "none" : "block";
    btn.setAttribute("aria-expanded", aberto ? "false" : "true");
  });
  div.appendChild(btn);
  div.appendChild(resp);
  faqLista.appendChild(div);
});

/* ===== FERRAMENTA DE IMPORTAÇÃO ===== */
var CHAVE = "quemsaiu_exportacoes";
var CHAVE_IGNORADAS = "quemsaiu_ignoradas";

var memoria = {};
function lerDados() {
  try { return JSON.parse(localStorage.getItem(CHAVE)) || []; }
  catch (e) { return memoria[CHAVE] || []; }
}
function gravarDados(v) {
  try { localStorage.setItem(CHAVE, JSON.stringify(v)); }
  catch (e) { memoria[CHAVE] = v; }
}
function apagarDadosLocais() {
  try { localStorage.removeItem(CHAVE); localStorage.removeItem(CHAVE_IGNORADAS); } catch (e) {}
  delete memoria[CHAVE];
  delete memoria[CHAVE_IGNORADAS];
}
function lerIgnoradas() {
  try { return JSON.parse(localStorage.getItem(CHAVE_IGNORADAS)) || []; }
  catch (e) { return memoria[CHAVE_IGNORADAS] || []; }
}
function gravarIgnoradas(v) {
  try { localStorage.setItem(CHAVE_IGNORADAS, JSON.stringify(v)); }
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

function mostrarErro(msg) { erroImport.innerHTML = '<div class="aviso-erro">' + msg + "</div>"; }
function limparErro() { erroImport.innerHTML = ""; }

function extrairUsuarios(json) {
  var itens = null;
  if (Array.isArray(json)) itens = json;
  else if (json && typeof json === "object") {
    var chaves = Object.keys(json);
    for (var i = 0; i < chaves.length; i++) {
      if (Array.isArray(json[chaves[i]])) { itens = json[chaves[i]]; break; }
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
  var seguidores = [], seguindo = [], achouAlgo = false, temHtml = false;

  for (var a = 0; a < arquivos.length; a++) {
    var arquivo = arquivos[a];
    var nome = arquivo.name.toLowerCase();
    var ehZip = nome.endsWith(".zip") || (!nome.endsWith(".json") && await pareceZip(arquivo));

    if (ehZip) {
      mostrarProgresso(15, "Abrindo o arquivo…");
      var zip = await JSZip.loadAsync(arquivo);
      var entradas = Object.keys(zip.files);
      for (var e = 0; e < entradas.length; e++) {
        var caminho = entradas[e];
        var base = caminho.split("/").pop().toLowerCase();
        if (ehArquivoSeguidores(base)) {
          mostrarProgresso(45, "Lendo seus seguidores…");
          var t1 = await zip.files[caminho].async("string");
          seguidores = seguidores.concat(extrairUsuarios(JSON.parse(t1)));
          achouAlgo = true;
        } else if (ehArquivoSeguindo(base)) {
          mostrarProgresso(75, "Lendo quem você segue…");
          var t2 = await zip.files[caminho].async("string");
          seguindo = seguindo.concat(extrairUsuarios(JSON.parse(t2)));
          achouAlgo = true;
        } else if (/^followers.*\.html$|^following\.html$/i.test(base)) {
          temHtml = true;
        }
      }
    } else if (nome.endsWith(".json")) {
      var texto = await arquivo.text();
      var b = nome.split("/").pop();
      if (ehArquivoSeguidores(b)) {
        seguidores = seguidores.concat(extrairUsuarios(JSON.parse(texto)));
        achouAlgo = true;
      } else if (ehArquivoSeguindo(b)) {
        seguindo = seguindo.concat(extrairUsuarios(JSON.parse(texto)));
        achouAlgo = true;
      } else {
        var ex = extrairUsuarios(JSON.parse(texto));
        if (ex.length > 0) { seguidores = seguidores.concat(ex); achouAlgo = true; }
      }
    }
  }

  if (!achouAlgo && temHtml) throw new Error("Esta exportação está em HTML. Refaça a exportação no Instagram escolhendo o formato JSON.");
  if (!achouAlgo) throw new Error('Não encontrei os dados de seguidores neste arquivo. Selecione o <b>.zip que você baixou do Instagram</b> — o nome começa com "instagram-". Se preferir, pode selecionar os arquivos "followers_1.json" e "following.json" de dentro dele.');

  mostrarProgresso(95, "Organizando a sua lista…");

  function unicos(l) {
    var v = {};
    return l.filter(function (u) { if (v[u]) return false; v[u] = true; return true; });
  }
  return { data: new Date().toISOString(), seguidores: unicos(seguidores), seguindo: unicos(seguindo) };
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
    " · última: " + formatarData(u.data) + " (" + u.seguidores.length + " seguidores)";
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
  var podeIgnorar = tipo === "naoSegue";

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
          '<span class="avatar" style="background:' + corDoUsuario(u) + '">' + u.slice(0, 2).toUpperCase() + "</span>" +
          '<span class="usuario-nome">@' + u + "</span>" +
          '<button class="btn-restaurar-um" data-restaurar="' + u + '">Restaurar</button></div>';
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
      '<span class="avatar" style="background:' + corDoUsuario(u) + '">' + u.slice(0, 2).toUpperCase() + "</span>" +
      '<span class="usuario-nome"><a href="https://www.instagram.com/' + encodeURIComponent(u) + '/" target="_blank" rel="noopener">@' + u + "</a></span>" +
      seloPara(u, seguindoSet, tipo) +
      (podeIgnorar ? '<button class="btn-ignorar" data-ignorar="' + u + '" title="Esconder esta conta da lista" aria-label="Esconder conta @' + u + '">&times;</button>' : "") +
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

  var saiu = anterior ? anterior.seguidores.filter(function (u) { return !seguidoresSet.has(u); }) : [];
  var entrou = anterior ? atual.seguidores.filter(function (u) { return anterior.seguidores.indexOf(u) === -1; }) : [];
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

  if (abaAtual === "saiu") renderizarLista(saiu, "saiu", seguindoSet, "Ninguém deixou de te seguir entre as duas listas.");
  else if (abaAtual === "entrou") renderizarLista(entrou, "entrou", seguindoSet, "Nenhum seguidor novo entre as duas listas.");
  else {
    renderizarLista(naoSeguemVolta, "naoSegue", null, "Todo mundo que você segue também te segue.");
    var dica = document.createElement("p");
    dica.style.cssText = "font-size:11px; color:#475569; margin:10px 0 0; line-height:1.5;";
    dica.innerHTML = 'Toque no nome para abrir o perfil. Se abrir uma página em branco, a conta não existe mais — use o <b>&times;</b> para escondê-la desta lista.';
    listaResultado.appendChild(dica);
  }
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
    var dados = lerDados();
    dados.push(nova);
    gravarDados(dados.slice(-10));
    mostrarProgresso(100, "Pronto!");
    atualizarStatus();
    renderizarResultado();
    setTimeout(esconderProgresso, 700);
  } catch (erro) {
    esconderProgresso();
    mostrarErro(erro && erro.message ? erro.message : "Não consegui ler este arquivo. Confira se é a exportação do Instagram em JSON.");
  } finally {
    btnImportar.disabled = false;
    btnImportar.textContent = "📄 Ver a minha lista";
    inputArquivo.value = "";
  }
});

btnComparar.addEventListener("click", function () { abaAtual = "saiu"; renderizarResultado(); });

document.getElementById("btnApagar").addEventListener("click", function () {
  apagarDadosLocais();
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
      var dados = lerDados();
      dados.push(nova);
      gravarDados(dados.slice(-10));
      mostrarProgresso(100, "Pronto!");
      atualizarStatus();
      renderizarResultado();
      setTimeout(esconderProgresso, 700);
    } catch (erro) {
      esconderProgresso();
      mostrarErro(erro && erro.message ? erro.message : "Não consegui ler o arquivo compartilhado.");
    } finally {
      btnImportar.disabled = false;
      btnImportar.textContent = "📄 Ver a minha lista";
    }
  } catch (e) {
    mostrarErro("Não consegui abrir o arquivo compartilhado. Tente pelo botão de importar.");
  }
}
verificarArquivoCompartilhado();
