# Avisos no celular (Fase 1): tudo com servidor, permissão e inscrição de mentira (o navegador de teste não tem serviço de aviso).
import os, sys, tempfile, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixtures
from playwright.sync_api import sync_playwright
T = tempfile.mkdtemp(prefix="quemsaiu-") + "/"
Z = T + "z/"
fixtures.criar_zips(Z)
U = "http://127.0.0.1:8765/index.html"
SERVIDOR = "https://quemsaiu-avisos.cole-seu-subdominio.workers.dev"
falhas = 0
def ok(c, m):
    global falhas
    print(("OK    " if c else "FALHA ") + m)
    if not c: falhas += 1

MOCK = """
window.__QS_CONTAGEM_TESTE = true;
%s
window.__perm = 'granted'; window.__subs = 0; window.__unsubs = 0; window.__subOpts = null; window.__sub = null;
Object.defineProperty(Notification, 'requestPermission', { value: async function () { return window.__perm; }, configurable: true });
PushManager.prototype.subscribe = async function (o) {
  window.__subOpts = { userVisibleOnly: o.userVisibleOnly, len: new Uint8Array(o.applicationServerKey).length, primeiro: new Uint8Array(o.applicationServerKey)[0] };
  window.__subs++;
  window.__sub = { endpoint: 'https://fcm.googleapis.com/fcm/send/TESTE', unsubscribe: async function () { window.__unsubs++; window.__sub = null; return true; } };
  return window.__sub;
};
PushManager.prototype.getSubscription = async function () { return window.__sub; };
"""

def novo_contexto(br, com_flag=True):
    ctx = br.new_context(viewport={"width": 390, "height": 844})
    ctx.add_init_script(MOCK % ("window.__QS_AVISOS_TESTE = true;" if com_flag else ""))
    chamadas = {"registrar": [], "apagar": [], "m": [], "status": 200}
    def tratar(rota):
        req = rota.request
        cab = {"access-control-allow-origin": "*", "access-control-allow-headers": "content-type", "access-control-allow-methods": "POST, OPTIONS"}
        if req.method == "OPTIONS":
            return rota.fulfill(status=204, headers=cab)
        rotaNome = req.url.rsplit("/", 1)[-1]
        chamadas[rotaNome].append(json.loads(req.post_data or "{}"))
        rota.fulfill(status=chamadas["status"], headers=cab, content_type="application/json", body="{}")
    ctx.route(SERVIDOR + "/**", tratar)
    ctx.on("request", lambda r: chamadas["m"].append(r.url.rsplit("/", 1)[-1]) if "/m/" in r.url else None)
    return ctx, chamadas

def abrir_guia(pg):
    pg.click("#btnDescobrir"); pg.wait_for_timeout(300)
    pg.click("#btnComecar"); pg.wait_for_timeout(300)
    pg.click("#togglePasso"); pg.wait_for_timeout(300)

with sync_playwright() as p:
    br = p.chromium.launch()

    # 1. desligado por padrão: nada aparece e nada é chamado
    ctx, ch = novo_contexto(br, com_flag=False); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(U); pg.wait_for_timeout(300); abrir_guia(pg); pg.click("#btnJaPedi"); pg.wait_for_timeout(400)
    ok(not pg.is_visible("#blocoAviso"), "1 sem a chave ligada, o bloco de aviso não aparece")
    ok(ch["registrar"] == [] and ch["apagar"] == [] and "pediu.txt" not in ch["m"], "2 sem a chave ligada, nada é enviado ao servidor nem contado")
    ctx.close()

    # 3. fluxo normal
    ctx, ch = novo_contexto(br); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("dialog", lambda d: d.accept())
    pg.goto(U); pg.wait_for_timeout(300); abrir_guia(pg)
    ok(not pg.is_visible("#blocoAviso"), "3 antes do 'Já pedi' o bloco de aviso não aparece")
    pg.click("#btnJaPedi"); pg.wait_for_timeout(500)
    ok(pg.is_visible("#blocoAviso") and "nunca a sua lista" in pg.inner_text("#textoAviso") and "até 4 vezes" in pg.inner_text("#textoAviso"), "4 depois do 'Já pedi' explica o que guarda antes de pedir a permissão")
    ok(pg.evaluate("window.__subs") == 0 and ch["registrar"] == [], "5 só explicar não pede permissão nem registra")
    ok(ch["m"].count("pediu.txt") == 1, "6 conta o evento anônimo 'pediu' uma vez | %r" % ch["m"])
    pg.click("#btnAtivarAviso"); pg.wait_for_timeout(800)
    ok(len(ch["registrar"]) == 1, "7 ativar registra uma vez no servidor")
    r = ch["registrar"][0] if ch["registrar"] else {}
    ok(sorted(r.keys()) == ["aparelho", "endpoint", "fuso", "pedido_em"], "8 envia só aparelho, endpoint, fuso e data do pedido | %r" % sorted(r.keys()))
    ok(r.get("endpoint", "").startswith("https://fcm.googleapis.com/") and len(r.get("aparelho", "")) == 36 and "T" in r.get("pedido_em", ""), "9 valores no formato esperado")
    o = pg.evaluate("window.__subOpts") or {}
    ok(o.get("userVisibleOnly") is True and o.get("len") == 65 and o.get("primeiro") == 4, "10 inscrição pede aviso visível e usa a chave pública de 65 bytes | %r" % o)
    guardado = json.loads(pg.evaluate("localStorage.getItem('quemsaiu_aviso')") or "{}")
    ok(list(guardado.keys()) == ["aparelho"] and guardado.get("aparelho") == r.get("aparelho"), "11 no aparelho fica só o número do aparelho")
    ok(pg.is_visible("#btnDesligarAviso") and not pg.is_visible("#btnAtivarAviso") and "Aviso ligado" in pg.inner_text("#notaAviso"), "12 mostra 'Aviso ligado' e o botão de desligar")

    # 13. desligar
    pg.click("#btnDesligarAviso"); pg.wait_for_timeout(800)
    ok(len(ch["apagar"]) == 1 and ch["apagar"][0] == {"aparelho": r.get("aparelho")}, "13 desligar apaga o registro no servidor")
    ok(pg.evaluate("localStorage.getItem('quemsaiu_aviso')") is None and pg.evaluate("window.__unsubs") == 1, "14 desligar cancela a inscrição e apaga o número do aparelho")
    ok(pg.is_visible("#btnAtivarAviso"), "15 depois de desligar dá para ativar de novo")

    # 16. mandar a lista cancela os avisos
    pg.click("#btnAtivarAviso"); pg.wait_for_timeout(800)
    ok(len(ch["registrar"]) == 2, "16 ativar de novo registra")
    pg.reload(); pg.wait_for_timeout(500)
    ok(ch["m"].count("voltou.txt") == 1, "17 abrir o site com pedido conta 'voltou' uma vez | %r" % ch["m"])
    pg.set_input_files("#inputArquivo", Z + "instagram-a-2026-10-01-x.zip"); pg.wait_for_timeout(1800)
    ok(len(ch["apagar"]) == 2 and pg.evaluate("localStorage.getItem('quemsaiu_aviso')") is None, "18 mandar a lista cancela os avisos no servidor e no aparelho")
    ok(pg.evaluate("localStorage.getItem('quemsaiu_pedido')") is None and ch["m"].count("mandou-lista.txt") == 1, "19 apaga o pedido e conta 'mandou lista'")

    # 20. Desfazer cancela
    pg.click("#btnApagar"); pg.wait_for_timeout(500)
    abrir_guia(pg) if not pg.is_visible("#btnJaPedi") else None
    pg.click("#btnJaPedi"); pg.wait_for_timeout(400); pg.click("#btnAtivarAviso"); pg.wait_for_timeout(800)
    antes = len(ch["apagar"])
    pg.click("#btnDesfazerPedido"); pg.wait_for_timeout(800)
    ok(len(ch["apagar"]) == antes + 1 and pg.evaluate("localStorage.getItem('quemsaiu_aviso')") is None, "20 'Desfazer' também cancela o aviso")

    # 21. Apagar meus dados cancela (o botão só existe quando há lista guardada)
    pg.set_input_files("#inputArquivo", Z + "instagram-a-2026-10-01-x.zip"); pg.wait_for_timeout(1800)
    if not pg.is_visible("#btnJaPedi"): abrir_guia(pg)
    pg.click("#btnJaPedi"); pg.wait_for_timeout(400); pg.click("#btnAtivarAviso"); pg.wait_for_timeout(800)
    antes = len(ch["apagar"])
    pg.click("#btnApagar"); pg.wait_for_timeout(800)
    ok(len(ch["apagar"]) == antes + 1 and pg.evaluate("localStorage.getItem('quemsaiu_aviso')") is None, "21 'Apagar meus dados' também cancela o aviso")
    ok(errs == [], "22 sem erros de JS | %s" % errs)
    ctx.close()

    # 23. permissão negada
    ctx, ch = novo_contexto(br); pg = ctx.new_page()
    pg.goto(U); pg.wait_for_timeout(300); abrir_guia(pg); pg.click("#btnJaPedi"); pg.wait_for_timeout(300)
    pg.evaluate("window.__perm = 'denied'"); pg.click("#btnAtivarAviso"); pg.wait_for_timeout(600)
    ok("Sem a permissão" in pg.inner_text("#notaAviso") and ch["registrar"] == [] and pg.evaluate("window.__subs") == 0, "23 permissão negada: explica e não registra nada")
    ok(pg.evaluate("localStorage.getItem('quemsaiu_aviso')") is None and pg.is_visible("#btnAtivarAviso") and not pg.is_disabled("#btnAtivarAviso"), "24 permissão negada: nada fica guardado e o botão continua disponível")
    ctx.close()

    # 25. servidor com erro
    ctx, ch = novo_contexto(br); pg = ctx.new_page(); ch["status"] = 500
    pg.goto(U); pg.wait_for_timeout(300); abrir_guia(pg); pg.click("#btnJaPedi"); pg.wait_for_timeout(300)
    pg.click("#btnAtivarAviso"); pg.wait_for_timeout(800)
    ok("Não consegui ligar" in pg.inner_text("#notaAviso") and pg.evaluate("window.__unsubs") == 1 and pg.evaluate("localStorage.getItem('quemsaiu_aviso')") is None, "25 servidor com erro: avisa, desfaz a inscrição e não guarda nada")
    ok(pg.is_visible("#btnJaPedi") is False and pg.is_visible("#jaPediFeito"), "26 o 'Já pedi' continua valendo mesmo sem aviso")

    # 27. o service worker mostra o texto fixo e abre o site ao tocar
    resultado = pg.evaluate("""async () => {
      const texto = await (await fetch('service-worker.js')).text();
      const ouvintes = {}, mostradas = [], abertas = []; let fechou = 0;
      const eu = { addEventListener: (n, f) => { ouvintes[n] = f; },
        registration: { showNotification: async (t, o) => { mostradas.push([t, o]); } },
        clients: { matchAll: async () => [], openWindow: async (u) => { abertas.push(u); }, claim: async () => {} },
        skipWaiting() {} };
      new Function('self', texto)(eu);
      let esperou = [];
      ouvintes.push({ waitUntil: (p) => esperou.push(p), data: null });
      await Promise.all(esperou); esperou = [];
      ouvintes.notificationclick({ notification: { close: () => { fechou++; } }, waitUntil: (p) => esperou.push(p) });
      await Promise.all(esperou);
      return { mostradas, abertas, fechou };
    }""")
    t, o = resultado["mostradas"][0]
    ok(t == "Quem Saiu" and o["body"] == "Seu arquivo do Instagram pode estar pronto. Toque para mandar a lista." and o["tag"] == "quemsaiu-aviso", "27 o aviso tem o texto fixo e não depende de conteúdo do servidor | %r" % o["body"])
    ok(resultado["fechou"] == 1 and resultado["abertas"] == ["./?aviso=1"], "28 tocar no aviso fecha e abre o site | %r" % resultado["abertas"])
    ctx.close(); br.close()

print("OK=%d FALHAS=%d" % (0, falhas)); raise SystemExit(1 if falhas else 0)
