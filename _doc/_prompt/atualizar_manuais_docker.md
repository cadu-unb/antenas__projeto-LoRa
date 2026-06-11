# Prompt — Atualizar Manuais com Docker

```markdown
# PAPEL E CONTEXTO

Você é o Arquiteto de Software Principal e responsável por documentação técnica, operação e onboarding do projeto `antenas__projeto-LoRa`.

A aplicação agora envolve execução local com `uv`, interface Streamlit e execução via Docker/Docker Compose. Precisamos atualizar os arquivos em `doc/manual/` para refletir o estado operacional real da aplicação.

Antes de escrever, leia:

- `doc/manual/usuario_simulador_multino.md`
- `doc/manual/preparacao_kml_google_earth.md`
- `doc/manual/metricas_rf_e_interpretacao.md`
- `doc/manual/operacao_lan_e_deploy.md`
- `pyproject.toml`
- `Dockerfile`
- `docker-compose.yml`
- `src/lora_antenna/app.py`
- `src/lora_antenna/pages/standalone.py`
- `src/lora_antenna/pages/campus.py`

# OBJETIVO

Atualizar a documentação em `doc/manual/` para que um usuário consiga:

1. Entender a finalidade do simulador.
2. Preparar corretamente um KML no Google Earth.
3. Rodar a aplicação localmente com `uv`.
4. Rodar a aplicação via Docker/Docker Compose.
5. Acessar a aplicação em LAN pela porta `3953`.
6. Interpretar métricas RF, SIR, risco, viabilidade e canais.
7. Resolver erros comuns de KML, Docker, portas, dependências e SRTM.

# ARQUIVOS A ATUALIZAR

## 1. `doc/manual/usuario_simulador_multino.md`

Atualizar para explicar o fluxo real da aplicação:

- Aba/página Standalone
- Aba/página Campus KML
- Upload de KML
- Cálculo batch multiponto
- SIR e interferência co-canal
- Otimização de canais
- Interpretação de `feasible`, `link_risk`, `sir_decodable`
- Limitações do modelo

O manual deve orientar o usuário final, sem entrar demais em código.

## 2. `doc/manual/preparacao_kml_google_earth.md`

Atualizar com instruções práticas:

- criar marcadores P1–P8
- criar polígonos `BUILDING`, `OBSTACLE`, `CAMPUS`
- exportar como `.kml`, não `.kmz`
- validar nomes dos pontos
- validar polígonos
- usar o arquivo existente `_path/kml/mascara_campus_darcy_ribeiro.kml` como exemplo
- explicar mensagens de erro comuns no upload

## 3. `doc/manual/metricas_rf_e_interpretacao.md`

Atualizar com:

- frequência ANATEL `915–928 MHz`
- canais usados pela aplicação
- potência em dBm
- FSPL
- potência recebida
- margem de enlace
- `feasible`
- `LinkRisk`: LOW, MEDIUM, HIGH
- SIR
- `sir_decodable`
- interferência co-canal
- diferença entre enlace viável e enlace decodificável
- por que `DEFAULT_RX_SENSITIVITY_DBM = -137.0`
- diferença entre distância Haversine e referência MATLAB/flat-earth

## 4. `doc/manual/operacao_lan_e_deploy.md`

Atualizar com foco operacional:

### Execução local com uv

Incluir comandos:

```powershell
uv sync --extra dev
uv run streamlit run src/lora_antenna/app.py --server.port 3953 --server.address 0.0.0.0
```

### Execução com Docker

Incluir:

```powershell
docker build -t lora-antenna-platform .
docker run --rm -p 3953:3953 lora-antenna-platform
```

### Execução com Docker Compose

Incluir:

```powershell
docker compose up --build
docker compose down
```

### Acesso LAN

Explicar:

- acessar `http://localhost:3953`
- acessar `http://<IP_DA_MAQUINA>:3953`
- descobrir IP no Windows com `ipconfig`
- liberar porta `3953` no firewall
- verificar container e logs

### Troubleshooting Docker

Incluir problemas comuns:

- porta `3953` já em uso
- Docker não iniciado
- build falha por dependência
- aplicação sobe mas não abre no navegador
- container sem acesso à internet para SRTM
- KML não aparece por volume/caminho errado
- diferença entre execução local e Docker

# REGRAS DE DOCUMENTAÇÃO

- Escrever em PT-BR.
- Usar linguagem clara, operacional e precisa.
- Não inventar comandos que não funcionam no estado atual do projeto.
- Se algum recurso ainda for parcial, marcar como “em desenvolvimento” ou “dependente da implementação”.
- Não remover a restrição ANATEL `915–928 MHz`.
- Não recomendar frequências `433 MHz` ou `868 MHz`.
- Não dizer que Docker está pronto se `Dockerfile` ou `docker-compose.yml` ainda não existirem.
- Usar caminhos relativos ao projeto.
- Manter cada manual focado no seu público:
  - usuário final
  - preparação KML
  - interpretação RF
  - operação/deploy

# VALIDAÇÃO FINAL

Depois de atualizar, verificar:

```powershell
rg -n "433|868" doc/manual
rg -n "3953|docker|uv run|streamlit|915" doc/manual
```

Se `433` ou `868` aparecerem, devem estar explicitamente marcados como fora da faixa ANATEL ou em contexto histórico de “não usar”.

# SAÍDA ESPERADA

Ao final, relatar:

- arquivos atualizados
- principais mudanças em cada manual
- qualquer ponto que permaneça dependente de implementação
```
