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
