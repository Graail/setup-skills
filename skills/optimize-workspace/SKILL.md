---
name: optimize-workspace
description: Use sempre que o usuário começar um projeto novo, cliente novo ou fluxo de trabalho novo, e para "workspace", "pipeline em etapas", setup ou status. Organiza o trabalho em etapas ICM com dados em OKF.
---

# Optimize Workspace

Junta dois métodos que se completam:

- **ICM**, Interpretable Context Methodology (Van Clief e McDermott, 2026,
  arXiv:2603.16021, MIT), organiza **o trabalho**. Pastas numeradas são etapas.
  Arquivos markdown dizem ao agente qual papel ter em cada etapa. Um único
  agente, lendo os arquivos certos na hora certa, faz o trabalho de um sistema
  multiagente.
- **OKF**, Open Knowledge Format v0.2 do Google (Apache 2.0), organiza **o
  conhecimento**. Um arquivo por conceito, com tipo, fonte, quem verificou e
  quando vence.

O ICM manda no fluxo. O OKF vale só dentro da pasta de conhecimento que as
etapas leem. Ver "Como ICM e OKF se encaixam".

## Ao começar um projeto novo

Esta skill roda no início de todo projeto novo, sem o usuário pedir. Faça uma
triagem curta antes de construir qualquer coisa:

1. Leia o que o usuário quer fazer. Responda internamente: o trabalho é
   **sequencial**, **revisável** e **repetível** (ver abaixo)? Depende de
   **dados que mudam** (preços, catálogo, clientes, regras)?
2. Diga ao usuário, em 2 ou 3 linhas, o que você recomenda:
   - **Workspace completo (ICM + `knowledge/` em OKF):** fluxo repetível que usa dados que mudam.
   - **Workspace ICM sem `knowledge/`:** fluxo repetível com regras estáveis.
   - **Sem workspace:** tarefa única, conversa, pergunta, ou fluxo que não se repete. Diga isso numa linha e siga com a tarefa normal.
3. Pergunte se ele quer seguir com a recomendação. Não crie pastas antes do sim.
4. Se ele aceitar, siga "Como construir um workspace novo", começando pela Descoberta.
5. Se já existe um workspace para este projeto (pasta com `CLAUDE.md` e `stages/`), não crie outro: leia o `CLAUDE.md` dele e mostre o `status`.

## Quando usar e quando não usar

Use para fluxos **sequenciais** (etapa 2 depende da 1), **revisáveis** (um
humano confere cada saída) e **repetíveis** (mesmo fluxo, entrada nova a cada
vez): produção de conteúdo, relatórios, material de treinamento, pesquisa,
auditorias, propostas.

Não use para: agentes que conversam entre si em tempo real, muitos usuários ao
mesmo tempo no mesmo fluxo, ou desvios automáticos complexos no meio do fluxo.
Nesses casos diga ao usuário que ICM não é a ferramenta certa.

## Como ICM e OKF se encaixam

**Quando usar o OKF.** Use quando o fluxo depende de dados que mudam ou que
precisam de confiança: preços, catálogo, clientes, regras de negócio, métricas,
fatos com fonte. Exemplo: montar uma proposta a partir de um catálogo de
compras. Não use para um fluxo só criativo (roteiro, post, design) com regras
estáveis: o ICM sozinho resolve e o OKF só acrescenta peso. Na dúvida, pergunte
ao usuário na fase de Descoberta.

**Regra 1, duas Camadas 3.** O ICM diz que a Camada 3 é estável ("a fábrica").
O OKF diz que o conhecimento é reescrito o tempo todo. Separe:

| Pasta | O que guarda | Muda? | Formato |
|---|---|---|---|
| `_config/`, `references/`, `shared/` | Voz, design, regras de produção | Quase nunca, só no setup | Markdown ICM comum |
| `knowledge/` | Fatos e dados do negócio | Sim, com data e fonte | Conceitos OKF |

**Regra 2, quem manda na rota.** O `CONTEXT.md` de cada etapa é a única rota
de execução. Ele diz quais arquivos de `knowledge/` carregar. O `index.md` do
OKF só lista o que existe dentro de uma pasta de `knowledge/`. Use o
`index.md` para achar o arquivo certo quando a tabela Inputs aponta para uma
pasta inteira, nunca para decidir qual etapa rodar.

**Regra 3, escopo do OKF.** Frontmatter OKF só em arquivos de `knowledge/`.
Nunca em `CLAUDE.md`, `CONTEXT.md`, questionário, modelos ou `output/`.

**Regra 4, confiança vira checagem.** Ao carregar um conceito de `knowledge/`,
o agente confere `status`, `verified` e `stale_after` (ver "Ler um conceito").
Isso é o que o OKF dá ao ICM: o agente sabe se pode confiar no dado antes de
usar.

**Regra 5, origem na saída.** Quando uma saída de etapa usa um fato de
`knowledge/`, ela cita o caminho do conceito (`/precos/cama-casal.md`). Assim o
humano que revisa a saída sabe de onde veio cada número. O paper do ICM lista
isso como trabalho futuro; esta skill já aplica.

## Cinco princípios

1. **Uma etapa, uma tarefa.** Etapa que pesquisa não escreve. Etapa que escreve não monta.
2. **Texto puro como interface.** Etapas se comunicam por arquivos markdown. Sem banco de dados, sem formato binário entre etapas.
3. **Contexto em camadas.** O agente carrega só o que a etapa atual pede. Mais contexto piora o resultado.
4. **Toda saída é superfície de edição.** O humano pode abrir, editar e salvar a saída antes da etapa seguinte. A etapa seguinte lê o que ele deixou.
5. **Configure a fábrica, não o produto.** O setup acontece uma vez. Cada execução gera um produto novo com a mesma configuração.

## As cinco camadas de contexto

O agente desce as camadas e para quando tem o que precisa.

| Camada | Arquivo | Pergunta | Quando carregar |
|---|---|---|---|
| 0 | `CLAUDE.md` do workspace | Onde estou? | Sempre, ao entrar (~800 tokens) |
| 1 | `CONTEXT.md` do workspace | Para onde vou? | Ao entrar (~300 tokens) |
| 2 | `stages/0N-nome/CONTEXT.md` | O que faço? | Por tarefa (200 a 500 tokens) |
| 3 | `references/`, `shared/`, `_config/`, `skills/`, `knowledge/` | Que regras e fatos valem? | Só o que a tabela Inputs pede |
| 4 | `output/` das etapas, material do usuário | Com o que trabalho? | Só o que a tabela Inputs pede |

Camada 3 é a fábrica: regras estáveis, configuradas uma vez, tratadas como
restrição ("escreva assim"). Camada 4 é o produto: muda a cada execução, tratada
como entrada ("transforme isto"). Meta: 2.000 a 8.000 tokens por etapa. Nunca
carregue o workspace inteiro.

## Estrutura de um workspace

```
nome-do-workspace/
  CLAUDE.md                 # Camada 0: mapa, gatilhos, rotas, o que carregar
  CONTEXT.md                # Camada 1: tabela de rotas por tipo de tarefa
  setup/questionnaire.md    # Onboarding, uma vez só
  _config/                  # Camada 3: marca, voz, design (ou brand-vault/)
  shared/                   # Camada 3: recursos usados por várias etapas
  skills/                   # Camada 3: skills de domínio copiadas para cá (opcional)
  knowledge/                # Camada 3 viva, em OKF (opcional)
    index.md                #   lista o que existe, com a description de cada conceito
    log.md                  #   histórico de mudanças
    [grupo]/[conceito].md   #   um arquivo por conceito
  stages/
    01-nome/
      CONTEXT.md            # Camada 2: contrato da etapa
      references/           # Camada 3 só desta etapa
      output/               # Camada 4: saída desta etapa (.gitkeep quando vazia)
    02-nome/ ...
```

## Gatilhos

Ao entrar num workspace, leia o `CLAUDE.md` dele e depois o `CONTEXT.md`.

- **`setup`**: leia `setup/questionnaire.md`, faça todas as perguntas numa só mensagem, substitua os placeholders nos arquivos indicados, depois procure `{{` no workspace inteiro. Se sobrar algum, pergunte o que falta. Setup só termina com zero placeholders.
- **`status`**: varra `stages/*/output/`. Pasta com arquivo além de `.gitkeep` = COMPLETA (liste os arquivos). Vazia = PENDENTE. Mostre assim:

```
Status do pipeline: [nome]

  [01-nome]  ----->  [02-nome]  ----->  [03-nome]
   COMPLETA           PENDENTE           PENDENTE
  (arquivo.md)        (vazia)            (vazia)
```

- **Rodar etapa** ("rode a etapa 2", "próxima etapa", ou um tema novo para a etapa 01): siga "Como rodar uma etapa".

## Como rodar uma etapa

1. Leia o `CONTEXT.md` da etapa. Ele é o ponto de controle.
2. Carregue **só** os arquivos e seções da tabela Inputs. Se a coluna diz uma seção, leia só essa seção. Para arquivos de `knowledge/`, siga "Ler um conceito".
3. Na etapa de entrada (01), pergunte os dados desta execução (tema, público, escopo). Eles não ficam no questionário.
4. Siga o Process passo a passo.
5. Em cada Checkpoint, pare, mostre o que a tabela manda e espere a decisão do usuário.
6. Antes de salvar, rode o Audit. Se um item falhar, revise e rode de novo.
7. Salve em `output/[slug-do-tema]-[tipo].md`, com a origem de cada fato de `knowledge/` (Regra 5). Diga ao usuário onde salvou, que ele pode editar antes da próxima etapa e quais conceitos usados estavam vencidos ou não verificados.
8. Não comece a etapa seguinte sem o usuário pedir.

Nunca use saídas antigas de `output/` como modelo de qualidade. As regras estão
na Camada 3. Saídas antigas são as piores saídas.

## Como construir um workspace novo

Cinco fases, com o usuário. Não pule o checkpoint de cada fase.

**1. Descoberta.** Pergunte o fluxo de ponta a ponta: com o que começa, com o
que termina. Ache os pontos naturais onde um humano quer revisar. Para cada
etapa: o que entra, o que sai, o que o agente precisa saber. Liste: contexto
compartilhado entre etapas; dados que mudam de usuário para usuário (viram
placeholders); etapas opcionais (viram seções condicionais); ferramentas
externas (Node, Python, ffmpeg); skills já instaladas que servem ao domínio.
Se o projeto entrega software, inclua a etapa final de desempenho (ver
"Fechamento: otimização de desempenho").
Separe o que o agente precisa saber em dois grupos (Regra 1): regras estáveis
de produção e fatos do negócio que mudam. Se houver fatos que mudam, proponha
a pasta `knowledge/` em OKF e liste os conceitos e quem os mantém.
*Checkpoint:* mostre o mapa do fluxo. O usuário confirma etapas, entregas e
se usa `knowledge/`.

**2. Mapeamento.** Escreva o contrato (Inputs, Process, Outputs) de cada etapa.
Desenhe o grafo de dependências em ASCII. Confira: sem referência circular, toda
saída é lida por alguma etapa seguinte ou é a entrega final, cada informação tem
um só arquivo de origem. *Checkpoint:* mostre o grafo e os contratos.

**3. Montagem.** Crie as pastas e arquivos com os modelos abaixo. Etapas
criativas (escrita, design, ideias) recebem pelo menos um Checkpoint e um Audit.
Etapas lineares (extrair, converter, renderizar) podem não ter. Arquivos de
referência levam `{{PLACEHOLDERS}}` para os dados do usuário. Coloque `.gitkeep`
em cada `output/`. Se usar `knowledge/`, crie `index.md`, `log.md` e um conceito
por arquivo com `status: draft` até o usuário preencher e revisar. Placeholders
não entram em `knowledge/`: fatos vêm de fontes, não do questionário.

**4. Questionário.** Varra todos os `{{...}}`. Separe em dois grupos:
*sistema* (identidade, marca, design, ferramentas: viram perguntas) e
*execução* (tema, público da peça, escopo: ficam para a etapa 01). Escreva o
questionário com as regras da seção "Questionário".

**5. Validação.** Rode a lista de "Validação" abaixo. Corrija o que falhar e
rode de novo. Entregue um relatório curto de passou/falhou.

## Convenções (as 15 do ICM, resumidas)

1. **Contrato de etapa:** todo CONTEXT.md de etapa tem Inputs, Process, Outputs. Sem exceção.
2. **Passagem por `output/`:** etapa N grava em `stages/0N-nome/output/`; etapa N+1 lê de `../0N-nome/output/`.
3. **Referência numa direção só:** se A aponta para B, B não aponta para A.
4. **Rota por seção:** a tabela Inputs diz qual seção do arquivo carregar, não só o arquivo. Use "Arquivo inteiro" quando precisar de tudo.
5. **Fonte canônica:** cada regra mora num só arquivo. Os outros apontam para ele.
6. **CONTEXT.md é rota, não conteúdo:** sem definições, regras ou exemplos longos. 25 a 80 linhas.
7. **Pré-requisitos:** guia de instalação de ferramenta fica em `references/` da etapa que usa (ou em `shared/` se várias usam).
8. **Questionário:** ver seção própria.
9. **Skills empacotadas:** skills de domínio podem ser copiadas para `skills/` e citadas na tabela Inputs. Não empacote skills sobre o próprio agente.
10. **Spec é contrato:** etapas de especificação dizem O QUE e QUANDO, não COMO. Detalhes de implementação ficam na etapa de construção.
11. **Checkpoints:** etapas criativas param para o humano escolher a direção entre passos.
12. **Audit:** checklist com condição de aprovação sem ambiguidade, rodado antes de gravar a saída.
13. **Validação de valor:** etapas de conteúdo definem que tipo de valor a peça entrega e travam isso antes de escrever.
14. **Documentos acima de saídas:** o agente aprende com a Camada 3, nunca com saídas antigas.
15. **Constantes compartilhadas:** em workspaces que geram código, cores, fontes e tempos ficam num arquivo único que todo código importa.

**Limites:** CONTEXT.md até 80 linhas. Arquivo de referência até 200 linhas
(acima disso, divida). Nomes em `minusculas-com-hifen`, etapas com `01-`,
`02-`, placeholders em `{{CAIXA_ALTA_COM_UNDERLINE}}`, sem espaços em nomes.
Linguagem simples.

## Placeholders

- Sintaxe: `{{NOME_DA_MARCA}}`, `{{COR_PRIMARIA}}`. Nomes descritivos, prefixos comuns para grupos.
- Seção condicional, só envolvendo uma seção inteira (título e tudo abaixo dele até o próximo título de mesmo nível):

```
{{?ETAPA_VIDEO}}

## Configuração de vídeo

...

{{/ETAPA_VIDEO}}
```

- Nunca envolva item de lista ou trecho de frase.
- Não use placeholders em `CLAUDE.md`, no `CONTEXT.md` raiz nem no próprio questionário. Eles precisam funcionar antes do setup.

## Questionário

Regras: lista numerada única, sem grupos; todas as perguntas de uma vez;
só nível de sistema; derive o que for possível em vez de perguntar; cada
pergunta tem padrão ou exemplo; pergunte uma vez e nunca mais; para voz e
estilo, peça exemplos concretos (2 ou 3 frases que soam certo, 1 que soa
errado), não descrições.

Formato de cada pergunta:

```
### P1: [pergunta em linguagem simples]
- Placeholder: `{{NOME}}`
- Arquivos: `_config/identidade.md`, `stages/02-roteiro/references/voz.md`
- Tipo: texto livre | escolha | sim/não
- Padrão: [valor se o usuário pular]
- Derivados: `{{OUTRO}}` (preenchido a partir desta resposta)

### P2: [etapa opcional?]
- Tipo: sim/não
- Se NÃO: remover `stages/0N-nome/` e o bloco `{{?NOME}}`
```

Se houver regras de voz derivadas, mostre as regras montadas ao usuário para
revisão antes de fechar o setup.

## Modelos

**`CLAUDE.md` do workspace (Camada 0)**

```
# [Nome do workspace]

[Uma frase: o que este workspace faz.]

## Mapa de pastas
[árvore com uma linha de descrição por pasta]

## Gatilhos
| Palavra | Ação |
|---|---|
| `setup` | Rodar o questionário de onboarding |
| `status` | Mostrar o estado de todas as etapas |

## Rotas
| Tarefa | Ir para |
|---|---|
| [tarefa 1] | `stages/01-[nome]/CONTEXT.md` |

## O que carregar
| Tarefa | Carregar | NÃO carregar |
|---|---|---|
| [tarefa 1] | [lista mínima] | [o que pular e por quê] |

## Passagem entre etapas
Cada etapa grava em seu `output/`. A seguinte lê de lá. Se você editar uma
saída, a etapa seguinte usa a sua versão.
```

**`CONTEXT.md` do workspace (Camada 1)**

```
# [Nome do workspace]

[Uma frase.]

## Rotas por tarefa
| Tipo de tarefa | Ir para | Descrição |
|---|---|---|
| [tarefa] | `stages/01-[nome]/CONTEXT.md` | [o que a etapa faz] |

## Recursos compartilhados
| Recurso | Local | Contém |
|---|---|---|
| [pasta] | `_config/` | [o que tem] |
```

**`CONTEXT.md` de etapa (Camada 2)**

```
# [Nome da etapa]

[Uma frase: o que esta etapa faz.]

## Inputs
| Origem | Arquivo/Local | Seção/Escopo | Por quê |
|---|---|---|---|
| Etapa anterior | `../01-[nome]/output/[slug]-[tipo].md` | Arquivo inteiro | Material de entrada |
| Referência | `references/[arquivo].md` | Seção "[nome]" | [o que dá] |
| Conhecimento | `../../knowledge/[grupo]/[conceito].md` | Arquivo inteiro | [fato que a etapa usa] |

## Process
1. [Uma ação concreta por passo. Específico o bastante para dois agentes
   chegarem a saídas parecidas. Ruim: "escreva o roteiro". Bom: "escreva o
   roteiro inteiro de uma vez e audite contra as restrições de voz".]
2. ...
N. Salvar em output/

## Checkpoints
| Depois do passo | Agente mostra | Humano decide |
|---|---|---|
| [n] | [opções ou rascunho] | [direção] |

## Audit
| Verificação | Condição de aprovação |
|---|---|
| [nome] | [o que é passar, sem ambiguidade] |

## Outputs
| Artefato | Local | Formato |
|---|---|---|
| [nome] | `output/[slug]-[tipo].md` | [descrição] |
```

Apague Checkpoints e Audit em etapas lineares.

## Conhecimento em OKF (`knowledge/`)

Formato baseado no Open Knowledge Format v0.2 do Google. Cada arquivo é um
"conceito" com frontmatter YAML e corpo em markdown. Só `type` é obrigatório.

```
---
type: Regra de Negócio           # obrigatório; texto livre
title: Política de reembolso
description: Uma frase que resume o conceito.
tags: [financeiro, clientes]
status: stable                   # draft | stable | deprecated (ausente = stable)
generated: { by: claude/opus, at: 2026-10-30T14:00:00Z }
verified: { by: human:yolo, at: 2026-10-30T15:00:00Z }
stale_after: 2027-01-30T00:00:00Z
sources:
  - id: politica-v3
    resource: https://exemplo.com/politica
    title: Política de reembolso v3
---

O prazo é de 7 dias.[^politica-v3]

[^politica-v3]: Política de reembolso v3
```

Campos e convenções:

- **Autor (`generated.by`, `verified[].by`):** `ferramenta/versão` para agente, `human:<id>` para pessoa, `process:<id>` para rotina automática. Conteúdo revisado por pessoa sempre usa `human:`.
- **`verified`** pode ser um item ou uma lista. Um item sozinho conta como lista de um.
- **Fonte por afirmação:** nota de rodapé cujo rótulo é o `id` em `sources`.
- **Datas:** ISO 8601 com fuso (`2026-10-30T14:00:00Z`). Em `log.md`, títulos `## AAAA-MM-DD`, mais recente primeiro.
- **Nomes reservados:** `index.md` e `log.md`. Não use para conceitos.
- **Links** entre conceitos com caminho a partir de `knowledge/` (`/precos/cama-casal.md`). Link quebrado não é erro: pode ser conhecimento ainda não escrito.
- **`index.md`** lista os conceitos da pasta, um por linha: `* [Título](arquivo.md) - description`.
- Tipo desconhecido ou campo extra não é erro. Preserve campos que você não conhece ao reescrever.

### Ler um conceito

Ao carregar um arquivo de `knowledge/` numa etapa:

1. Leia o frontmatter antes do corpo.
2. **Nível de confiança:** sem `verified` = não verificado; só por agente ou `process:` = confirmado por máquina; com `human:` = revisado por pessoa.
3. **Vencido:** se hoje >= `stale_after`, o conceito está vencido.
4. **`status: deprecated`:** não use; procure o substituto pelos links. **`draft`:** use só com aviso.
5. Use o conceito mesmo sem verificação (o OKF nunca rejeita um conceito), mas registre: vencido, não verificado ou rascunho vira aviso no Audit e na mensagem final ao usuário.
6. Se o conceito vencido ou não verificado decide um número que vai para o cliente (preço, prazo, valor), pare num Checkpoint e peça confirmação ao usuário antes de seguir.

### Escrever ou atualizar um conceito

Só quando o usuário pedir ou quando uma etapa tem essa tarefa no Process.

1. Um conceito por arquivo. Até 200 linhas; acima disso, divida em conceitos ligados.
2. Preencha `generated` com você como autor e a hora atual. Não preencha `verified` em seu nome como `human:`.
3. Ponha cada fato com nota de rodapé para uma entrada de `sources`. Fato sem fonte fica com `status: draft`.
4. Defina `stale_after` para dados com prazo (preço, estoque, contato). Pergunte o prazo ao usuário se não souber.
5. Atualize a linha do conceito no `index.md` da pasta e acrescente uma entrada no `log.md` (`**Creation**`, `**Update**` ou `**Deprecation**`).
6. Quando o usuário revisar e aprovar, acrescente `{ by: human:<id dele>, at: <agora> }` em `verified` e mude `status` para `stable`.
7. Para aposentar um conceito, use `status: deprecated` e um link para o substituto. Não apague: outros conceitos e saídas antigas apontam para ele.

### Cálculos atestados (avançado)

O OKF tem o tipo `Attested Computation`: uma consulta ou cálculo fixo (SQL, script)
com parâmetros tipados, em que o agente só preenche os valores e não reescreve
o cálculo. Use só se o usuário tiver métricas oficiais calculadas por código.
O agente nunca edita o bloco `# Computation`; só preenche `parameters`.

## Validação

Rode antes de entregar um workspace novo ou alterado:

1. Todo caminho em toda tabela Inputs aponta para um arquivo que existe.
2. O grafo de referências não tem ciclo.
3. Todo `{{PLACEHOLDER}}` tem pergunta no questionário, e toda pergunta tem placeholder em algum arquivo.
4. Todo bloco `{{?SECAO}}` envolve uma seção inteira.
5. A saída da etapa N é o caminho que a etapa N+1 lê.
6. Nenhum CONTEXT.md tem conteúdo de referência (só título, frase, Inputs, Process, Checkpoints, Audit, Outputs).
7. Etapas criativas têm Checkpoint e Audit; os números de passo nos Checkpoints existem.
8. Especificações não têm detalhe de implementação.
9. CONTEXT.md até 80 linhas; referência até 200 linhas.
10. Nomes em minúsculas com hífen; etapas numeradas com dois dígitos; `.gitkeep` em `output/` vazio.
11. Ferramentas externas têm guia de instalação.
12. Se usar `knowledge/`: todo conceito tem frontmatter com `type`; `index.md` e `log.md` seguem o formato e não guardam conceitos; datas em ISO 8601 com fuso; nenhum frontmatter OKF fora de `knowledge/`; nenhum placeholder dentro de `knowledge/`.
13. Se usar `knowledge/`: toda etapa que lê um conceito com preço, prazo ou valor para cliente tem no Audit a checagem "conceitos usados não estão vencidos nem em rascunho, ou o usuário confirmou".

## Fechamento: otimização de desempenho

Vale quando o projeto entrega software: app, site, API ou painel. Na
Descoberta, ponha uma última etapa `0N-desempenho` no mapa do fluxo, ou um item
final no plano do projeto quando não houver workspace. Ela só roda quando todo o
resto está pronto e publicado no lugar onde vai rodar de verdade. Otimizar
antes disso mede um app que ainda vai mudar.

**Protocolo**
1. **Medir antes de mexer.** Anote no plano os números de partida: velocidade
   de carregamento no celular (LCP, INP, CLS), tamanho do JS por tela, tempo e
   quantidade de consultas por tela e uso de CPU no servidor.
2. **Corrigir pelo maior gargalo, um de cada vez.** Use a lista abaixo como
   cardápio. Ela não é tarefa obrigatória: só entra o item que a medição apontar.
   Marque como "não se aplica" o que a arquitetura já resolve ou não usa.
3. **Validar em condições reais.** Repita as medições em celular simples e rede
   lenta, com os dados completos, e compare com os números de partida. Uma
   correção que não melhora o número volta atrás.

**Checklist** (31 dicas do reel da @breakingbreach, vistas em 2026-11-03)
- *Medir:* rastrear requisições lentas no servidor; acompanhar a velocidade de
  usuários reais com uma ferramenta de monitoramento.
- *Banco e servidor:* corrigir consultas N+1; rodar em paralelo as requisições
  independentes; evitar requisições duplicadas; selecionar só as colunas usadas;
  criar índices para as consultas comuns; paginar resultados da API; guardar em
  cache os dados muito lidos; pôr timeout nas APIs externas; mandar tarefas
  lentas para segundo plano; deixar o servidor perto dos usuários; usar pool de
  conexões; balancear carga entre instâncias.
- *O que vai para o navegador:* renderizar no servidor ou no build; dividir o
  JavaScript por página; remover dependências não usadas; carregar scripts de
  terceiros depois da página; ativar compressão Brotli ou Gzip; servir arquivos
  estáticos por CDN; ativar cache do navegador para os arquivos estáticos.
- *Imagens e fontes:* servir imagens em WebP; adiar as imagens abaixo da dobra;
  hospedar as fontes no próprio site e só com os pesos usados.
- *Telas:* mostrar esqueleto de carregamento; atualizar a tela antes da resposta
  do servidor, com desfazer se der erro; debounce na busca e no autocompletar;
  virtualizar listas longas; evitar renderizações desnecessárias; transmitir
  respostas de IA token a token (só se houver IA).
- *Validar:* testar em celular simples e rede lenta.

Antes de mudar uma tela por causa de desempenho, confira a mudança com as
heurísticas de Nielsen e com o design system do projeto.

## Segurança e dados

- Nunca grave chave de API, senha ou token em arquivo do workspace. Use `.env` fora do controle de versão e um arquivo modelo só com nomes das variáveis.
- Não grave dados pessoais de clientes em referências nem em `knowledge/` sem necessidade. Se precisar, use só o mínimo e avise o usuário (LGPD).
- Etapas que chamam serviços externos (API de voz, imagem, IA de outro fornecedor) mandam dados para fora. Marque isso no CONTEXT.md da etapa e avise o usuário no setup.
- Skill copiada da internet para `skills/` é código de terceiro. Audite antes de copiar.
