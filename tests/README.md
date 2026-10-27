# Testes do Quem Saiu

Testes automáticos que abrem o site num navegador de verdade (Chromium) e conferem a importação,
a comparação das listas, o armazenamento, os avisos e o Compartilhar. Eles não enviam nada para fora:
os arquivos do Instagram usados são inventados e criados na hora (`fixtures.py`).

## Como rodar

Na pasta do projeto:

```
pip install playwright && playwright install chromium   # só na primeira vez
python3 tests/rodar_todos.py
```

O script liga sozinho um servidor local na porta 8765. Termina com "Tudo certo." ou lista as falhas.

## Quando rodar

**Antes de publicar qualquer mudança em `script.js`, `index.html`, `style.css` ou `service-worker.js`.**
Se mexer num comportamento de propósito, atualize o teste que o descreve; se criar um comportamento novo,
crie um teste para ele.

## O que cada arquivo cobre

| Arquivo | Cobre |
| --- | --- |
| `importacao_formato.py` | `extrairUsuarios()`: formatos aceitos e recusados, várias listas, nomes estranhos (limite de 10%) |
| `importacao_erros_e_zip.py` | nomes com HTML (sem execução), arquivos errados, leitura do .zip, falha ao guardar, lista bem menor, apagar dados, botão × |
| `fluxo_geral.py` | textos do site, Ajuda igual ao JSON-LD, nenhuma requisição para fora, status e explicações das abas, aviso de arquivo antigo, contas grandes |
| `importacao_segura.py` | não guardar lista repetida, não misturar arquivos, formato desconhecido não vira "lista vazia" |
| `link_do_perfil.py` | o Instagram não recebe o endereço do site ao abrir um perfil |
| `textos_e_contadores.py` | explicação das abas, números que contam só as contas visíveis, contas escondidas |
| `dados_guardados.py` | dado ruim no armazenamento não quebra a página; versão das listas |
| `aparencia.py` | o site avisa ao navegador para não escurecer a página sozinho (modo escuro forçado de alguns celulares) |
| `passo_a_passo.py` | o passo a passo: um passo por vez, Voltar/Próximo, barra de progresso, variante do computador, texto presente sem JavaScript |
| `ajustes_menores.py` | nomes com "(1)", limpeza da cópia temporária e Compartilhar |

## O que **não** é testado aqui

Exportações reais do Instagram, celular de verdade (o Android do Compartilhar), iPhone/Safari e a
Cloudflare. Os testes usam o Chromium do computador. Esta pasta também é publicada junto com o site.
