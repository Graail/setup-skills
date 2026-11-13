@echo off
rem Executor local: Claude Code ligado ao Strata (Qwen3.8-Flash-Next) em localhost.
rem O Strata precisa estar rodando (START-HERE.bat na pasta do Strata) antes deste comando.
rem O Strata ignora o nome do modelo; o Claude Code so precisa de um nome que conhece.
setlocal
if not defined STRATA_URL set "STRATA_URL=http://127.0.0.1:8080"
set "ANTHROPIC_BASE_URL=%STRATA_URL%"
if not defined ANTHROPIC_AUTH_TOKEN set "ANTHROPIC_AUTH_TOKEN=local"
set "ANTHROPIC_MODEL=claude-sonnet-5-5"
set "ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-sonnet-5-5"
set "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1"
claude %*
