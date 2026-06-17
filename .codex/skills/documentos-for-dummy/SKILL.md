---
name: documentos-for-dummies
description: Generate beginner-first documentation for any application, library, script, service, server, pipeline, CLI, API, module, or technical repository. Use when Codex needs to explain how to install, configure, run, test, inspect files, understand folder structure, trace function/module/data flows, document commands, document servers, document scripts, document environment variables, or create docs/for-dummies guides for practical project usage without assuming prior programming or terminal knowledge.
---

# Documentos For dummies

## Core Goal

Produce documentation that helps an absolute beginner open a technical project, understand what it does, run it, find important files, follow basic flows, and modify only safe areas.

Write in Portuguese unless the user asks for another language or the repository clearly uses another language for user-facing documentation.

## Workflow

1. Inspect the repository before writing:
   - Read `README.md`, package/config files, scripts, entrypoints, server files, CLI files, test files, `.env.example`, docs, and main source folders.
   - Use `rg --files` first, then inspect only files relevant to practical usage and flow understanding.
   - Do not read secrets from `.env` files unless the user explicitly asks and it is necessary; prefer `.env.example`.
2. Identify what exists:
   - Languages, package managers, dependency files, scripts, CLIs, servers, tests, generated outputs, data files, APIs, routes, modules, and important folders.
   - Commands that are actually present in files or clearly implied by standard tooling. Do not invent commands.
3. Trace simple flows:
   - For scripts and CLIs, explain what runs first and what it calls next.
   - For servers and APIs, explain request path, route/controller/service/data flow when identifiable.
   - For pipelines, explain input, processing steps, and output files.
4. Create `docs/for-dummies/` in the target repository.
5. Always create `docs/for-dummies/README.md`.
6. Create extra files only when useful for the project, such as:
   - `como-iniciar-o-projeto.md`
   - `como-rodar-o-servidor.md`
   - `como-executar-scripts.md`
   - `como-entender-a-estrutura.md`
   - `como-funcionam-os-fluxos.md`
   - `como-funcionam-as-funcoes.md`
   - `erros-comuns.md`
   - `glossario.md`
7. If requested, create a report with created files, analyzed files, identified commands, detected servers/scripts, documented function flows, unknown points, and future documentation recommendations.

## Writing Rules

- Use simple, patient, practical language.
- Assume the reader does not know programming, terminal usage, folder structures, dependencies, APIs, routes, servers, or environment variables.
- Explain technical terms immediately in plain language.
- Prefer short useful explanations and numbered steps.
- Always include file paths when discussing files.
- Always explain why important commands are used.
- Use fenced code blocks for commands.
- Say `não identificado automaticamente` when the repository does not show enough evidence.
- Do not invent files, commands, ports, servers, environment variables, or behavior.
- Connect explanations to real project usage.
- Warn what can be changed safely and what should not be changed without understanding impact.

## Required README Structure

`docs/for-dummies/README.md` must include these sections when applicable:

```markdown
# Documentação for dummies

## O que é este projeto?

## O que você consegue fazer com ele?

## Antes de começar

## Como iniciar do zero

## Como saber se funcionou?

## Problemas comuns

## Glossário rápido

## Encadeamento de funções
```

Add or remove subsections inside those sections based on project evidence, but keep the beginner-first purpose.

## Flow Explanation Pattern

When functions, scripts, modules, or files call each other, explain as numbered steps:

1. The user runs or opens the entrypoint.
2. The entrypoint reads inputs or configuration.
3. It calls the next function, script, route, or module.
4. That part processes data.
5. The result appears as terminal output, file output, API response, UI screen, plot, or another visible effect.

If the flow cannot be confirmed from code, say which part is not identified automatically.

## Quality Checklist

Before finishing, verify the docs answer:

- What is this project or part?
- What is it for?
- Where is it located?
- Which files are involved?
- What does each important file do?
- What must be installed first?
- Which commands are used?
- How does the user start the app, server, script, or process?
- What should happen after running it?
- Which common errors may appear?
- How can common errors be solved?
- How does the basic function/module/data flow work?
- What can the user modify safely?
- What should the user avoid changing without understanding impact?
