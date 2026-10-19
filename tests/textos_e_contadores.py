import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixtures
import json
from playwright.sync_api import sync_playwright
U="http://127.0.0.1:8765/index.html"
def ok(c,m): print(("OK    " if c else "FALHA ")+m)
with sync_playwright() as p:
    br=p.chromium.launch(); ctx=br.new_context(viewport={"width":390,"height":844}); pg=ctx.new_page(); errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.goto(U); pg.wait_for_timeout(300)
    A=["u%03d"%i for i in range(100)]; B=A[:97]
    pg.evaluate("""([A,B])=>{localStorage.setItem("quemsaiu_exportacoes",JSON.stringify([
       {data:"2026-10-01T10:00:00Z",seguidores:A,seguindo:["u097","u001"]},
       {data:"2026-10-14T10:00:00Z",seguidores:B,seguindo:["u097","u001"]}]));}""",[A,B])
    pg.reload(); pg.wait_for_timeout(400); pg.click("#btnDescobrir"); pg.click("#btnComecar"); pg.wait_for_timeout(200)
    t=lambda s: pg.evaluate("s=>document.querySelector(s).innerText",s)
    bol=lambda cls: pg.evaluate("c=>document.querySelector('.aba-res.'+c+' .bolha').innerText",cls)
    ok(bol("saiu")=="3","3a aba 'saiu' começa com 3 | %s"%bol("saiu"))
    ok("trocado de nome de usuário" in t("#listaResultado"),"3b a explicação da aba 'saiu' cita a troca de nome")
    pg.click('[data-ignorar="u099"]'); pg.wait_for_timeout(500)
    ok(bol("saiu")=="2","3c esconder 1 conta: o número da aba cai para 2 | %s"%bol("saiu"))
    ok("2" in t(".aba-res.saiu") and "contas escondidas" not in t("#listaResultado") and "1 conta escondida" in t("#listaResultado"),"3d rodapé diz '1 conta escondida'")
    pg.evaluate("['u097','u098'].forEach(ignorarConta)"); pg.evaluate("renderizarResultado()"); pg.wait_for_timeout(200)
    ok(bol("saiu")=="0" and "Todas as contas desta lista estão escondidas." in t("#listaResultado") and "Ninguém deixou" not in t("#listaResultado"),"3e tudo escondido: não diz 'ninguém deixou de te seguir' | %r"%t("#listaResultado")[-120:].replace("\n"," | "))
    pg.click("#btnRestaurar"); pg.wait_for_timeout(300)
    ok(bol("saiu")=="3","3f 'Mostrar todas' devolve o número 3")
    pg.click('button[data-res="entrou"]'); pg.wait_for_timeout(200)
    ok("trocou de nome" in t("#listaResultado") and "Nenhum seguidor novo" in t("#listaResultado"),"3g aba 'entrou' vazia (sem escondidas) mantém a mensagem antiga")
    ok(errs==[],"sem erros de JavaScript | %s"%errs)
    br.close()
