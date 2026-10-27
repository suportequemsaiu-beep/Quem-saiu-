import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
U = "http://127.0.0.1:8765/index.html"
def ok(c, m): print(("OK    " if c else "FALHA ") + m)

with sync_playwright() as p:
    br = p.chromium.launch()
    for esquema in ("light", "dark"):
        ctx = br.new_context(viewport={"width": 390, "height": 844}, color_scheme=esquema)
        pg = ctx.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(U); pg.wait_for_timeout(400)
        meta = pg.evaluate("(document.querySelector('meta[name=color-scheme]')||{}).content")
        ok(meta == "only light", "1 [%s] a página avisa ao navegador para não escurecê-la sozinho (meta color-scheme) | %r" % (esquema, meta))
        cs = pg.evaluate("getComputedStyle(document.documentElement).colorScheme")
        ok(sorted(cs.split())==["light","only"], "2 [%s] o CSS também fixa o esquema claro (%r)" % (esquema, cs))
        ok(pg.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(15, 23, 42)", "3 [%s] o fundo continua azul-marinho do projeto" % esquema)
        ok(pg.evaluate("getComputedStyle(document.querySelector('.cabeca')).backgroundColor") == "rgb(226, 232, 240)", "4 [%s] a figura da porta continua clara" % esquema)
        ok(errs == [], "5 [%s] sem erros de JavaScript" % esquema)
        ctx.close()
    br.close()
