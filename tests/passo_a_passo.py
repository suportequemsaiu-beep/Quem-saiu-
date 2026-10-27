import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
U = "http://127.0.0.1:8765/index.html"
def ok(c, m): print(("OK    " if c else "FALHA ") + m)

def abrir(pg):
    pg.goto(U); pg.wait_for_timeout(300)
    pg.click("#btnDescobrir"); pg.wait_for_timeout(400)
    pg.click("#btnComecar"); pg.wait_for_timeout(300)

def etapa_visivel(pg):
    return pg.evaluate("[...document.querySelectorAll('#listaEtapas .etapa')].filter(e=>getComputedStyle(e).display!=='none'&&getComputedStyle(e).visibility!=='hidden').map(e=>e.querySelector('h3').textContent)")

with sync_playwright() as p:
    br = p.chromium.launch()

    # celular
    ctx = br.new_context(viewport={"width": 390, "height": 844}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    abrir(pg)
    ok(not pg.is_visible("#corpoPasso"), "1 o passo a passo começa fechado")
    pg.click("#togglePasso"); pg.wait_for_timeout(300)
    ok(pg.is_visible("#corpoPasso"), "2 abre ao tocar no botão")
    ok(pg.evaluate("document.getElementById('togglePasso').getAttribute('aria-expanded')") == "true", "3 aria-expanded fica true")
    v = etapa_visivel(pg)
    ok(len(v) == 1 and v[0] == "Abra o menu", "4 mostra só um passo por vez, começando pelo primeiro | %r" % v)
    ok("Passo 1 de 12" in pg.inner_text(".passo-contagem"), "5 contagem 'Passo 1 de 12' (12 passos no celular)")
    ok(not pg.is_visible(".passo-voltar"), "6 no primeiro passo não há 'Voltar'")
    ok(pg.evaluate("document.querySelectorAll('.etapa.atual .etapa-desenho svg').length") == 1, "7 o passo tem um desenho")
    ok(pg.evaluate("document.querySelector('.etapa-desenho').innerHTML.toLowerCase().includes('instagram')") is False, "8 o desenho não traz o nome nem a marca do Instagram")
    ok(pg.get_attribute(".passo-trilha", "aria-valuenow") == "1", "9 a barra de progresso informa o passo (aria)")
    pg.click(".passo-proximo"); pg.wait_for_timeout(350)
    v = etapa_visivel(pg)
    ok(v == ["Central de Contas"], "10 Próximo leva ao passo 2 | %r" % v)
    ok(pg.is_visible(".passo-voltar"), "11 aparece 'Voltar'")
    pg.click(".passo-voltar"); pg.wait_for_timeout(350)
    ok(etapa_visivel(pg) == ["Abra o menu"], "12 Voltar retorna ao passo 1")
    vistos = []
    for i in range(11):
        pg.click(".passo-proximo"); pg.wait_for_timeout(120)
        vistos += etapa_visivel(pg)
    ok(len(vistos) == 11 and "Mande para o Quem Saiu" == vistos[-1], "13 percorre os 12 passos; o último é o do Android | %r" % vistos[-1:])
    ok("Notificar" in vistos, "14 o passo 'Notificar' está no caminho")
    ok(pg.inner_text(".passo-proximo").strip() == "Já tenho o arquivo", "15 no último passo o botão vira 'Já tenho o arquivo'")
    ok(pg.evaluate("document.getElementById('corpoPasso').getAttribute('data-fase')") == "enviar", "16 a fase do último passo é 'enviar'")
    pg.click(".passo-proximo"); pg.wait_for_timeout(400)
    ok(not pg.is_visible("#corpoPasso"), "17 'Já tenho o arquivo' fecha o passo a passo")
    ok(pg.evaluate("document.activeElement && document.activeElement.id") == "btnImportar", "18 e leva o foco ao botão 'Ver a minha lista'")
    pg.click("#togglePasso"); pg.wait_for_timeout(300)
    ok(etapa_visivel(pg) == ["Abra o menu"], "19 ao reabrir, volta ao primeiro passo")
    ok(pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "20 sem rolagem lateral")
    ok(errs == [], "21 sem erros de JavaScript | %r" % errs)
    ctx.close()

    # computador
    ctx = br.new_context(viewport={"width": 1280, "height": 800}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    abrir(pg)
    pg.click("#togglePasso"); pg.wait_for_timeout(300)
    ok("de 12" in pg.inner_text(".passo-contagem"), "22 no computador também são 12 passos (o final muda)")
    for i in range(11):
        pg.click(".passo-proximo"); pg.wait_for_timeout(100)
    v = etapa_visivel(pg)
    ok(v == ["Escolha o arquivo aqui"], "23 no computador o último passo é o de escolher o arquivo | %r" % v)
    ok(errs == [], "24 sem erros de JavaScript no computador")
    ctx.close()

    # sem JavaScript: a lista inteira aparece
    ctx = br.new_context(viewport={"width": 390, "height": 844}, java_script_enabled=False); pg = ctx.new_page()
    pg.goto(U); pg.wait_for_timeout(300)
    texto = pg.content()
    ok("Toque em <b>Notificar</b>" in texto and "Central de Contas" in texto, "25 sem JavaScript, o texto de todos os passos continua no HTML")
    ctx.close()
    br.close()
