# Servidor de avisos do Quem Saiu (Fase 1)

**Estado: escrito e testado, NÃO implantado. O site não usa este servidor enquanto `AVISOS_ATIVO` for `false` em `script.js`.**

## O que é
Um Cloudflare Worker (programa pequeno que roda na Cloudflare) com um banco D1. Ele só faz isto:
- guarda, para cada aparelho que ligou os avisos: um número aleatório, o endereço do aviso daquele navegador, o fuso horário e a data do "Já pedi";
- a cada 30 minutos manda um aviso **sem texto nenhum dentro** (o texto fixo está no `service-worker.js` do site): 1, 3, 7 e 14 dias depois do pedido, só entre 9h e 20h no fuso do aparelho. Depois do 4º aviso apaga o registro;
- apaga o registro quando a pessoa manda a lista, desliga o aviso, toca em "Desfazer" ou "Apagar meus dados", ou quando o serviço de aviso diz que o endereço não existe mais (404/410).

**Nunca guarda:** lista de seguidores, arquivos, e-mail, nome de usuário ou senha do Instagram. Não escreve nada nos registros (logs).

Mudança em relação à especificação: não guardamos as chaves `p256dh` e `auth` da inscrição, porque o aviso vai sem conteúdo e elas não são usadas. Menos dados guardados.

## Arquivos
- `src/index.js` — o Worker (rotas `/registrar`, `/apagar`, `/saude` e o envio a cada 30 minutos).
- `schema.sql` — a única tabela (`aparelhos`).
- `wrangler.toml` — configuração (cron, banco, origens permitidas).
- `gerar-chaves-vapid.mjs` — cria o par de chaves que identifica o Quem Saiu perante os serviços de aviso.
- `teste/worker.test.mjs` — 16 testes (rodar: `node --test servidor/teste/worker.test.mjs`).

## Como implantar (a Janaína só tem o celular: este caminho usa o painel da Cloudflare)
1. **Criar o banco.** Painel da Cloudflare → Armazenamento e bancos de dados → D1 → Criar banco `quemsaiu-avisos`. Abra o banco → Console → cole o conteúdo de `schema.sql` e execute. Copie o **ID do banco** e coloque em `wrangler.toml` no lugar de `COLE_AQUI_O_ID_DO_BANCO` (peça ao Claude).
2. **Criar o Worker a partir do GitHub.** Workers e Pages → Criar → Workers → importar repositório `Quem-saiu-` → diretório raiz `servidor` → nome `quemsaiu-avisos` → implantar. (Alternativa com computador: `cd servidor && npx wrangler deploy`.)
3. **Guardar os segredos.** No Worker → Configurações → Variáveis e segredos → adicionar como **segredo**: `VAPID_PUBLICA` e `VAPID_PRIVADA_JWK` (os valores estão no arquivo que o Claude enviou; a chave privada **nunca** vai para o repositório nem para o chat).
4. **Ligar o banco ao Worker** (se não vier do `wrangler.toml`): Worker → Configurações → Associações → D1 → nome da variável `DB`.
5. **Conferir o cron.** Worker → Configurações → Gatilhos → deve aparecer `*/30 * * * *`.
6. **Testar:** abrir `https://quemsaiu-avisos.<seu-subdominio>.workers.dev/saude` deve mostrar `{"ok":true}`.
7. **Ligar no site (o Claude faz, em ramificação):** colocar o endereço do Worker em `AVISOS_URL`, trocar `AVISOS_ATIVO` para `true`, publicar a política nova (`RASCUNHO-politica.md`) **no mesmo momento**, subir o `?v=`.

## Antes de ligar para o público
- Testar no Android/Chrome da Janaína: ativar o aviso, esperar o aviso de teste (pode forçar com `UPDATE aparelhos SET proximo_envio = 0` no console do D1, dentro das 9h–20h), tocar nele.
- iPhone/Safari: **não testado** (aviso web no iPhone só funciona com o site instalado na tela inicial).
- Revisão jurídica da política (servidor, Cloudflare como operador, transferência internacional): pendente.
- O plano grátis do Worker tem limite de pedidos e de tempo por execução; com poucos usuários basta. Medir no beta.
- Os horários dos avisos (1, 3, 7 e 14 dias) são uma hipótese a medir, não algo comprovado.
