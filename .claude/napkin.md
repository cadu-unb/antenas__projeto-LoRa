# Napkin Runbook

## Curation Rules
- Re-prioritize on every read.
- Keep recurring, high-value notes only.
- Max 10 items per category.
- Each item includes date + "Do instead".

## Execution & Validation (Highest Priority)
1. **[2026-06-21] Hidden report folders are part of the working context**
   Do instead: use `rg --files -uu .reports` or PowerShell `Get-ChildItem -Force` when auditing reports.

## Shell & Command Reliability
1. **[2026-06-21] Prefer approved `uv` commands for Python checks**
   Do instead: run project tests through `uv run` when validating backend behavior.

## Domain Behavior Guardrails
1. **[2026-06-21] Distinguish implemented features from external MATLAB prompt outputs**
   Do instead: label `.reports/externo/prompt/return` MATLAB files as reference/generated external material unless mirrored in backend/frontend code.

## User Directives
1. **[2026-06-21] Keep project reports aligned with actual repo state**
   Do instead: cross-check report claims against source files, docs, tests, and prompt artifacts before editing summaries.
