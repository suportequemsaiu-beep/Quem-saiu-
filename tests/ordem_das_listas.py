# A ordem das listas vale pela data real (nome do .zip ou seguidor mais recente), não pela ordem de envio;
# com 3 ou mais listas, compara a mais antiga com a mais nova.
import os, sys, json, zipfile, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
U = "http://127.0.0.1:8765/index.html"
T = tempfile.mkdtemp(prefix="quemsaiu-ordem-") + "/"
falhas = 0
def ok(c, m):
    global falhas
    print(("OK    " if c else "FALHA ") + m)
    if not c: falhas += 1
def seg(nomes, ts=None):
    return json.dumps([{"string_list_data": [dict({"value": x, "href": "https://www.instagram.com/" + x}, **({"timestamp": ts[x]} if ts and x in ts else {}))]} for x in nomes])
def zipar(nome, seguidores, ts=None):
    with zipfile.ZipFile(T + nome, "w") as zf:
        zf.writestr("connections/followers_and_following/followers_1.json", seg(seguidores, ts))
        zf.writestr("connections/followers_and_following/following.json", json.dumps({"relationships_following": []}))
    return T + nome
def json_seg(nome, seguidores, ts=None):
    os.makedirs(T + nome.split("|")[0], exist_ok=True)
    p = T + nome.split("|")[0] + "/followers_1.json"
    open(p, "w").write(seg(seguidores, ts)); return p
def novo(b):
    pg = b.new_page(viewport={"width": 390, "height": 844}); pg.erros = []; pg.dialogos = []
    pg.on("pageerror", lambda e: pg.erros.append(str(e)))
    pg.on("dialog", lambda d: (pg.dialogos.append(d.message), d.accept()))
    pg.goto(U); pg.wait_for_timeout(400)
    pg.click("#btnDescobrir"); pg.wait_for_timeout(400); pg.click("#btnComecar"); pg.wait_for_timeout(300)
    return pg
def enviar(pg, arq): pg.set_input_files("#inputArquivo", arq); pg.wait_for_timeout(1200)
def st(pg): return pg.inner_text("#statusImport")
def nomes(pg, aba):
    pg.click(".aba-res." + aba); pg.wait_for_timeout(250)
    return sorted(x.strip("@") for x in pg.eval_on_selector_all("#listaResultado .usuario-nome a", "e=>e.map(x=>x.textContent)"))

with sync_playwright() as p:
    b = p.chromium.launch()

    # 1) três listas com data no nome, enviadas fora de ordem
    pg = novo(b)
    enviar(pg, [zipar("instagram-ana-2026-11-20-nnn.zip", ["a", "b", "c", "e", "f"])])
    enviar(pg, [zipar("instagram-ana-2026-10-01-ooo.zip", ["a", "b", "c", "d"])])
    enviar(pg, [zipar("instagram-ana-2026-10-15-mmm.zip", ["a", "b", "c", "e", "x"])])
    tit = pg.inner_text("#tituloResultado")
    ok("3 listas" in st(pg), "1 as três listas ficam guardadas | %r" % st(pg)[:60])
    ok(pg.dialogos == [], "2 nenhuma pergunta de 'arquivo mais antigo' | %r" % pg.dialogos)
    ok("1 de out." in tit and "20 de nov." in tit and "15 de out." not in tit and tit.index("1 de out.") < tit.index("20 de nov."), "3 o título compara a mais antiga com a mais nova (as do meio ficam de fora) | %r" % tit)
    ok(nomes(pg, "saiu") == ["d"], "4 deixaram de te seguir: só quem estava na mais antiga e não está na mais nova")
    ok(nomes(pg, "entrou") == ["e", "f"], "5 começaram a te seguir: e, f (x, da lista do meio, não conta)")
    ok(not pg.erros, "6 sem erros de JS | %r" % pg.erros); pg.close()

    # 2) sem data no nome: vale o seguidor mais recente dentro do arquivo
    pg = novo(b)
    NOVO = 1763600000  # 2025-11-20
    VELHO = 1759300000  # 2025-10-01
    enviar(pg, json_seg("novo", ["a", "b", "c", "e"], {"e": NOVO, "a": VELHO - 5000}))
    enviar(pg, json_seg("velho", ["a", "b", "c", "d"], {"d": VELHO, "a": VELHO - 5000}))
    ok("2 listas" in st(pg) and pg.dialogos == [], "7 sem data no nome: duas listas, sem pergunta | %r %r" % (st(pg)[:40], pg.dialogos))
    ok(nomes(pg, "saiu") == ["d"] and nomes(pg, "entrou") == ["e"], "8 enviada fora de ordem, a ordem vem do seguidor mais recente: saiu d, entrou e")
    pg.close()

    # 3) listas já guardadas antes (sem nenhuma pista): continua valendo a ordem de envio
    pg = novo(b)
    antigas = [{"v": 1, "data": "2026-10-01T10:00:00.000Z", "seguidores": ["a", "b", "c"], "seguindo": []},
               {"v": 1, "data": "2026-10-20T10:00:00.000Z", "seguidores": ["a", "b", "z"], "seguindo": []}]
    pg.evaluate("d=>localStorage.setItem('quemsaiu_exportacoes',JSON.stringify(d))", antigas); pg.reload(); pg.wait_for_timeout(500)
    pg.click("#btnDescobrir"); pg.wait_for_timeout(300); pg.click("#btnComecar"); pg.wait_for_timeout(300); pg.click("#btnComparar"); pg.wait_for_timeout(500)
    ok(nomes(pg, "saiu") == ["c"] and nomes(pg, "entrou") == ["z"], "9 listas antigas sem pista seguem pela ordem de envio: saiu c, entrou z")
    ok(not pg.erros, "10 sem erros de JS | %r" % pg.erros); pg.close()
    b.close()
print("OK=%d FALHAS=%d" % (0, falhas)); raise SystemExit(1 if falhas else 0)
