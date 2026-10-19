#!/usr/bin/env python3
"""Roda todos os testes do Quem Saiu num navegador de verdade (Chromium, via Playwright).

Como usar (na pasta do projeto):
    pip install playwright && playwright install chromium     # só na primeira vez
    python3 tests/rodar_todos.py

O script liga sozinho um servidor local na porta 8765 (a pasta do site), roda cada arquivo de
teste e mostra um resumo. Termina com erro (código 1) se qualquer verificação falhar.
"""
import os, socket, subprocess, sys, time, urllib.request

PASTA = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(PASTA)
PORTA = 8765
ARQUIVOS = [
    "importacao_formato.py", "importacao_erros_e_zip.py", "fluxo_geral.py", "importacao_segura.py",
    "link_do_perfil.py", "textos_e_contadores.py", "dados_guardados.py", "ajustes_menores.py",
]


def porta_ocupada():
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", PORTA)) == 0


def main():
    if porta_ocupada():
        print("A porta %d já está em uso. Feche o servidor que estiver nela e rode de novo." % PORTA)
        return 2
    servidor = subprocess.Popen([sys.executable, "-m", "http.server", str(PORTA), "--bind", "127.0.0.1"],
                                cwd=RAIZ, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    falhas_total = 0
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen("http://127.0.0.1:%d/index.html" % PORTA).read()
                break
            except Exception:
                time.sleep(0.1)
        for arq in ARQUIVOS:
            r = subprocess.run([sys.executable, os.path.join(PASTA, arq)], capture_output=True, text=True, cwd=RAIZ)
            linhas = (r.stdout or "").splitlines()
            ok = sum(1 for l in linhas if l.startswith("OK"))
            falhas = [l for l in linhas if l.startswith("FALHA")]
            quebrou = r.returncode != 0
            print("%-28s OK=%-3d FALHAS=%d%s" % (arq, ok, len(falhas), "  (o teste terminou com erro)" if quebrou else ""))
            for l in falhas:
                print("   " + l)
            if quebrou:
                print("   " + (r.stderr or "").strip().splitlines()[-1] if (r.stderr or "").strip() else "   sem detalhes")
            falhas_total += len(falhas) + (1 if quebrou else 0)
    finally:
        servidor.terminate()
    print("\nTudo certo." if falhas_total == 0 else "\nHÁ FALHAS: %d." % falhas_total)
    return 0 if falhas_total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
