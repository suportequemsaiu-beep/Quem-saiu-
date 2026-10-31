import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
U = "http://127.0.0.1:8765/index.html"
def ok(c, m): print(("OK    " if c else "FALHA ") + m)

with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(viewport={"width": 390, "height": 844}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(U); pg.wait_for_timeout(300)
    pg.click("#btnDescobrir"); pg.wait_for_timeout(400)
    ok("Nada é enviado para servidor nenhum" not in pg.inner_text("body").split("Sua lista")[0], "1 frase abaixo do 'Começar agora' foi removida")
    pg.click("#btnComecar"); pg.wait_for_timeout(300)
    ok("Mandar lista" in pg.inner_text("#btnImportar"), "2 botão de cima: 'Mandar lista'")
    ok("Ver a comparação" in pg.inner_text("#btnComparar"), "3 botão de baixo: 'Ver a comparação'")
    ok(pg.get_attribute("#btnComparar", "aria-disabled") == "true", "4 sem lista, o botão de baixo fica apagado")
    ok(pg.query_selector("#avisoRapido") is None, "5 aviso ainda não aparece")
    pg.click("#btnComparar", force=True); pg.wait_for_timeout(400)
    ok(pg.evaluate("getComputedStyle(document.getElementById('avisoRapido')).opacity") == "1" and "ainda não enviou a primeira lista" in pg.inner_text("#avisoRapido"), "6 ao tocar sem lista aparece o aviso")
    ok(pg.get_attribute("#avisoRapido", "role") == "status", "7 aviso é lido por leitor de tela (role=status)")
    pg.wait_for_timeout(3500)
    ok(pg.evaluate("getComputedStyle(document.getElementById('avisoRapido')).opacity") == "0", "8 o aviso some depois de ~3 segundos")
    ok(not pg.is_visible("#cardResultado"), "9 sem lista, nada de resultado aparece")
    pg.evaluate("localStorage.setItem('quemsaiu_exportacoes', JSON.stringify([{data:'2026-10-01T00:00:00Z',seguidores:['a','b'],seguindo:['a','c']}]))")
    pg.reload(); pg.wait_for_timeout(300)
    pg.click("#btnDescobrir"); pg.wait_for_timeout(400); pg.click("#btnComecar"); pg.wait_for_timeout(300)
    ok(pg.get_attribute("#btnComparar", "aria-disabled") == "false", "10 com 1 lista guardada o botão de baixo fica ativo")
    pg.click("#btnComparar"); pg.wait_for_timeout(500)
    ok(pg.is_visible("#cardResultado"), "11 com lista, o botão mostra a lista")
    ok(not errs, "12 sem erros de JS | %r" % errs)
    br.close()
