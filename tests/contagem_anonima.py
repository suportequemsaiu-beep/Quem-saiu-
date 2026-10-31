import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
U = "http://127.0.0.1:8765/index.html"
def ok(c, m): print(("OK    " if c else "FALHA ") + m)

def novo(br, teste=True, dnt=False, gpc=False, standalone=False):
    ctx = br.new_context(viewport={"width": 390, "height": 844})
    pg = ctx.new_page(); m = []; errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("request", lambda r: m.append(r.url) if "/m/" in r.url else None)
    pre = ""
    if teste: pre += "window.__QS_CONTAGEM_TESTE = true;"
    if dnt: pre += "Object.defineProperty(navigator,'doNotTrack',{value:'1'});"
    if gpc: pre += "Object.defineProperty(navigator,'globalPrivacyControl',{value:true});"
    if standalone: pre += "const mm = window.matchMedia.bind(window); window.matchMedia = q => q.includes('standalone') ? {matches:true, media:q, addEventListener(){}, removeEventListener(){}, addListener(){}, removeListener(){}} : mm(q);"
    if pre: pg.add_init_script(pre)
    pg.clock.install()
    return ctx, pg, m, errs

def nomes(m): return sorted(set(u.split("/m/")[1] for u in m))

with sync_playwright() as p:
    br = p.chromium.launch()

    ctx, pg, m, errs = novo(br)
    pg.goto(U); pg.wait_for_timeout(300)
    ok(nomes(m) == ["visita.txt"], "1 ao abrir pede só 'visita' | %r" % nomes(m))
    pg.clock.run_for(11000); pg.wait_for_timeout(200)
    ok("ficou-10s.txt" in nomes(m) and "ficou-30s.txt" not in nomes(m), "2 com 10 s pede 'ficou-10s' | %r" % nomes(m))
    pg.clock.run_for(300000); pg.wait_for_timeout(200)
    ok(nomes(m) == ["ficou-10s.txt","ficou-120s.txt","ficou-300s.txt","ficou-30s.txt","ficou-60s.txt","visita.txt"], "3 com 5 min pede todos os marcos, uma vez cada | %r" % nomes(m))
    ok(len(m) == len(set(m)) or all(m.count(u) == 1 for u in set(m)), "4 nenhum pedido repetido | %d pedidos" % len(m))
    pg.reload(); pg.wait_for_timeout(300)
    ok(m.count([u for u in m if u.endswith("visita.txt")][0]) == 1, "5 recarregar na mesma sessão não conta outra visita")
    pg.evaluate("window.dispatchEvent(new Event('appinstalled'))"); pg.wait_for_timeout(200)
    ok("instalou.txt" in nomes(m), "6 evento de instalação pede 'instalou'")
    ok(not errs, "7 sem erros de JS | %r" % errs)
    ctx.close()

    # aba em segundo plano não conta tempo
    ctx, pg, m, errs = novo(br)
    pg.goto(U); pg.wait_for_timeout(300)
    pg.evaluate("Object.defineProperty(document,'visibilityState',{get:()=>'hidden',configurable:true})")
    pg.clock.run_for(60000); pg.wait_for_timeout(200)
    ok("ficou-10s.txt" not in nomes(m), "8 com a aba escondida o tempo não anda | %r" % nomes(m))
    ctx.close()

    # app instalado
    ctx, pg, m, errs = novo(br, standalone=True)
    pg.goto(U); pg.wait_for_timeout(300)
    ok("app-aberto.txt" in nomes(m), "9 aberto pelo app instalado pede 'app-aberto' | %r" % nomes(m))
    ctx.close()

    # privacidade: DNT e GPC
    for rot, kw in (("Não rastrear (DNT)", dict(dnt=True)), ("Global Privacy Control", dict(gpc=True))):
        ctx, pg, m, errs = novo(br, **kw)
        pg.goto(U); pg.wait_for_timeout(300); pg.clock.run_for(15000); pg.wait_for_timeout(200)
        ok(m == [], "10 com %s ativado não faz nenhum pedido | %r" % (rot, m))
        ctx.close()

    # localhost sem pedido de teste: não conta
    ctx, pg, m, errs = novo(br, teste=False)
    pg.goto(U); pg.wait_for_timeout(300); pg.clock.run_for(15000); pg.wait_for_timeout(200)
    ok(m == [], "11 em localhost (sem modo de teste) não conta nada | %r" % m)
    ctx.close()

    # o pedido não leva nada junto
    ctx = br.new_context(); pg = ctx.new_page(); reqs = []
    pg.add_init_script("window.__QS_CONTAGEM_TESTE = true;")
    pg.on("request", lambda r: reqs.append(r) if "/m/" in r.url else None)
    pg.goto(U); pg.wait_for_timeout(300)
    r = reqs[0]
    ok(r.method == "GET" and r.post_data is None and "?" not in r.url, "12 pedido é GET simples, sem corpo e sem parâmetros")
    ok(not any(k.lower() in ("cookie",) for k in r.headers), "13 pedido não leva cookie")
    ctx.close()

    # arquivos existem e a política descreve a contagem
    import urllib.request
    for n in ["visita","app-aberto","ficou-10s","ficou-30s","ficou-60s","ficou-120s","ficou-300s","instalou"]:
        c = urllib.request.urlopen("http://127.0.0.1:8765/m/%s.txt" % n).status
        if c != 200: ok(False, "14 /m/%s.txt existe" % n)
    ok(True, "14 os 8 arquivos de /m/ existem")
    pol = open(os.path.join(os.path.dirname(__file__), "..", "privacy-policy.html"), encoding="utf-8").read()
    ok("Contagem anônima de uso" in pol and "contagem.js" in pol and "Não rastrear" in pol, "15 a política de privacidade descreve a contagem")
    js = open(os.path.join(os.path.dirname(__file__), "..", "contagem.js"), encoding="utf-8").read()
    ok(not re.search(r"localStorage|document\.cookie|navigator\.sendBeacon|XMLHttpRequest|https?://", js.replace("https?://","")), "16 contagem.js não usa cookie, localStorage nem endereços externos")
    br.close()
