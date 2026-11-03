# Os botões do exemplo continuam pulando até a pessoa tocar em um deles
from playwright.sync_api import sync_playwright
U="http://127.0.0.1:8765/index.html"; falhas=0
def ok(c,m):
    global falhas
    print(("OK    " if c else "FALHA ")+m)
    if not c: falhas+=1
with sync_playwright() as p:
    br=p.chromium.launch(); pg=br.new_context(viewport={"width":390,"height":844}).new_page(); errs=[]
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(U); pg.wait_for_timeout(300); pg.click("#btnDescobrir"); pg.wait_for_timeout(1500)
    nome=lambda: pg.evaluate("getComputedStyle(document.querySelector('.aba-prova[data-lista=entrou]')).animationName")
    inf=lambda: pg.evaluate("getComputedStyle(document.querySelector('.aba-prova[data-lista=entrou]')).animationIterationCount")
    ok(nome()=="convite" and inf()=="infinite","1 botão não selecionado pula sem parar")
    pg.wait_for_timeout(9000)
    ok(nome()=="convite","2 depois de vários segundos ainda pula")
    pg.click('.aba-prova[data-lista=entrou]'); pg.wait_for_timeout(300)
    ok(nome()=="none" and pg.evaluate("getComputedStyle(document.querySelector('.aba-prova[data-lista=naoSegue]')).animationName")=="none","3 depois do primeiro toque param de pular")
    ok("Começaram" in pg.inner_text(".aba-prova.ativa") and pg.get_attribute(".aba-prova.ativa","aria-pressed")=="true","4 o toque troca a aba normalmente")
    ok(errs==[],"5 sem erros de JS | %s"%errs)
    br.close()
print("OK=%d FALHAS=%d"%(0,falhas)); raise SystemExit(1 if falhas else 0)
