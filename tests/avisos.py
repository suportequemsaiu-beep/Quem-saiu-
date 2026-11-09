# Avisos no celular (Fase 1): tudo com servidor, permissão e inscrição de mentira (o navegador de teste não tem serviço de aviso).
import os, sys, tempfile, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixtures
from playwright.sync_api import sync_playwright
T = tempfile.mkdtemp(prefix="quemsaiu-") + "/"
Z = T + "z/"
fixtures.criar_zips(Z)
U = "http://127.0.0.1:8765/index.html"
SERVIDOR = "https://quemsaiu-avisos.suporte-quemsaiu.workers.dev"
falhas = 0
def ok(c, m):
    global falhas
    print(("OK    " if c else "FALHA ") + m)
    if not c: falhas += 1

MOCK = """
window.__QS_CONTAGEM_TESTE = true;
%s
window.__perm = 'granted'; window.__subs = 0; window.__unsubs = 0; window.__subOpts = null; window.__sub = null;
window.__permPedidos = 0; window.__permEspera = false; window.__resolverPerm = null;
(function () {
  var atual = 'default'; try { atual = sessionStorage.getItem('__permAtual') || 'default'; } catch (e) {}
  function fixar(v) { atual = v; try { sessionStorage.setItem('__permAtual', v); } catch (e) {} }
  Object.defineProperty(Notification, 'permission', { get: function () { return atual; }, configurable: true });
  Object.defineProperty(Notification, 'requestPermission', { value: function () {
    window.__permPedidos++;
    if (window.__permEspera && atual === 'default') return new Promise(function (res) { window.__resolverPerm = function () { fixar(window.__perm); res(window.__perm); }; });
    fixar(window.__perm); return Promise.resolve(window.__perm);
  }, configurable: true });
})();
function criarSub() {
  return { endpoint: 'https://fcm.googleapis.com/fcm/send/TESTE', unsubscribe: async function () { window.__unsubs++; window.__sub = null; try { sessionStorage.removeItem('__subAtiva'); } catch (e) {} return true; } };
}
PushManager.prototype.subscribe = async function (o) {
  window.__subOpts = { userVisibleOnly: o.userVisibleOnly, len: new Uint8Array(o.applicationServerKey).length, primeiro: new Uint8Array(o.applicationServerKey)[0] };
  window.__subs++;
  window.__sub = criarSub();
  try { sessionStorage.setItem('__subAtiva', '1'); } catch (e) {}
  return window.__sub;
};
/* o navegador de verdade guarda a inscrição entre aberturas do site; aqui isso é imitado com sessionStorage */
PushManager.prototype.getSubscription = async function () {
  if (!window.__sub && sessionStorage.getItem('__subAtiva') === '1') window.__sub = criarSub();
  return window.__sub;
};
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

def abrir_ferramenta(pg):
    pg.click("#btnDescobrir"); pg.wait_for_timeout(300)
    pg.click("#btnComecar"); pg.wait_for_timeout(300)

def garantir_guia(pg):
    if not pg.is_visible("#btnJaPedi"):
        pg.click("#togglePasso"); pg.wait_for_timeout(300)

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
    ok(ch["registrar"] == [] and ch["apagar"] == [] and "pediu.txt" not in ch["m"] and pg.evaluate("window.__permPedidos") == 0, "2 sem a chave ligada, nada é enviado ao servidor, nada é contado e a permissão não é pedida")
    ctx.close()

    # 3. fluxo normal: a permissão é pedida ao abrir o site e o aviso liga ao tocar em "Começar agora"
    ctx, ch = novo_contexto(br); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("dialog", lambda d: d.accept())
    pg.goto(U); pg.wait_for_timeout(500)
    ok(pg.evaluate("window.__permPedidos") == 1, "3 ao abrir o site o navegador é perguntado uma vez sobre notificações")
    ok(pg.evaluate("window.__subs") == 0 and ch["registrar"] == [] and pg.evaluate("localStorage.getItem('quemsaiu_aviso')") is None, "4 só abrir o site não liga nada: sem inscrição, sem servidor")
    abrir_ferramenta(pg); pg.wait_for_timeout(500)
    ok(pg.evaluate("window.__subs") == 1 and ch["registrar"] == [], "5 ao tocar em 'Começar agora' o aviso liga neste aparelho, sem falar com o servidor")
    guardado = json.loads(pg.evaluate("localStorage.getItem('quemsaiu_aviso')") or "{}")
    ok(list(guardado.keys()) == ["aparelho"], "6 no aparelho fica só o número do aparelho | %r" % list(guardado.keys()))
    ok(pg.is_visible("#btnDesligarAviso") and not pg.is_visible("#btnAtivarAviso") and "Aviso ligado" in pg.inner_text("#notaAviso") and "nunca a sua lista" in pg.inner_text("#notaAviso") and "até 4 vezes" in pg.inner_text("#notaAviso"), "7 mostra 'Aviso ligado', explica o que guarda e oferece desligar")
    abrir_guia(pg); pg.click("#btnJaPedi"); pg.wait_for_timeout(800)
    ok(len(ch["registrar"]) == 1, "8 só ao tocar em 'Já pedi' o servidor é avisado")
    r = ch["registrar"][0] if ch["registrar"] else {}
    ok(sorted(r.keys()) == ["aparelho", "endpoint", "fuso", "pedido_em"], "9 envia só aparelho, endpoint, fuso e data do pedido | %r" % sorted(r.keys()))
    ok(r.get("endpoint", "").startswith("https://fcm.googleapis.com/") and len(r.get("aparelho", "")) == 36 and "T" in r.get("pedido_em", ""), "10 valores no formato esperado")
    o = pg.evaluate("window.__subOpts") or {}
    ok(o.get("userVisibleOnly") is True and o.get("len") == 65 and o.get("primeiro") == 4, "11 inscrição pede aviso visível e usa a chave pública de 65 bytes | %r" % o)
    ok("aviso no celular" not in pg.inner_text("#jaPediFeito") and "volte aqui" in pg.inner_text("#jaPediFeito"), "12 depois de 'Já pedi' só aparece o 'Anotado… volte aqui'")
    ok(ch["m"].count("pediu.txt") == 1, "13 conta o evento anônimo 'pediu' uma vez | %r" % ch["m"])
    pg.reload(); pg.wait_for_timeout(600)
    ok(len(ch["registrar"]) == 1 and ch["m"].count("voltou.txt") == 1 and pg.evaluate("window.__permPedidos") == 0, "14 ao reabrir não registra de novo, não pergunta de novo e conta 'voltou' uma vez | %r" % ch["m"])

    # 15. desligar
    pg.click("#btnDesligarAviso"); pg.wait_for_timeout(800)
    ok(len(ch["apagar"]) == 1 and ch["apagar"][0] == {"aparelho": r.get("aparelho")}, "15 desligar apaga o registro no servidor")
    ok(pg.evaluate("localStorage.getItem('quemsaiu_aviso')") is None and pg.evaluate("window.__unsubs") == 1 and pg.is_visible("#btnAtivarAviso"), "16 desligar cancela a inscrição, apaga o número do aparelho e dá para ativar de novo")
    pg.reload(); pg.wait_for_timeout(600)
    ok(pg.evaluate("localStorage.getItem('quemsaiu_aviso')") is None and pg.evaluate("window.__subs") == 0 and pg.is_visible("#btnAtivarAviso"), "16b quem desligou o aviso não é ligado de novo sozinho ao reabrir")

    # 17. com o pedido já feito, ativar registra na hora
    pg.click("#btnAtivarAviso"); pg.wait_for_timeout(800)
    ok(len(ch["registrar"]) == 2 and pg.evaluate("localStorage.getItem('quemsaiu_aviso_desligado')") is None, "17 ativar com pedido já feito registra na hora e tira a marca de 'desligado'")

    # 18. mandar a lista para os lembretes, mas o aviso continua ligado para o próximo pedido
    pg.set_input_files("#inputArquivo", Z + "instagram-a-2026-10-01-x.zip"); pg.wait_for_timeout(1800)
    guardado = json.loads(pg.evaluate("localStorage.getItem('quemsaiu_aviso')") or "{}")
    ok(len(ch["apagar"]) == 2 and list(guardado.keys()) == ["aparelho"], "18 mandar a lista apaga o registro no servidor e mantém o aviso ligado | %r" % list(guardado.keys()))
    ok(pg.evaluate("localStorage.getItem('quemsaiu_pedido')") is None and ch["m"].count("mandou-lista.txt") == 1, "19 apaga o pedido e conta 'mandou lista'")

    # 20. novo pedido registra de novo; Desfazer apaga o registro e mantém o aviso
    garantir_guia(pg); pg.click("#btnJaPedi"); pg.wait_for_timeout(800)
    ok(len(ch["registrar"]) == 3, "20 um novo 'Já pedi' registra de novo")
    antes = len(ch["apagar"])
    pg.click("#btnDesfazerPedido"); pg.wait_for_timeout(800)
    guardado = json.loads(pg.evaluate("localStorage.getItem('quemsaiu_aviso')") or "{}")
    ok(len(ch["apagar"]) == antes + 1 and list(guardado.keys()) == ["aparelho"], "21 'Desfazer' apaga o registro no servidor e mantém o aviso ligado")

    # 22. Apagar meus dados desliga tudo
    garantir_guia(pg); pg.click("#btnJaPedi"); pg.wait_for_timeout(800)
    antes = len(ch["apagar"])
    pg.click("#btnApagar"); pg.wait_for_timeout(800)
    ok(len(ch["apagar"]) == antes + 1 and pg.evaluate("localStorage.getItem('quemsaiu_aviso')") is None, "22 'Apagar meus dados' desliga o aviso e apaga o registro")
    ok(pg.evaluate("localStorage.getItem('quemsaiu_aviso_desligado')") is None, "22b 'Apagar meus dados' também limpa a escolha de desligar")
    ok(errs == [], "23 sem erros de JS | %s" % errs)
    ctx.close()

    # 24. permissão negada ao abrir o site
    ctx, ch = novo_contexto(br); pg = ctx.new_page(); pg.add_init_script("window.__perm = 'denied'")
    pg.goto(U); pg.wait_for_timeout(500); abrir_ferramenta(pg); pg.wait_for_timeout(400)
    ok(pg.evaluate("window.__subs") == 0 and ch["registrar"] == [] and pg.evaluate("localStorage.getItem('quemsaiu_aviso')") is None, "24 permissão negada: o aviso não liga e nada vai ao servidor")
    pg.click("#btnAtivarAviso"); pg.wait_for_timeout(500)
    ok("Sem a permissão" in pg.inner_text("#notaAviso") and pg.is_visible("#btnAtivarAviso") and not pg.is_disabled("#btnAtivarAviso"), "25 permissão negada: o botão explica como liberar e continua disponível")
    ctx.close()

    # 25b. a pessoa ignorou o pedido do navegador: dá para ativar depois pelo botão
    ctx, ch = novo_contexto(br); pg = ctx.new_page(); pg.add_init_script("window.__perm = 'default'")
    pg.goto(U); pg.wait_for_timeout(500); abrir_ferramenta(pg); pg.wait_for_timeout(300)
    ok(pg.evaluate("window.__subs") == 0 and pg.is_visible("#btnAtivarAviso"), "25b pedido ignorado: nada liga sozinho e o botão aparece")
    pg.evaluate("window.__perm = 'granted'"); pg.click("#btnAtivarAviso"); pg.wait_for_timeout(600)
    ok(pg.evaluate("window.__subs") == 1 and pg.is_visible("#btnDesligarAviso"), "25c ao ativar pelo botão o aviso liga")
    ctx.close()

    # 25d. a permissão é dada só depois de tocar em Começar: liga na hora
    ctx, ch = novo_contexto(br); pg = ctx.new_page(); pg.add_init_script("window.__permEspera = true")
    pg.goto(U); pg.wait_for_timeout(500); abrir_ferramenta(pg); pg.wait_for_timeout(300)
    ok(pg.evaluate("window.__subs") == 0, "25d pedido ainda sem resposta: nada liga")
    pg.evaluate("window.__resolverPerm()"); pg.wait_for_timeout(800)
    ok(pg.evaluate("window.__subs") == 1 and pg.is_visible("#btnDesligarAviso"), "25e permissão dada depois de tocar em Começar: o aviso liga na hora")
    ctx.close()

    # 25f. a pessoa ignorou o pedido ao abrir o site: ao tocar em Começar pedimos de novo
    ctx, ch = novo_contexto(br); pg = ctx.new_page(); pg.add_init_script("window.__perm = 'default'")
    pg.goto(U); pg.wait_for_timeout(500)
    ok(pg.evaluate("window.__permPedidos") == 1, "25f ao abrir o site o pedido aparece uma vez")
    pg.evaluate("window.__perm = 'granted'")
    abrir_ferramenta(pg); pg.wait_for_timeout(700)
    ok(pg.evaluate("window.__permPedidos") >= 2 and pg.evaluate("window.__subs") == 1 and pg.is_visible("#btnDesligarAviso"), "25g pedido ignorado: ao tocar em 'Começar agora' pergunta de novo e, se permitir, o aviso liga")
    ctx.close()

    # 25h. a pessoa NEGOU: o navegador não deixa perguntar de novo, então só explicamos como liberar
    ctx, ch = novo_contexto(br); pg = ctx.new_page(); pg.add_init_script("window.__perm = 'denied'")
    pg.goto(U); pg.wait_for_timeout(500); abrir_ferramenta(pg); pg.wait_for_timeout(500)
    ok(pg.evaluate("window.__permPedidos") == 1 and "libere as notificações" in pg.inner_text("#notaAviso") and pg.evaluate("window.__subs") == 0, "25h permissão negada: não pergunta de novo ao tocar em 'Começar agora' e explica como liberar")
    ctx.close()

    # 25i. pedido ignorado de novo: não insiste mais de uma vez por visita
    ctx, ch = novo_contexto(br); pg = ctx.new_page(); pg.add_init_script("window.__perm = 'default'")
    pg.goto(U); pg.wait_for_timeout(500); abrir_ferramenta(pg); pg.wait_for_timeout(400)
    pg.click("#btnVoltarInicio") if pg.query_selector("#btnVoltarInicio") else None
    pg.evaluate("document.getElementById('btnComecar').click()"); pg.wait_for_timeout(400)
    ok(pg.evaluate("window.__permPedidos") == 2, "25i ignorou de novo: no máximo um pedido a mais por visita | %s" % pg.evaluate("window.__permPedidos"))
    ctx.close()

    # 26. servidor com erro ao religar o aviso já com pedido feito
    ctx, ch = novo_contexto(br); pg = ctx.new_page()
    pg.goto(U); pg.wait_for_timeout(500); abrir_guia(pg); pg.wait_for_timeout(300); pg.click("#btnJaPedi"); pg.wait_for_timeout(600)
    pg.click("#btnDesligarAviso"); pg.wait_for_timeout(600); ch["status"] = 500
    pg.click("#btnAtivarAviso"); pg.wait_for_timeout(800)
    ok("Não consegui ligar" in pg.inner_text("#notaAviso") and pg.evaluate("window.__unsubs") == 2 and pg.evaluate("localStorage.getItem('quemsaiu_aviso')") is None, "26 servidor com erro: avisa, desfaz a inscrição e não guarda nada")
    ok(pg.is_visible("#btnJaPedi") is False and pg.is_visible("#jaPediFeito"), "27 o 'Já pedi' continua valendo mesmo sem aviso")
    ctx.close()

    # 28. servidor fora do ar no 'Já pedi': tenta de novo na próxima vez que o site abrir
    ctx, ch = novo_contexto(br); pg = ctx.new_page()
    pg.goto(U); pg.wait_for_timeout(500); abrir_ferramenta(pg); pg.wait_for_timeout(800)
    ch["status"] = 500
    abrir_guia(pg); pg.click("#btnJaPedi"); pg.wait_for_timeout(800)
    ok(json.loads(pg.evaluate("localStorage.getItem('quemsaiu_aviso')")) == {"aparelho": json.loads(pg.evaluate("localStorage.getItem('quemsaiu_aviso')"))["aparelho"]} and pg.is_visible("#btnDesligarAviso"), "28 servidor fora do ar no 'Já pedi': o aviso continua ligado, ainda sem registro")
    ch["status"] = 200; pg.reload(); pg.wait_for_timeout(800)
    guardado = json.loads(pg.evaluate("localStorage.getItem('quemsaiu_aviso')") or "{}")
    ok("registrado" in guardado, "29 ao reabrir o site o registro é refeito sozinho | %r" % guardado)
    ctx.close()

    ctx, ch = novo_contexto(br); pg = ctx.new_page(); pg.goto(U); pg.wait_for_timeout(300)
    # 30-31. o service worker mostra o texto fixo e abre o site ao tocar
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
    ok(t == "Quem Saiu" and o["body"] == "Seu arquivo do Instagram pode estar pronto. Toque para mandar a lista." and o["tag"] == "quemsaiu-aviso", "30 o aviso tem o texto fixo e não depende de conteúdo do servidor | %r" % o["body"])
    ok(resultado["fechou"] == 1 and resultado["abertas"] == ["./?aviso=1"], "31 tocar no aviso fecha e abre o site | %r" % resultado["abertas"])
    ctx.close()

    # 32-36. modo de teste só neste aparelho: ?avisos=teste liga, ?avisos=desligar desliga
    ctx, ch = novo_contexto(br, com_flag=False); pg = ctx.new_page()
    pg.goto(U + "?avisos=teste"); pg.wait_for_timeout(400)
    ok("avisos=" not in pg.url, "32 o endereço secreto some da barra depois de usado | %s" % pg.url)
    abrir_ferramenta(pg)
    ok(pg.is_visible("#blocoAviso"), "33 com ?avisos=teste o bloco de aviso aparece neste aparelho")
    ok("pediu.txt" not in ch["m"], "34 no modo de teste o funil anônimo não é contado")
    pg.goto(U); pg.wait_for_timeout(400)
    ok(pg.evaluate("localStorage.getItem('quemsaiu_avisos_teste')") == "1", "35 o modo de teste continua ligado ao reabrir sem o parâmetro")
    pg.goto(U + "?avisos=desligar"); pg.wait_for_timeout(400)
    ok(pg.evaluate("localStorage.getItem('quemsaiu_avisos_teste')") is None, "36 ?avisos=desligar volta ao normal")
    ctx.close(); br.close()

print("OK=%d FALHAS=%d" % (0, falhas)); raise SystemExit(1 if falhas else 0)
