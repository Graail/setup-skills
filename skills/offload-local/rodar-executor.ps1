<#
.SYNOPSIS
  Roda o executor local (Qwen3.8-Flash-Next no Strata) tarefa por tarefa, cada uma numa conversa nova.

.DESCRIPTION
  Rotação automática de contexto: cada tarefa do TASKS.md roda num processo
  novo do executor, com o contexto vazio. O que passa de uma tarefa para a
  outra fica nos arquivos (TASKS.md, PROGRESS.md, BLOCKED.md), não na conversa.

  Para quando:
  - não há mais tarefa com "Status: pendente";
  - uma tarefa termina como "bloqueada";
  - o status da tarefa não muda (o executor travou ou o contexto estourou);
  - sobra mudança sem commit depois da tarefa;
  - a branch atual é a main;
  - chega ao limite -MaxTarefas.

.EXAMPLE
  # Na raiz do projeto:
  & "$HOME\.claude\skills\offload-local\rodar-executor.ps1"
  & "$HOME\.claude\skills\offload-local\rodar-executor.ps1" -MaxTarefas 3
  & "$HOME\.claude\skills\offload-local\rodar-executor.ps1" -Comando claude-local -DryRun
#>
param(
  [string]$Comando = (Join-Path $PSScriptRoot "claude-local.cmd"),
  [int]$MaxTarefas = 10,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Ler-Tarefas {
  if (-not (Test-Path "TASKS.md")) { throw "TASKS.md não existe nesta pasta. Rode o script na raiz do projeto." }
  $texto = Get-Content "TASKS.md" -Raw -Encoding utf8
  $blocos = [regex]::Matches($texto, '(?ms)^## (T\d+)\b.*?(?=^## T\d+\b|\z)')
  foreach ($b in $blocos) {
    $status = [regex]::Match($b.Value, '(?m)^- Status:\s*(.+)$').Groups[1].Value.Trim()
    $branch = [regex]::Match($b.Value, '(?m)^- Branch:\s*(.+)$').Groups[1].Value.Trim()
    [pscustomobject]@{ Id = $b.Groups[1].Value; Status = $status; Branch = $branch }
  }
}

# Mudanças sem commit fora dos arquivos do protocolo (o executor atualiza
# TASKS.md, PROGRESS.md e BLOCKED.md depois do commit da tarefa).
function Sujo {
  git status --porcelain --untracked-files=no |
    Where-Object { $_ -notmatch '\s(TASKS|PROGRESS|BLOCKED)\.md$' }
}

function Status-De([string]$id) {
  (Ler-Tarefas | Where-Object Id -eq $id | Select-Object -First 1).Status
}

if (-not $DryRun -and -not (Get-Command $Comando -ErrorAction SilentlyContinue)) {
  throw "Comando '$Comando' não encontrado. Passe o comando do executor com -Comando."
}

$projeto = Split-Path -Leaf (Get-Location)
$pastaLog = Join-Path $env:TEMP "offload-logs\$projeto"
New-Item -ItemType Directory -Force $pastaLog | Out-Null

# O executor pode editar arquivos e rodar só estes comandos sem perguntar.
$permitidos = @(
  "Read", "Edit", "Write", "Glob", "Grep",
  "Bash(git status*)", "Bash(git diff*)", "Bash(git branch --show-current)",
  "Bash(git switch *)", "Bash(git add *)", "Bash(git commit *)", "Bash(git restore *)",
  "Bash(git log *)", "Bash(npm run build*)", "Bash(npm run lint*)",
  "Bash(npx tsc *)", "Bash(grep *)"
)
$proibidos = @(
  "Bash(git push*)", "Bash(git merge*)", "Bash(git rebase*)", "Bash(git reset*)",
  "Bash(npm install*)", "Bash(npm uninstall*)", "Bash(rm *)",
  "Read(.env.local)", "Read(**/.env*)", "WebFetch", "WebSearch"
)

for ($n = 1; $n -le $MaxTarefas; $n++) {
  $tarefa = Ler-Tarefas | Where-Object Status -eq "pendente" | Select-Object -First 1
  if (-not $tarefa) { Write-Host "Fila vazia: nenhuma tarefa pendente."; break }

  $atual = (git branch --show-current).Trim()
  if ($atual -eq "main" -and $tarefa.Branch -eq "") {
    Write-Host "Parei: a branch atual é a main e a $($tarefa.Id) não diz a branch."; break
  }
  if (Sujo) {
    Write-Host "Parei: há mudanças sem commit antes da $($tarefa.Id). Resolva e rode de novo."; break
  }

  $prompt = @"
Você é o EXECUTOR local. Siga a skill offload-local, papel executor.
Faça só a tarefa $($tarefa.Id) do TASKS.md, do começo ao fim, e pare.
Você roda pelo script de rotação: não espere /clear e não comece outra tarefa.
"@
  # Uma linha só: o claude-local.cmd repassa os argumentos com %*, e uma quebra de linha
  # corta o resto (as flags de permissão sumiam e o executor ficava sem poder editar).
  $prompt = ($prompt -replace "\r?\n", " ").Trim()

  $log = Join-Path $pastaLog ("{0}-{1:yyyyMMdd-HHmmss}.log" -f $tarefa.Id, (Get-Date))
  Write-Host "[$n] $($tarefa.Id) (branch $($tarefa.Branch)) -> log: $log"

  if ($DryRun) {
    Write-Host "    DryRun: rodaria '$Comando -p ...' e pararia aqui."; break
  }

  & $Comando -p $prompt --permission-mode acceptEdits `
      --allowedTools $permitidos --disallowedTools $proibidos *> $log

  $depois = Status-De $tarefa.Id
  Write-Host "    status: $depois"

  if ($depois -like "bloqueada*") { Write-Host "Parei: $($tarefa.Id) bloqueada. Veja o BLOCKED.md."; break }
  if ($depois -eq "pendente") {
    Write-Host "Parei: $($tarefa.Id) continua pendente (travou ou o contexto estourou). Veja o log."; break
  }
  if (Sujo) {
    Write-Host "Parei: $($tarefa.Id) deixou mudanças sem commit. Veja o log."; break
  }
}
