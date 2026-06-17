# Glossário

Termos técnicos em linguagem acessível.

---

**dBi** — decibel relativo à antena isotrópica. Mede o ganho de uma antena comparado a uma antena teórica que irradia igualmente em todas as direções. Dipolo λ/2 = 2.15 dBi. Parabólica 0.6 m = ~24 dBi.

**dBm** — decibel relativo a 1 mW. Potência de transmissão típica de gateway LoRa: 20–30 dBm (100 mW a 1 W).

**EIRP** (Effective Isotropic Radiated Power) — potência total irradiada na direção de ganho máximo. EIRP = P_tx (dBm) + G_tx (dBi) − perda_cabo (dB).

**FSPL** (Free-Space Path Loss) — perda de percurso no espaço livre. Aumenta com distância e frequência. FSPL (dB) = 20·log(d) + 20·log(f) + 92.45 (d em km, f em GHz).

**Ganho** — relação entre a intensidade irradiada na direção de máxima irradiação e a de uma antena de referência (isotrópica). Não aumenta a potência total; concentra a energia em uma direção.

**Impedância** — resistência ao fluxo de corrente alternada, em ohms (Ω). A maioria dos sistemas usa Z₀ = 50 Ω. Desacasamento (antena ≠ 50 Ω) causa reflexões e perda de eficiência.

**ITM** (Irregular Terrain Model) — modelo de propagação em terreno irregular desenvolvido pelo NTIA/ITS. Implementado aqui de forma simplificada. Versão completa: splat! ou NTIA C++.

**Job** — simulação assíncrona enfileirada no backend. Retorna `job_id` imediatamente. Status consultado via polling (a cada 2 s). Estados: PENDING → RUNNING → DONE | FAILED_* | CANCELLED.

**KML** — formato XML do Google Earth para dados geográficos. Nível 0: pontos com coordenadas. Nível 1: polígonos (renderizados no mapa, sem penalidade física nesta versão).

**λ (lambda)** — comprimento de onda. λ = c / f, onde c = 3×10⁸ m/s. Para 915 MHz: λ ≈ 32.8 cm. Para 868 MHz: λ ≈ 34.5 cm.

**Link budget** — contabilidade de ganhos e perdas no enlace de rádio. Margem = EIRP_tx − FSPL − G_rx + G_tx − limiar_rx. Positiva = enlace viável.

**Longley-Rice (ITM)** — modelo de perda de percurso para terreno irregular. Parâmetro principal: Δh (irregularidade do terreno em metros). Ver `docs/calculos/07-longley-rice-itm.md`.

**MoM** (Method of Moments) — método numérico que discretiza a distribuição de corrente na antena e resolve o sistema linear resultante. Mais preciso que analítico para geometrias complexas. Implementado via PyNEC (wrapper NEC-2).

**Monopolo** — haste condutora sobre plano de terra. Funciona como metade de um dipolo espelhado pelo plano condutor.

**Okumura-Hata** — modelo empírico de perda de percurso para enlaces móveis terrestres (150–1500 MHz). Baseado em medições de Okumura em Tóquio (1968) e reformulado por Hata (1980).

**Padrão de irradiação** — distribuição espacial da energia irradiada. Representado no diagrama polar. Omnidirecional: irradiação igual em todos os azimutes. Direcional: concentrado em um ângulo específico.

**PyNEC** — biblioteca Python que encapsula o NEC-2 (Numerical Electromagnetics Code). Requer compilador C para instalação. Em Linux/WSL2: `pip install PyNEC`. Em Windows: MSVC ou MinGW necessário.

**Solver** — módulo de cálculo. Rápido (analítico), Padrão (MoM/PyNEC ou abertura), Preciso (MoM completo).

**SWR** (Standing Wave Ratio) — razão de onda estacionária. Indica o grau de casamento entre a impedância da antena e a linha de transmissão (50 Ω). SWR = 1.0: casamento perfeito. SWR < 2.0: aceitável. SWR > 3.0: descasamento significativo.

**LoRa** — modulação de espalhamento espectral (Chirp Spread Spectrum) para redes LPWAN. Frequências no Brasil/AU: 915 MHz (ISM). Europa: 868 MHz.

**LPWAN** — Low-Power Wide-Area Network. Redes sem fio de baixo consumo e longa distância. LoRa é uma das tecnologias de modulação usadas em LPWAN.
