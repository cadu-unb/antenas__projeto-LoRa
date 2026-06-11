# Operação em LAN e Deploy

## Pré-requisitos

| Requisito | Versão mínima | Verificação |
|-----------|--------------|-------------|
| Python | 3.13 | `python --version` |
| uv | 0.4+ | `uv --version` |
| Git | qualquer | `git --version` |

Para execução via Docker:

| Requisito | Versão mínima | Verificação |
|-----------|--------------|-------------|
| Docker Desktop | 24+ | `docker --version` |
| Docker Compose | v2 (embutido no Docker Desktop) | `docker compose version` |

## Instalação

```powershell
git clone <url-do-repositorio>
cd antenas__projeto-LoRa
uv sync
```

`uv sync` lê `pyproject.toml` e instala todas as dependências em ambiente virtual isolado.

Para instalar também as dependências de desenvolvimento (pytest, pytest-cov):

```powershell
uv sync --extra dev
```

## Dependências Principais

| Pacote | Uso |
|--------|-----|
| `pydantic>=2.12` | Modelos de dados e validação |
| `shapely>=2.1` | Ray tracing 2D (interseção de polígonos) |
| `requests>=2.32` | Consulta SRTM via opentopodata.org |
| `matplotlib>=3.10` | Visualizações estáticas |
| `contextily>=1.7` | Mapas de fundo para matplotlib |
| `streamlit>=1.36` | Interface web da aplicação |
| `folium>=0.17` | Mapa interativo na página Campus KML |
| `streamlit-folium>=0.22` | Integração folium com Streamlit |

## Executando Testes

```powershell
uv run pytest
uv run pytest -v          # verbose
uv run pytest --cov=src   # com cobertura
```

## Execução Local com uv

### Acesso apenas local

```powershell
uv run streamlit run src/lora_antenna/app.py --server.port 3953
```

Acesso: `http://localhost:3953`

### Acesso em rede local (LAN)

```powershell
uv run streamlit run src/lora_antenna/app.py --server.port 3953 --server.address 0.0.0.0
```

Outros dispositivos na mesma rede acessam via `http://<IP_DA_MAQUINA>:3953`.

Para descobrir o IP no Windows:

```powershell
ipconfig
```

Procurar pelo endereço IPv4 da interface em uso (ex: `192.168.1.100`).

## Execução com Docker

### Build da imagem

```powershell
docker build -t lora-antenna-platform .
```

### Executar container

```powershell
docker run --rm -p 3953:3953 lora-antenna-platform
```

- `--rm`: remove o container ao parar
- `-p 3953:3953`: mapeia porta do host para porta do container

Acesso: `http://localhost:3953`

Para acesso LAN, o mapeamento `-p 3953:3953` já expõe em todas as interfaces do host.

### Parar o container

`Ctrl+C` no terminal, ou em outro terminal:

```powershell
docker ps                          # listar containers em execução
docker stop <container_id>
```

## Execução com Docker Compose

### Subir

```powershell
docker compose up --build
```

`--build` reconstrói a imagem se o `Dockerfile` ou código-fonte mudou.

Para rodar em background:

```powershell
docker compose up --build -d
```

### Verificar logs

```powershell
docker compose logs -f lora-ui
```

### Parar

```powershell
docker compose down
```

## Acesso em Rede Local (LAN)

Após subir a aplicação (uv ou Docker), qualquer dispositivo na mesma rede pode acessar:

```
http://<IP_DA_MAQUINA>:3953
```

### Liberar porta no firewall (Windows)

PowerShell como administrador:

```powershell
New-NetFirewallRule -DisplayName "LoRa UI 3953" `
  -Direction Inbound -Protocol TCP -LocalPort 3953 -Action Allow
```

Para verificar se a regra foi criada:

```powershell
Get-NetFirewallRule -DisplayName "LoRa UI 3953"
```

Para remover:

```powershell
Remove-NetFirewallRule -DisplayName "LoRa UI 3953"
```

## Uso Programático (sem UI)

O motor de cálculo pode ser usado diretamente via Python sem Streamlit:

```python
from pathlib import Path
from lora_antenna.gis.kml_parser import parse_kml
from lora_antenna.antenna.base import Antenna
from lora_antenna.gis.multi_link import run_link_budget_batch

doc = parse_kml(Path("campus.kml").read_bytes())
antenna = Antenna(gain_dbi=2.15, losses_db=0.5)
results = run_link_budget_batch(doc, antenna, frequency_hz=915_200_000.0)

for r in results:
    print(r.origin_label, "→", r.dest_label, r.link_margin_db, "dB", r.feasible)
```

## Troubleshooting Docker

### Porta 3953 já em uso

```
Error starting userland proxy: listen tcp4 0.0.0.0:3953: bind: address already in use
```

Verificar quem usa a porta:

```powershell
netstat -ano | Select-String "3953"
```

Parar o processo ou mudar a porta host: `-p 3954:3953`.

### Docker Desktop não iniciado

```
error during connect: ... Is the docker daemon running?
```

Iniciar Docker Desktop e aguardar o ícone na bandeja ficar estável.

### Build falha por dependência

```
ERROR [5/5] RUN uv sync --no-dev
```

Verificar `pyproject.toml` e `uv.lock` presentes na raiz. O `uv.lock` deve ser commitado no repositório.

### Aplicação sobe mas não abre no navegador

1. Verificar logs: `docker compose logs -f lora-ui`
2. Confirmar que Streamlit iniciou: procurar `You can now view your Streamlit app in your browser`
3. Verificar porta: `docker ps` deve mostrar `0.0.0.0:3953->3953/tcp`
4. Verificar firewall (ver seção acima)

### Container sem acesso à internet (SRTM)

O simulador consulta `opentopodata.org` para obter altitude SRTM dos nós.
Em container sem saída para internet:

- Altitude dos nós cai para 0 automaticamente
- Erro é silencioso: `distance_3d_m = distance_m` (sem componente de altitude)
- Funcionalidade RF não é bloqueada

Para adicionar DNS/proxy no compose:

```yaml
services:
  lora-ui:
    build: .
    ports:
      - "3953:3953"
    dns:
      - 8.8.8.8
```

### KML não carrega por volume/caminho errado

Se quiser montar um KML do host dentro do container via volume:

```powershell
docker run --rm -p 3953:3953 -v "C:\meus-kmls:/app/data" lora-antenna-platform
```

O KML deve ser feito upload via interface web — o volume `./data` é opcional e serve apenas para persistência de arquivos extras.

### Diferença entre execução local e Docker

| Aspecto | uv local | Docker |
|---------|----------|--------|
| Python | sistema/uv | 3.13-slim (isolado) |
| Dependências | `uv sync` | `uv sync --no-dev` (no-dev) |
| Hot reload | não (sem `--reload`) | não |
| Acesso LAN | requer `--server.address 0.0.0.0` | automático (CMD já inclui) |
| SRTM | depende do DNS local | depende da rede do container |

## Estrutura de Pacotes

```
src/lora_antenna/
├── core/           # Constantes, validadores — zero dependências externas
├── antenna/        # Modelos de antena — zero GIS
├── propagation/    # Friis, SIR, batch executor — zero GIS
│   └── batch/      # Contratos + executor puros
├── gis/            # Orquestração geográfica (KML, SRTM, ray tracing)
├── network/        # Plano de canais, coloração de grafo
└── models/         # Modelos compartilhados (GeographicPosition)
```

**Regra de fronteira (imutável):** `propagation/`, `core/`, `antenna/` nunca importam `gis/`, `network/`, `shapely`, `requests` ou `streamlit`.
