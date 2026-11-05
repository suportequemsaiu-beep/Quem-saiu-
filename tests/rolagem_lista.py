# Esconder (x) ou restaurar uma conta não pode levar a lista de volta ao início.
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
U = "http://127.0.0.1:8765/index.html"
falhas = 0
def ok(c, m):
    global falhas
    print(("OK    " if c else "FALHA ") + m)
    if not c: falhas += 1

ANTES = ["conta%02d" % i for i in range(60)]
DEPOIS = ANTES[:5]   # 55 contas saíram
dados = [{"data": "2026-10-01T00:00:00Z", "seguidores": ANTES, "seguindo": []},
         {"data": "2026-11-01T00:00:00Z", "seguidores": DEPOIS, "seguindo": []}]

with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(viewport={"width": 390, "height": 844}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(U); pg.wait_for_timeout(300)
    pg.evaluate("d => localStorage.setItem('quemsaiu_exportacoes', JSON.stringify(d))", dados)
    pg.reload(); pg.wait_for_timeout(300)
    pg.click("#btnDescobrir"); pg.wait_for_timeout(400); pg.click("#btnComecar"); pg.wait_for_timeout(300)
    pg.click("#btnComparar"); pg.wait_for_timeout(500)
    ok(pg.is_visible(".lista-usuarios"), "1 a lista de quem saiu aparece")
    pg.evaluate("document.querySelector('.lista-usuarios').scrollTop = 100000"); pg.wait_for_timeout(100)
    antes = pg.evaluate("document.querySelector('.lista-usuarios').scrollTop")
    ok(antes > 500, "2 a lista está rolada até o fim (scrollTop=%s)" % antes)
    ultimo = pg.evaluate("document.querySelectorAll('.btn-ignorar').length - 1")
    pg.evaluate("n => document.querySelectorAll('.btn-ignorar')[n].click()", ultimo); pg.wait_for_timeout(500)
    depois = pg.evaluate("document.querySelector('.lista-usuarios').scrollTop")
    ok(depois > 500, "3 ao esconder uma conta no fim, a lista NÃO volta ao início (scrollTop=%s)" % depois)
    ok(pg.evaluate("document.querySelectorAll('.btn-ignorar').length") == 54, "4 a conta foi mesmo escondida (54 sobraram)")
    # esconder uma do meio mantém a posição
    pg.evaluate("document.querySelector('.lista-usuarios').scrollTop = 400"); pg.wait_for_timeout(100)
    pg.evaluate("document.querySelectorAll('.btn-ignorar')[12].click()"); pg.wait_for_timeout(500)
    meio = pg.evaluate("document.querySelector('.lista-usuarios').scrollTop")
    ok(abs(meio - 400) < 5, "5 esconder uma conta do meio mantém a posição (scrollTop=%s)" % meio)
    # painel de escondidas e restaurar uma
    pg.click("#btnVerEscondidas"); pg.wait_for_timeout(300)
    ok(abs(pg.evaluate("document.querySelector('.lista-usuarios').scrollTop") - 400) < 5, "6 abrir o painel de escondidas mantém a posição da lista")
    pg.click("[data-restaurar]"); pg.wait_for_timeout(300)
    ok(abs(pg.evaluate("document.querySelector('.lista-usuarios').scrollTop") - 400) < 5, "7 restaurar uma conta mantém a posição da lista")
    # trocar de aba começa do início
    pg.evaluate("document.querySelector('.lista-usuarios').scrollTop = 400")
    pg.click("button[data-res='entrou']"); pg.wait_for_timeout(300)
    pg.click("button[data-res='saiu']"); pg.wait_for_timeout(300)
    ok(pg.evaluate("document.querySelector('.lista-usuarios').scrollTop") == 0, "8 voltar a uma aba depois de trocar começa do início")
    ok(not errs, "9 sem erros de JS | %r" % errs)
    br.close()
print("OK=%d FALHAS=%d" % (0, falhas)); raise SystemExit(1 if falhas else 0)
