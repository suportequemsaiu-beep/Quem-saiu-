# Quem Saiu

Ferramenta web que mostra quem deixou de seguir uma conta no Instagram. Funciona
comparando a lista de seguidores em dois momentos, a partir da exportação oficial
de dados que o próprio Instagram fornece ao titular da conta.

- Site: https://quemsaiu.com.br
- Suporte: suporte.quemsaiu@gmail.com

## Como funciona

- Sem login e sem senha do Instagram.
- Toda a leitura acontece no navegador; nada é enviado a servidor.
- Funciona no celular (pensado primeiro para Android, instalável como app) e no
  computador, pelo navegador.

## Arquivos

| Arquivo | Para que serve |
| --- | --- |
| `index.html` | Estrutura e textos |
| `style.css` | Todo o visual (inclui o layout para telas largas, a partir de 900 px) |
| `script.js` | Comportamento: importação, comparação, compartilhar, PWA |
| `service-worker.js` | Recebe o arquivo compartilhado pelo Android |
| `manifest.json` | Configuração do app instalável |
| `privacy-policy.html` | Política de privacidade |
| `INSTRUCOES.md` | Regras, decisões e histórico do projeto — leia antes de alterar |

Hospedagem: Cloudflare, com publicação automática a cada alteração na branch `main`.
