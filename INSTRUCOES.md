# Quem Saiu — instruções do projeto

Leia este arquivo antes de alterar qualquer coisa no projeto.

## O que é

Ferramenta web que mostra quem deixou de seguir uma conta no Instagram.
Funciona comparando a lista de seguidores em dois momentos, a partir da
exportação oficial de dados que o próprio Instagram fornece ao titular da conta.

Site: https://suportequemsaiu-beep.github.io/Quem-saiu-/
Suporte: suporte.quemsaiu@gmail.com

## Regras que não podem ser quebradas

1. **Nada sai do aparelho do usuário.** Não existe servidor, backend ou banco de
   dados. Toda leitura acontece no navegador. É proibido adicionar qualquer
   ferramenta que envie dados para terceiros — incluindo Sentry, Datadog,
   NewRelic, Google Analytics ou similares. Isso quebraria a promessa central do
   produto e a política de privacidade publicada.

2. **Nunca pedir login ou senha do Instagram.** A base legal do produto é o
   direito de portabilidade de dados (LGPD/GDPR): o usuário baixa os próprios
   dados e importa aqui. Qualquer solução que envolva credenciais do Instagram
   está descartada em definitivo.

3. **Sem referências a tempo nos textos.** Não escrever "volte em alguns dias",
   "aguarde uma semana" ou equivalentes. O gatilho do produto é um evento, não o
   calendário: a pessoa volta quando **nota que o número de seguidores mudou**.
   Exceção permitida: informar que o link de download do Instagram expira em
   4 dias, porque é uma regra prática do Instagram, não do nosso produto.

4. **Não usar a identidade visual da Meta.** Nada de gradiente do Instagram,
   logotipo ou elementos que sugiram afiliação. O rodapé declara explicitamente
   que o produto não é afiliado ao Instagram/Meta.

5. **Celular primeiro.** A maioria dos usuários está no Android. A importação de
   arquivo é o coração do produto; a extensão de Chrome é acessório e pode ser
   descartada sem afetar o resto.

## Decisões de produto já tomadas

- A entrada não pede nada ao usuário: primeiro desperta interesse (porta
  animada + "Alguém saiu sem avisar"), depois mostra uma amostra do resultado,
  e só então oferece a ferramenta.
- Os rótulos das listas são explícitos: "Deixaram de te seguir",
  "Começaram a te seguir", "Não te seguem de volta". Não usar "Saíram" e
  "Entraram" sozinhos — são ambíguos para quem chega.
- A instalação como app (PWA) é incentivada porque cria recorrência, mas nunca
  obrigatória. Quem não instalar precisa conseguir usar tudo normalmente.
- A exportação do Instagram às vezes deixa alguém de fora da lista de
  seguidores. Isso não tem correção possível do nosso lado; o usuário resolve
  escondendo a conta pelo botão ×.
- O Instagram não informa quais contas foram desativadas ou excluídas. Também é
  resolvido pelo botão ×.

## Segurança e limites da hospedagem

**Segredos nunca entram no repositório.** Hoje o projeto não tem nenhuma chave,
token ou variável de ambiente — porque não existe backend nem serviço pago. Se
um dia precisar de alguma (por exemplo, para acionar uma IA por GitHub Actions),
a chave vai em **Secrets do repositório**, nunca dentro de um arquivo. O
repositório é público: tudo que entra nele fica visível para sempre, inclusive no
histórico de commits. Uma chave vazada precisa ser revogada, não só apagada.

**Tornar o repositório privado não protege o código do site.** Todo visitante
baixa o HTML, o CSS e o JavaScript para o próprio navegador. Além disso, o
GitHub Pages só funciona em repositórios públicos no plano gratuito — privatizar
tiraria o site do ar.

**O GitHub Pages não permite uso comercial.** Os termos proíbem usá-lo para
rodar negócio online, e-commerce ou SaaS, e desaconselham transações sensíveis
como senhas e cartões. Consequência prática: **quando o Quem Saiu tiver planos
pagos, a hospedagem precisa mudar.** Não é opcional.

**Cobrança não pode ser verificada só no navegador.** Qualquer checagem feita em
JavaScript pode ser burlada por quem abrir as ferramentas do navegador. Planos
pagos exigem um servidor validando o pagamento — o que conflita com a promessa
"nada sai do aparelho" e precisa de uma decisão de arquitetura consciente, não
uma gambiarra no código do site.

## Como o código está organizado

- `index.html` — o site inteiro: HTML, CSS e JavaScript em um arquivo só.
  Não há build, dependências ou framework. Editar direto.
- `manifest.json` — configuração do app instalável (PWA), incluindo o
  compartilhamento de arquivos do Android.
- `service-worker.js` — recebe o arquivo compartilhado pelo Android e entrega
  para a página.
- `privacy-policy.html` — política de privacidade.
- `icone-*.png` — ícones do app.

Biblioteca externa: JSZip, carregada por CDN, usada para abrir o .zip no
navegador. É a única dependência.

## Armadilhas conhecidas

- **Ordem importa no HTML.** O JavaScript fica no fim do arquivo e procura os
  elementos por id. Qualquer elemento novo precisa ser declarado **antes** dos
  blocos `<script>`, senão o código não o encontra.
- **Não usar `accept` restritivo no seletor de arquivo.** O Android às vezes
  reporta o .zip do Instagram com outro tipo e o arquivo fica invisível para o
  usuário. A validação é feita por conteúdo (assinatura do ZIP), não por
  extensão.
- **O formato dos arquivos da exportação não é uniforme.** Em `followers_1.json`
  o nome de usuário vem no campo `value`; em `following.json` vem em `title`,
  e o `href` usa o formato `instagram.com/_u/usuario`. O extrator precisa
  cobrir os três casos.
- **Diferença de datas entre as listas é normal.** Os registros de "seguindo"
  costumam ser mais antigos que os de "seguidores". Isso não indica exportação
  incompleta — não criar alertas baseados nisso.

## Como validar antes de publicar

Não há testes automatizados. Antes de qualquer publicação, conferir no celular:

1. A porta animada aparece e o botão "Quero descobrir" revela a amostra.
2. As três abas da amostra trocam de lista ao toque.
3. "Começar agora" abre a ferramenta e o passo a passo expande.
4. Importar um .zip real do Instagram gera a lista correta.
5. O botão × esconde uma conta e o painel "contas escondidas" permite restaurar.
6. Nenhum erro no console do navegador.
