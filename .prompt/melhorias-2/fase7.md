# Prompt — Melhorias 2 — Fase 7

Use como referência principal o arquivo `.reports/melhorias-2/plano-implementacao.md`, especialmente a seção **Fase 7 — API, Biblioteca e Frontend**. Esta fase deve respeitar os campos e presets definidos nas fases anteriores.

## Objetivo

Garantir que API, biblioteca e frontend preservem e exibam os novos campos físicos de `AntennaSpec`.

## Arquivos alvo

- `backend/app/api/library_routes.py`
- `backend/app/storage/antenna_storage.py`
- `frontend/public/sandbox.html`
- `frontend/public/library.html`
- `frontend/public/js/api-client.js`
- `docs/for-dummies/06-como-salvar-antena-json.md`

## Passos

1. Leia o plano e revise os campos novos de `AntennaSpec`.
2. Verifique se as rotas de CRUD preservam:
   - `gmax_dbi`;
   - `hpbw_deg`;
   - `polarization`;
   - `is_directional`;
   - `pattern_model`;
   - `practicality_score`;
   - `multi_direction_score`;
   - `notes`.
3. Atualize a biblioteca para exibir os campos físicos principais.
4. Atualize o sandbox para preencher valores sugeridos por tipo:
   - ganho máximo;
   - HPBW;
   - polarização;
   - modelo de padrão;
   - direcionalidade.
5. Coloque campos avançados em seção recolhível ou discreta, mantendo a UI limpa.
6. Atualize import/export JSON.
7. Atualize a documentação de salvamento de antena.
8. Faça teste manual mínimo:
   - criar `commercial_omni_6dbi`;
   - confirmar `hpbw_deg=35` e `polarization="linear vertical"`;
   - salvar e reabrir;
   - exportar JSON;
   - importar JSON antigo sem campos novos.

## Critérios de aceite

- Criar uma antena `commercial_omni_6dbi` pela UI salva `hpbw_deg`, `polarization` e scores.
- Importar JSON antigo continua funcionando.
- Exportar JSON novo mantém os campos.
- A UI não fica poluída por campos avançados.

## Validação

Execute testes de API existentes, se houver suite específica. Faça também o teste manual mínimo descrito nos passos.

## Report final obrigatório

Ao concluir, crie um report objetivo e conciso em `.reports/melhorias-2/fase7.md` descrevendo:

- mudanças na API/storage;
- mudanças no frontend;
- resultado do teste manual mínimo;
- testes automatizados executados;
- pendências ou riscos restantes.
