import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
U = "http://127.0.0.1:8765/index.html"
def ok(c, m): print(("OK    " if c else "FALHA ") + m)

with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(viewport={"width": 390, "height": 844}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    reqs = []; pg.on("request", lambda r: reqs.append(r.url))
    pg.goto(U); pg.wait_for_timeout(300)
    pg.click("#btnDescobrir"); pg.wait_for_timeout(400)
    ok(pg.is_visible("#btnExemplo") and "exemplo completo" in pg.inner_text("#btnExemplo"), "1 botão 'Ver um exemplo completo' aparece embaixo da amostra")
    ok(not pg.is_visible("#cardResultado"), "2 antes de tocar não há resultado")
    pg.click("#btnExemplo"); pg.wait_for_timeout(500)
    ok(pg.is_visible("#cardResultado") and pg.is_visible("#avisoExemplo"), "3 abre o resultado com o aviso de exemplo")
    ok("Nada foi guardado" in pg.inner_text("#avisoExemplo"), "4 aviso diz que nada foi guardado")
    abas = pg.evaluate("[...document.querySelectorAll('#abasResultado .aba-res')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())")
    ok(len(abas) == 3 and abas[0].startswith("3") and abas[1].startswith("2") and abas[2].startswith("4"), "5 abas com 3 / 2 / 4 contas | %r" % abas)
    ok(pg.evaluate("document.querySelectorAll('#listaResultado a').length") == 0, "6 sem links para perfis de verdade")
    ok(pg.evaluate("[...document.querySelectorAll('#listaResultado .usuario-nome')].every(e=>e.innerText.endsWith('.exemplo'))"), "7 só contas fictícias (.exemplo)")
    ok(pg.evaluate("localStorage.getItem('quemsaiu_exportacoes')") is None and pg.evaluate("localStorage.getItem('quemsaiu_ignoradas')") is None, "8 nada foi gravado no aparelho")
    pg.click("#listaResultado .btn-ignorar >> nth=0"); pg.wait_for_timeout(450)
    ok(pg.evaluate("localStorage.getItem('quemsaiu_ignoradas')") is None, "9 esconder uma conta no exemplo não grava nada")
    pg.click(".aba-res.naoSegue"); pg.wait_for_timeout(200)
    ok("abrir o perfil" not in pg.inner_text("#listaResultado"), "10 no exemplo some a dica de abrir perfil")
    ok(not any("instagram.com" in u for u in reqs), "11 nenhuma chamada ao Instagram")
    pg.click("#btnSairExemplo"); pg.wait_for_timeout(400)
    ok(not pg.is_visible("#cardResultado") and not pg.is_visible("#avisoExemplo"), "12 ao sair do exemplo o resultado some (sem lista real)")
    ok("Nenhuma lista guardada" in pg.inner_text("#statusImport"), "13 status volta ao normal")
    ok(pg.get_attribute("#btnComparar", "aria-disabled") == "true", "14 'Ver a comparação' volta a ficar apagado")
    ok(not errs, "15 sem erros de JS | %r" % errs)
    ctx.close()

    # com lista real guardada: o exemplo não mexe nela
    ctx = br.new_context(viewport={"width": 390, "height": 844}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    real = [{"data": "2026-10-01T00:00:00Z", "seguidores": ["real1", "real2"], "seguindo": ["real1", "real3"]}]
    pg.goto(U); pg.evaluate("localStorage.setItem('quemsaiu_exportacoes', %s)" % json.dumps(json.dumps(real)))
    pg.reload(); pg.wait_for_timeout(300)
    pg.click("#btnDescobrir"); pg.wait_for_timeout(400)
    pg.click("#btnExemplo"); pg.wait_for_timeout(500)
    ok("exemplo" in pg.inner_text("#listaResultado"), "16 com lista real guardada o exemplo mostra o exemplo")
    pg.click("#btnSairExemplo"); pg.wait_for_timeout(400)
    ok(pg.is_visible("#cardResultado") and "real3" in pg.inner_text("#listaResultado"), "17 ao sair volta a lista real")
    ok(json.loads(pg.evaluate("localStorage.getItem('quemsaiu_exportacoes')")) == real, "18 a lista real continua intacta")
    # tocar em 'Mandar lista' durante o exemplo sai do exemplo
    pg.click("#btnExemplo"); pg.wait_for_timeout(400)
    with pg.expect_file_chooser(timeout=3000) as fc:
        pg.click("#btnImportar")
    ok(not pg.is_visible("#avisoExemplo"), "19 'Mandar lista' no meio do exemplo sai do exemplo e abre o seletor")
    # apagar durante o exemplo não apaga os dados reais
    pg.click("#btnExemplo"); pg.wait_for_timeout(400)
    pg.once("dialog", lambda d: d.accept())
    pg.click("#btnApagar"); pg.wait_for_timeout(400)
    ok(pg.evaluate("localStorage.getItem('quemsaiu_exportacoes')") is not None and not pg.is_visible("#avisoExemplo"), "20 'Apagar' durante o exemplo só sai do exemplo, sem apagar os dados reais")
    ok(not errs, "21 sem erros de JS | %r" % errs)
    ctx.close()
    br.close()
