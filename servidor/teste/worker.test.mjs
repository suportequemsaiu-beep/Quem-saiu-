// Testes do servidor de avisos, sem internet e sem Cloudflare: banco D1 de mentira (node:sqlite) e fetch de mentira.
// Rodar:  node --test servidor/teste/
import test from "node:test";
import assert from "node:assert/strict";
import { DatabaseSync } from "node:sqlite";
import { readFileSync } from "node:fs";
import worker, { enderecoValido, fusoValido, dentroDaJanela, registrar, apagar, rodada, DEPOIS_DO_PEDIDO } from "../src/index.js";

const HORA = 3600 * 1000, DIA = 24 * HORA;
const SCHEMA = readFileSync(new URL("../schema.sql", import.meta.url), "utf8");

function bancoDeMentira() {
  const db = new DatabaseSync(":memory:");
  db.exec(SCHEMA);
  const preparar = (sql) => {
    const comando = db.prepare(sql);
    return {
      bind: (...args) => ({
        run: async () => { comando.run(...args); return { success: true }; },
        all: async () => ({ results: comando.all(...args) })
      })
    };
  };
  return { db, DB: { prepare: preparar } };
}

async function ambiente() {
  const par = await crypto.subtle.generateKey({ name: "ECDSA", namedCurve: "P-256" }, true, ["sign", "verify"]);
  const priv = await crypto.subtle.exportKey("jwk", par.privateKey);
  const pub = await crypto.subtle.exportKey("jwk", par.publicKey);
  const ponto = Buffer.concat([Buffer.from([4]), Buffer.from(pub.x, "base64url"), Buffer.from(pub.y, "base64url")]).toString("base64url");
  const { db, DB } = bancoDeMentira();
  return {
    db, pub,
    env: {
      DB, VAPID_PUBLICA: ponto, VAPID_PRIVADA_JWK: JSON.stringify({ kty: "EC", crv: "P-256", x: priv.x, y: priv.y, d: priv.d }),
      VAPID_CONTATO: "mailto:contato@exemplo.com", ORIGENS_PERMITIDAS: "https://quemsaiu.com.br,https://www.quemsaiu.com.br"
    }
  };
}

const ID = "123e4567-e89b-42d3-a456-426614174000";
const ENDERECO = "https://fcm.googleapis.com/fcm/send/abc123";
function pedidoPost(corpo, origem) {
  return new Request("https://avisos.exemplo.workers.dev/registrar", {
    method: "POST", headers: { "content-type": "application/json", ...(origem ? { origin: origem } : {}) }, body: JSON.stringify(corpo)
  });
}
function inserir(db, extra) {
  const l = Object.assign({ aparelho: ID, endpoint: ENDERECO, fuso: "America/Sao_Paulo", pedido_em: 0, estagio: 0, proximo_envio: 0, criado_em: 0 }, extra);
  db.prepare("INSERT INTO aparelhos (aparelho, endpoint, fuso, pedido_em, estagio, proximo_envio, criado_em) VALUES (?,?,?,?,?,?,?)")
    .run(l.aparelho, l.endpoint, l.fuso, l.pedido_em, l.estagio, l.proximo_envio, l.criado_em);
}
function simularEnvios(status) {
  const original = globalThis.fetch; const chamadas = [];
  globalThis.fetch = async (url, opcoes) => { chamadas.push({ url, opcoes }); return { status: typeof status === "function" ? status(url) : status }; };
  return { chamadas, restaurar: () => { globalThis.fetch = original; } };
}
/* 15h em Brasília (dentro da janela de 9h às 20h) */
const AGORA_NA_JANELA = Date.UTC(2026, 10, 10, 18, 0, 0);

test("só aceita endereços de aviso dos serviços conhecidos, por https", () => {
  assert.equal(enderecoValido(ENDERECO), true);
  assert.equal(enderecoValido("https://updates.push.services.mozilla.com/wpush/v2/xyz"), true);
  assert.equal(enderecoValido("http://fcm.googleapis.com/x"), false);
  assert.equal(enderecoValido("https://exemplo.com/x"), false);
  assert.equal(enderecoValido("https://fcm.googleapis.com.exemplo.com/x"), false);
  assert.equal(enderecoValido("https://fcm.googleapis.com:8443/x"), false);
  assert.equal(enderecoValido("https://u:p@fcm.googleapis.com/x"), false);
  assert.equal(enderecoValido(123), false);
});

test("valida fuso horário", () => {
  assert.equal(fusoValido("America/Sao_Paulo"), true);
  assert.equal(fusoValido("Marte/Olimpo"), false);
  assert.equal(fusoValido(null), false);
});

test("janela de 9h às 20h no fuso do aparelho", () => {
  const sp = "America/Sao_Paulo";
  assert.equal(dentroDaJanela(Date.UTC(2026, 10, 10, 11, 59), sp), false); /* 8h59 */
  assert.equal(dentroDaJanela(Date.UTC(2026, 10, 10, 12, 0), sp), true);   /* 9h00 */
  assert.equal(dentroDaJanela(Date.UTC(2026, 10, 10, 22, 59), sp), true);  /* 19h59 */
  assert.equal(dentroDaJanela(Date.UTC(2026, 10, 10, 23, 0), sp), false);  /* 20h00 */
  assert.equal(dentroDaJanela(Date.UTC(2026, 10, 10, 12, 0), "Asia/Tokyo"), false); /* 21h em Tóquio */
});

test("registrar guarda só o necessário e agenda o primeiro aviso", async () => {
  const { db, env } = await ambiente();
  const agora = AGORA_NA_JANELA;
  const r = await registrar(pedidoPost({ aparelho: ID, endpoint: ENDERECO, fuso: "America/Sao_Paulo", pedido_em: new Date(agora - 2 * HORA).toISOString() }), env, agora);
  assert.equal(r.status, 200);
  const linhas = db.prepare("SELECT * FROM aparelhos").all();
  assert.equal(linhas.length, 1);
  assert.deepEqual(Object.keys(linhas[0]).sort(), ["aparelho", "criado_em", "endpoint", "estagio", "fuso", "pedido_em", "proximo_envio"]);
  assert.equal(linhas[0].estagio, 0);
  assert.equal(linhas[0].proximo_envio, agora - 2 * HORA + DEPOIS_DO_PEDIDO[0]);
});

test("registrar de novo recomeça a contagem (mesmo aparelho, novo pedido)", async () => {
  const { db, env } = await ambiente();
  inserir(db, { estagio: 2, proximo_envio: 5 });
  const r = await registrar(pedidoPost({ aparelho: ID, endpoint: ENDERECO, fuso: "America/Sao_Paulo", pedido_em: new Date(AGORA_NA_JANELA).toISOString() }), env, AGORA_NA_JANELA);
  assert.equal(r.status, 200);
  const l = db.prepare("SELECT * FROM aparelhos").all();
  assert.equal(l.length, 1);
  assert.equal(l[0].estagio, 0);
});

test("registrar recusa dados inválidos", async () => {
  const { db, env } = await ambiente();
  const base = { aparelho: ID, endpoint: ENDERECO, fuso: "America/Sao_Paulo", pedido_em: new Date().toISOString() };
  for (const ruim of [{ aparelho: "x" }, { endpoint: "https://exemplo.com/a" }, { fuso: "Marte/Olimpo" }]) {
    const r = await registrar(pedidoPost({ ...base, ...ruim }), env, Date.now());
    assert.equal(r.status, 400);
  }
  const grande = await registrar(pedidoPost({ ...base, lixo: "x".repeat(3000) }), env, Date.now());
  assert.equal(grande.status, 400);
  const semJson = await registrar(new Request("https://a.b/registrar", { method: "POST", body: "isto não é json" }), env, Date.now());
  assert.equal(semJson.status, 400);
  assert.equal(db.prepare("SELECT COUNT(*) AS n FROM aparelhos").get().n, 0);
});

test("apagar remove o aparelho", async () => {
  const { db, env } = await ambiente();
  inserir(db, {});
  const r = await apagar(pedidoPost({ aparelho: ID }), env);
  assert.equal(r.status, 200);
  assert.equal(db.prepare("SELECT COUNT(*) AS n FROM aparelhos").get().n, 0);
});

test("origem não permitida é recusada; origem permitida recebe CORS", async () => {
  const { env } = await ambiente();
  const ruim = await worker.fetch(pedidoPost({}, "https://site-malvado.com"), env);
  assert.equal(ruim.status, 403);
  const pre = await worker.fetch(new Request("https://a.b/registrar", { method: "OPTIONS", headers: { origin: "https://quemsaiu.com.br" } }), env);
  assert.equal(pre.status, 204);
  assert.equal(pre.headers.get("access-control-allow-origin"), "https://quemsaiu.com.br");
  const outra = await worker.fetch(new Request("https://a.b/qualquer", { method: "GET" }), env);
  assert.equal(outra.status, 404);
});

test("rodada: envia aviso sem conteúdo, assinado com VAPID válido, e avança o estágio", async () => {
  const { db, env, pub } = await ambiente();
  const pedido = AGORA_NA_JANELA - 2 * DIA;
  inserir(db, { pedido_em: pedido, estagio: 0, proximo_envio: AGORA_NA_JANELA - HORA, criado_em: pedido });
  const sim = simularEnvios(201);
  try {
    const enviados = await rodada(env, AGORA_NA_JANELA);
    assert.equal(enviados, 1);
    assert.equal(sim.chamadas.length, 1);
    const { url, opcoes } = sim.chamadas[0];
    assert.equal(url, ENDERECO);
    assert.equal(opcoes.method, "POST");
    assert.equal(opcoes.body, undefined); /* nenhum conteúdo */
    const auth = opcoes.headers.authorization;
    const m = /^vapid t=([\w-]+)\.([\w-]+)\.([\w-]+), k=([\w-]+)$/.exec(auth);
    assert.ok(m, "cabeçalho vapid no formato certo");
    assert.equal(m[4], env.VAPID_PUBLICA);
    const corpo = JSON.parse(Buffer.from(m[2], "base64url").toString());
    assert.equal(corpo.aud, "https://fcm.googleapis.com");
    assert.equal(corpo.sub, "mailto:contato@exemplo.com");
    assert.ok(corpo.exp > AGORA_NA_JANELA / 1000 && corpo.exp <= AGORA_NA_JANELA / 1000 + 24 * 3600);
    const chavePublica = await crypto.subtle.importKey("jwk", pub, { name: "ECDSA", namedCurve: "P-256" }, false, ["verify"]);
    const valido = await crypto.subtle.verify({ name: "ECDSA", hash: "SHA-256" }, chavePublica, Buffer.from(m[3], "base64url"), new TextEncoder().encode(m[1] + "." + m[2]));
    assert.equal(valido, true, "assinatura ES256 confere");
    const l = db.prepare("SELECT * FROM aparelhos").get();
    assert.equal(l.estagio, 1);
    assert.ok(l.proximo_envio >= pedido + DEPOIS_DO_PEDIDO[1]);
  } finally { sim.restaurar(); }
});

test("rodada: fora da janela de horário não envia nada", async () => {
  const { db, env } = await ambiente();
  inserir(db, { proximo_envio: 1, criado_em: AGORA_NA_JANELA - DIA });
  const sim = simularEnvios(201);
  try {
    const madrugada = Date.UTC(2026, 10, 10, 6, 0); /* 3h em Brasília */
    assert.equal(await rodada(env, madrugada), 0);
    assert.equal(sim.chamadas.length, 0);
    assert.equal(db.prepare("SELECT estagio FROM aparelhos").get().estagio, 0);
  } finally { sim.restaurar(); }
});

test("rodada: endereço que o serviço diz que não existe mais (404/410) é apagado", async () => {
  for (const status of [404, 410]) {
    const { db, env } = await ambiente();
    inserir(db, { proximo_envio: 1, criado_em: AGORA_NA_JANELA - DIA });
    const sim = simularEnvios(status);
    try {
      await rodada(env, AGORA_NA_JANELA);
      assert.equal(db.prepare("SELECT COUNT(*) AS n FROM aparelhos").get().n, 0, "status " + status);
    } finally { sim.restaurar(); }
  }
});

test("rodada: erro temporário (429/500) mantém o registro para tentar de novo", async () => {
  for (const status of [429, 500]) {
    const { db, env } = await ambiente();
    inserir(db, { proximo_envio: 1, criado_em: AGORA_NA_JANELA - DIA });
    const sim = simularEnvios(status);
    try {
      assert.equal(await rodada(env, AGORA_NA_JANELA), 0);
      const l = db.prepare("SELECT * FROM aparelhos").get();
      assert.equal(l.estagio, 0);
      assert.equal(l.proximo_envio, 1);
    } finally { sim.restaurar(); }
  }
});

test("rodada: depois do último aviso o registro é apagado", async () => {
  const { db, env } = await ambiente();
  inserir(db, { estagio: DEPOIS_DO_PEDIDO.length - 1, proximo_envio: 1, criado_em: AGORA_NA_JANELA - DIA });
  const sim = simularEnvios(201);
  try {
    assert.equal(await rodada(env, AGORA_NA_JANELA), 1);
    assert.equal(db.prepare("SELECT COUNT(*) AS n FROM aparelhos").get().n, 0);
  } finally { sim.restaurar(); }
});

test("rodada: não envia antes da hora e apaga registros muito antigos", async () => {
  const { db, env } = await ambiente();
  inserir(db, { aparelho: "123e4567-e89b-42d3-a456-426614174001", proximo_envio: AGORA_NA_JANELA + DIA, criado_em: AGORA_NA_JANELA - DIA });
  inserir(db, { aparelho: "123e4567-e89b-42d3-a456-426614174002", proximo_envio: AGORA_NA_JANELA + DIA, criado_em: AGORA_NA_JANELA - 50 * DIA });
  const sim = simularEnvios(201);
  try {
    assert.equal(await rodada(env, AGORA_NA_JANELA), 0);
    assert.equal(sim.chamadas.length, 0);
    assert.deepEqual(db.prepare("SELECT aparelho FROM aparelhos").all().map((l) => l.aparelho), ["123e4567-e89b-42d3-a456-426614174001"]);
  } finally { sim.restaurar(); }
});

test("não escreve nada nos registros (logs)", async () => {
  const { db, env } = await ambiente();
  inserir(db, { proximo_envio: 1, criado_em: AGORA_NA_JANELA - DIA });
  const sim = simularEnvios(201);
  const escritas = [];
  const orig = { log: console.log, error: console.error, warn: console.warn, info: console.info };
  for (const k of Object.keys(orig)) console[k] = (...a) => escritas.push(a);
  try {
    await rodada(env, AGORA_NA_JANELA);
    await registrar(pedidoPost({ aparelho: "x" }), env, Date.now());
  } finally { Object.assign(console, orig); sim.restaurar(); }
  assert.deepEqual(escritas, []);
});

test("o esquema do banco não tem lugar para lista, e-mail ou usuário", () => {
  assert.ok(!/seguidor|email|e-mail|usuario|username|senha|lista/i.test(SCHEMA.replace(/--.*$/gm, "")));
});
