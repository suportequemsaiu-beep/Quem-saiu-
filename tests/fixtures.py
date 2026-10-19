"""Arquivos de teste no formato da exportação do Instagram (criados na hora, nada é baixado)."""
import json, os, zipfile


def seg(n):
    return {"string_list_data": [{"value": n, "href": "https://www.instagram.com/" + n, "timestamp": 1}]}


def fol(n):
    return {"title": n, "string_list_data": [{"href": "https://www.instagram.com/_u/" + n, "timestamp": 1}]}


def _zip(caminho, arquivos):
    with zipfile.ZipFile(caminho, "w") as z:
        for nome, conteudo in arquivos.items():
            z.writestr(nome, json.dumps(conteudo))


def criar_zips(pasta):
    """Cria quatro .zip de teste em `pasta` (100 seguidores; 90 na exportação mais nova)."""
    os.makedirs(pasta, exist_ok=True)
    base = ["u%03d" % i for i in range(100)]
    pasta_dados = "connections/followers_and_following/"

    def normal(caminho, seguidores, seguindo, extra=None):
        arquivos = {
            pasta_dados + "followers_1.json": [seg(x) for x in seguidores],
            pasta_dados + "following.json": {"relationships_following": [fol(x) for x in seguindo]},
        }
        arquivos.update(extra or {})
        _zip(caminho, arquivos)

    normal(pasta + "instagram-a-2026-10-01-x.zip", base, base[:20])
    normal(pasta + "instagram-a-2026-10-14-y.zip", base[:90], base[:20])
    # followers_2 em formato que o app não conhece
    normal(pasta + "parcial.zip", base, base[:20],
           {pasta_dados + "followers_2.json": {"novo_formato": [{"foo": 1, "bar": 2}]}})
    # following.json em formato que o app não conhece
    _zip(pasta + "seguindo_estranho.zip", {
        "followers_1.json": [seg(x) for x in base],
        "following.json": {"novo": [{"foo": 1}], "outro": "x"},
    })
