# Evolução

O que mudou em cada skill, em qual projeto e por quê. Mais recente primeiro.

## 2026-11-13

- **oss-worker → local-worker**: novo nome. O script (`local.py`) fala com a API
  compatível com OpenAI do Strata em vez da API do Ollama. A estimativa de tempo
  saiu do script (velocidade não entra na decisão). Prompts em inglês.
- **offload-local**: o executor troca o gpt-oss:20b (Ollama) pelo
  Qwen3.8-Flash-Next no Strata (API Anthropic em `127.0.0.1:8080`). Novo
  `claude-local.cmd` liga o Claude Code ao Strata; o `rodar-executor.ps1` usa ele
  por padrão. Motivo: a Yolo trocou de modelo local.

## 2026-11-10

- **oss-worker** e **offload-local**: entram no repositório. Na `oss-worker`, a
  regra de "vale usar?" agora é de uso geral e decide só pelo custo em tokens
  do Claude (delega se L < 0,7 × D). Velocidade não entra na conta e os
  exemplos de tarefa saíram. Motivo: a Yolo quer uma ferramenta de economia de
  tokens, sem viés a favor nem contra o modelo local.

## 2026-11-07

- **nielsen-heuristicas** (projeto yolo-guia): entra no repositório, sem
  mudança. Três modos: auditoria, criação e checagem do pedido antes de
  implementar. Motivo: a Yolo quer usar a skill em todos os projetos.

## 2026-11-06

- **ponytail** e mais cinco (`-review`, `-audit`, `-debt`, `-gain`, `-help`):
  entram no repositório, copiadas sem mudança do commit `96608e0` do
  DietrichGebert/ponytail, depois da auditoria com a `audit-repo`. Só as skills:
  os hooks e o painel com webhook do plugin ficaram de fora. Motivo: a Yolo quer
  usar o ponytail em todos os projetos.

## 2026-11-03

- **audit-repo**: entra no repositório. Antes se chamava `auditoria-repo-clonado`;
  o nome mudou para ficar mais fácil de chamar. Conteúdo sem mudança.
- **CLAUDE.md**: regras gerais da Yolo (tratamento por "Yolo", fala guiada pelo
  ASD-STE100, não assumir nada, LGPD). O `start` copia para cada projeto.
- **karpathy-guidelines** e **humanizer-pt**: entram no repositório, sem mudança.
- **sync.mjs**, **START.md**: sistema de paridade e roteiro de início.
- **optimize-workspace** (projeto yolo-guia): nova seção "Fechamento:
  otimização de desempenho" (medir, corrigir pelo maior gargalo, validar), com
  as 31 dicas do reel da @breakingbreach. Motivo: a Yolo quer que todo projeto
  de software termine com essa etapa.

## 2026-11-14 — offload-local (projeto blupee-rupee)
- Autorização permanente da usuária: o Claude pode ligar o Strata sempre que precisar, sem perguntar. Antes confere se a API já responde e se o ComfyUI está fechado (mesma GPU); avisa em uma linha.
- Por quê: o planejador parava o trabalho esperando a usuária ligar o servidor.
