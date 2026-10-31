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

5. **Celular primeiro, computador também.** A maioria dos usuários está no
   Android, e o visual base é o do celular. O computador é atendido pelo mesmo
   site no navegador, com ajustes de layout que só valem em telas a partir de
   900 px (bloco `@media (min-width: 900px)` no fim do `style.css`) — mudanças
   para o computador nunca devem alterar o celular. A importação de arquivo é o
   coração do produto. O site no navegador já cobre o computador.

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
baixa o HTML, o CSS e o JavaScript para o próprio navegador.

**Hospedagem já migrada (out/2026).** O GitHub Pages não permite uso comercial
(os termos proíbem negócio online, e-commerce ou SaaS), por isso o site saiu de
lá e hoje roda na Cloudflare (projeto `quem-saiu`, em Workers e Pages). Antes de
cobrar qualquer plano, conferir os termos do plano da Cloudflare para uso
comercial — isso ainda não foi verificado.

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
de um servidor (a hospedagem já está na Cloudflare, mas hoje só serve arquivos
estáticos; o servidor do chat ainda não existe).

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

**Decisão:** adiado. Reavaliar junto com os planos pagos, e apenas com
orientação sobre as obrigações de LGPD.

## Regra: política de privacidade e textos andam juntos

A política precisa descrever o que o site faz **naquele momento** — nunca o que
ele fará depois. Toda mudança que altere o comportamento (chat com IA, servidor,
planos pagos, qualquer envio de dados) exige revisar a política **antes** do
lançamento, não depois.

Atenção: a mensagem de privacidade vive em **dois lugares**, e os dois precisam
ser atualizados juntos, senão o site se contradiz:
1. `privacy-policy.html`
2. O texto dentro do site ("Seus dados são lidos aqui no seu navegador. Nada é
   enviado para servidor nenhum.")

A política é datada. Toda revisão atualiza a data (última: 19 de outubro de 2026,
quando passou a constar que o navegador não informa ao Instagram de qual site o usuário veio;
antes: 15 de outubro, JSZip local e cópia temporária do Compartilhar).


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
- Não usar a marca Instagram em nome, domínio ou logo.

**Por que o modelo atual é seguro:** enquanto tudo roda no navegador, o projeto
provavelmente não é controlador nem operador — quem trata é o próprio usuário, no
aparelho dele. É o chat com IA que muda essa condição.

## Ideia avaliada: convites que liberam acesso (adiada)

Adiada junto com o chat e os planos pagos: exigiria contas de usuário e servidor, que hoje não existem. Os detalhes comerciais ficam fora deste arquivo público.

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
- Hospedagem: **Cloudflare** (projeto `quem-saiu`, em Workers e Pages). O
  domínio `quemsaiu.com.br` e o `www.quemsaiu.com.br` apontam para ele, e cada
  alteração na branch `main` gera uma publicação nova (confirmado no painel em
  7/out/2026). O GitHub Pages deixou de ser a hospedagem; o arquivo `CNAME` na
  raiz é sobra dele e não é necessário para a Cloudflare. Não conferi se o
  endereço antigo `suportequemsaiu-beep.github.io/Quem-saiu-/` ainda
  redireciona.
- O painel da Cloudflare mostra "visitantes únicos" do domínio. É contagem feita
  pelo próprio provedor, sem nenhum código nosso no site — por isso não quebra a
  regra 1. É estimativa (conta por endereço de IP e inclui robôs).
- Repositório: github.com/suportequemsaiu-beep/Quem-saiu- (público, branch main)
- E-mail do projeto: suporte.quemsaiu@gmail.com
- Domínio registrado no registro.br.
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
(com aria-expanded corrigido em todo o FAQ, não só no passo a passo); reforço
"nunca peça nem envie sua senha" na aba Suporte; abas do resultado redesenhadas
com o número numa bolinha antes do texto (branca quando ativa, colorida
quando não — contraste conferido nas duas variações).

**Concluído (estava pendente desde a discussão sobre "bom HTML"):** CSS e
JavaScript separados em `style.css` e `script.js`. Ver "Como o código está
organizado" para os detalhes.

**Atualizações de out/2026 (publicadas):**
- Botão discreto "Compartilhar" no canto direito, acima da porta (menor no
  celular). Usa o compartilhamento do aparelho quando existe; senão copia o
  link e mostra "Link copiado". Envia só o endereço do site, nunca dados da
  lista. Texto padrão: "Descubra quem deixou de te seguir no Instagram — sem
  login e sem senha."
- Passo 1 do "como pego o arquivo": o primeiro item é um passo escrito ("Abra
  seu perfil, toque no menu ☰ e toque em Central de Contas (pode aparecer como
  Conta Meta)"). **Não há link para a Central de Contas**: no Android o app do
  Instagram captura o link e abre só o feed. A lista tem 7 itens.
- Layout para computador (telas ≥ 900 px): início em duas colunas, menu em uma
  linha, conteúdo numa coluna de 680 px, efeito ao passar o mouse. No
  computador o passo 3 do passo a passo é outro ("Baixe e escolha o arquivo
  aqui"), porque o atalho de Compartilhar do Android não existe lá; o passo 3
  de celular fica oculto nessa largura.
- A resposta do FAQ "Existe versão para computador?" explica que basta abrir o
  site no navegador.
- Política de privacidade: hospedagem corrigida para Cloudflare, nota sobre o
  botão Compartilhar, data atualizada.
- Botão Compartilhar mais claro (texto `#cbd5e1`, borda `#64748b`, fundo leve).
- Celular: removido o retângulo azul padrão do Android ao tocar
  (`-webkit-tap-highlight-color`). Em troca, todo botão encolhe um pouco ao ser
  pressionado (regra genérica no topo do `style.css`, como o "Quero descobrir");
  regras próprias de cada botão continuam valendo por cima.
- Botão Compartilhar: ao fechar o menu do Android, o foco voltava ao botão e a
  borda azul de teclado (`:focus-visible`) ficava até tocar em outro lugar. O
  script agora tira o foco do botão (`blur`) após o compartilhamento.
- Causa real da borda azul que "grudava" no Compartilhar: o `:hover` no celular
  fica ativo depois do toque até tocar em outro lugar. Todos os efeitos de
  passar o mouse agora só valem em aparelhos com mouse (`@media (hover: hover)`).
- Atalho da Central de Contas: testado em out/2026 (o link abria só o feed);
  tentamos um link direto com dica e, no fim, o link foi removido (ver acima).
- Clareza para buscadores e IAs (out/2026): o texto visível agora diz que a lista
  fica guardada só no aparelho e que nas próximas vezes basta importar o arquivo
  novo (passos 1 e 2 da home + pergunta nova na Ajuda). Motivo: uma IA avaliou o
  app supondo que não havia histórico salvo, porque nada na página dizia isso.
  Também foram criados `robots.txt`, `sitemap.xml`, `llms.txt` e dados
  estruturados (JSON-LD no `<head>` do `index.html`). **As respostas do JSON-LD
  e do `llms.txt` precisam bater com as da Ajuda (os `<details>` da aba Ajuda no `index.html`)**; ao mudar uma,
  mude as outras. Regra: nunca esconder texto "para robôs" (é cloaking e pode
  penalizar o site); a informação tem de estar visível para todo mundo.
- Correções de código (out/2026), todas testadas no navegador:
  - Nomes de usuário vindos do arquivo passam por `escapar()` antes de entrar na
    tela (antes, um arquivo adulterado executava script). Erros de leitura só
    mostram HTML quando criados com `erroAmigavel()`; os demais viram mensagem
    padrão em português.
  - A importação recusa arquivo sem lista de seguidores (ex.: só o
    `following.json`) e ignora `.json` desconhecidos (antes, qualquer `.json`
    virava "seguidores"). Se a lista nova tiver menos da metade dos seguidores
    da anterior (e a anterior tiver 20 ou mais), pergunta antes de guardar.
  - Se o navegador não deixar gravar, a lista fica na memória, o status diz "só
    enquanto esta página estiver aberta" e aparece um aviso (antes, falhava em
    silêncio).
  - "Apagar meus dados" pede confirmação e também apaga a cópia do arquivo
    recebida pelo Compartilhar (Cache Storage `quemsaiu-compartilhado`).
  - O × para esconder contas existe em todas as abas do resultado (a Ajuda já
    prometia isso); a escolha vale para todas as abas.
  - Comparação com `Set` (50 mil seguidores comparam em menos de 1 s).
- Rodada de avaliação por IAs (out/2026): cinco IAs (ChatGPT, Gemini, Grok,
  Perplexity, Kimi) avaliaram o site só pelo que está escrito. O que apareceu e
  o que foi feito:
  - **"Minutos a horas" no `llms.txt`** era uma frase minha, nunca confirmada, e o
    título "fatos confirmados pelo criador" fazia as IAs repetirem como fato.
    Agora o tempo da exportação é "varia" e o título é só "Como funciona".
    **Regra: nada no `llms.txt`, na Ajuda ou nos dados estruturados pode ser
    escrito como confirmado sem a Janaína ter confirmado.**
  - **"Sem risco de banimento"** saiu da descrição do site e da prévia do link
    (promessa que não dá para garantir; nenhuma IA a via, e a página não dizia
    nada sobre banimento). A política agora diz só que o app não acessa a conta
    e que não há garantia sobre como o Instagram trata ferramentas de terceiros.
    A frase da "portabilidade de dados" saiu da política até um advogado
    confirmar.
  - **iPhone/Safari nunca foi testado** e isso está escrito em todo lugar. O
    atalho Compartilhar → Quem Saiu só existe no Android. O JSON-LD não diz
    mais "Qualquer navegador".
  - **A Ajuda agora é HTML puro** (`<details>` no `index.html`), e não mais montada
    por JavaScript: as IAs não liam as respostas. O JSON-LD (FAQPage) tem as
    mesmas 18 perguntas e respostas. Para mudar uma resposta: edite o
    `<details>` e copie o texto igual para o JSON-LD.
  - ~~Bloco "O que vale saber antes de começar" na home~~ — **removido em 27/out/2026 por
    decisão da dona do site.** Os mesmos avisos continuam na Ajuda ("Quantas listas ficam
    guardadas?", "Funciona no iPhone?"), na política de privacidade, no `llms.txt`, na dica ao
    lado do botão de importar e no aviso de arquivo mais antigo.
  - Abas do resultado explicam o que mostram; o botão de apagar diz o que remove;
    o status com 1 lista pede um arquivo mais novo.
  - **Aviso de arquivo mais antigo:** o app compara as duas listas mais recentes
    **na ordem em que foram importadas**, não pela data do arquivo. Se o nome do
    .zip trouxer a data (`instagram-usuario-AAAA-MM-DD-xxxx.zip`, formato que
    ainda não foi conferido num arquivo real) e ela for anterior à da última lista
    guardada, o app pergunta antes de guardar. Sem data no nome, não há aviso.
  - **Limite de armazenamento:** o navegador deixa guardar uns 5 milhões de
    caracteres no `localStorage`. Medido: uma conta de 50 mil seguidores enche em
    6 listas; de 300 mil, nem a segunda lista cabe. Agora `guardarNova()`
    descarta as listas mais antigas até caber, mantendo sempre as 2 mais
    recentes; se nem 2 couberem (contas acima de uns 150 mil seguidores), a lista
    vale só nesta página e o app avisa. A solução definitiva seria usar
    IndexedDB (não feito).
  - Teste com 300 mil seguidores: leitura em ~1,5 s no computador. Se 60 mil
    contas mudarem, abrir a aba leva ~5 s (renderiza todas as linhas). Em celular
    não foi medido.
  - **JSZip agora é servido pelo próprio site** (`jszip.min.js`, versão 3.10.1,
    licença MIT/GPL no cabeçalho do arquivo, que não deve ser removido). Não há
    mais nenhuma requisição para fora do site, e a política foi atualizada.
  - Exemplo da amostra: `@yuri22` (usado com autorização da pessoa) no lugar
    de um perfil de pessoa famosa. Os outros nomes da amostra
    (`@bruno_costa`, `@paula.mendes`) parecem inventados, mas podem existir.
  - Pendente para um advogado: política de privacidade/LGPD antes de cobrar,
    quem aparece como responsável pelo site, e "Ainda 100% gratuito".
  - Se as IAs não abrirem a política ou o `llms.txt` (aconteceu com uma), vale
    olhar na Cloudflare (Segurança → Bots) se há bloqueio de robôs de IA.
- **Fora do repositório (só a Janaína consegue ver/mudar; a IA não tem acesso ao
  painel da Cloudflare nem às configurações do GitHub):**
  - Cloudflare → Segurança → Bots: conferir se "bloquear robôs de IA" está ligado
    (se estiver, IAs que leem o site em tempo real podem não abrir a política nem
    o `llms.txt`, o que já aconteceu com uma).
  - Cloudflare → Análises (Web Analytics): se estiver ligado, a política já cobre
    ("estatísticas agregadas de visitas" pela hospedagem); se algum dia for
    desligado ou trocado, revisar o texto da política.
  - Cloudflare → SSL/TLS: "Sempre usar HTTPS" e, depois de confirmar que tudo
    funciona, HSTS.
  - Cloudflare → quem hospeda: o arquivo `CNAME` na raiz é resto do GitHub Pages;
    se a hospedagem for Cloudflare Pages, ele não faz nada.
  - GitHub → descrição e site do repositório (Settings → About).
  - **Cabeçalhos de segurança (`_headers`) ainda não foram criados.** Antes, confirmar
    que a hospedagem é Cloudflare Pages (só ela lê esse arquivo). Se criar uma
    política de conteúdo (CSP), ela precisa liberar só o próprio site e, se a
    Análise da Cloudflare estiver ligada, `static.cloudflareinsights.com`; qualquer
    recurso externo novo no site passa a exigir mudar a CSP.
- Leitura do arquivo (out/2026, por sugestão do ChatGPT): `extrairUsuarios()` não pega mais "a
  primeira lista que achar". Só vale uma lista cujos itens parecem contas
  (`string_list_data` ou `title`); se houver mais de uma, só a de nome conhecido
  (`relationships_following`/`relationships_followers`); se for ambíguo, ou se a lista
  não render nomes, ou se mais de 10% dos nomes não parecerem usuário do Instagram, a
  importação para com aviso (`formatoDiferente()`) e nada é guardado. Até 10% de nomes
  estranhos passam e aparecem como estão (não são descartados em silêncio). Testado com
  arquivos de teste, não com exportações reais; se o Instagram mudar o formato de
  verdade, ajustar `CHAVES_CONHECIDAS` e `pareceItemDeConta()`.
- Importação mais estrita (out/2026, auditoria): (1) `extrairUsuarios()` não devolve mais
  "lista vazia" quando o formato é desconhecido: só `[]` e um objeto com uma chave conhecida e
  lista vazia (quem não segue ninguém) valem como vazios; qualquer outra coisa (`{}`, `null`, objeto
  sem lista de contas) para com `formatoDiferente()`. (2) `processarArquivos()` só aceita um .zip
  sozinho, ou arquivos .json de nomes diferentes; dois .zip, .zip + .json ou o mesmo nome duas vezes
  param com aviso (antes as listas de datas diferentes eram misturadas). (3) `guardarNova()` não cria
  lista nova quando os seguidores são iguais aos da última (o mesmo arquivo importado duas vezes
  fazia a comparação ser da lista com ela mesma); se só o "seguindo" mudou, atualiza esse campo na
  lista existente. O aviso usa `mostrarAviso()` (estilo `.aviso-info`).
- Dados guardados (out/2026, auditoria): `lerDados()` só aceita itens com cara de lista guardada
  (`listaValida()`: `data` texto, `seguidores` e `seguindo` listas de textos); o resto do
  armazenamento é ignorado em vez de quebrar a página (antes um valor ruim parava o script e deixava
  de registrar o service worker e de receber o Compartilhar). Toda lista nova leva `v: 1`
  (`VERSAO_DADOS`). **Se o formato guardado mudar um dia, aumente `VERSAO_DADOS` e faça a migração
  em `lerDados()`; listas sem `v` (anteriores a esta versão) continuam valendo.**
- Pequenos ajustes (out/2026): nomes de arquivo com " (1)" (o Android renomeia downloads repetidos)
  valem como o original e contam como repetidos se o original também for escolhido; ao abrir o site
  sem vir do Compartilhar, uma cópia temporária que tenha sobrado no `Cache Storage` é apagada.
- **Testes (out/2026):** a pasta `tests/` tem testes automáticos no navegador (Playwright/Chromium).
  **Antes de publicar qualquer mudança em `script.js`, `index.html`, `style.css` ou `service-worker.js`,
  rode `python3 tests/rodar_todos.py` e só publique com "Tudo certo."** Mudou um comportamento de
  propósito? Atualize o teste. Criou um comportamento novo? Crie um teste. Eles não cobrem celular
  de verdade nem iPhone. A pasta é publicada junto com o site (não tem nada sigiloso).
- **Tema escuro (out/2026):** o visual do site é escuro e fixo (não há versão clara). Alguns celulares
  escurecem sites por conta própria e estragavam o visual (fundo quase preto, figura da porta cinza
  quase invisível, visto no celular de um amigo). Por isso o `index.html` tem
  `<meta name="color-scheme" content="only light">` e o `style.css` tem `:root { color-scheme: only light; }`:
  isso pede ao navegador para não escurecer a página e **não muda nada na aparência normal**. Não foi
  possível reproduzir o escurecimento no computador; a confirmação é pedir um print de um celular
  afetado. Se um dia o site ganhar um tema claro de verdade, revisar essas duas linhas.
- Cache: o `index.html` chama `style.css?v=…` e `script.js?v=…`. **Sempre que
  mudar o CSS ou o JS, troque o número depois de `?v=`** (hoje `20261029c`), senão
  celulares e a Cloudflare podem continuar mostrando a versão antiga.

**Não começado:** logo definitivo (o ícone atual é provisório, feito em CSS,
propositalmente deixado para perto do lançamento).

**Adiado de propósito:** chat com IA, planos pagos e convites — todos dependem
de um servidor, que ainda não existe. (Hospedagem já está na Cloudflare.)

## Descobertas de campo (testadas no aparelho, não supostas)

- **"Notificar" no Instagram (27/out/2026, print de um amigo):** na tela de exportação, o botão
  "Iniciar exportação" fica apagado enquanto "Notificar — Escolha uma forma de entrega" não for
  escolhido. O passo a passo não citava isso e a pessoa não conseguia terminar; agora o passo existe
  (depois de "Exportar para dispositivo") e há uma pergunta na Ajuda. Foi visto em um único print,
  não testado por nós; o Instagram muda a tela de vez em quando.
- **Passo a passo novo (27/out/2026, pedido da criadora: "dar uma cara nova"):** os 12 passos agora
  aparecem **um por vez**, com barra de progresso, botões Voltar/Próximo e uma telinha desenhada em
  cada passo. Os passos ficam escritos no `index.html` (`<ol id="listaEtapas">`, um `<li class="passo-etapa">`
  por passo, com `data-fase` e `data-tela`), então robôs e quem estiver sem JavaScript veem a lista
  inteira. O `script.js` só monta a barra, os botões e os desenhos (desenhos feitos à mão em SVG,
  telas genéricas, sem logo nem cores do Instagram; aviso "os desenhos são só um guia"). Os passos
  ficam todos na mesma célula de uma grade, para os botões não pularem de lugar. No computador
  (≥ 900 px) o último passo é `.so-computador`; no celular é `.so-celular`. Para mudar um passo,
  edite o `<li>` (texto) e a função de `DESENHOS` (desenho). Teste: `tests/passo_a_passo.py`.
- **Exportar tudo (28/out/2026, decisão da criadora):** o passo "Personalizar informações / só Seguidores e
  seguindo" saiu do passo a passo: a pessoa exporta tudo (padrão do Instagram) e o site lê só os arquivos
  `followers_*.json` e `following.json` dentro do .zip, ignorando o resto. Como um .zip com fotos e vídeos
  pode ter GB, acima de 100 MB o `script.js` não usa o JSZip (que carrega tudo na memória): lê só o índice
  do .zip e os poucos arquivos necessários (`listarEntradasZipGrande`, com Zip64 e `DecompressionStream`).
  Não testado em celular real nem com .zip de GB de verdade; também **não testado**: o caminho Compartilhar
  do Android com arquivo enorme (o service worker copia o arquivo para o cache). Se der problema, a saída é
  voltar o passo "só Seguidores e seguindo" (está no histórico do git).
- **Tela "Sua lista" e cartão de instalar (29/out/2026):** quem ainda não tem lista vê o passo a passo
  aberto, na frente (etapa 1) e o botão "Ver a minha lista" depois (etapa 2); com lista guardada o passo a
  passo fica recolhido e o botão vem primeiro (classe `sem-lista` no `#cardLista`, definida em
  `atualizarStatus`). A classe dos passos é `passo-etapa` (não usar `.etapa`: é da lista "Como funciona"
  da tela inicial e a mistura deixou aquela lista com letra escura). "Prefiro usar sem instalar" é um link em tom areia
  (não azul, para o site não ficar enjoativo) (nem botão, nem quase invisível); títulos das vantagens: "Abra com um clique", "Atalho para o Instagram", "Mantenha
  a mesma privacidade com muito mais facilidade". `?v=` atual: `20261029c`.
- **Cartão da "Sua lista" e passo do e-mail (29/out/2026):** o cartão da tela "Sua lista" é cinza-grafite
  (não azul), para não ficar tudo igual no site; o passo "Espere o e-mail" manda olhar a caixa de entrada
  ou o spam. `?v=` atual: `20261030b`.
- **Bloco "Já na primeira vez" (31/out/2026):** saiu da tela inicial a pedido da criadora (o texto sobre descobrir quem você segue e não te segue de volta). A função continua no site.
- **Nome "Conta Meta" (28/out/2026):** no passo a passo e na Ajuda o nome principal é "Conta Meta", como
  aparece na tela "Configurações e atividade" do celular da criadora; "Central de Contas" fica só como
  alternativa citada no passo 2.

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

Publicar o Quem Saiu na Play Store pode **não exigir computador** — existe o
PWABuilder (ferramenta web, não precisa
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

**Status:** avaliado, não iniciado. Não depende claramente de computador, mas
ainda não confirmamos se o próprio Google Play Console funciona bem pelo
navegador do celular.

## Avaliação de sugestões de UI recebidas de outra IA (Gemini, ago/2026)

Foram 4 sugestões de "elevar a UI para parecer software profissional". Cada
uma verificada contra o código real antes de decidir:

1. **Mockups das telas do Instagram no passo a passo** — feito em 27/out/2026
   como desenhos genéricos (sem imagens do Instagram), ver "Passo a passo novo".
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

- `index.html` — só estrutura e texto (HTML puro, ~550 linhas; inclui a Central de Ajuda em `<details>` e o JSON-LD). Aponta para
  `style.css` (`<link rel="stylesheet">`) e `script.js` (`<script src="...">`
  no fim do `<body>`). Editar aqui só o que é estrutura/conteúdo visível.
- `style.css` — todo o CSS do site (~280 linhas). Editar aqui qualquer cor,
  tamanho, espaçamento, animação. O que é só do computador fica no bloco
  `@media (min-width: 900px)` no fim do arquivo.
- `script.js` — todo o JavaScript do site (~689 linhas, o que antes eram os
  dois blocos `<script>` inline, agora concatenados em um arquivo). Editar
  aqui qualquer comportamento, lógica de importação, PWA.
- `manifest.json` — configuração do app instalável (PWA), incluindo o
  compartilhamento de arquivos do Android.
- `service-worker.js` — recebe o arquivo compartilhado pelo Android e entrega
  para a página.
- `privacy-policy.html` — política de privacidade.
- `icone-*.png` — ícones do app.

Biblioteca: JSZip 3.10.1 (`jszip.min.js`, copiada para dentro do site, sem CDN),
usada para abrir o .zip no navegador. É a única dependência.

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
- **A leitura do site por ferramenta pode mostrar uma versão antiga.** Em
  7/out/2026 a ferramenta de busca ainda mostrava o texto velho quando o site
  já estava atualizado (cache). Para saber se uma publicação entrou, olhar o
  site no navegador ou a aba Deployments do projeto na Cloudflare.
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
7. O botão "Compartilhar" abre a lista de apps do aparelho (ou copia o link).
8. No computador (tela larga): início em duas colunas, "Sua lista" na mesma
   coluna do resto, e o passo 3 mostrando a versão para computador. No celular,
   conferir que nada disso mudou.
