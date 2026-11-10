---
name: offload-local
description: Protocolo para dividir o trabalho entre o Claude na nuvem (planeja) e o modelo local gpt-oss (executa). Use quando o projeto tiver TASKS.md, quando a pessoa disser "offload", "planeje para o local", "prepare tarefas para o gpt-oss", ou quando você rodar como executor local (claude-local).
---

# Offload local: a nuvem planeja, o modelo local executa

Dois papéis. Descubra o seu antes de agir:
- **Planejador**: o Claude na nuvem (comando `claude`). Tem internet, contexto grande e vê imagens.
- **Executor**: o gpt-oss:20b local (comando `claude-local`). Contexto de 64k, sem internet, sem imagens.

Se não souber qual é o seu papel, pergunte.

Arquivos na raiz do projeto:
- `TASKS.md`: fila de tarefas. Só o planejador escreve tarefas novas.
- `PROGRESS.md`: feito, pendente, problemas abertos.
- `BLOCKED.md`: tarefas em que o executor falhou duas vezes.

## Papel: planejador (nuvem)

1. Leia `PROGRESS.md`, `BLOCKED.md`, `TASKS.md` e `git log --oneline -15`.
2. Revise os commits do executor (`git show <hash>`). Corrija ou reverta o que estiver errado.
3. Resolva cada item do `BLOCKED.md`: faça você mesmo ou reescreva a tarefa menor. Depois apague o item.
4. Tome as decisões, faça as pesquisas na web e leia as imagens. O executor não pode fazer isso.
5. Crie a branch de trabalho (`offload/<tema>`) e escreva as tarefas no `TASKS.md`, no formato abaixo.
6. Atualize o `PROGRESS.md`.

Regras para cada tarefa:
- Uma mudança pequena: até 3 arquivos e cerca de 15 minutos de trabalho.
- Diga os arquivos exatos e o que mudar. Não deixe decisões para o executor.
- Inclua um comando de verificação que termina com sucesso ou com erro (por exemplo `npm run build`, `npx tsc --noEmit`, um `grep`).
- Inclua o texto exato da mensagem de commit.
- Tarefas independentes. Se uma depende de outra, coloque na ordem certa.
- Caiba em 64k de contexto. O Claude Code já usa uma parte grande disso antes da
  tarefa começar. Diga o trecho a ler (`src/x.ts`, linhas 40-90) e nunca peça para
  ler um arquivo grande inteiro. Se a tarefa pede mais que isso, divida.

Formato:

```
## T01 — <título curto>
- Status: pendente
- Branch: offload/<tema>
- Arquivos: src/caminho/arquivo.tsx
- Fazer: <instrução exata>
- Verificar: <comando>
- Commit: "<mensagem>"
- Notas:
```

`Notas:` começa vazio. O executor escreve ali onde parou, se a tarefa for
interrompida.

## Rodar a fila sem parar (rotação de contexto)

O script `rodar-executor.ps1` (nesta pasta da skill) roda uma tarefa por
processo, cada uma com o contexto vazio, até a fila acabar. Ele para numa tarefa
bloqueada, numa tarefa que continua pendente ou em mudanças sem commit. Na raiz
do projeto:

```powershell
& "$HOME\.claude\skills\offload-local\rodar-executor.ps1"            # fila toda
& "$HOME\.claude\skills\offload-local\rodar-executor.ps1" -DryRun    # só mostra
```

Os logs ficam em `%TEMP%\offload-logs\<projeto>`.

## Papel: executor (local)

Faça **uma tarefa por conversa**. Na conversa manual, depois o usuário usa
`/clear`. Pelo script de rotação, cada tarefa já começa numa conversa nova.

1. Leia o `TASKS.md`. Pegue a primeira tarefa com `Status: pendente` (ou a tarefa
   que o prompt citar). Se o campo `Notas:` tiver texto, continue de onde ele diz.
2. Confira a branch: `git branch --show-current`. Se não for a branch da tarefa, use `git switch <branch>`. Nunca trabalhe na `main`.
3. Faça só o que a tarefa diz. Não mude outros arquivos. Não refatore.
4. Rode o comando de **Verificar**.
5. Se passar: `git add <arquivos da tarefa>`, `git commit -m "<mensagem da tarefa>"`, mude o status para `feita (<hash>)` e escreva uma linha no `PROGRESS.md`.
6. Se falhar: corrija e verifique de novo. Na segunda falha, desfaça as mudanças (`git restore <arquivos>`), mude o status para `bloqueada` e escreva no `BLOCKED.md`: a tarefa, o comando, o erro (as últimas 20 linhas) e o que você tentou.
7. Pare. Não comece a próxima tarefa.

Leia só o que a tarefa cita, e só os trechos indicados. Se a conversa ficar longa
(muitos arquivos lidos, muitas tentativas), escreva em `Notas:` o que já foi feito
e o que falta, e pare sem mudar o status.

O executor nunca:
- faz `git push`, merge, rebase ou `reset --hard`;
- lê, mostra ou altera `.env.local` ou qualquer segredo;
- instala ou remove pacotes (`npm install <pacote>`), a não ser que a tarefa diga;
- apaga arquivos que a tarefa não cita;
- escreve tarefas novas no `TASKS.md`.

Se a tarefa não estiver clara, não adivinhe: marque como `bloqueada` e explique no `BLOCKED.md`.
