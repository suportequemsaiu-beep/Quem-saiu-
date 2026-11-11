# Alvos de toque de 44 px, "Saiba mais" na explicação e aviso em contorno.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
U = "http://127.0.0.1:8765/index.html"
falhas = 0
def ok(c, m):
    global falhas
    print(("OK    " if c else "FALHA ") + m)
    if not c: falhas += 1
ANTES = ["conta%02d" % i for i in range(30)]
dados = [{"data": "2026-10-01T00:00:00Z", "seguidores": ANTES, "seguindo": ANTES[:10]},
         {"data": "2026-11-01T00:00:00Z", "seguidores": ANTES[:20] + ["nova1"], "seguindo": ANTES[:10]}]
def dentro(pg, x, y, seletor):
    return pg.evaluate("([x,y,s])=>{const e=document.elementFromPoint(x,y);return !!(e&&e.closest(s))}", [x, y, seletor])
with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(viewport={"width": 390, "height": 844}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    ctx.add_init_script("window.__QS_AVISOS_TESTE = true;")
    pg.goto(U); pg.wait_for_timeout(300)
    hs = pg.evaluate("[...document.querySelectorAll('nav .abas button')].map(b=>b.getBoundingClientRect().height)")
    ok(all(h >= 44 for h in hs), "1 as abas do topo têm 44 px de toque | %s" % hs)
    r = pg.evaluate("(()=>{const b=document.getElementById('btnCompartilhar').getBoundingClientRect();return [b.left,b.top,b.width,b.height]})()")
    ok(dentro(pg, r[0] - 4, r[1] - 7, "#btnCompartilhar") and dentro(pg, r[0] + r[2] / 2, r[1] + r[3] + 7, "#btnCompartilhar"), "2 'Compartilhar' aceita toque 8 px acima e abaixo (área de 44 px)")
    ok(pg.evaluate("document.documentElement.scrollWidth") <= 390, "3 a página não ganhou rolagem horizontal")
    pg.evaluate("d=>localStorage.setItem('quemsaiu_exportacoes',JSON.stringify(d))", dados); pg.reload(); pg.wait_for_timeout(400)
    pg.click("#btnDescobrir"); pg.wait_for_timeout(300); pg.click("#btnComecar"); pg.wait_for_timeout(400)
    ok("Ativar aviso" in pg.inner_text("#btnAtivarAviso"), "4 o aviso é oferecido")
    fundo = pg.evaluate("getComputedStyle(document.getElementById('btnAtivarAviso')).backgroundColor")
    ok(fundo != "rgb(0, 107, 161)" and pg.evaluate("document.getElementById('btnAtivarAviso').getBoundingClientRect().height") >= 44, "5 'Ativar aviso' não é mais azul cheio (concorria com 'Mandar lista') e tem 44 px | %s" % fundo)
    pg.click("#btnComparar"); pg.wait_for_timeout(600)
    ok(pg.evaluate("document.getElementById('explicaMais').hidden") is True, "6 a explicação do resultado começa curta")
    ok("O arquivo não diz o motivo" in pg.inner_text("#listaResultado .explica-aba"), "7 o aviso de que o arquivo não diz o motivo continua visível")
    pg.click(".saiba-mais"); pg.wait_for_timeout(200)
    ok(not pg.evaluate("document.getElementById('explicaMais').hidden") and pg.get_attribute(".saiba-mais", "aria-expanded") == "true" and "desativado" in pg.inner_text("#explicaMais"), "8 'Saiba mais' abre o resto da explicação")
    pg.click(".saiba-mais"); pg.wait_for_timeout(200)
    ok(pg.evaluate("document.getElementById('explicaMais').hidden") is True, "9 'Mostrar menos' fecha de novo")
    b = pg.evaluate("(()=>{const e=document.querySelector('.btn-ignorar').getBoundingClientRect();return [e.left,e.top,e.width,e.height]})()")
    ok(dentro(pg, b[0] - 6, b[1] - 7, ".btn-ignorar") and dentro(pg, b[0] + b[2] + 6, b[1] + b[3] + 7, ".btn-ignorar"), "10 o × aceita toque até 8 px ao redor (área de 44 px)")
    alt = pg.evaluate("[document.querySelector('.usuario-nome a').getBoundingClientRect().height, document.querySelector('.item-usuario').getBoundingClientRect().height]")
    ok(alt[0] >= 44 and alt[1] <= 49, "11 o nome tem 44 px de toque e a linha continua com 48 px | %s" % alt)
    n = pg.evaluate("document.querySelectorAll('.btn-ignorar').length")
    pg.evaluate("document.querySelector('.btn-ignorar').click()"); pg.wait_for_timeout(500)
    ok(pg.evaluate("document.querySelectorAll('.btn-ignorar').length") == n - 1, "12 esconder uma conta continua funcionando")
    ok(not errs, "13 sem erros de JS | %r" % errs)
    br.close()
print("OK=%d FALHAS=%d" % (0, falhas)); raise SystemExit(1 if falhas else 0)
