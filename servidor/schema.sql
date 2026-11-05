-- Quem Saiu — avisos (Fase 1). Uma linha por aparelho que ativou os avisos.
-- NÃO guarda lista de seguidores, arquivos, nomes de usuário nem e-mails.
CREATE TABLE IF NOT EXISTS aparelhos (
  aparelho      TEXT PRIMARY KEY,         -- número aleatório criado no aparelho (não é login)
  endpoint      TEXT NOT NULL,            -- endereço do aviso daquele navegador (Google/Mozilla/Apple/Microsoft)
  fuso          TEXT NOT NULL,            -- ex.: America/Sao_Paulo (para só avisar entre 9h e 20h)
  pedido_em     INTEGER NOT NULL,         -- quando a pessoa tocou em "Já pedi" (ms)
  estagio       INTEGER NOT NULL DEFAULT 0, -- quantos avisos já foram enviados (0 a 3)
  proximo_envio INTEGER NOT NULL,         -- a partir de quando o próximo aviso pode sair (ms)
  criado_em     INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_aparelhos_proximo ON aparelhos (proximo_envio);
