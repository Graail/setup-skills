# Roteiro de início (para o Claude)

Siga quando a pessoa disser para começar um projeto com este repositório.

## No início do projeto

1. Clone este repositório numa pasta irmã do projeto (`../setup-skills`). Se ele
   já existir, rode `git pull` nele.
2. Rode `node ../setup-skills/sync.mjs start .` na pasta do projeto. Isso instala
   as skills em `.claude/skills/` e grava `.claude/setup-skills.lock.json`.
3. Se o repositório tiver `CLAUDE.md`, o `start` copia esse arquivo para
   `.claude/setup-skills.CLAUDE.md`. Garanta que o `CLAUDE.md` do projeto tenha,
   na primeira linha, `@.claude/setup-skills.CLAUDE.md`, para que as regras
   gerais valham no projeto. Crie o `CLAUDE.md` do projeto se ele não existir.
4. Rode a triagem da skill `optimize-workspace` ("Ao começar um projeto novo").
5. Diga à pessoa, em poucas linhas, o que foi instalado e o que a triagem
   recomenda.

## Durante o projeto

- Quando uma regra de uma skill falhar ou faltar, corrija a skill **dentro do
  projeto** e anote o motivo. Regra que só vale para este projeto vai no
  `CLAUDE.md` do projeto, não na skill.

## No fim do projeto (ou quando a pessoa pedir paridade)

1. Rode `node ../setup-skills/sync.mjs status .`.
2. Para cada skill que "o projeto melhorou", mostre à pessoa a diferença e
   pergunte se ela vale para todos os projetos.
3. Com o sim, rode `push` só com essas skills, registre em `EVOLUCAO.md` (data,
   projeto, o que mudou e por quê), commite e envie o setup-skills.
4. Skill "mudou nos dois lados": compare as duas versões, junte à mão e mostre
   o resultado antes de enviar.
