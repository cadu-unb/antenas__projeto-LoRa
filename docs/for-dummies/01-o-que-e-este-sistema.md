# O que é este sistema

Sistema de planejamento de enlace LoRa. Permite criar antenas, simular parâmetros eletromagnéticos e calcular link budget entre pontos geográficos reais.

## Os três módulos

### Sandbox

Onde você cria e experimenta antenas. Informe tipo, frequência e geometria — o sistema calcula ganho (dBi), impedância (Ω), SWR e traça o diagrama de irradiação.

Três modos de simulação:

| Modo | Velocidade | Solver |
|---|---|---|
| Rápido | < 1 s | Analítico (fórmulas fechadas) |
| Padrão | 1–30 s | MoM via PyNEC |
| Preciso | 1–30 min | MoM completo ou abertura |

### Biblioteca

Armazena as antenas que você salvar do Sandbox. Cada antena é um arquivo `.json` com spec completa + resultados. Você pode importar, exportar e reusar em múltiplos cenários.

### Link Planner

Configura um enlace entre dois ou mais nós. Cada nó recebe uma antena da Biblioteca. O sistema calcula:
- Distância geodésica
- FSPL (Free-Space Path Loss)
- Margem de enlace = EIRP − FSPL − limiar de recepção

Semáforo de viabilidade: verde (> 10 dB), amarelo (0–10 dB), vermelho (< 0 dB).

## Fluxo típico

```
Sandbox → criar antena → Salvar na Biblioteca
                                    ↓
                         Link Planner → montar enlace → Calcular → Exportar
```

## O que este sistema NÃO faz

- Detecção automática de obstáculos por imagem de satélite
- Ray Tracing urbano sem modelo 3D da cena
- MoM para parabólicas grandes (usa aproximação de abertura)
- KML com extrusão 3D de edificações (nível 2)

## Requisitos mínimos

- Python 3.13+
- uv (gerenciador de pacotes)
- Navegador moderno (Chrome, Firefox, Edge)

Para simulações no modo Padrão/Preciso em Linux ou WSL2: PyNEC instalado (`pip install PyNEC`).
