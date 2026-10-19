import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixtures
import json
from playwright.sync_api import sync_playwright
T=tempfile.mkdtemp(prefix="quemsaiu-")+"/"
def ok(c,m): print(("OK    " if c else "FALHA ")+m)
def item(n): return {"title":n,"string_list_data":[{"href":"https://www.instagram.com/_u/"+n,"timestamp":1}]}
def segitem(n): return {"string_list_data":[{"value":n,"href":"https://www.instagram.com/"+n,"timestamp":1}]}
def w(name,obj): open(T+name,"w").write(json.dumps(obj)); return T+name

with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844}); errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto("http://127.0.0.1:8765/index.html"); pg.wait_for_timeout(400)
    def ex(obj,nome="x.json"):
        return pg.evaluate("""([o,n])=>{try{return {ok:extrairUsuarios(o,n)}}catch(e){return {erro:e.message,amigavel:!!e.amigavel}}}""",[obj,nome])
    r=ex([segitem("a"),segitem("b")]); ok(r.get("ok")==["a","b"],"A lista direta de seguidores (formato atual)")
    r=ex({"relationships_following":[item("u1"),item("u2")]}); ok(r.get("ok")==["u1","u2"],"B objeto relationships_following (formato atual)")
    r=ex({"meta":[{"x":1},{"y":2}],"relationships_following":[item("u1")]}); ok(r.get("ok")==["u1"],"C lista de metadados antes da lista certa: pega a certa (antes pegava a errada)")
    r=ex({"relationships_following":[item("u1")],"outra":[item("z")]}); ok(r.get("ok")==["u1"],"E duas listas de contas: usa a de nome conhecido")
    r=ex({"aaa":[item("u1")],"bbb":[item("z")]},"following.json"); ok("erro" in r and r["amigavel"] and "following.json" in r["erro"],"D duas listas de contas sem nome conhecido: para com aviso | %r"%(r.get("erro","")[:60],))
    r=ex({"x":[{"foo":1}]},"following.json"); ok("erro" in r and r["amigavel"],"F lista sem cara de conta e sem nome conhecido: para com aviso (antes devolvia vazio em silêncio)")
    r=ex([{"title":"12:30 pm","string_list_data":[]},{"title":"Fulano de Tal","string_list_data":[]},{"title":"outra coisa qualquer","string_list_data":[]}],"followers_1.json")
    ok("erro" in r and r["amigavel"],"G nomes que não parecem usuário: para com aviso")
    r=ex([{"title":"","string_list_data":[]},{"title":"","string_list_data":[]}],"followers_1.json"); ok("erro" in r and r["amigavel"],"H itens que não rendem nenhum nome: para com aviso")
    r=ex({"relationships_following":[]}); ok(r.get("ok")==[],"I quem você segue vazio é válido (conta que não segue ninguém)")
    r=ex([segitem("ana.silva_1"),segitem("b.c")]); ok(r.get("ok")==["ana.silva_1","b.c"],"J nomes com ponto e sublinhado passam")
    # nomes misturados (ponto levantado pelo ChatGPT)
    def mistura(v,i): return [item("ok_%d"%k) for k in range(v)]+[item("nome estranho %d"%k) for k in range(i)]
    r=ex(mistura(6,4),"followers_1.json"); ok("erro" in r and r["amigavel"],"N 60% válidos / 40% estranhos: agora PARA com aviso (antes passava)")
    r=ex(mistura(8,2),"followers_1.json"); ok("erro" in r,"N2 80% válidos: para com aviso")
    r=ex(mistura(19,1),"followers_1.json"); ok(len(r.get("ok",[]))==20 and "nome estranho 0" in r["ok"],"N3 95%% válidos: passa e o nome estranho NÃO é descartado em silêncio | %d nomes"%len(r.get("ok",[])))
    r=ex(mistura(9,1),"followers_1.json"); ok(len(r.get("ok",[]))==10,"N4 exatamente 90% válidos: passa")
    # formatos diferentes do esperado
    for nome,val,esp in [("lista vazia []",[],[]),("objeto com lista vazia",{"relationships_following":[]},[])]:
        r=ex(val); ok(r.get("ok")==esp,"O %s: continua valendo como lista vazia"%nome)
    for nome,val in [("null",None),("número",5),("texto","abc"),("objeto vazio",{})]:
        r=ex(val,"following.json"); ok("erro" in r and r["amigavel"],"O %s: agora para com aviso (antes devolvia vazio em silêncio)"%nome)
    for nome,val in [("lista de textos",["a","b"]),("lista de números",[1,2,3]),("lista de listas",[[1],[2]])]:
        r=ex(val,"followers_1.json"); ok("erro" in r and r["amigavel"],"P %s: para com aviso"%nome)
    r=ex({"a":{"b":[item("x")]}},"following.json"); ok("erro" in r and r["amigavel"],"Q lista escondida dentro de outro objeto: não adivinha, para com aviso")
    r=ex({"relationships_followers":[segitem("f1")],"relationships_following":[item("g1")]},"x.json"); ok("erro" in r,"R duas listas, as duas de nome conhecido: ambíguo, para com aviso")
    # pela tela
    pg.click("#btnDescobrir"); pg.wait_for_timeout(400); pg.click("#btnComecar"); pg.wait_for_timeout(300)
    pg.set_input_files("#inputArquivo",[w("followers_1.json",[segitem("a"),segitem("b")]),w("following.json",{"aaa":[item("u1")],"bbb":[item("z")]})]); pg.wait_for_timeout(1200)
    txt=pg.evaluate("document.querySelector('#erroImport').innerText"); st=pg.evaluate("document.querySelector('#statusImport').innerText")
    ok("formato do arquivo following.json" in txt and "Nenhuma lista" in st,"K pela tela: aviso com o nome do arquivo e nada guardado | %r"%txt[:70])
    pg.set_input_files("#inputArquivo",[w("followers_1.json",[segitem("a"),segitem("b")]),w("following.json",{"relationships_following":[item("a")]})]); pg.wait_for_timeout(1200)
    st=pg.evaluate("document.querySelector('#statusImport').innerText"); ok("1 lista guardada" in st and "2 seguidores" in st,"L pela tela: arquivo normal continua funcionando | %s"%st)
    ok(errs==[],"M sem erros de JavaScript | %s"%errs)
    b.close()
