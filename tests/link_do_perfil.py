import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixtures
from playwright.sync_api import sync_playwright
U="http://127.0.0.1:8765/index.html"
def ok(c,m): print(("OK    " if c else "FALHA ")+m)
with sync_playwright() as p:
    br=p.chromium.launch(); ctx=br.new_context(viewport={"width":390,"height":844}); pg=ctx.new_page(); errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.goto(U); pg.wait_for_timeout(300)
    pg.evaluate("""localStorage.setItem("quemsaiu_exportacoes",JSON.stringify([{data:new Date().toISOString(),seguidores:["x"],seguindo:["alguem.teste","b_c"]}]))""")
    pg.reload(); pg.wait_for_timeout(400); pg.click("#btnDescobrir"); pg.click("#btnComecar"); pg.wait_for_timeout(200)
    vistos=[]
    def rota(route): vistos.append(route.request.headers.get("referer")); route.fulfill(status=200,body="ok")
    ctx.route("https://www.instagram.com/**",rota)
    rel=pg.evaluate("document.querySelector('.item-usuario a').getAttribute('rel')")
    ok("noopener" in rel and "noreferrer" in rel,"link do perfil tem rel=%r"%rel)
    with ctx.expect_page() as nova: pg.click('.item-usuario a')
    nova.value.wait_for_load_state()
    ok(len(vistos)==1 and not vistos[0],"o Instagram não recebe cabeçalho Referer | %r"%vistos)
    ok(nova.value.url.startswith("https://www.instagram.com/alguem.teste/"),"abre o perfil certo | %s"%nova.value.url)
    ok(pg.evaluate("window.opener===null && true"),"página original segue aberta")
    ok(errs==[],"sem erros de JavaScript | %s"%errs)
    br.close()
