import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixtures
import json
from playwright.sync_api import sync_playwright
T=tempfile.mkdtemp(prefix="quemsaiu-")+"/"
U="http://127.0.0.1:8765/index.html"
fixtures.criar_zips(T+"z/")
def ok(c,m): print(("OK    " if c else "FALHA ")+m)
def seg(n): return {"string_list_data":[{"value":n,"href":"https://www.instagram.com/"+n,"timestamp":1}]}
def fol(n): return {"title":n,"string_list_data":[{"href":"https://www.instagram.com/_u/"+n,"timestamp":1}]}
def w(name,obj): open(T+name,"w").write(json.dumps(obj)); return T+name
with sync_playwright() as p:
    br=p.chromium.launch()
    def novo():
        ctx=br.new_context(viewport={"width":390,"height":844}); pg=ctx.new_page(); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("dialog",lambda d:d.accept())
        pg.goto(U); pg.wait_for_timeout(1500); pg.reload(); pg.wait_for_timeout(500); return ctx,pg,errs
    ctx,pg,errs=novo(); pg.click("#btnDescobrir"); pg.click("#btnComecar"); pg.wait_for_timeout(200)
    t=lambda s: pg.evaluate("s=>document.querySelector(s).innerText",s)
    pg.set_input_files("#inputArquivo",[w("followers_1 (1).json",[seg("a"),seg("b")]),w("following (2).json",{"relationships_following":[fol("a")]})]); pg.wait_for_timeout(1200)
    ok("1 lista guardada" in t("#statusImport") and "2 seguidores" in t("#statusImport"),"5a nomes com ' (1)' do Android são aceitos | %s"%t("#statusImport")[:50])
    ctx.close()
    ctx,pg,errs=novo(); pg.click("#btnDescobrir"); pg.click("#btnComecar"); pg.wait_for_timeout(200)
    pg.set_input_files("#inputArquivo",[w("followers_1 (1).json",[seg("a")]),w("followers_1.json",[seg("b")])]); pg.wait_for_timeout(1200)
    ok("mais de uma vez" in t("#erroImport") and "Nenhuma lista" in t("#statusImport"),"5b followers_1.json + followers_1 (1).json juntos: recusa como repetido")
    ctx.close()
    # cópia temporária órfã
    ctx,pg,errs=novo()
    pg.evaluate("caches.open('quemsaiu-compartilhado').then(c=>c.put('arquivo-compartilhado',new Response('x')))")
    antes=pg.evaluate("caches.has('quemsaiu-compartilhado')")
    pg.goto(U); pg.wait_for_timeout(800)
    depois=pg.evaluate("caches.has('quemsaiu-compartilhado')")
    ok(antes and not depois,"5c abrir o site sem vir do Compartilhar apaga a cópia temporária que sobrou | antes=%s depois=%s"%(antes,depois))
    # fluxo de compartilhar continua funcionando
    z=list(open(T+"z/instagram-a-2026-10-01-x.zip","rb").read())
    pg.evaluate("""z=>{var f=document.createElement('form');f.method='POST';f.action='receber';f.enctype='multipart/form-data';
      var i=document.createElement('input');i.type='file';i.name='arquivo';var dt=new DataTransfer();dt.items.add(new File([new Uint8Array(z)],'instagram-a-2026-10-01-x.zip',{type:'application/zip'}));i.files=dt.files;f.appendChild(i);document.body.appendChild(f);f.submit();}""",z)
    pg.wait_for_timeout(2500)
    ok("1 lista guardada" in t("#statusImport") and "100 seguidores" in t("#statusImport"),"5d Compartilhar com arquivo bom continua importando | %s"%t("#statusImport")[:60])
    ok(not pg.evaluate("caches.has('quemsaiu-compartilhado').then(async h=>h?(await (await caches.open('quemsaiu-compartilhado')).keys()).length>0:false)"),"5e e a cópia temporária é apagada depois da leitura")
    ok(errs==[],"sem erros de JavaScript | %s"%errs)
    br.close()
