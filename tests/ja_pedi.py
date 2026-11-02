import os, sys, tempfile, datetime, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixtures
from playwright.sync_api import sync_playwright
T = tempfile.mkdtemp(prefix="quemsaiu-") + "/"
Z = T + "z/"
fixtures.criar_zips(Z)
U = "http://127.0.0.1:8765/index.html"
def ok(c, m): print(("OK    " if c else "FALHA ") + m)

def abrir_guia(pg):
    pg.click("#btnDescobrir"); pg.wait_for_timeout(300)
    pg.click("#btnComecar"); pg.wait_for_timeout(300)
    pg.click("#togglePasso"); pg.wait_for_timeout(300)

with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(viewport={"width": 390, "height": 844}, accept_downloads=True); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(U); pg.wait_for_timeout(300)
    abrir_guia(pg)
    ok(pg.is_visible("#btnJaPedi") and "Já pedi" in pg.inner_text("#btnJaPedi"), "1 o guia tem o botão 'Já pedi o arquivo ao Instagram'")
    ok("ainda não enviou nenhuma lista" in pg.inner_text("#statusImport") and "mais recente do Instagram" in pg.inner_text("#statusImport"), "2 estado vazio com o texto novo | %r" % pg.inner_text("#statusImport")[:90])
    ok(pg.evaluate("localStorage.getItem('quemsaiu_pedido')") is None, "3 antes de tocar nada foi guardado")
    pg.click("#btnJaPedi"); pg.wait_for_timeout(300)
    v = json.loads(pg.evaluate("localStorage.getItem('quemsaiu_pedido')"))
    ok(list(v.keys()) == ["data"], "4 guarda só a data | %r" % list(v.keys()))
    ok(pg.is_visible("#jaPediFeito") and "Anotado" in pg.inner_text("#jaPediFeito"), "5 mostra 'Anotado' e as opções de lembrete")
    ok(not pg.is_visible("#avisoVolta"), "6 logo depois de tocar o aviso de volta não aparece")

    # download do lembrete
    with pg.expect_download() as d:
        pg.click('[data-lembrar="1h"]')
    arq = d.value; ics = open(arq.path(), encoding="utf-8", newline="").read()
    ok(arq.suggested_filename.endswith(".ics"), "7 baixa um arquivo .ics | %s" % arq.suggested_filename)
    ok(ics.startswith("BEGIN:VCALENDAR\r\n") and "BEGIN:VALARM" in ics and "TRIGGER:PT0S" in ics and ics.rstrip().endswith("END:VCALENDAR"), "8 .ics tem evento e alarme, com quebras de linha CRLF")
    ok("pode já ter chegado" in ics and "https://quemsaiu.com.br" in ics, "9 texto do lembrete sem prometer que o arquivo está pronto")
    linha = [l for l in ics.split("\r\n") if l.startswith("DTSTART:")][0][8:]
    ini = datetime.datetime.strptime(linha, "%Y%m%dT%H%M%S"); dif = (ini - datetime.datetime.now()).total_seconds()
    ok(3000 < dif < 3900, "10 'Em 1 hora' marca cerca de 1 hora à frente | %.0f s" % dif)
    ok("não garante" in pg.inner_text("#notaLembrete"), "11 o aviso diz que o Instagram não garante o prazo")

    # voltar ao site
    pg.reload(); pg.wait_for_timeout(400)
    ok(pg.is_visible("#ferramenta") and pg.is_visible("#avisoVolta"), "12 ao voltar a ferramenta abre sozinha com o aviso")
    ok("Baixou o arquivo?" in pg.inner_text("#avisoVolta") and "Você pediu o arquivo em" in pg.inner_text("#avisoVolta"), "13 aviso: 'Baixou o arquivo?' e a data do pedido")
    with pg.expect_file_chooser(timeout=3000):
        pg.click("#btnAvisoVolta")
    ok(True, "14 tocar no aviso abre o seletor de arquivos")
    pg.click("#btnAindaNaoChegou"); pg.wait_for_timeout(200)
    ok(not pg.is_visible("#avisoVolta") and pg.evaluate("localStorage.getItem('quemsaiu_pedido')") is not None, "15 'Ainda não chegou' esconde o aviso e mantém o pedido")

    # enviar a primeira lista
    pg.reload(); pg.wait_for_timeout(300)
    pg.set_input_files("#inputArquivo", Z + "instagram-a-2026-10-01-x.zip"); pg.wait_for_timeout(1500)
    ok(pg.evaluate("localStorage.getItem('quemsaiu_pedido')") is None and not pg.is_visible("#avisoVolta"), "16 ao enviar a lista o pedido é apagado")
    ok(pg.is_visible("#pontoPartida") and "Ponto de partida salvo" in pg.inner_text("#pontoPartida") and "quem deixou de te seguir" in pg.inner_text("#pontoPartida"), "17 aparece 'Ponto de partida salvo' com a explicação")
    ok("Ponto de partida salvo" in pg.inner_text("#tituloResultado"), "18 título do resultado também")
    pg.set_input_files("#inputArquivo", Z + "instagram-a-2026-10-14-y.zip"); pg.wait_for_timeout(1500)
    ok(not pg.is_visible("#pontoPartida"), "19 com a segunda lista o aviso de ponto de partida some")

    # apagar dados apaga o pedido
    pg.click("#btnJaPedi") if pg.is_visible("#btnJaPedi") else None
    pg.evaluate("localStorage.setItem('quemsaiu_pedido', JSON.stringify({data:new Date().toISOString()}))")
    pg.once("dialog", lambda d: d.accept()); pg.click("#btnApagar"); pg.wait_for_timeout(300)
    ok(pg.evaluate("localStorage.getItem('quemsaiu_pedido')") is None, "20 'Apagar meus dados' também apaga o pedido")
    ok(not errs, "21 sem erros de JS | %r" % errs)
    ctx.close()

    # desfazer
    ctx = br.new_context(viewport={"width": 390, "height": 844}); pg = ctx.new_page()
    pg.goto(U); pg.wait_for_timeout(300); abrir_guia(pg)
    pg.click("#btnJaPedi"); pg.wait_for_timeout(200); pg.click("#btnDesfazerPedido"); pg.wait_for_timeout(200)
    ok(pg.evaluate("localStorage.getItem('quemsaiu_pedido')") is None and pg.is_visible("#btnJaPedi"), "22 'Desfazer' apaga o pedido e volta o botão")
    ctx.close()

    # 'Esta noite' fica indisponível depois das 19h30
    ctx = br.new_context(viewport={"width": 390, "height": 844}); pg = ctx.new_page()
    pg.clock.install(time=datetime.datetime(2026, 11, 2, 21, 0, 0))
    pg.goto(U); pg.wait_for_timeout(300); abrir_guia(pg); pg.click("#btnJaPedi"); pg.wait_for_timeout(200)
    ok(pg.is_disabled("#btnLembrarNoite"), "23 às 21h o lembrete 'Esta noite' fica indisponível")
    ctx.close()
    ctx = br.new_context(viewport={"width": 390, "height": 844}, accept_downloads=True); pg = ctx.new_page()
    pg.clock.install(time=datetime.datetime(2026, 11, 2, 10, 0, 0))
    pg.goto(U); pg.wait_for_timeout(300); abrir_guia(pg); pg.click("#btnJaPedi"); pg.wait_for_timeout(200)
    with pg.expect_download() as d: pg.click('[data-lembrar="noite"]')
    ics = open(d.value.path(), encoding="utf-8", newline="").read()
    ok("DTSTART:20261102T200000" in ics, "24 às 10h, 'Esta noite' marca 20h do mesmo dia")
    with pg.expect_download() as d: pg.click('[data-lembrar="manha"]')
    ics = open(d.value.path(), encoding="utf-8", newline="").read()
    ok("DTSTART:20261103T090000" in ics, "25 'Amanhã' marca 9h do dia seguinte")
    ctx.close()
    br.close()
