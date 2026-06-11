# Operação em LAN e Deploy

## Pré-requisitos

| Requisito | Versão mínima | Verificação |
|-----------|--------------|-------------|
| Python | 3.13 | `python --version` |
| uv | 0.4+ | `uv --version` |
| Git | qualquer | `git --version` |

## Instalação

```bash
git clone <url-do-repositorio>
cd antenas__projeto-LoRa
uv sync
```

`uv sync` lê `pyproject.toml` e instala todas as dependências em ambiente virtual isolado.

## Dependências principais

| Pacote | Uso |
|--------|-----|
| `pydantic>=2.12` | Modelos de dados e validação |
| `shapely>=2.1` | Ray tracing 2D (interseção de polígonos) |
| `requests>=2.32` | Consulta SRTM via opentopodata.org |
| `matplotlib>=3.10` | Visualizações estáticas |
| `contextily>=1.7` | Mapas de fundo para matplotlib |

## Executando Testes

```bash
uv run pytest
```

## Executando a UI (prospectivo)

**Atenção:** a interface Streamlit (`app.py`) ainda não foi implementada.
Os comandos abaixo são válidos **quando `app.py` existir**.

```bash
uv run streamlit run src/lora_antenna/app.py --server.port 3953
```

Acesso local: `http://localhost:3953`

## Acesso em Rede Local (LAN)

Para tornar a UI acessível a outros dispositivos na mesma rede:

```bash
uv run streamlit run src/lora_antenna/app.py \
  --server.port 3953 \
  --server.address 0.0.0.0
```

Outros dispositivos acessam via `http://<IP-do-servidor>:3953`.

Para descobrir o IP do servidor:

```bash
# Linux/macOS
ip addr show

# Windows
ipconfig
```

## Firewall

Liberar porta 3953 TCP de entrada:

```bash
# Linux (ufw)
ufw allow 3953/tcp

# Windows (PowerShell, como administrador)
New-NetFirewallRule -DisplayName "LoRa UI" -Direction Inbound -Protocol TCP -LocalPort 3953 -Action Allow
```

## Dockerfile (prospectivo)

**Atenção:** arquivo ainda não criado. Estrutura planejada:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

COPY src/ ./src/

EXPOSE 3953
CMD ["uv", "run", "streamlit", "run", "src/lora_antenna/app.py",
     "--server.port", "3953", "--server.address", "0.0.0.0"]
```

## docker-compose.yml (prospectivo)

**Atenção:** arquivo ainda não criado. Estrutura planejada:

```yaml
services:
  lora-ui:
    build: .
    ports:
      - "3953:3953"
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

Subir:

```bash
docker compose up -d
```

Parar:

```bash
docker compose down
```

## Uso Programático (sem UI)

O motor de cálculo pode ser usado diretamente via Python:

```python
from lora_antenna.gis.kml_parser import parse_kml
from lora_antenna.antenna.base import Antenna
from lora_antenna.gis.multi_link import run_link_budget_batch

doc = parse_kml(Path("campus.kml"))
antenna = Antenna(gain_dbi=2.15, losses_db=0.5)
results = run_link_budget_batch(doc, antenna, frequency_hz=915_200_000.0)

for r in results:
    print(r.origin_label, "→", r.dest_label, r.link_margin_db, "dB", r.feasible)
```

## Variáveis de Ambiente

Nenhuma variável obrigatória no momento. Para desabilitar consultas SRTM em ambiente offline:
defina `SRTM_DISABLED=1` (suporte prospectivo — verificar implementação atual em `gis/srtm.py`).

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

Regra de fronteira: `propagation/`, `core/`, `antenna/` nunca importam `gis/`, `network/`, `shapely` ou `requests`.
