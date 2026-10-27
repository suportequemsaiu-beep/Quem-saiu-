import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixtures
import json, re, time, zipfile, urllib.request, html as H
from playwright.sync_api import sync_playwright
B=tempfile.mkdtemp(prefix="quemsaiu-")+"/"
T=B
os.makedirs(B+"avaliacao/telas", exist_ok=True)
URL="http://127.0.0.1:8765/index.html"
def seg(n): return json.dumps([{"string_list_data":[{"value":x,"href":"https://www.instagram.com/"+x}]} for x in n])
def sgd(n): return json.dumps({"relationships_following":[{"title":x,"string_list_data":[{"href":"https://www.instagram.com/_u/"+x}]} for x in n]})
def zipar(nome, seguidores, seguindo=()):
    p=T+nome
    with zipfile.ZipFile(p,"w") as zf:
        zf.writestr("connections/followers_and_following/followers_1.json",seg(seguidores))
        zf.writestr("connections/followers_and_following/following.json",sgd(seguindo))
    return p
def ok(c,m): print(("OK    " if c else "FALHA ")+m)
def abrir(b, w=390, h=844):
    pg=b.new_page(viewport={"width":w,"height":h})
    pg.erros=[]; pg.externos=[]
    pg.on("pageerror",lambda e:pg.erros.append(str(e)))
    pg.on("console",lambda m:pg.erros.append(m.text) if m.type=="error" else None)
    pg.on("request",lambda r:pg.externos.append(r.url) if not r.url.startswith("http://127.0.0.1") and not r.url.startswith("data:") else None)
    pg.goto(URL); pg.wait_for_timeout(500); return pg
def comecar(pg):
    pg.click("#btnDescobrir"); pg.wait_for_timeout(500); pg.click("#btnComecar"); pg.wait_for_timeout(300)
def enviar(pg,files,esp=1200):
    pg.set_input_files("#inputArquivo",files); pg.wait_for_timeout(esp)
def st(pg): return pg.evaluate("document.querySelector('#statusImport').innerText")

cru=urllib.request.urlopen(URL).read().decode("utf-8")

with sync_playwright() as p:
    b=p.chromium.launch()

    # N1 estático: textos novos estão no HTML cru (o que um robô vê sem JavaScript)
    ok("sem risco de banimento" not in cru.lower(),"N1 'sem risco de banimento' não aparece em lugar nenhum do index.html")
    ok("cdnjs" not in cru,"N1 index.html não chama mais o CDN")
    ok("jszip.min.js" in cru,"N1 JSZip vem do próprio site")
    for frase in ["Funciona no iPhone?","Quantas listas ficam guardadas?","O Quem Saiu acessa a minha conta do Instagram?","E se o Instagram mudar o formato do arquivo?",
                  "No Chrome do Android","O tempo para o arquivo ficar pronto varia",
                  "Remove as listas guardadas e as contas escondidas","Peça um novo arquivo ao Instagram","Toque em <b>Notificar</b>","está apagado. O que faço?"]:
        ok(frase in cru,"N1 HTML cru contém: "+frase)
    ok("adamsandler" not in cru and "adamsandler" not in open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"script.js"),encoding="utf-8").read().lower(),"N1 @adamsandler removido")

    # N2 Ajuda: 18 <details>, respostas no HTML cru iguais às do JSON-LD
    det=re.findall(r'<summary class="faq-q">(.*?)<span aria-hidden="true">\+</span></summary>\s*<p class="faq-a">(.*?)</p>',cru,re.S)
    ok(len(det)==18,"N2 18 perguntas da Ajuda escritas em HTML (%d)"%len(det))
    ld=json.loads(re.search(r'<script type="application/ld\+json">\n(.*?)\n</script>',cru,re.S).group(1))
    ent=ld[1]["mainEntity"]
    iguais=all(H.unescape(q)==e["name"] and H.unescape(a)==e["acceptedAnswer"]["text"] for (q,a),e in zip(det,ent)) and len(ent)==len(det)
    ok(iguais,"N2 JSON-LD tem exatamente as mesmas 18 perguntas e respostas da Ajuda")
    ok("Navegadores modernos" in ld[0]["operatingSystem"] and "Qualquer navegador" not in cru,"N2 operatingSystem sem 'Qualquer navegador'")

    # N3 página: sem requisições externas, sem erros, bloco visível, amostra
    pg=abrir(b)
    ok("vale-saber" not in cru and pg.locator(".vale-saber").count()==0,"N3 bloco 'O que vale saber antes de começar' removido da tela inicial")
    pg.screenshot(path=B+"avaliacao/telas/n_home_inicio.png",full_page=True)
    pg.click("#btnDescobrir"); pg.wait_for_timeout(500)
    pg.click("[data-lista=naoSegue]"); pg.wait_for_timeout(200)
    ok("@yuri22" in pg.evaluate("document.querySelector('#listaProva').innerText"),"N3 amostra mostra @yuri22")
    pg.screenshot(path=B+"avaliacao/telas/n_home_revelado.png",full_page=True)
    ok(pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")==0,"N3 sem rolagem lateral (celular)")
    # Ajuda
    pg.click("[data-tab=ajuda]"); pg.wait_for_timeout(300)
    s=pg.locator("#ajuda summary.faq-q").first
    ok(pg.evaluate("document.querySelectorAll('#ajuda details[open]').length")==0,"N3 Ajuda começa toda recolhida")
    pg.locator("#ajuda summary", has_text="Funciona no iPhone?").click(); pg.wait_for_timeout(250)
    ok(pg.is_visible("text=Ainda não testamos no iPhone"),"N3 tocar na pergunta abre a resposta")
    pg.screenshot(path=B+"avaliacao/telas/n_ajuda_aberta.png",full_page=True)
    pg.locator("#ajuda summary", has_text="Funciona no iPhone?").click(); pg.wait_for_timeout(250)
    ok(not pg.is_visible("text=Ainda não testamos no iPhone"),"N3 tocar de novo recolhe")
    ok(pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")==0,"N3 Ajuda sem rolagem lateral")
    ok(pg.externos==[],"N3 nenhuma requisição para fora do site | %s"%pg.externos)
    ok(pg.erros==[],"N3 sem erros de JavaScript/console | %s"%pg.erros)
    pg.close()

    # N4 status com 1 e 2 listas + explicação das abas + nota do apagar
    pg=abrir(b); comecar(pg)
    enviar(pg,[zipar("instagram-ana-2026-10-01-aaa.zip",["a","b","c","d"],["a","b","x"])])
    ok("importe um arquivo mais novo para comparar" in st(pg),"N4 1 lista: status pede um arquivo mais novo | %s"%st(pg))
    ok(pg.inner_text("#listaResultado .explica-aba")=="Quem você segue e não te segue de volta.","N4 aba 'Não te seguem de volta' explicada")
    enviar(pg,[zipar("instagram-ana-2026-10-10-bbb.zip",["a","b","e"],["a","b","x"])])
    ok("2 listas" in st(pg) and "importe um arquivo mais novo" not in st(pg),"N4 2 listas: status sem o pedido | %s"%st(pg))
    pg.click("[data-res=saiu]"); pg.wait_for_timeout(250)
    ok("O arquivo não diz o motivo" in pg.inner_text("#listaResultado .explica-aba"),"N4 aba 'Deixaram de te seguir' explicada")
    pg.click("[data-res=entrou]"); pg.wait_for_timeout(250)
    ok(pg.inner_text("#listaResultado .explica-aba").startswith("Estão na lista atual e não estavam na anterior"),"N4 aba 'Começaram a te seguir' explicada")
    pg.locator(".nota-apagar").scroll_into_view_if_needed()
    ok(pg.is_visible(".nota-apagar"),"N4 nota embaixo do botão de apagar visível")
    pg.locator("#cardResultado").screenshot(path=B+"avaliacao/telas/n_resultado.png")
    ok(pg.erros==[],"N4 sem erros de JavaScript | %s"%pg.erros)
    pg.close()

    # N5 arquivo mais antigo
    pg=abrir(b); comecar(pg)
    enviar(pg,[zipar("instagram-ana-2026-10-10-aaa.zip",["a","b","c"],["a"])])
    msgs=[]; pg.once("dialog",lambda d:(msgs.append(d.message),d.dismiss()))
    enviar(pg,[zipar("instagram-ana-2026-10-01-bbb.zip",["a","b","c","d"],["a"])])
    ok(len(msgs)==1 and "01/10/2026" in msgs[0] and "10/10/2026" in msgs[0] and "1 lista guardada" in st(pg),"N5 arquivo mais antigo: pergunta e, ao recusar, não guarda | %r"%(msgs[:1],))
    pg.once("dialog",lambda d:d.accept())
    enviar(pg,[zipar("instagram-ana-2026-10-01-bbb.zip",["a","b","c","d"],["a"])])
    ok("2 listas" in st(pg),"N5 aceitar guarda mesmo assim")
    pg.close()
    pg=abrir(b); comecar(pg)
    enviar(pg,[zipar("instagram-ana-2026-10-10-aaa.zip",["a","b","c"],["a"])])
    msgs=[]; pg.on("dialog",lambda d:(msgs.append(d.message),d.accept()))
    enviar(pg,[zipar("instagram-ana-2026-10-10-ccc.zip",["a","b"],["a"])])
    enviar(pg,[zipar("instagram-ana-2026-10-20-ddd.zip",["a","b","z"],["a"])])
    enviar(pg,[zipar("instagram-sem-data.zip",["a","b","z","y"],["a"])])
    ok(msgs==[] and "4 listas" in st(pg),"N5 mesma data, mais nova ou nome sem data: não pergunta nada | %s"%msgs)
    pg.close()

    # N6 lista grande
    def grande(n_seg, mudam, tag):
        pg=abrir(b); comecar(pg)
        base=["user_%d"%i for i in range(n_seg)]
        t0=time.time(); enviar(pg,[zipar("instagram-big-2026-10-01-x.zip",base,base[:800])],esp=500)
        pg.wait_for_function("document.querySelector('#statusImport').innerText.includes('lista')",timeout=120000)
        t1=time.time()-t0
        novo=base[mudam:]+["novo_%d"%i for i in range(mudam)]
        t0=time.time(); enviar(pg,[zipar("instagram-big-2026-10-10-y.zip",novo,base[:800])],esp=300)
        pg.wait_for_function("document.querySelector('#statusImport').innerText.includes('2 listas')",timeout=180000)
        t2=time.time()-t0
        abas=pg.evaluate("document.querySelector('#abasResultado').innerText.replace(/\\n/g,' ')")
        t0=time.time(); pg.click("[data-res=saiu]"); pg.wait_for_timeout(100)
        nli=pg.evaluate("document.querySelectorAll('#listaResultado li').length"); t3=time.time()-t0
        print("      %s: 1ª importação %.1fs | 2ª importação %.1fs | abrir aba 'saiu' (%d linhas) %.1fs | %s | erros=%s"%(tag,t1,t2,nli,t3,abas,pg.erros))
        pg.close()
    grande(300000, 2000, "300 mil seguidores, 2 mil mudam")
    grande(300000, 60000, "300 mil seguidores, 60 mil mudam (caso extremo)")
    b.close()
