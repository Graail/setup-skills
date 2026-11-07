---
name: nielsen-heuristicas
description: Audita ou orienta interfaces pelas 10 heurísticas de usabilidade de Nielsen. Use quando o usuário pedir uma auditoria de usabilidade ("audite o app", "avalie pelas heurísticas", "/nielsen-heuristicas"). Use também SEMPRE antes de criar ou alterar qualquer interface, app, site, landing page, tela, componente ou peça gráfica: quando Claude cria por conta própria, segue as heurísticas por padrão; quando o usuário pede algo específico ou manda uma referência para implementar (inclusive código importado de outro lugar), Claude checa o pedido contra as heurísticas e, se houver conflito, avisa e pergunta ANTES de implementar.
---

# Heurísticas de Nielsen

Três modos de uso. Escolha pelo contexto:

| Situação | Modo |
|---|---|
| O usuário pede uma auditoria de usabilidade | **A. Auditoria** |
| Claude vai criar uma interface ou peça por iniciativa própria | **B. Criação** |
| O usuário pede uma interface, mudança ou peça específica, ou manda uma referência | **C. Checagem do pedido** |

Fale sempre em português, de forma direta. Cite a heurística pelo número e nome (ex.: "H5 — Prevenção de erros").

## As 10 heurísticas e o que verificar

1. **H1 — Visibilidade do status do sistema.** Carregamentos com feedback (texto ou indicador); ações confirmadas (salvo, enviado); onde a pessoa está (aba ativa, título); dados reais em vez de valores fixos ("Dia 1 de 3" precisa vir dos dados).
2. **H2 — Correspondência com o mundo real.** Linguagem de quem usa, sem jargão técnico, códigos ou slugs na tela; ordem e formatos naturais (datas e moeda locais).
3. **H3 — Controle e liberdade.** Saída clara de qualquer fluxo (voltar, cancelar); desfazer ações; nada que prenda a pessoa num passo.
4. **H4 — Consistência e padrões.** Mesmo componente para a mesma função; convenções da plataforma (logout no perfil/conta, Enter envia formulário, ícones conhecidos); termos iguais em todo o produto; tokens do design system.
5. **H5 — Prevenção de erros.** Ações destrutivas ou difíceis de desfazer longe de toques acidentais e com confirmação; validação antes do envio; botões desabilitados explicando o porquê; padrões seguros.
6. **H6 — Reconhecer em vez de lembrar.** Opções visíveis; campos pré-preenchidos com o que o sistema já sabe; contexto à vista, sem exigir memória entre telas.
7. **H7 — Flexibilidade e eficiência.** Atalhos para quem já sabe (autocomplete, Enter, gestos); boas escolhas padrão; menos passos para tarefas frequentes.
8. **H8 — Estética e design minimalista.** Só o que importa para a tarefa; hierarquia clara; nada competindo com a ação principal; texto legível (tamanho e contraste WCAG AA: 4,5:1 para texto normal).
9. **H9 — Reconhecer, diagnosticar e recuperar de erros.** Mensagem diz o que houve e o que fazer, sem código de erro; nunca culpe a pessoa; ofereça o caminho de correção.
10. **H10 — Ajuda e documentação.** Dicas no contexto quando a tarefa não é óbvia; estados vazios que explicam o próximo passo.

Severidade (para auditorias e conflitos):
- **0** não é problema · **1** cosmético · **2** menor · **3** grave (corrigir antes de lançar) · **4** catástrofe (impede a tarefa).

## A. Auditoria

1. Mapeie as telas e fluxos principais (rotas, componentes, estados vazios, de erro e de carregamento). Se der para rodar o app, abra e use de verdade, num viewport de celular quando o produto for mobile.
2. Avalie cada tela contra as 10 heurísticas. Para cada achado registre: tela/arquivo:linha, heurística, severidade, o problema em uma frase, a recomendação concreta.
3. Entregue um relatório ordenado por severidade (maior primeiro), com:
   - resumo no topo (quantos achados por severidade e os 3 mais urgentes);
   - tabela de achados;
   - o que já está bom (curto).
4. Salve o relatório no projeto (ex.: `docs/AUDITORIA-NIELSEN.md`) quando houver um repositório; senão, entregue na conversa.
5. Não corrija nada durante a auditoria. Ao final, ofereça corrigir, começando pelos de severidade 3 e 4.

## B. Criação por iniciativa de Claude

Ao criar uma interface, app, site, landing page ou peça gráfica sem uma especificação detalhada do usuário, siga as 10 heurísticas por padrão: estados de carregamento, vazio e erro; mensagens de erro com saída; confirmação em ações destrutivas; padrões da plataforma; legibilidade e contraste. Não é preciso pedir permissão para seguir as heurísticas.

## C. Checagem do pedido do usuário (antes de implementar)

Quando o usuário pedir uma interface, uma mudança visual ou de fluxo, ou mandar uma referência ou código para implementar:

1. Antes de escrever código, confira cada item do pedido contra as 10 heurísticas.
2. Itens **sem conflito**: siga em frente.
3. Itens **com conflito**: NÃO implemente esses itens ainda. Diga ao usuário:
   - qual item conflita;
   - as heurísticas envolvidas (número e nome) e a severidade;
   - por que conflita, em uma ou duas frases, com o risco concreto para quem usa;
   - **1:** pergunte se ele quer seguir assim mesmo;
   - **2:** sugira uma alternativa que respeite as heurísticas e atenda à intenção do pedido.
4. Só pule a checagem se o usuário disser explicitamente que pode pular (para aquele pedido ou de forma geral). Registre a permissão e respeite o escopo dela.
5. Se o pedido for ambíguo e uma das leituras conflitar, implemente a leitura sem conflito e avise.
