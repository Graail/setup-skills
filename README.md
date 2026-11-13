# setup-skills

Ponto de partida de todo projeto: as skills e regras que o Claude Code usa, e
um sistema de paridade para que o que um projeto melhorar volte para cá e chegue
aos próximos.

## Como começar um projeto

Na pasta do projeto novo, diga ao Claude:

> Comece com github.com/Graail/setup-skills

O Claude segue o [START.md](START.md): instala as skills, liga as regras gerais
e faz a triagem do projeto com a `optimize-workspace`.

## Regras gerais

O [CLAUDE.md](CLAUDE.md) daqui vale em todo projeto: o `start` copia o arquivo
para `.claude/setup-skills.CLAUDE.md`, e o `CLAUDE.md` do projeto o importa com
`@.claude/setup-skills.CLAUDE.md`. Para mudar uma regra geral, edite aqui; o
`pull` leva a versão nova aos projetos.

## Skills

| Skill | O que faz | Origem |
|---|---|---|
| [`optimize-workspace`](skills/optimize-workspace/SKILL.md) | Organiza o trabalho em etapas ICM com dados em OKF. Fecha projetos de software com o protocolo de desempenho. | Própria |
| [`karpathy-guidelines`](skills/karpathy-guidelines/SKILL.md) | Regras para escrever código: pensar antes, simplicidade, mudanças cirúrgicas, meta verificável. | [andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) (MIT) |
| [`humanizer-pt`](skills/humanizer-pt/SKILL.md) | Tira de textos em português os padrões de escrita de IA, sem mudar o que dizem. | Adaptação de [humanizer](https://github.com/blader/humanizer) (MIT) |
| [`audit-repo`](skills/audit-repo/SKILL.md) | Audita um repositório de terceiros antes de clonar ou instalar: só leitura, sem rodar o código, e avisa sobre vazamento de dados, telemetria e processamento externo. | Própria |
| [`local-worker`](skills/local-worker/SKILL.md) | Usa o modelo local (Qwen3.8-Flash-Next no Strata) como ajudante do Claude. Decide só pela economia de tokens do Claude: delega quando delegar e conferir custa menos que fazer direto. | Própria |
| [`offload-local`](skills/offload-local/SKILL.md) | Divide o trabalho: o Claude na nuvem planeja tarefas em `TASKS.md` e o modelo local (Qwen3.8-Flash-Next no Strata) executa cada uma, com comando de verificação. | Própria |
| [`nielsen-heuristicas`](skills/nielsen-heuristicas/SKILL.md) | Audita ou orienta telas pelas 10 heurísticas de Nielsen. Antes de criar ou mudar uma interface, confere o pedido e avisa sobre conflitos antes de implementar. | Própria |
| [`ponytail`](skills/ponytail/SKILL.md) | Modo "dev sênior preguiçoso": a menor mudança que resolve a tarefa inteira, e uma resposta que diz o que ficou de fora. Níveis lite, full e ultra. | [ponytail](https://github.com/DietrichGebert/ponytail) (MIT), só as skills, commit `96608e0` |
| [`ponytail-review`](skills/ponytail-review/SKILL.md) | Revisão de uma mudança: lógica, segurança, carga, testes, velocidade e o que cortar. Só relata. | idem |
| [`ponytail-audit`](skills/ponytail-audit/SKILL.md) | A mesma revisão para o repositório inteiro, por ordem de importância. Só relata. | idem |
| [`ponytail-debt`](skills/ponytail-debt/SKILL.md) | Lista os comentários `shortcut:` (atalhos deixados de propósito) como dívida técnica. | idem |
| [`ponytail-gain`](skills/ponytail-gain/SKILL.md) | Mostra a economia medida no benchmark do autor. | idem |
| [`ponytail-help`](skills/ponytail-help/SKILL.md) | Cartão de ajuda do ponytail. | idem |

## Paridade

Cada projeto guarda uma cópia das skills em `.claude/skills/` e um lock
(`.claude/setup-skills.lock.json`) com a versão de cada uma na última
sincronização. Com o lock, o script sabe quem mudou:

| Estado | O que fazer |
|---|---|
| igual nos dois | nada |
| o repo tem versão nova | `pull` atualiza o projeto |
| o projeto melhorou a skill | `push` traz para cá; depois registrar em [EVOLUCAO.md](EVOLUCAO.md) e commitar |
| mudou nos dois lados | comparar à mão e juntar |

```bash
node sync.mjs status <pasta-do-projeto>
```

```bash
node sync.mjs pull <pasta-do-projeto>
```

```bash
node sync.mjs push <pasta-do-projeto> [skill...]
```

Só precisa de Node 18 ou mais novo. O `pull` nunca sobrescreve uma skill que o
projeto mudou.

## Como evoluir

1. Melhore a skill dentro do projeto, onde o problema apareceu.
2. No fim do projeto (ou quando a melhoria estiver testada), rode `status` e
   `push`.
3. Registre em [EVOLUCAO.md](EVOLUCAO.md) o que mudou, em qual projeto e por quê.
4. Commite aqui. Os outros projetos recebem no próximo `pull`.

Melhoria que só vale para um projeto fica no projeto (no `CLAUDE.md` dele), não
na skill.

## Licenças

Ver [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
