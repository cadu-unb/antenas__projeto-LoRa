# Prompt — Sistema de Antenas LoRa — Fase 3

## Objetivo

Implementar Sandbox Rápido com 4 painéis, preview analítico e botão de salvar na biblioteca.

Solvers avançados ficam fora desta fase.

## Contexto obrigatório

Leia antes de executar:

- `.plan/plan_v2.md`
- `.reports/sistema-antenas/Fase_2.md`, se existir

## Tarefas

1. Criar `frontend/public/sandbox.html`.
2. Criar layout em 4 painéis:
   - visual físico;
   - parâmetros;
   - resultado EM;
   - irradiação.
3. Painel visual:
   - dipolo: dois braços;
   - monopolo: haste + plano;
   - helicoidal: espiras;
   - parabólica: refletor + foco.
4. Painel parâmetros:
   - frequência;
   - geometria;
   - material;
   - alimentação;
   - solver.
5. Habilitar apenas modo `Rápido`.
6. Criar `backend/app/api/sandbox_routes.py`.
7. Implementar:

```text
POST /api/v1/sandbox/preview
```

8. Endpoint deve:
   - aceitar `AntennaSpec` parcial;
   - retornar resultado analítico em menos de 2 segundos;
   - usar fixture fixa para tipos sem solver real.
9. Painel resultado deve exibir:
   - ganho em dBi;
   - impedância em Ω;
   - SWR;
   - eficiência em %.
10. Painel irradiação deve usar Canvas 2D.
11. Botão "Salvar na Biblioteca" deve chamar `POST /api/v1/antennas`.
12. Criar `docs/for-dummies/05-como-criar-antena-no-sandbox.md`.
13. Criar `tests/test_sandbox.py`.

## Checkpoints obrigatórios

- [ ] Seleção de tipo muda SVG sem reload
- [ ] Edição de parâmetro atualiza visual em tempo real
- [ ] `POST /api/v1/sandbox/preview` retorna em menos de 2 segundos
- [ ] Painel 3 mostra valores com unidades corretas
- [ ] Painel 4 mostra diagrama polar 2D
- [ ] "Salvar na Biblioteca" grava spec com `results`
- [ ] Antena salva aparece em `library.html` sem reload
- [ ] Input inválido mostra erro antes de chamar API
- [ ] `pytest tests/test_sandbox.py` passa

## Devolutiva obrigatória

Criar:

```text
.reports/sistema-antenas/Fase_3.md
```

O relatório deve conter:

- telas criadas;
- endpoint criado;
- comportamento do preview;
- integração com biblioteca;
- comandos executados;
- resultado dos testes;
- checkpoints marcados;
- limitações dos solvers rápidos.

## Regra final

Não implemente MoM, Longley-Rice, Ray Tracing ou fila de jobs nesta fase.
