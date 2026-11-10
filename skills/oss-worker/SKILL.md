---
name: oss-worker
description: Protocolo para o Claude usar o gpt-oss:20b local (Ollama) como ajudante durante a sessão. Decide se vale usar, faz a projeção de custo, escolhe o formato (chamada única, lote item a item ou plano em .md), roda com auto-compactação de contexto e confere sempre o resultado. O único critério é a economia de tokens do Claude. Use quando o Ollama estiver ligado e delegar puder custar menos tokens que fazer direto, ou quando a pessoa disser "usa o gpt-oss", "modelo local", "ollama".
---

# oss-worker: o gpt-oss como ajudante do Claude

Ferramenta: `python ~/.claude/skills/oss-worker/oss.py` (só stdlib). Diferente da skill
`offload-local` (o gpt-oss trabalha sozinho no Claude Code por um `TASKS.md`), aqui o
Claude continua no comando e chama o modelo local para pedaços pequenos.

## 1. Vale usar? Só o custo em tokens do Claude decide

Objetivo da skill: economizar tokens do Claude. Serve para qualquer tipo de tarefa.

Rode `oss.py probe` e `oss.py estimate <arquivos> --out <tokens de saída> [--per-item]`.
Depois compare dois custos, sempre em tokens do Claude:

- **D (fazer direto):** o que você leria + o que você escreveria para fazer a tarefa sozinho.
- **L (delegar):** escrever o prompt e o handoff + ler a saída para conferir (seção 5)
  + corrigir os erros. Se um script faz a tarefa, compare também com o custo de escrever o script.

Decisão:
- **L < 0,7 × D → delegue.** A margem de 30% cobre o risco de refazer (se falhar, você paga L e depois D).
- **L ≥ 0,7 × D → faça você mesmo.**

Não entra na conta: velocidade do modelo local, tempo de espera, preferência por fazer você mesmo.
Seja honesto nas duas direções. Não infle L para evitar o modelo local, nem diminua L para usá-lo.
Se a conta diz que delegar é mais barato, delegue.

Só os limites técnicos impedem o uso: a entrada não cabe em ~60% do contexto (mesmo dividida em partes),
ou a tarefa precisa de internet ou de imagem.

Registre a conta em 3 linhas antes de rodar: D estimado, L estimado, decisão.

## 3. Escolha do formato

- **Uma chamada (`run`)**: uma tarefa pequena, entrada < 60% do contexto. Use `--check` com um comando que falha se a saída estiver errada (`{out}` = arquivo de saída).
- **Lote (`map`)**: muitos itens independentes. Um item por chamada, sem histórico: o contexto nunca cresce. Saída JSON; `--check-key` exige chaves. Retoma de onde parou.
- **Sessão (`chat`)**: só quando o modelo precisa lembrar das respostas anteriores. Auto-compactação: perto de 60% do contexto o script resume os turnos antigos num "estado" e guarda só os 4 últimos turnos.
- **Plano em .md (`offload-local`)**: trabalho longo que o gpt-oss faz sozinho com ferramentas (editar arquivos, rodar build). Use quando a pessoa não estiver olhando e cada tarefa tiver um comando de verificação.

## 4. Regras de execução

- Uma tarefa pequena por chamada. Diga o formato exato da saída e dê 1-2 exemplos.
- Quando der, dê ao modelo uma lista fechada de respostas em vez de uma pergunta aberta (fica mais barato conferir).
- Falhou duas vezes? Faça você mesmo. Não gaste uma terceira tentativa.
- Decisões de design ficam com o Claude e com a pessoa.
- Nada de dados pessoais ou segredos nos prompts (LGPD), mesmo sendo local.

## 5. Conferência (obrigatória)

Sempre confira o resultado antes de usar:
1. Validação automática: JSON válido, chaves presentes, valores dentro da lista fechada, ids que existem.
2. Amostra manual: leia pelo menos 10% dos itens (no mínimo 5) e todos os casos raros.
3. Se a amostra tiver mais de 1 erro em 10, refaça o lote com um prompt melhor ou faça você mesmo.
4. Registre no relatório: quantos itens, quantos conferidos, quantos corrigidos.

## Limites medidos (2026-11-08, RTX 5060 Ti 16 GB + 32 GB RAM)

gpt-oss:20b MXFP4, `OLLAMA_CONTEXT_LENGTH=65536` (o modelo aceita 131072, o Ollama carrega 65536).
~85 tok/s de saída. Orçamento seguro por chamada: ~39k tokens (60%).
