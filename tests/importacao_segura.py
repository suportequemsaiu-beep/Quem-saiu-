import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixtures
import json, zipfile
from playwright.sync_api import sync_playwright
T=tempfile.mkdtemp(prefix="quemsaiu-")+"/"
Z=T+"z/"
fixtures.criar_zips(Z)
U="http://127.0.0.1:8765/index.html"
def ok(c,m): print(("OK    " if c else "FALHA ")+m)
def seg(n): return {"string_list_data":[{"value":n,"href":"https://www.instagram.com/"+n,"timestamp":1}]}
def fol(n): return {"title":n,"string_list_data":[{"href":"https://www.instagram.com/_u/"+n,"timestamp":1}]}
def w(name,obj): open(T+name,"w").write(json.dumps(obj)); return T+name
def mkzip(path,files):
    with zipfile.ZipFile(path,"w") as z:
        for k,v in files.items(): z.writestr(k,json.dumps(v))
    return path
L=lambda n:["u%03d"%i for i in range(n)]
def F(names): return w("followers_1.json",[seg(x) for x in names])
def G(names,nome="following.json"): return w(nome,{"relationships_following":[fol(x) for x in names]})
with sync_playwright() as p:
    br=p.chromium.launch()
    def novo():
        ctx=br.new_context(viewport={"width":390,"height":844}); pg=ctx.new_page(); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("dialog",lambda d:d.accept())
        pg.goto(U); pg.wait_for_timeout(300); pg.click("#btnDescobrir"); pg.click("#btnComecar"); pg.wait_for_timeout(200)
        return ctx,pg,errs
    def imp(pg,files): pg.set_input_files("#inputArquivo",files); pg.wait_for_timeout(1300)
    def t(pg,s): return pg.evaluate("s=>document.querySelector(s).innerText",s)
    def n(pg): return len(json.loads(pg.evaluate("localStorage.getItem('quemsaiu_exportacoes')") or "[]"))
    def ultima(pg): return json.loads(pg.evaluate("localStorage.getItem('quemsaiu_exportacoes')"))[-1]
    # ---- item 1
    ctx,pg,errs=novo()
    A=L(100); B=L(90); S=L(10)
    imp(pg,[F(A),G(S)]); ok(n(pg)==1,"1a primeira importação guarda")
    imp(pg,[F(A),G(S)]); ok(n(pg)==1 and "ninguém saiu nem entrou" in t(pg,"#erroImport"),"1b mesma lista logo após a primeira: não guarda de novo e explica | %r"%t(pg,"#erroImport")[:70])
    ok(pg.evaluate("!!document.querySelector('#erroImport .aviso-info')"),"1b' o aviso usa o estilo neutro, não o de erro")
    imp(pg,[F(B),G(S)]); ok(n(pg)==2,"1c lista diferente guarda normalmente")
    ok("10" in t(pg,"#abasResultado").split("\n")[0],"1c comparação correta: 10 saíram")
    imp(pg,[F(B),G(S)]); ok(n(pg)==2,"1d importar B outra vez não cria 3ª lista | %s"%t(pg,"#statusImport")[:40])
    ok(t(pg,"#abasResultado").split("\n")[0].strip()=="10","1d comparação continua mostrando as 10 saídas de verdade")
    imp(pg,[F(B),G(S+["u050"])]); ok(n(pg)==2 and ultima(pg)["seguindo"]==S+["u050"] and "quem você segue foi atualizada" in t(pg,"#erroImport"),"1e seguidores iguais e 'seguindo' mudou: atualiza o 'seguindo' sem criar lista | %r"%t(pg,"#erroImport")[:120])
    imp(pg,[F(B[:50]),G(S)]); ok(n(pg)==3,"1f lista muito diferente ainda passa pelo aviso de lista menor e guarda (confirm aceito)")
    ctx.close()
    # ---- item 2
    ctx,pg,errs=novo()
    imp(pg,[Z+"instagram-a-2026-10-01-x.zip",Z+"instagram-a-2026-10-14-y.zip"]); ok(n(pg)==0 and "um arquivo .zip" in t(pg,"#erroImport"),"2a dois .zip: recusa e não guarda | %r"%t(pg,"#erroImport")[:60])
    imp(pg,[Z+"instagram-a-2026-10-01-x.zip",F(A)]); ok(n(pg)==0 and "um arquivo .zip" in t(pg,"#erroImport"),"2b .zip + .json: recusa")
    imp(pg,[F(A),F(B)]); ok(n(pg)==0 and "mais de uma vez" in t(pg,"#erroImport") and "followers_1.json" in t(pg,"#erroImport"),"2c o mesmo nome de arquivo duas vezes: recusa e diz qual | %r"%t(pg,"#erroImport")[:70])
    imp(pg,[Z+"instagram-a-2026-10-01-x.zip"]); ok(n(pg)==1 and t(pg,"#erroImport")=="","2d um .zip sozinho: funciona")
    ctx.close()
    ctx,pg,errs=novo()
    imp(pg,[F(A),G(S)]); ok(n(pg)==1,"2e followers_1.json + following.json juntos: continua funcionando")
    ctx.close()
    ctx,pg,errs=novo()
    sem=T+"semextensao"; open(sem,"wb").write(open(Z+"instagram-a-2026-10-01-x.zip","rb").read())
    imp(pg,[sem]); ok(n(pg)==1,"2f zip sem extensão (assinatura PK), sozinho: funciona")
    ctx.close()
    ctx,pg,errs=novo()
    p2=mkzip(T+"partes.zip",{"c/followers_1.json":[seg(x) for x in L(60)],"c/followers_2.json":[seg(x) for x in ["v%03d"%i for i in range(40)]],"c/following.json":{"relationships_following":[fol(x) for x in S]}})
    imp(pg,[p2]); ok(n(pg)==1 and len(ultima(pg)["seguidores"])==100,"2g um .zip com followers_1 e followers_2 normais: junta as duas partes (100)")
    ctx.close()
    # ---- item 3
    ctx,pg,errs=novo()
    imp(pg,[Z+"parcial.zip"]); ok(n(pg)==0 and "followers_2.json" in t(pg,"#erroImport"),"3a followers_2 em formato novo: para e diz o nome | %r"%t(pg,"#erroImport")[:70])
    imp(pg,[Z+"seguindo_estranho.zip"]); ok(n(pg)==0 and "following.json" in t(pg,"#erroImport"),"3b following em formato novo: para e diz o nome")
    p3=mkzip(T+"semseguir.zip",{"followers_1.json":[seg(x) for x in A],"following.json":{"relationships_following":[]}})
    imp(pg,[p3]); ok(n(pg)==1 and ultima(pg)["seguindo"]==[] and t(pg,"#erroImport")=="","3c quem não segue ninguém (lista vazia legítima): importa normalmente")
    ctx.close()
    ctx,pg,errs=novo()
    p4=mkzip(T+"followers_vazio.zip",{"followers_1.json":[],"following.json":{"relationships_following":[fol("a")]}})
    imp(pg,[p4]); ok(n(pg)==0 and "seguidores" in t(pg,"#erroImport"),"3d zero seguidores: continua avisando que não achou seguidores | %r"%t(pg,"#erroImport")[:60])
    ctx.close()
    ctx,pg,errs=novo(); ok(errs==[],"4 sem erros de JavaScript | %s"%errs); ctx.close()
    br.close()
