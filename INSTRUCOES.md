# Quem Saiu — instruções do projeto

Leia este arquivo antes de alterar qualquer coisa no projeto.

## O que é

Ferramenta web que mostra quem deixou de seguir uma conta no Instagram.
Funciona comparando a lista de seguidores em dois momentos, a partir da
exportação oficial de dados que o próprio Instagram fornece ao titular da conta.

Site: https://quemsaiu.com.br (domínio próprio, HTTPS ativo desde ago/2026)
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

## Ideia avaliada: chat com IA (adiada, não descartada)

Ideia: um chat onde o usuário pergunta sobre a própria lista ("por que fulano
aparece aqui?"), inspirado no app Pierre. Ficaria só no plano pago; o plano
gratuito manteria tudo no aparelho.

**É tecnicamente possível**, mas exige servidor: o modelo de IA roda fora do
celular e a chave de acesso não pode ficar no código do site. Ou seja, depende
da migração de hospedagem que os planos pagos já exigem.

**O que muda de categoria — e é o ponto principal:** as listas não contêm apenas
dados de quem usa o site. São centenas de nomes de **outras pessoas**, que nunca
concordaram com nada. Enquanto tudo fica no aparelho, é o usuário mexendo nos
próprios dados. No momento em que isso vai para um servidor, o projeto passa a
ser responsável por dados pessoais de terceiros perante a LGPD — com deveres de
segurança, de resposta a solicitações e de notificação em caso de vazamento. O
consentimento de quem assina o plano **não cobre os seguidores dele**.

**Correção de uma premissa:** a promessa "nada sai do aparelho" não é o que
protege o projeto dos termos da Meta. O que protege é a origem dos dados — o
usuário baixando a própria exportação oficial (portabilidade), em vez de login
ou raspagem. Essa base continua válida mesmo com servidor. A promessa de
privacidade é um compromisso com o usuário e um diferencial de mercado, não um
escudo jurídico contra a Meta.

**Observação de produto:** o Pierre precisa de IA porque os dados dele são
abertos (gastos, categorias, períodos, padrões). Aqui os dados são duas listas
de nomes, e as dúvidas possíveis são poucas e conhecidas. Boa parte do valor do
chat pode ser entregue sem IA, sem servidor e sem custo — por exemplo, um "por
que esta conta está aqui?" ao lado de cada nome, explicando na hora.

**Decisão:** adiado. Reavaliar quando houver migração de hospedagem e planos
pagos, e apenas com orientação sobre as obrigações de LGPD.

## Regra: política de privacidade e textos andam juntos

A política precisa descrever o que o site faz **naquele momento** — nunca o que
ele fará depois. Toda mudança que altere o comportamento (chat com IA, servidor,
planos pagos, qualquer envio de dados) exige revisar a política **antes** do
lançamento, não depois.

Atenção: a mensagem de privacidade vive em **três lugares**, e todos precisam ser
atualizados juntos, senão o site se contradiz:
1. `privacy-policy.html`
2. O texto dentro do site ("Seus dados são lidos aqui no seu navegador. Nada é
   enviado para servidor nenhum.")
3. A descrição da extensão na Chrome Web Store

A política é datada. Toda revisão atualiza a data.

**Caso real (set/2026):** a política descrevia a extensão de Chrome como se já
estivesse publicada ("A extensão lê... e salva..."), mas ela nunca foi ao ar —
o site já dizia "em produção". Foi removida a seção inteira da extensão da
política (e a menção a ela na seção de Termos do Instagram), até que exista
de verdade. **Lembrete: quando a extensão for publicada, trazer essa seção de
volta** — o texto antigo com as permissões (storage, host_permissions em
instagram.com) está no histórico do repositório, não precisa reescrever do
zero.

## Checklist antes de ligar o chat com IA (ou qualquer envio de dados)

Levantamento jurídico feito em agosto/2026. Não substitui advogado.

**Textos (risco mais provável — CDC, não LGPD):**
- Reescrever "nada sai do aparelho" nos TRÊS lugares antes de ligar a IA. Manter
  a promessa apenas para o plano gratuito. Prometer o que não se cumpre é
  publicidade enganosa.
- Termos de Uso próprios, com limitação de responsabilidade e aviso de que o
  resultado é estimativa.
- Direito de arrependimento de 7 dias e cancelamento tão fácil quanto assinar.
- Canal de contato para pedidos sobre dados.

**Código e operação:**
- Anonimizar os @ de terceiros antes de enviar à IA (trocar por "Usuário 1").
  É a medida que mais reduz risco: sem identificador, quase todo o problema de
  base legal desaparece.
- Não reter nada no servidor: processar e descartar. Não se vaza o que não se tem.
- Com o fornecedor de IA: contrato de tratamento de dados, retenção zero, não usar
  para treinamento, cláusulas de transferência internacional.
- Plano de resposta a incidente pronto (prazo curto para notificar).

**Estrutura:**
- Empresa com CNPJ recebendo as assinaturas. Nunca o CPF pessoal do responsável.
- Não publicar a extensão de Chrome (maior atrito com os termos da Meta).
- Não usar a marca Instagram em nome, domínio ou logo.

**Por que o modelo atual é seguro:** enquanto tudo roda no navegador, o projeto
provavelmente não é controlador nem operador — quem trata é o próprio usuário, no
aparelho dele. É o chat com IA que muda essa condição.

## Ideia avaliada: convites que liberam acesso (adiada)

Ideia: quem convida X pessoas ganha tokens ou tempo de plano. Serve de marketing
para um produto sem verba de divulgação.

**Decidido:** nada de plano vitalício por convite. Convite dá tokens ou tempo —
nunca acesso permanente, senão cria uma via onde ninguém paga e o custo fica.

**Contra fraude, o produto tem uma defesa natural:** para usar de verdade é
preciso uma exportação real do Instagram, que demora e exige conta com histórico.
Isso torna caro fabricar convidado. Três mecanismos aproveitam isso:
- Recompensa só quando o convidado **importa uma lista**, não ao se cadastrar.
- Exigir lista com tamanho mínimo (conta nova quase não tem seguidores).
- Identificar por uma **impressão digital** do nome de usuário (código embaralhado,
  não reversível): garante uma recompensa por conta sem guardar dado pessoal.

**O que a ideia exige e hoje não existe:** contas de usuário. Sem identificar
quem convidou quem, não há programa de convites — e isso significa login,
servidor e mais dados sob responsabilidade do projeto.

**Sobre custo:** o limite de uso da IA precisa ser controlado no servidor, com
teto por usuário e **teto global de gasto**, para o pior cenário do mês ser
conhecido. Cuidado com o efeito dobrado: cada convite traz um usuário que custa
e ainda premia quem convidou.

**Decisão:** adiado junto com o chat e os planos pagos.

## Como trabalhar neste projeto (combinado com o dono)

- **Nunca trabalhar sobre suposição.** Verificar antes de propor; se não der para
  verificar, dizer que não deu e pedir o dado. Marcar explicitamente o que é
  inferência. Já houve um caso em que um alerta foi criado com base num palpite
  não verificado, e ele acusava um problema que não existia — teve que ser
  removido depois.
- **Avisar honestamente quando um dia não for produtivo.** Não enfeitar.
- **Sem pressa.** O objetivo é qualidade em cada detalhe, não velocidade. Publicar
  na loja só quando o site estiver redondo.
- O dono costuma usar **ditado por voz**: quando a transcrição parecer errada,
  perguntar antes de responder em vez de supor.

## Contas e endereços do projeto

- Site: **https://quemsaiu.com.br** — domínio próprio, ativo, com HTTPS.
  O endereço antigo (suportequemsaiu-beep.github.io/Quem-saiu-/) redireciona
  sozinho para cá.
- Hospedagem: ainda GitHub Pages (o domínio próprio só trocou o endereço, não
  a hospedagem — troca de hospedagem continua pendente para quando houver
  planos pagos, ver "Segurança e limites da hospedagem").
- Repositório: github.com/suportequemsaiu-beep/Quem-saiu- (público, branch main)
- E-mail do projeto: suporte.quemsaiu@gmail.com
- Domínio registrado no registro.br, R$ 40/ano, no nome do responsável legal
  (titular precisa ter 18 anos); e-mail de contato do domínio é o do projeto.
- Etiquetas de SEO e Open Graph já publicadas com o endereço definitivo
  (quemsaiu.com.br) — descrição para buscadores e cartão de compartilhamento
  com título, descrição e ícone.
## Estado atual e pendências

**Funcionando e publicado, em quemsaiu.com.br:** entrada com porta animada,
cartão de amostra interativo, mecânica em 3 passos (com título de seção oculto
para leitor de tela, corrigindo hierarquia), seção do app, faixa de instalação
(recolhe ao rolar, reaparece ao voltar ao topo), ferramenta de importação com
barra de progresso em etapas, PWA instalável, recebimento de arquivo por
compartilhamento do Android (testado ponta a ponta), passo a passo em três
balões coloridos e numerados (Peça o arquivo / Fique de olho no e-mail / Baixe
e mande para cá), aba Suporte com orientação de como relatar problema,
domínio próprio com HTTPS e etiquetas de SEO/Open Graph.

**Acessibilidade concluída:** auditada com WAVE, nota subiu de 8.3 para 9.7.
Inclui leitor de tela (aria-live, aria-label, aria-expanded, aria-pressed,
aria-current), navegação por teclado no logo, hierarquia de títulos corrigida
(h1 único → h2 → h3, com título oculto "Como funciona" preenchendo o vão antes
da mecânica), e uma varredura completa de contraste que corrigiu:
  - Textos secundários que usavam a cor errada para o fundo (claro vs escuro).
  - Os botões principais do site (fundo azul `#0ea5e9` com texto branco
    reprovava a 2,77:1) — corrigidos para `#0369a1` (5,93:1). Isso NÃO deve
    ser revertido para `#0ea5e9` em nenhum botão com texto branco em cima;
    o azul claro só é seguro em gradientes decorativos ou como texto sobre
    fundo claro.
  - A paleta de avatares reais (`PALETA_AVATAR`) tinha 9 das 10 cores
    reprovando contraste com as iniciais brancas — reconstruída inteira:
    `#0369a1, #c2410c, #047857, #7c3aed, #db2777, #b45309, #0f766e, #4f46e5,
    #dc2626, #4d7c0f`. Qualquer cor nova adicionada a essa paleta precisa ser
    testada contra branco (mínimo 4,5:1) antes de entrar.
  - A aba ativa "Começaram a te seguir" (verde `#16a34a` com texto branco,
    3,30:1) — corrigida para `#15803d` (5,02:1).

**Nomes dos botões decididos:** "Ver a minha lista" (era "Importar exportação
do Instagram") e "Ver o que mudou" (era "Comparar com a exportação anterior").

**Também publicado, mais recente:** pergunta nova no FAQ sobre app sem senha
(com aria-expanded corrigido em todo o FAQ, não só no passo a passo); texto da
extensão do Chrome mudou de link clicável para "está em produção" (removido
código morto: LINK_CHROME_STORE e o listener que ficou órfão); reforço
"nunca peça nem envie sua senha" na aba Suporte; abas do resultado redesenhadas
com o número numa bolinha antes do texto (branca quando ativa, colorida
quando não — contraste conferido nas duas variações).

**Concluído (estava pendente desde a discussão sobre "bom HTML"):** CSS e
JavaScript separados em `style.css` e `script.js`. Ver "Como o código está
organizado" para os detalhes.

**Não começado:** logo definitivo (o ícone atual é provisório, feito em CSS,
propositalmente deixado para perto do lançamento), medição de uso que respeite
privacidade.

**Adiado de propósito:** extensão de Chrome, chat com IA, planos pagos,
convites — todos dependem de sair do GitHub Pages.

## Descobertas de campo (testadas no aparelho, não supostas)

- O compartilhamento de .zip do Android para o PWA **funciona**. Caminho mais
  curto testado: Chrome → menu ⋮ → Transferências → três pontinhos no arquivo →
  Compartilhar → Quem Saiu. O app abre já com a lista pronta.
- A notificação do Instagram avisando que a exportação ficou pronta **nem sempre
  chega**; o e-mail é o aviso confiável.
- O gerenciador de arquivos é um caminho ruim: exige mudar ordenação e caçar o
  arquivo. Não ensinar isso como principal.
- Não existe forma de um site ler a pasta Downloads nem de agendar notificação
  sem servidor. Ambos verificados.

## Ordem de trabalho: preview antes do código

Sempre mostrar o preview de qualquer mudança visual/textual primeiro, e só depois
o código pronto para colar no site. Isso dá espaço para o dono pedir ajustes antes
de qualquer coisa ir pro arquivo real — evita colar, perceber um problema, e ter
que desfazer.

## Erro cometido: confiar na própria busca como prova de que o arquivo estava íntegro

Quando o site ficou com tela azul (sintoma clássico de `</style>`, `</head>` ou
`<body>` faltando na colagem), a IA buscou o site com sua própria ferramenta de
busca, viu o conteúdo aparecer normalmente, e concluiu que o arquivo estava
correto — descartando a hipótese por várias mensagens.

**O erro:** a ferramenta de busca da IA lê o texto de forma tolerante, sem
executar um parser de HTML/CSS de verdade. Ela consegue "ler" o conteúdo mesmo
que uma tag de fechamento esteja faltando, porque não está validando a
estrutura — só extraindo texto. Navegadores de verdade (Chrome, Opera) e
ferramentas que renderizam de verdade (como o WAVE) não perdoam esse erro: se
o `</style>` sumir, tudo que vem depois é tratado como CSS e a página não
aparece.

**A lição:** buscar o próprio site nunca prova que o HTML está bem formado —
só prova que o servidor respondeu alguma coisa. Para confirmar que as tags de
fechamento estão no lugar certo, é preciso olhar o código-fonte de verdade
(no GitHub, ou via view-source: no navegador), não confiar na leitura
"tolerante" de uma ferramenta de busca.

## Limite de tamanho ao colar blocos pelo celular

Descobrimos por dois incidentes que blocos de código muito longos cortam ao
serem copiados/colados no editor do GitHub pelo celular do dono — mesmo dentro
do limite de linhas que já usávamos (~230-320 linhas). O corte real aconteceu
em ~89,9% de um bloco de ~22.230 caracteres (~20.000 caracteres copiados antes
de truncar).

**Regra:** ao dividir o arquivo para colagem, manter cada bloco abaixo de
~15.000 caracteres, não só abaixo de ~320 linhas — CSS denso (muitas
propriedades por linha) pode estourar caracteres bem antes de estourar linhas.
Se um bloco ultrapassar isso, dividir em sub-partes menores mesmo que fique
com mais de 5 partes no total.

## Ideia avaliada: publicar na Play Store via PWA (TWA)

Diferente da extensão de Chrome, publicar o Quem Saiu na Play Store pode **não
exigir computador** — existe o PWABuilder (ferramenta web, não precisa
instalar nada local, diferente do Bubblewrap CLI que exige Node/JDK/Android
SDK). Você digita o endereço do site e ele gera o pacote sozinho.

**Já cumprimos:** HTTPS ✓, manifest válido ✓, política de privacidade ✓.

**Ainda seria necessário:** conta de desenvolvedor do Google Play (US$25,
taxa única), arquivo `assetlinks.json` de verificação de domínio, materiais
da loja (ícone em alta resolução, imagem de destaque, screenshots, descrição).

**Alerta técnico (verificado em pesquisa, ago/2026):** desde 31/08/2026 a Play
Store exige apps compilados para Android 16 (targetSdk 36). Conferir se o
PWABuilder já está atualizado para isso antes de gerar o pacote.

**Sobre ASO (App Store Optimization):** só se aplica depois de existir uma
ficha na loja — é um campo de texto (descrição longa, até 4.000 caracteres)
preenchido no Google Play Console na hora de criar a ficha, repetindo as
palavras-chave principais 4-5 vezes de forma natural. Não é algo para editar
no `index.html` agora.

**Status:** avaliado, não iniciado. Mais promissor que a extensão de Chrome
por não depender claramente de computador, mas ainda não confirmamos se o
próprio Google Play Console funciona bem pelo navegador do celular.

## Avaliação de sugestões de UI recebidas de outra IA (Gemini, ago/2026)

Foram 4 sugestões de "elevar a UI para parecer software profissional". Cada
uma verificada contra o código real antes de decidir:

1. **Mockups das telas do Instagram no passo a passo** — válido, mas já
   discutido e adiado antes (ver decisão sobre screenshots). Trabalhoso de
   produzir, sem decisão de fazer ainda.
2. **Dashboard de resultados com cards simultâneos** (em vez das 3 abas
   atuais, mostrar os 3 números ao mesmo tempo, tipografia grande, cores
   pastel) — única sugestão genuinamente nova. É mudança de arquitetura de
   navegação, não só de cor. Qualquer cor nova precisa ser reconferida a
   4,5:1 de contraste antes de entrar (já tivemos dois incidentes disso).
   Decisão pendente do dono.
3. **Arrastar-e-soltar (drag-and-drop) no upload** — não se aplica: não
   existe gesto de "arrastar" natural no toque de celular, e o projeto é
   mobile primeiro por decisão explícita. Descartado por incompatibilidade
   de plataforma, não por qualidade da ideia.
4. **"Adicionar dark mode"** — sugestão baseada em premissa falsa. O site é
   escuro por padrão (`background: #0f172a`) desde a primeira versão do
   projeto. Nada a fazer aqui.

**Lição:** ferramentas de IA que avaliam o site sem executar o código (só
leem texto/descrição) erram sobre o que já existe. Sempre conferir no código
real antes de aplicar sugestão externa — já aconteceu 3 vezes nesta mesma
categoria (Perplexity e Gemini, duas vezes).

## Como o código está organizado

Desde ago/2026, separado em três arquivos (antes era um `index.html` só):

- `index.html` — só estrutura e texto (HTML puro, ~294 linhas). Aponta para
  `style.css` (`<link rel="stylesheet">`) e `script.js` (`<script src="...">`
  no fim do `<body>`). Editar aqui só o que é estrutura/conteúdo visível.
- `style.css` — todo o CSS do site (~223 linhas). Editar aqui qualquer cor,
  tamanho, espaçamento, animação.
- `script.js` — todo o JavaScript do site (~637 linhas, o que antes eram os
  dois blocos `<script>` inline, agora concatenados em um arquivo). Editar
  aqui qualquer comportamento, lógica de importação, PWA.
- `manifest.json` — configuração do app instalável (PWA), incluindo o
  compartilhamento de arquivos do Android.
- `service-worker.js` — recebe o arquivo compartilhado pelo Android e entrega
  para a página.
- `privacy-policy.html` — política de privacidade.
- `icone-*.png` — ícones do app.

Biblioteca externa: JSZip, carregada por CDN, usada para abrir o .zip no
navegador. É a única dependência.

**Por que separar ajudou:** cada arquivo sozinho cabe numa colagem só (menos
o CSS e o JS, que ainda passam de ~15.000 caracteres e precisam de 2 blocos
cada — mas nunca mais precisam ser recolados junto com o HTML). Editar uma
cor não exige mais tocar no arquivo inteiro de 1000+ linhas.

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
- **Buscar o próprio site nunca prova que o HTML está bem formado.** Ferramentas
  de busca/leitura tolerante conseguem extrair texto mesmo com uma tag de
  fechamento faltando. Só um navegador de verdade (ou view-source:) revela isso.
- **Blocos de colagem acima de ~15.000 caracteres cortam no celular do dono**,
  mesmo dentro do limite de linhas. Dividir por caracteres, não só por linhas.
- **Toda cor de texto branco sobre fundo colorido precisa ser testada a 4,5:1
  antes de entrar no código** (calculando com a fórmula de luminância relativa
  do WCAG). Isso já causou dois incidentes: os botões principais e a paleta de
  avatares. `#0ea5e9` (azul claro) especificamente **reprova** com texto
  branco em cima — usar `#0369a1` nesses casos.

## Como validar antes de publicar

Não há testes automatizados. Antes de qualquer publicação, conferir no celular:

1. A porta animada aparece e o botão "Quero descobrir" revela a amostra.
2. As três abas da amostra trocam de lista ao toque.
3. "Começar agora" abre a ferramenta e o passo a passo expande.
4. Importar um .zip real do Instagram gera a lista correta.
5. O botão × esconde uma conta e o painel "contas escondidas" permite restaurar.
6. Nenhum erro no console do navegador.
