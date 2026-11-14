import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
U = "http://127.0.0.1:8765/index.html"
def ok(c, m): print(("OK    " if c else "FALHA ") + m)
LISTA = json.dumps([{"v": 1, "data": "2026-10-01T10:00:00.000Z", "seguidores": ["a", "b"], "seguindo": ["a"]}])

def comecar(pg):
    pg.click("#btnDescobrir"); pg.wait_for_timeout(300)
    pg.click("#btnComecar"); pg.wait_for_timeout(300)

with sync_playwright() as p:
    br = p.chromium.launch()
    # 1) quem ainda não tem a lista: a dica do arquivo não aparece
    ctx = br.new_context(viewport={"width": 390, "height": 844}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(U); pg.wait_for_timeout(300); comecar(pg)
    ok(not pg.is_visible("#dicaArquivo"), "1 sem lista e sem pedido: a dica 'Recentes ou Downloads' não aparece")
    # 2) depois do "Já pedi" ela aparece, com o texto completo
    pg.click("#togglePasso"); pg.wait_for_timeout(300)
    pg.click("#btnJaPedi"); pg.wait_for_timeout(300)
    t = pg.inner_text("#dicaArquivo") if pg.is_visible("#dicaArquivo") else ""
    ok("Recentes" in t and "Downloads" in t and "instagram-" in t and "descompactar" in t, "2 depois do 'Já pedi' a dica aparece | %r" % t[:60])
    # 3) desfazer: some de novo
    pg.click("#btnDesfazerPedido"); pg.wait_for_timeout(300)
    ok(not pg.is_visible("#dicaArquivo"), "3 ao desfazer o pedido a dica some")
    ok(errs == [], "4 sem erros no console | %r" % errs[:1]); ctx.close()
    # 5) quem já tem uma lista guardada (voltou com o arquivo novo) vê a dica
    ctx = br.new_context(viewport={"width": 390, "height": 844}); ctx.add_init_script("localStorage.setItem('quemsaiu_exportacoes', %s)" % json.dumps(LISTA)); pg = ctx.new_page()
    pg.goto(U); pg.wait_for_timeout(300); comecar(pg)
    ok(pg.is_visible("#dicaArquivo"), "5 com uma lista já guardada a dica aparece"); ctx.close()
    br.close()
