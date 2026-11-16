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


def chegar_em_ja_pedi(pg):
    """abre o passo a passo e avança até o passo em que o 'Já pedi' aparece"""
    if not pg.is_visible("#corpoPasso"):
        pg.click("#togglePasso"); pg.wait_for_timeout(300)
    for _ in range(12):
        if pg.is_visible("#btnJaPedi") or pg.is_visible("#jaPediFeito"): break
        pg.click(".passo-proximo"); pg.wait_for_timeout(120)

def garantir_guia(pg):
    if not pg.is_visible("#btnJaPedi") and not pg.is_visible("#jaPediFeito"):
        chegar_em_ja_pedi(pg)

def abrir_guia(pg):
    pg.click("#btnDescobrir"); pg.wait_for_timeout(300)
    pg.click("#btnComecar"); pg.wait_for_timeout(300)
    chegar_em_ja_pedi(pg)

with sync_playwright() as p:
    br = p.chromium.launch()

    # 1. desligado por padrão: nada aparece e nada é chamado
    ctx, ch = novo_contexto(br, com_flag=False); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(U); pg.wait_for_timeout(300); abrir_guia(pg); pg.click("#btnJaPedi"); pg.wait_for_timeout(400)
    ok(not pg.is_visible("#blocoAviso"), "1 sem a chave ligada, o bloco de aviso não aparece")
    ok(ch["registrar"] == [] and ch["apagar"] == [] and "pediu.txt" not in ch["m"] and pg.evaluate("window.__permPedidos") == 0, "2 sem a chave ligada, nada é enviado ao servidor, nada é contado e a permissão não é pedida")
    ctx.close()

    # 3. fluxo normal: nada é pedido ao abrir nem ao tocar em "Começar agora"; o aviso é oferecido depois de "Já pedi"
    ctx, ch = novo_contexto(br); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("dialog", lambda d: d.accept())
    pg.goto(U); pg.wait_for_timeout(500)
    ok(pg.evaluate("window.__permPedidos") == 0, "3 ao abrir o site o navegador NÃO é perguntado sobre notificações")
    abrir_ferramenta(pg); pg.wait_for_timeout(400)
    ok(pg.evaluate("window.__permPedidos") == 0 and not pg.is_visible("#blocoAviso") and pg.evaluate("window.__subs") == 0, "4 em 'Sua lista' não aparece oferta de aviso e nada é pedido")
    pg.click("#togglePasso"); pg.wait_for_timeout(300)
    ok(not pg.is_visible("#btnJaPedi"), "4a no primeiro passo ainda não existe o botão 'Já pedi'")
    chegar_em_ja_pedi(pg)
    ok(not pg.is_visible("#blocoAviso"), "4b com os passos abertos, antes de 'Já pedi', o aviso ainda não aparece")
    pg.click("#btnJaPedi"); pg.wait_for_timeout(500)
    ok(pg.is_visible("#blocoAviso") and pg.is_visible("#btnAtivarAviso") and "Quer ser avisado quando estiver pronto?" in pg.inner_text("#tituloAviso") and not pg.is_visible("#textoAnotado") and pg.is_visible("#btnDesfazerPedido"), "5 depois de 'Já pedi' aparece só a pergunta 'Quer ser avisado quando estiver pronto?', com o botão e o × de desfazer")
    ok(pg.evaluate("window.__permPedidos") == 0 and pg.evaluate("window.__subs") == 0 and ch["registrar"] == [], "6 a oferta só aparece: ainda não pede permissão, não liga e não fala com o servidor")
    pg.click("#btnAtivarAviso"); pg.wait_for_timeout(800)
    ok(pg.evaluate("window.__permPedidos") == 1 and pg.evaluate("window.__subs") == 1, "7 ao tocar em 'Ativar notificação' o navegador pede a permissão e o aviso liga")
    ok(len(ch["registrar"]) == 1, "8 como o pedido já foi feito, o servidor é avisado na hora")
    ok(pg.evaluate("document.getElementById('avisoRapido').classList.contains('visivel')") and "ativada" in pg.inner_text("#avisoRapido"), "8b depois de ativar aparece só um aviso pequeno ('Notificação ativada')")
    pg.wait_for_timeout(3000)
    ok(not pg.evaluate("document.getElementById('avisoRapido').classList.contains('visivel')"), "8c o aviso pequeno some sozinho em poucos segundos")
    r = ch["registrar"][0] if ch["registrar"] else {}
    ok(sorted(r.keys()) == ["aparelho", "endpoint", "fuso", "pedido_em"], "9 envia só aparelho, endpoint, fuso e data do pedido | %r" % sorted(r.keys()))
    ok(r.get("endpoint", "").startswith("https://fcm.googleapis.com/") and len(r.get("aparelho", "")) == 36 and "T" in r.get("pedido_em", ""), "10 valores no formato esperado")
    o = pg.evaluate("window.__subOpts") or {}
    ok(o.get("userVisibleOnly") is True and o.get("len") == 65 and o.get("primeiro") == 4, "11 inscrição pede aviso visível e usa a chave pública de 65 bytes | %r" % o)
    guardado = json.loads(pg.evaluate("localStorage.getItem('quemsaiu_aviso')") or "{}")
    ok(not pg.is_visible("#blocoAviso") and pg.is_visible("#textoAnotado") and "volte aqui" in pg.inner_text("#textoAnotado") and sorted(guardado.keys()) == ["aparelho", "registrado"], "12 depois de ativar o bloco some e volta o 'Anotado… volte aqui'")
    ok(ch["m"].count("pediu.txt") == 1, "13 conta o evento anônimo 'pediu' uma vez | %r" % ch["m"])
    pg.reload(); pg.wait_for_timeout(600)
    ok(len(ch["registrar"]) == 1 and ch["m"].count("voltou.txt") == 1 and pg.evaluate("window.__permPedidos") == 0, "14 ao reabrir não registra de novo, não pergunta de novo e conta 'voltou' uma vez | %r" % ch["m"])

    # 15. ao reabrir, a oferta não volta: o aviso continua ligado
    garantir_guia(pg)
    ok(pg.is_visible("#jaPediFeito") and not pg.is_visible("#blocoAviso") and pg.evaluate("window.__subs") == 0, "15 ao reabrir o aviso continua ligado e a oferta não aparece de novo")

    # 18. mandar a lista: o aviso continua ligado para o próximo pedido
    pg.set_input_files("#inputArquivo", Z + "instagram-a-2026-10-01-x.zip"); pg.wait_for_timeout(1800)
    guardado = json.loads(pg.evaluate("localStorage.getItem('quemsaiu_aviso')") or "{}")
    ok(len(ch["apagar"]) == 1 and list(guardado.keys()) == ["aparelho"], "18 mandar a lista apaga o registro no servidor e mantém o aviso ligado | %r" % list(guardado.keys()))
    ok(pg.evaluate("localStorage.getItem('quemsaiu_pedido')") is None and ch["m"].count("mandou-lista.txt") == 1, "19 apaga o pedido e conta 'mandou lista'")

    # 20. novo pedido com o aviso já ligado: registra de novo sem pedir permissão outra vez; Desfazer apaga o registro e mantém o aviso
    permAntes = pg.evaluate("window.__permPedidos")
    garantir_guia(pg); pg.click("#btnJaPedi"); pg.wait_for_timeout(800)
    ok(len(ch["registrar"]) == 2 and pg.evaluate("window.__permPedidos") == permAntes and not pg.is_visible("#blocoAviso"), "20 um novo 'Já pedi' com o aviso ligado registra de novo, sem pedir permissão outra vez")
    antes = len(ch["apagar"])
    pg.click("#btnDesfazerPedido"); pg.wait_for_timeout(800)
    guardado = json.loads(pg.evaluate("localStorage.getItem('quemsaiu_aviso')") or "{}")
    ok(len(ch["apagar"]) == antes + 1 and list(guardado.keys()) == ["aparelho"], "21 'Desfazer' apaga o registro no servidor e mantém o aviso ligado")

    # 22. Apagar meus dados desliga tudo
    garantir_guia(pg); pg.click("#btnJaPedi"); pg.wait_for_timeout(800)
    antes = len(ch["apagar"])
    pg.click("#btnApagar"); pg.wait_for_timeout(800)
    ok(len(ch["apagar"]) == antes + 1 and pg.evaluate("localStorage.getItem('quemsaiu_aviso')") is None, "22 'Apagar meus dados' desliga o aviso e apaga o registro")
    ok(errs == [], "23 sem erros de JS | %s" % errs)
    ctx.close()

    # 24. permissão negada: explica como liberar, não liga nada e o botão continua disponível
    ctx, ch = novo_contexto(br); pg = ctx.new_page(); pg.add_init_script("window.__perm = 'denied'")
    pg.goto(U); pg.wait_for_timeout(500); abrir_guia(pg); pg.click("#btnJaPedi"); pg.wait_for_timeout(400)
    pg.click("#btnAtivarAviso"); pg.wait_for_timeout(500)
    ok(pg.evaluate("window.__subs") == 0 and ch["registrar"] == [] and pg.evaluate("localStorage.getItem('quemsaiu_aviso')") is None, "24 permissão negada: o aviso não liga e nada vai ao servidor")
    ok("Sem a permissão" in pg.inner_text("#notaAviso") and "libere as notificações" in pg.inner_text("#notaAviso") and pg.is_visible("#btnAtivarAviso") and not pg.is_disabled("#btnAtivarAviso"), "25 permissão negada: explica como liberar e o botão continua disponível")
    ctx.close()

    # 25b. a pessoa ignorou o pedido do navegador: dá para tentar de novo pelo mesmo botão
    ctx, ch = novo_contexto(br); pg = ctx.new_page(); pg.add_init_script("window.__perm = 'default'")
    pg.goto(U); pg.wait_for_timeout(500); abrir_guia(pg); pg.click("#btnJaPedi"); pg.wait_for_timeout(400)
    ok(pg.evaluate("window.__subs") == 0 and pg.is_visible("#btnAtivarAviso"), "25b pedido ignorado: nada liga sozinho e o botão aparece")
    pg.evaluate("window.__perm = 'granted'"); pg.click("#btnAtivarAviso"); pg.wait_for_timeout(600)
    ok(pg.evaluate("window.__subs") == 1 and not pg.is_visible("#blocoAviso"), "25c ao ativar pelo botão o aviso liga")
    ctx.close()

    # 26. servidor com erro ao ativar o aviso já com pedido feito
    ctx, ch = novo_contexto(br); pg = ctx.new_page(); ch["status"] = 500
    pg.goto(U); pg.wait_for_timeout(500); abrir_guia(pg); pg.click("#btnJaPedi"); pg.wait_for_timeout(500)
    pg.click("#btnAtivarAviso"); pg.wait_for_timeout(800)
    ok("Não consegui ligar" in pg.inner_text("#notaAviso") and pg.evaluate("window.__unsubs") == 1 and pg.evaluate("localStorage.getItem('quemsaiu_aviso')") is None, "26 servidor com erro: avisa, desfaz a inscrição e não guarda nada")
    ok(pg.is_visible("#btnJaPedi") is False and pg.is_visible("#jaPediFeito"), "27 o 'Já pedi' continua valendo mesmo sem aviso")
    ctx.close()

    # 28. servidor fora do ar no 'Já pedi' (aviso já ligado): tenta de novo na próxima vez que o site abrir
    ctx, ch = novo_contexto(br); pg = ctx.new_page()
    pg.goto(U); pg.wait_for_timeout(500); abrir_guia(pg); pg.click("#btnJaPedi"); pg.wait_for_timeout(400)
    pg.click("#btnAtivarAviso"); pg.wait_for_timeout(800)
    pg.click("#btnDesfazerPedido"); pg.wait_for_timeout(600)
    ch["status"] = 500
    garantir_guia(pg); pg.click("#btnJaPedi"); pg.wait_for_timeout(800)
    ok(json.loads(pg.evaluate("localStorage.getItem('quemsaiu_aviso')")) == {"aparelho": json.loads(pg.evaluate("localStorage.getItem('quemsaiu_aviso')"))["aparelho"]} and not pg.is_visible("#blocoAviso"), "28 servidor fora do ar no 'Já pedi': o aviso continua ligado e o registro fica para depois")
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
    abrir_guia(pg); pg.click("#btnJaPedi"); pg.wait_for_timeout(300)
    ok(pg.is_visible("#blocoAviso"), "33 com ?avisos=teste o bloco de aviso aparece neste aparelho (depois de 'Já pedi')")
    ok("pediu.txt" not in ch["m"], "34 no modo de teste o funil anônimo não é contado")
    pg.goto(U); pg.wait_for_timeout(400)
    ok(pg.evaluate("localStorage.getItem('quemsaiu_avisos_teste')") == "1", "35 o modo de teste continua ligado ao reabrir sem o parâmetro")
    pg.goto(U + "?avisos=desligar"); pg.wait_for_timeout(400)
    ok(pg.evaluate("localStorage.getItem('quemsaiu_avisos_teste')") is None, "36 ?avisos=desligar volta ao normal")
    ctx.close(); br.close()

print("OK=%d FALHAS=%d" % (0, falhas)); raise SystemExit(1 if falhas else 0)
