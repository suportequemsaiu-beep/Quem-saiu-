import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixtures
import json
from playwright.sync_api import sync_playwright
T=tempfile.mkdtemp(prefix="quemsaiu-")+"/"
U="http://127.0.0.1:8765/index.html"; CH="quemsaiu_exportacoes"; CI="quemsaiu_ignoradas"
def ok(c,m): print(("OK    " if c else "FALHA ")+m)
def seg(n): return {"string_list_data":[{"value":n,"href":"https://www.instagram.com/"+n,"timestamp":1}]}
def w(name,obj): open(T+name,"w").write(json.dumps(obj)); return T+name
with sync_playwright() as p:
    br=p.chromium.launch()
    def novo(chave=None,valor=None):
        ctx=br.new_context(viewport={"width":390,"height":844}); pg=ctx.new_page(); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("dialog",lambda d:d.accept())
        if valor is not None: pg.add_init_script("try{if(!sessionStorage.getItem('j'))localStorage.setItem(%s,%s);sessionStorage.setItem('j','1')}catch(e){}"%(json.dumps(chave),json.dumps(valor)))
        pg.goto(U); pg.wait_for_timeout(1200); return ctx,pg,errs
    ruins=[("objeto no lugar de lista",'{"a":1}'),("texto",'"abc"'),("lista com null",'[null]'),("sem 'seguidores'",'[{"data":"2026-01-01T00:00:00Z"}]'),
           ("JSON quebrado",'{{{'),("seguidores como objeto",'[{"data":"2026-01-01T00:00:00Z","seguidores":{"v":2}}]'),
           ("seguidores com números",'[{"data":"2026-01-01T00:00:00Z","seguidores":[1,2,3]}]')]
    for nome,val in ruins:
        ctx,pg,errs=novo(CH,val)
        reg=pg.evaluate("navigator.serviceWorker.getRegistration().then(r=>!!r)")
        st=pg.evaluate("document.querySelector('#statusImport').innerText")
        ok(errs==[] and reg and st.startswith("Nenhuma lista"),"4a dado ruim (%s): sem erro, service worker registrado, status normal | erros=%s reg=%s"%(nome,errs[:1],reg))
        pg.click("#btnDescobrir"); pg.click("#btnComecar"); pg.wait_for_timeout(200)
        pg.set_input_files("#inputArquivo",[w("followers_1.json",[seg("a"),seg("b")])]); pg.wait_for_timeout(1200)
        st=pg.evaluate("document.querySelector('#statusImport').innerText"); vis=pg.evaluate("document.querySelector('#btnApagar').offsetParent!==null")
        data=json.loads(pg.evaluate("localStorage.getItem('%s')"%CH))
        ok(st.startswith("1 lista guardada") and vis and len(data)==1 and data[0].get("v")==1,"4b depois, importar funciona, 'Apagar' aparece e a lista nova leva v=1 | %s"%st[:30])
        ctx.close()
    boa={"data":"2026-10-01T10:00:00Z","seguidores":["a","b"],"seguindo":["a"]}
    ctx,pg,errs=novo(CH,json.dumps([boa,None,{"data":1}]))
    ok(errs==[] and pg.evaluate("document.querySelector('#statusImport').innerText").startswith("1 lista guardada"),"4c mistura de uma lista boa com itens ruins: mantém a boa | %s"%pg.evaluate("document.querySelector('#statusImport').innerText")[:30]); ctx.close()
    antiga={"data":"2026-10-01T10:00:00Z","seguidores":["a","b"]}
    ctx,pg,errs=novo(CH,json.dumps([antiga]))
    ok(errs==[] and pg.evaluate("document.querySelector('#statusImport').innerText").startswith("1 lista guardada"),"4d lista antiga sem 'v' e sem 'seguindo' continua valendo (compatível)"); ctx.close()
    for nome,val in [("objeto",'{"a":1}'),("misturada",'[1,"x",null]')]:
        ctx,pg,errs=novo(CI,val)
        pg.evaluate("localStorage.setItem('%s',JSON.stringify([{data:'2026-10-01T10:00:00Z',seguidores:['a','b','c'],seguindo:[]},{data:'2026-10-14T10:00:00Z',seguidores:['a'],seguindo:[]}]))"%CH)
        pg.reload(); pg.wait_for_timeout(500)
        ok(errs==[],"4e contas escondidas ruins (%s): sem erro | %s"%(nome,errs[:1])); ctx.close()
    br.close()
