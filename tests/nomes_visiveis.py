# Nomes inteiros nas abas com etiqueta (Você segue / Você não segue / Você segue de volta), em 360 px.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
U = "http://127.0.0.1:8765/index.html"
falhas = 0
def ok(c, m):
    global falhas
    print(("OK    " if c else "FALHA ") + m)
    if not c: falhas += 1
SAIRAM = ["paula.mendes", "gabriel_santos", "jose.oliveira.mg", "pedro_henrique", "_fernanda.silva", "luciana.araujo", "ana.souza", "marcos_lott"]
ENTRARAM = ["natalia.costa", "guilherme_r", "sofia.almeida", "joao.vitor", "debora.lima", "meire.rocha"]
SEGUINDO = ["paula.mendes", "ana.souza", "natalia.costa", "sofia.almeida", "joao.vitor"] + ["z%d" % i for i in range(5)]
dados = [{"data": "2026-11-21T19:29:00Z", "seguidores": SAIRAM + ["x1", "x2"], "seguindo": SEGUINDO},
         {"data": "2026-11-21T19:30:00Z", "seguidores": ["x1", "x2"] + ENTRARAM, "seguindo": SEGUINDO}]
JS_LINHAS = """()=>[...document.querySelectorAll('.item-usuario')].map(li=>{
  const a=li.querySelector('.usuario-nome a'), s=li.querySelector('.selo'), r=li.getBoundingClientRect(), ar=a.getBoundingClientRect();
  const so=s?s.getBoundingClientRect():null;
  return {nome:a.textContent, cortado:a.scrollWidth>a.clientWidth+1, alturaLinha:r.height, alturaLink:ar.height,
          seloAbaixo:so?(so.top>=ar.top+ar.height/2):null, seloDentro:so?(so.right<=r.right+0.5 && so.left>=r.left-0.5):null, temSelo:!!s}})"""
with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(viewport={"width": 360, "height": 800}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(U); pg.wait_for_timeout(300)
    pg.evaluate("d=>localStorage.setItem('quemsaiu_exportacoes',JSON.stringify(d))", dados); pg.reload(); pg.wait_for_timeout(400)
    pg.click("#btnDescobrir"); pg.wait_for_timeout(300); pg.click("#btnComecar"); pg.wait_for_timeout(400)
    pg.click("#btnComparar"); pg.wait_for_timeout(600)

    pg.click(".aba-res.saiu"); pg.wait_for_timeout(300)
    L = pg.evaluate(JS_LINHAS)
    ok(len(L) == len(SAIRAM), "1 aba 'Deixaram de te seguir' mostra as %d contas | %d" % (len(SAIRAM), len(L)))
    ok(all(not l["cortado"] for l in L), "2 nenhum nome fica cortado em 360 px | cortados: %s" % [l["nome"] for l in L if l["cortado"]])
    ok(all(l["temSelo"] and l["seloAbaixo"] and l["seloDentro"] for l in L), "3 a etiqueta aparece embaixo do nome, dentro da linha")
    ok(all(l["alturaLink"] >= 44 for l in L) and all(48 <= l["alturaLinha"] <= 60 for l in L), "4 o nome tem 44 px de toque e a linha tem até 60 px | %s" % sorted({round(l["alturaLinha"]) for l in L}))
    ok(pg.evaluate("document.documentElement.scrollWidth") <= 360, "5 a página não ganhou rolagem horizontal")
    n = pg.evaluate("document.querySelectorAll('.btn-ignorar').length")
    pg.evaluate("document.querySelector('.btn-ignorar').click()"); pg.wait_for_timeout(500)
    ok(pg.evaluate("document.querySelectorAll('.btn-ignorar').length") == n - 1, "6 esconder uma conta continua funcionando")

    pg.click(".aba-res.entrou"); pg.wait_for_timeout(300)
    L = pg.evaluate(JS_LINHAS)
    ok(len(L) == len(ENTRARAM), "7 aba 'Começaram a te seguir' mostra as %d contas | %d" % (len(ENTRARAM), len(L)))
    ok(all(not l["cortado"] for l in L), "8 nenhum nome fica cortado, nem com 'Você segue de volta' | cortados: %s" % [l["nome"] for l in L if l["cortado"]])
    ok(any("Você segue de volta" in pg.inner_text(".item-usuario:nth-child(%d) .selo" % (i + 1)) for i in range(len(L))), "9 a etiqueta 'Você segue de volta' continua existindo")
    ok(all(l["seloAbaixo"] and l["seloDentro"] for l in L), "10 as etiquetas ficam embaixo do nome e dentro da linha")

    pg.click(".aba-res.naoSegue"); pg.wait_for_timeout(300)
    L = pg.evaluate(JS_LINHAS)
    ok(len(L) > 0 and all(not l["temSelo"] and abs(l["alturaLinha"] - 48) <= 1 and not l["cortado"] for l in L), "11 'Não te seguem de volta' não mudou: sem etiqueta, linha de 48 px, nomes inteiros")
    ok(not errs, "12 sem erros de JS | %r" % errs)
    br.close()
print("OK=%d FALHAS=%d" % (0, falhas)); raise SystemExit(1 if falhas else 0)
