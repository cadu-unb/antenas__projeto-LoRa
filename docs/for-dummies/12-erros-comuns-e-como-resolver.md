# Erros comuns e como resolver

## FAILED_MEMORY_LIMIT

**Mensagem:** "Limite de memória atingido: X GB usados de 25 GB permitidos."

**Causa:** A simulação tentou usar mais RAM do que o limite configurado (`MAX_RAM_GB = 25`).

**Solução:**
1. Reduza o número de segmentos (campo `segments` na geometria, se visível).
2. Use o modo **Padrão** em vez de **Preciso**.
3. Feche outras aplicações pesadas e repita.

---

## FAILED_TIME_LIMIT

**Mensagem:** "Simulação abortada após X min (limite: 30 min)."

**Causa:** A simulação ultrapassou o tempo máximo permitido (`MAX_RUNTIME_MIN = 30`).

**Solução:**
1. Use o modo **Padrão** em vez de **Preciso**.
2. Reduza a complexidade da geometria.
3. O modo **Rápido** nunca atinge este limite.

---

## Job status CANCELLED

**Causa:** Você clicou em "✕ Cancelar" ou o servidor reiniciou durante a simulação.

**Solução:** Inicie uma nova simulação.
O log parcial ainda está disponível em `backend/data/simulations/{job_id}/log.jsonl`.

---

## Barra de progresso trava em 0%

**Causa provável:** Backend não está rodando ou a rota `/api/v1/jobs/{id}` não responde.

**Solução:**
1. Verifique se o backend está ativo: `docker compose up` ou `uvicorn app.main:app`.
2. Abra o console do navegador (F12) e veja erros de rede.

---

## "Tipo sem solver analítico. Fixture fixa retornada."

**Causa:** O tipo de antena selecionado não tem solver implementado. Um resultado genérico foi retornado.

**Solução:** Use um dos 6 tipos suportados: `dipolo`, `monopolo`, `helicoidal`, `parabolica`, `pcb_compact`, `commercial_omni_6dbi`.

---

## SWR muito alto (> 5)

**Causa:** Geometria fora de ressonância para a frequência configurada.

**Solução:**
- Para dipolo: comprimento ≈ λ/2. Fórmula: `L = 150 / f_MHz` metros.
- Para monopolo: altura ≈ λ/4. Fórmula: `h = 75 / f_MHz` metros.
- Ajuste o comprimento até o SWR cair abaixo de 2.

---

## PyNEC não disponível (aviso no resultado)

**Causa:** PyNEC requer compilador C (MSVC no Windows, gcc no Linux).

**Impacto:** Modos Padrão e Preciso usam solver analítico como fallback. Resultados continuam válidos.

**Para instalar PyNEC no Linux/WSL:**
```bash
pip install PyNEC
```

**No Windows:** instale Visual C++ Build Tools antes de `pip install PyNEC`.
