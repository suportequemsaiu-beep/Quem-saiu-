/* Quem Saiu — servidor de avisos (Fase 1).
   Cloudflare Worker + banco D1 + Web Push (VAPID).

   O QUE FAZ
   - Guarda, para cada aparelho que ativou os avisos: um número aleatório, o endereço do aviso, o fuso
     e a data do "Já pedi". Nada mais.
   - A cada 30 minutos manda um aviso SEM TEXTO NENHUM DENTRO (o texto fixo "Seu arquivo do Instagram
     pode estar pronto" está no service-worker.js do site). Avisos: +24h, +72h, +7d e +14d depois do
     pedido, só entre 9h e 20h no fuso do aparelho. Depois do último, apaga o registro.

   O QUE NUNCA GUARDA
   - Lista de seguidores, arquivos, e-mails, senha ou nome de usuário do Instagram. Não escreve nos
     registros (logs) nenhum dado recebido. */

const HORA = 3600 * 1000;
const DIA = 24 * HORA;
/* quanto tempo depois do pedido sai cada aviso */
export const DEPOIS_DO_PEDIDO = [1 * DIA, 3 * DIA, 7 * DIA, 14 * DIA];
export const JANELA = { inicio: 9, fim: 20 }; /* horas locais: 9h até 19h59 */
const LIMITE_POR_RODADA = 40; /* o plano grátis limita pedidos e tempo por execução */
const GUARDAR_NO_MAXIMO = 45 * DIA;

/* só aceitamos endereços de aviso dos serviços conhecidos (evita usar o servidor para chamar sites quaisquer) */
const SERVICOS_ACEITOS = /(^|\.)(googleapis\.com|push\.services\.mozilla\.com|push\.apple\.com|notify\.windows\.com)$/;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

export function enderecoValido(texto) {
  try {
    if (typeof texto !== "string" || texto.length > 1000) return false;
    var u = new URL(texto);
    return u.protocol === "https:" && !u.username && !u.password && !u.port && SERVICOS_ACEITOS.test(u.hostname);
  } catch (e) { return false; }
}

export function fusoValido(fuso) {
  try { if (typeof fuso !== "string" || fuso.length > 64) return false; new Intl.DateTimeFormat("en-GB", { timeZone: fuso }); return true; }
  catch (e) { return false; }
}

export function horaLocal(agoraMs, fuso) {
  var h = new Intl.DateTimeFormat("en-GB", { timeZone: fuso, hour: "numeric", hourCycle: "h23" }).format(new Date(agoraMs));
  return parseInt(h, 10);
}

export function dentroDaJanela(agoraMs, fuso) {
  var h = horaLocal(agoraMs, fuso);
  return h >= JANELA.inicio && h < JANELA.fim;
}

/* quando sai o aviso número `estagio` (0 = primeiro), nunca antes de `minimo` */
export function proximoEnvio(pedidoEm, estagio, agoraMs) {
  return Math.max(pedidoEm + DEPOIS_DO_PEDIDO[estagio], agoraMs + 6 * HORA * (estagio > 0 ? 1 : 0));
}

/* ---------- respostas e CORS ---------- */
function origensPermitidas(env) {
  return String(env.ORIGENS_PERMITIDAS || "").split(",").map(function (s) { return s.trim(); }).filter(Boolean);
}
function cabecalhos(req, env) {
  var h = { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" };
  var origem = req.headers.get("origin");
  if (origem && origensPermitidas(env).indexOf(origem) !== -1) {
    h["access-control-allow-origin"] = origem;
    h["access-control-allow-methods"] = "POST, OPTIONS";
    h["access-control-allow-headers"] = "content-type";
    h["access-control-max-age"] = "86400";
    h["vary"] = "origin";
  }
  return h;
}
function resposta(req, env, status, corpo) {
  return new Response(JSON.stringify(corpo || {}), { status: status, headers: cabecalhos(req, env) });
}

async function lerJson(req) {
  var texto = await req.text();
  if (texto.length > 2048) throw new Error("grande");
  return JSON.parse(texto);
}

/* ---------- rotas ---------- */
export async function registrar(req, env, agora) {
  var d;
  try { d = await lerJson(req); } catch (e) { return resposta(req, env, 400, { erro: "pedido invalido" }); }
  if (!d || !UUID.test(String(d.aparelho)) || !enderecoValido(d.endpoint) || !fusoValido(d.fuso)) {
    return resposta(req, env, 400, { erro: "dados invalidos" });
  }
  var pedido = Date.parse(d.pedido_em);
  if (!(pedido > agora - 10 * DIA) || pedido > agora + 5 * 60 * 1000) pedido = agora;
  var primeiro = Math.max(pedido + DEPOIS_DO_PEDIDO[0], agora + HORA);
  await env.DB.prepare(
    "INSERT INTO aparelhos (aparelho, endpoint, fuso, pedido_em, estagio, proximo_envio, criado_em) VALUES (?1, ?2, ?3, ?4, 0, ?5, ?6) " +
    "ON CONFLICT(aparelho) DO UPDATE SET endpoint=?2, fuso=?3, pedido_em=?4, estagio=0, proximo_envio=?5"
  ).bind(d.aparelho, d.endpoint, d.fuso, pedido, primeiro, agora).run();
  return resposta(req, env, 200, { ok: true });
}

export async function apagar(req, env) {
  var d;
  try { d = await lerJson(req); } catch (e) { return resposta(req, env, 400, { erro: "pedido invalido" }); }
  if (!d || !UUID.test(String(d.aparelho))) return resposta(req, env, 400, { erro: "dados invalidos" });
  await env.DB.prepare("DELETE FROM aparelhos WHERE aparelho = ?1").bind(d.aparelho).run();
  return resposta(req, env, 200, { ok: true });
}

/* ---------- envio do aviso (Web Push sem conteúdo, assinado com VAPID) ---------- */
function base64url(bytes) {
  var s = ""; var b = new Uint8Array(bytes);
  for (var i = 0; i < b.length; i++) s += String.fromCharCode(b[i]);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function textoBase64url(t) { return base64url(new TextEncoder().encode(t)); }

export async function assinarVapid(env, audiencia, agoraMs) {
  var chave = await crypto.subtle.importKey("jwk", JSON.parse(env.VAPID_PRIVADA_JWK), { name: "ECDSA", namedCurve: "P-256" }, false, ["sign"]);
  var cabecalho = textoBase64url(JSON.stringify({ typ: "JWT", alg: "ES256" }));
  var corpo = textoBase64url(JSON.stringify({ aud: audiencia, exp: Math.floor(agoraMs / 1000) + 12 * 3600, sub: env.VAPID_CONTATO }));
  var assinatura = await crypto.subtle.sign({ name: "ECDSA", hash: "SHA-256" }, chave, new TextEncoder().encode(cabecalho + "." + corpo));
  return cabecalho + "." + corpo + "." + base64url(assinatura);
}

export async function enviarAviso(env, endpoint, cacheJwt, agoraMs) {
  var audiencia = new URL(endpoint).origin;
  if (!cacheJwt[audiencia]) cacheJwt[audiencia] = await assinarVapid(env, audiencia, agoraMs);
  var r = await fetch(endpoint, {
    method: "POST",
    headers: { authorization: "vapid t=" + cacheJwt[audiencia] + ", k=" + env.VAPID_PUBLICA, ttl: String(12 * 3600), urgency: "normal", "content-length": "0" }
  });
  return r.status;
}

/* ---------- a cada 30 minutos ---------- */
export async function rodada(env, agora) {
  await env.DB.prepare("DELETE FROM aparelhos WHERE criado_em < ?1").bind(agora - GUARDAR_NO_MAXIMO).run();
  var lista = await env.DB.prepare(
    "SELECT aparelho, endpoint, fuso, pedido_em, estagio FROM aparelhos WHERE proximo_envio <= ?1 ORDER BY proximo_envio LIMIT ?2"
  ).bind(agora, LIMITE_POR_RODADA).all();
  var cache = {}; var enviados = 0;
  for (var linha of lista.results) {
    if (!dentroDaJanela(agora, linha.fuso)) continue; /* fora do horário: fica para a próxima janela */
    var status;
    try { status = await enviarAviso(env, linha.endpoint, cache, agora); } catch (e) { continue; }
    if (status === 404 || status === 410) {
      await env.DB.prepare("DELETE FROM aparelhos WHERE aparelho = ?1").bind(linha.aparelho).run();
    } else if (status >= 200 && status < 300) {
      enviados += 1;
      var novo = linha.estagio + 1;
      if (novo >= DEPOIS_DO_PEDIDO.length) {
        await env.DB.prepare("DELETE FROM aparelhos WHERE aparelho = ?1").bind(linha.aparelho).run();
      } else {
        await env.DB.prepare("UPDATE aparelhos SET estagio = ?2, proximo_envio = ?3 WHERE aparelho = ?1")
          .bind(linha.aparelho, novo, proximoEnvio(linha.pedido_em, novo, agora)).run();
      }
    } /* outros erros (429, 5xx): tenta de novo na próxima rodada */
  }
  return enviados;
}

export default {
  async fetch(req, env) {
    var url = new URL(req.url);
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cabecalhos(req, env) });
    var origem = req.headers.get("origin");
    if (req.method === "POST" && origem && origensPermitidas(env).indexOf(origem) === -1) return resposta(req, env, 403, { erro: "origem nao permitida" });
    if (req.method === "POST" && url.pathname === "/registrar") return registrar(req, env, Date.now());
    if (req.method === "POST" && url.pathname === "/apagar") return apagar(req, env);
    if (req.method === "GET" && url.pathname === "/saude") return resposta(req, env, 200, { ok: true });
    return resposta(req, env, 404, { erro: "nao encontrado" });
  },
  async scheduled(evento, env, ctx) {
    ctx.waitUntil(rodada(env, Date.now()));
  }
};
