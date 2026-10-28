import os, sys, json, zipfile, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
def ok(c, m): print(("OK    " if c else "FALHA ") + m)
D = tempfile.mkdtemp(prefix="quemsaiu-grande-")
def seg(nomes): return json.dumps([{"string_list_data": [{"value": n, "href": "https://www.instagram.com/" + n}]} for n in nomes])
def sgd(nomes): return json.dumps({"relationships_following": [{"title": n, "string_list_data": [{"href": "https://www.instagram.com/_u/" + n}]} for n in nomes]})
SEGUIDORES = ["amigo%d" % i for i in range(30)]
SEGUINDO = ["conta%d" % i for i in range(25)]
LIXO = os.urandom(1024 * 1024) * 110  # ~110 MB: passa do limite que o site lê na memória
def zip_grande(nome, com_dados=True, entradas_extras=0):
    c = os.path.join(D, nome)
    with zipfile.ZipFile(c, "w", zipfile.ZIP_STORED, allowZip64=True) as z:
        z.writestr("your_instagram_activity/media/video_enorme.mp4", LIXO)
        for i in range(entradas_extras):
            z.writestr("posts/f%05d.jpg" % i, b"x")
        if com_dados:
            z.writestr("connections/followers_and_following/followers_1.json", seg(SEGUIDORES), zipfile.ZIP_DEFLATED)
            z.writestr("connections/followers_and_following/following.json", sgd(SEGUINDO), zipfile.ZIP_DEFLATED)
            z.writestr("connections/followers_and_following/recently_unfollowed_profiles.json", seg(["nao_deve_entrar"]), zipfile.ZIP_DEFLATED)
    return c

def abrir(b):
    pg = b.new_page(viewport={"width": 390, "height": 844}); pg.on("pageerror", lambda e: erros.append(str(e)))
    pg.goto("http://127.0.0.1:8765/index.html"); pg.wait_for_timeout(300)
    pg.click("#btnDescobrir"); pg.wait_for_timeout(400); pg.click("#btnComecar"); pg.wait_for_timeout(300)
    return pg
def enviar(pg, c, esp=3500):
    pg.set_input_files("#inputArquivo", c); pg.wait_for_timeout(esp)
def st(pg): return pg.evaluate("document.querySelector('#statusImport').innerText")
def er(pg): return pg.evaluate("document.querySelector('#erroImport').innerText")
def guardado(pg): return pg.evaluate("JSON.parse(localStorage.getItem('quemsaiu_exportacoes')||'[]')")

erros = []
with sync_playwright() as p:
    b = p.chromium.launch()

    c = zip_grande("grande.zip"); ok(os.path.getsize(c) > 100 * 1024 * 1024, "G0 o .zip de teste passa de 100 MB")
    pg = abrir(b); enviar(pg, c)
    g = guardado(pg)
    ok(len(g) == 1 and len(g[0]["seguidores"]) == 30 and len(g[0]["seguindo"]) == 25, "G1 .zip grande: lê só seguidores e seguindo (30 e 25) | %r" % [(len(x["seguidores"]), len(x["seguindo"])) for x in g])
    ok(not any("nao_deve_entrar" in x["seguidores"] + x["seguindo"] for x in g), "G2 ignora os outros arquivos do .zip")
    ok(er(pg) == "", "G3 sem mensagem de erro | %r" % er(pg))
    pg.close()

    c = zip_grande("grande64.zip", entradas_extras=70000)
    pg = abrir(b); enviar(pg, c, 6000)
    g = guardado(pg)
    ok(len(g) == 1 and len(g[0]["seguidores"]) == 30 and len(g[0]["seguindo"]) == 25, "G4 .zip grande com mais de 65 mil arquivos (Zip64) também funciona | %r" % er(pg)[:120])
    pg.close()

    c = zip_grande("sem_dados.zip", com_dados=False)
    pg = abrir(b); enviar(pg, c)
    ok("Não encontrei os dados de seguidores" in er(pg), "G5 .zip grande sem seguidores: mensagem clara | %r" % er(pg)[:100])
    pg.close()

    c = os.path.join(D, "quebrado.zip"); open(c, "wb").write(LIXO)
    pg = abrir(b); enviar(pg, c)
    ok("muito grande" in er(pg) and guardado(pg) == [], "G6 arquivo grande quebrado: mensagem clara e nada guardado | %r" % er(pg)[:100])
    pg.close()
    ok(erros == [], "G7 sem erros de JavaScript | %r" % erros)
    b.close()
for f in os.listdir(D): os.remove(os.path.join(D, f))
os.rmdir(D)
