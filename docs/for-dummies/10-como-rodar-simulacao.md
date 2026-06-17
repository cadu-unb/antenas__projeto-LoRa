# Como rodar uma simulação

## Modos disponíveis

| Modo | Botão | Tempo | Quando usar |
|---|---|---|---|
| Rápido | Calcular (Rápido) | < 0,5 s | Exploração inicial, ajuste de parâmetros |
| Padrão | Simular (Padrão) | 1–5 s | Resultado mais preciso via MoM |
| Preciso | Simular (Preciso) | 2–10 s | Maior resolução numérica |

## Passo a passo

1. Abra o **Sandbox** (`/sandbox.html`).
2. Selecione o tipo de antena (Dipolo, Monopolo, Helicoidal, Parabólica).
3. Configure frequência e geometria no **Painel 2**.
4. Clique em **Simular (Padrão)** ou **Simular (Preciso)**.
5. A interface retorna um `job_id` imediatamente — a simulação roda em background.
6. A barra de progresso mostra o andamento em tempo real (atualiza a cada 2 s).
7. Quando o status mudar para **DONE**, o resultado aparece automaticamente no Painel 3.

## Cancelar uma simulação

Clique em **✕ Cancelar** enquanto a barra estiver visível.
O servidor interrompe o job e salva o log parcial.

## Simulações enfileiradas

O sistema processa um job por vez. Se você iniciar outro enquanto o primeiro ainda roda,
o novo entra na fila (status **PENDING**) e começa quando o anterior terminar.

## Log de simulação

Cada job grava um arquivo JSONL em:

```
backend/data/simulations/{job_id}/log.jsonl
```

Útil para diagnóstico quando a simulação falhar.
