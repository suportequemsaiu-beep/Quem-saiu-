import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixtures
import json, os, time, zipfile
from playwright.sync_api import sync_playwright
B=tempfile.mkdtemp(prefix="quemsaiu-")+"/"
T=B
os.makedirs(B+"avaliacao/telas", exist_ok=True)
def seg(nomes): return json.dumps([{"string_list_data":[{"value":n,"href":"https://www.instagram.com/"+n}]} for n in nomes])
def sgd(nomes): return json.dumps({"relationships_following":[{"title":n,"string_list_data":[{"href":"https://www.instagram.com/_u/"+n}]} for n in nomes]})
def w(name,txt): open(T+name,"w").write(txt); return T+name
def novo(b,jszip=True,init=None):
    pg=b.new_page(viewport={"width":390,"height":844})
    if jszip: pass
    else: pg.route("**/jszip.min.js*",lambda r:r.abort())
    if init: pg.add_init_script(init)
    pg.goto("http://127.0.0.1:8765/index.html"); pg.wait_for_timeout(400)
    pg.click("#btnDescobrir"); pg.wait_for_timeout(500); pg.click("#btnComecar"); pg.wait_for_timeout(300); return pg
def enviar(pg,files,esp=1200):
    pg.set_input_files("#inputArquivo",files); pg.wait_for_timeout(esp)
def st(pg): return pg.evaluate("document.querySelector('#statusImport').innerText")
def er(pg): return pg.evaluate("document.querySelector('#erroImport').innerText")
def ok(c,m): print(("OK    " if c else "FALHA ")+m)
with sync_playwright() as p:
    b=p.chromium.launch()
    # T1 XSS
    pg=novo(b); pg.evaluate("window.__x=0")
    enviar(pg,[w("followers_1.json",seg(["<img src=x onerror=window.__x=1>"]+["normal%d"%i for i in range(19)])),w("following.json",sgd(["<img src=x onerror=window.__x=2>"]+["outra%d"%i for i in range(19)]))])
    ok(pg.evaluate("window.__x")==0,"T1 script malicioso NÃO executa")
    ok("<img src=x" in pg.evaluate("document.querySelector('#listaResultado').innerText"),"T1 o nome aparece como texto literal")
    ok(pg.evaluate("document.querySelectorAll('#listaResultado img').length")==0,"T1 nenhuma tag <img> injetada")
    pg.evaluate("window.__x=0"); pg.reload(); pg.wait_for_timeout(600); ok(pg.evaluate("window.__x||0")==0,"T1 ao reabrir com a lista guardada continua seguro"); pg.close()
    pg=novo(b); pg.evaluate("window.__x=0")
    enviar(pg,[w("followers_1.json",seg(["<img src=x onerror=window.__x=1>","normal"]))])
    ok(pg.evaluate("window.__x")==0 and "Nenhuma lista" in st(pg) and "formato do arquivo" in er(pg),"T1b lista metade maliciosa: recusada com aviso, nada executa e nada é guardado"); pg.close()
    # T2 só following
    pg=novo(b); enviar(pg,[w("following.json",sgd(["ana"]))])
    ok("Nenhuma lista" in st(pg) and "seguidores" in er(pg),"T2 só following.json: erro claro, nada guardado | %r"%er(pg)[:80]); pg.close()
    # T3 json qualquer
    pg=novo(b); enviar(pg,[w("blocked_profiles.json",seg(["fulano"]))])
    ok("Nenhuma lista" in st(pg) and er(pg)!="","T3 blocked_profiles.json recusado | %r"%er(pg)[:70]); pg.close()
    # T4 gravação falha
    pg=novo(b,init="Storage.prototype.setItem=function(){throw new Error('Quota')}")
    enviar(pg,[w("followers_1.json",seg(["a","b","c"])),w("following.json",sgd(["a"]))])
    ok("fecha" in er(pg) or "fechar" in er(pg),"T4 avisa que não conseguiu guardar | %r"%er(pg)[:70])
    ok("1 lista guardada" in st(pg) and "só enquanto" in st(pg),"T4 status honesto | %r"%st(pg))
    ok(pg.evaluate("document.querySelector('#cardResultado').style.display")=="block","T4 resultado aparece mesmo assim"); pg.close()
    # T5 lista incompleta
    nomes=["u%d"%i for i in range(30)]
    pg=novo(b); enviar(pg,[w("followers_1.json",seg(nomes))])
    msgs=[]; pg.once("dialog",lambda d:(msgs.append(d.message),d.dismiss()))
    enviar(pg,[w("followers_1.json",seg(nomes[:10]))])
    ok(len(msgs)==1 and "30" in msgs[0] and "10" in msgs[0] and "1 lista guardada" in st(pg),"T5 pergunta antes de guardar lista bem menor; recusar mantém 1 lista"); pg.close()
    pg=novo(b); enviar(pg,[w("followers_1.json",seg(nomes))]); pg.once("dialog",lambda d:d.accept())
    enviar(pg,[w("followers_1.json",seg(nomes[:10]))]); ok("2 listas guardadas" in st(pg),"T5 aceitar guarda a lista"); pg.close()
    # T6 apagar
    pg=novo(b); enviar(pg,[w("followers_1.json",seg(["a","b"]))])
    pg.evaluate("caches.open('quemsaiu-compartilhado').then(c=>c.put('arquivo-compartilhado',new Response('x')))"); pg.wait_for_timeout(300)
    pg.once("dialog",lambda d:d.dismiss()); pg.locator("#btnApagar").scroll_into_view_if_needed(); pg.click("#btnApagar"); pg.wait_for_timeout(300)
    ok("1 lista guardada" in st(pg),"T6 cancelar NÃO apaga")
    pg.once("dialog",lambda d:d.accept()); pg.click("#btnApagar"); pg.wait_for_timeout(600)
    ok("Nenhuma lista" in st(pg),"T6 confirmar apaga a lista")
    ok(pg.evaluate("caches.has('quemsaiu-compartilhado')")==False,"T6 apaga também a cópia do arquivo recebido pelo Compartilhar"); pg.close()
    # T7 × na aba saiu
    pg=novo(b)
    enviar(pg,[w("followers_1.json",seg(["ana","bia","caio","duda"])),w("following.json",sgd(["ana","bia","caio"]))])
    enviar(pg,[w("followers_1.json",seg(["ana","duda","eva"])),w("following.json",sgd(["ana","bia","caio"]))])
    pg.click("[data-res=saiu]"); pg.wait_for_timeout(300)
    n=pg.evaluate("document.querySelectorAll('#listaResultado .btn-ignorar').length"); ok(n==2,"T7 aba 'Deixaram de te seguir' tem × (%d contas)"%n)
    ov=pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth"); ok(ov==0,"T7 sem rolagem lateral no celular")
    pg.locator("#listaResultado").screenshot(path=B+"avaliacao/telas/teste_x_saiu.png")
    pg.click("#listaResultado .btn-ignorar"); pg.wait_for_timeout(500)
    ok(pg.evaluate("document.querySelectorAll('#listaResultado .btn-ignorar').length")==1 and "1 conta escondida" in pg.evaluate("document.querySelector('#listaResultado').innerText"),"T7 clicar no × esconde e mostra '1 conta escondida'"); pg.close()
    # T8 desempenho
    pg=novo(b); gr=["user_%d"%i for i in range(50000)]
    enviar(pg,[w("followers_1.json",seg(gr))],esp=3000)
    t=time.time(); enviar(pg,[w("followers_1.json",seg(gr[1000:]+["novo_%d"%i for i in range(500)]))],esp=100)
    pg.wait_for_function("document.querySelector('#statusImport').innerText.includes('2 listas')",timeout=60000)
    print("      T8 2ª importação de 50 mil seguidores: %.1fs | %s"%(time.time()-t,pg.evaluate("document.querySelector('#abasResultado').innerText.replace(/\\n/g,' ')"))); pg.close()
    # T9 zip / sem JSZip
    z=T+"instagram-teste.zip"
    with zipfile.ZipFile(z,"w") as zf:
        zf.writestr("connections/followers_and_following/followers_1.json",seg(["a","b","c"])); zf.writestr("connections/followers_and_following/following.json",sgd(["a","x"]))
    pg=novo(b); enviar(pg,[z]); ok("1 lista guardada" in st(pg) and "3 seguidores" in st(pg),"T9 .zip lido normalmente | %s"%st(pg)); pg.close()
    pg=novo(b,jszip=False); enviar(pg,[z]); ok("leitor" in er(pg),"T9 sem JSZip (sem internet): mensagem clara | %r"%er(pg)[:80]); pg.close()
    # T10 json quebrado
    pg=novo(b); enviar(pg,[w("followers_1.json","{ isto nao e json")]); ok("formato JSON" in er(pg) and "Unexpected" not in er(pg),"T10 JSON quebrado: mensagem padrão em português | %r"%er(pg)[:70]); pg.close()
    b.close()
