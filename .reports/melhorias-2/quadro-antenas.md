# Quadro de Antenas — Python atual vs `.reports/externo/`

Revisão feita a partir de todos os arquivos em `.reports/externo/`: `resume.md`, `prompt1.md`, `prompt2.md`, os 16 arquivos MATLAB em `prompt/return/` e o KML `Mapa Botões de Emergência UnB.kml`.

## Resumo executivo

O sistema Python atual já aceita 6 tipos de antena no sandbox/solver:

- `dipolo`
- `monopolo`
- `helicoidal`
- `parabolica`
- `pcb_compact`
- `commercial_omni_6dbi`

O material externo MATLAB também trabalha com 6 antenas, mas usa nomes e campos mais explícitos para comparação física:

- `Dipole_HalfWave`
- `Monopole_GroundPlane`
- `Helical_Axial`
- `Parabolic_Dish`
- `PCB_Compact`
- `Commercial_Omni_6dBi`

Diferença central: no Python, os dados específicos ficam distribuídos entre `AntennaSpec.geometry`, `AntennaSpec.results`, solver e `NodeSpec`; no MATLAB externo, cada antena já nasce com campos tabulares fixos (`Gmax_dBi`, `HPBW_deg`, `Polarization`, `IsDirectional`, `PatternModel`, `PracticalityScore`, `MultiDirectionScore`, `Notes`).

## Campos comuns usados hoje no Python

### `AntennaSpec`

Campos aceitos pelo schema atual:

| Campo | Uso atual |
|---|---|
| `schema_version` | Versão do schema; default `"1.0"` |
| `id` | UUID automático |
| `name` | Nome legível da antena |
| `type` | Tipo usado para escolher solver |
| `frequency_hz` | Frequência central da simulação |
| `units` | Unidades livres |
| `geometry` | Parâmetros por tipo de antena |
| `material` | Dados livres; pouco usado no cálculo atual |
| `solver` | `rapido`, `padrao`, `preciso`, etc.; default `rapido` |
| `results` | Resultados calculados/salvos, como ganho e padrão |
| `metadata` | Dados livres |

### `NodeSpec` que afeta antena/enlace

Campos por nó que alteram o cálculo de enlace:

| Campo | Default | Uso |
|---|---:|---|
| `antenna_id` | `null` | Referencia uma `AntennaSpec` salva |
| `tx_power_dbm` | `14.0` | Potência TX |
| `rx_sensitivity_dbm` | `-137.0` | Sensibilidade RX |
| `cable_loss_db` | `0.0` | Perda de cabo/conector |
| `extra_loss_db` | `0.0` | Perda adicional |
| `fading_margin_db` | `0.0` | Margem de fading tratada como perda |
| `polarization_loss_db` | `0.0` | Perda de polarização |
| `azimuth_deg` | `null` | Se preenchido, ativa ganho direcional via `pattern_g()` |
| `tilt_deg` | `0.0` | Elevação/tilt do boresight |
| `lora_module_id` | `null` | Seleção de módulo LoRa |

### `LinkScenario`

| Campo | Default | Uso |
|---|---:|---|
| `frequency_hz` | obrigatório | Frequência do enlace |
| `propagation_model` | `fspl` | `fspl`, `okumura_hata` ou `longley_rice` |

## Quadro comparativo por tipo de antena

| Python atual | MATLAB externo | Entradas usadas no Python | Valores/defaults Python | Campos/valores em `.reports/externo/` |
|---|---|---|---|---|
| `dipolo` | `Dipole_HalfWave` | `frequency_hz`; `geometry.length_m`; `geometry.diameter_mm` no MoM/PyNEC | `length_m = lambda/2`; `diameter_mm = 1.5` quando PyNEC modela fio; ganho nominal `2.15 dBi`; impedância alvo aprox. `73 ohm`; padrão toroidal `sin²(theta)` | `Name=Dipole_HalfWave`; `Type=Omnidirectional vertical`; `Gmax_dBi=2.15`; `HPBW_deg=78`; `Polarization=linear vertical`; `IsDirectional=false`; `PatternModel=dipole`; `PracticalityScore=8`; `MultiDirectionScore=9` |
| `monopolo` | `Monopole_GroundPlane` | `frequency_hz`; `geometry.height_m`; `geometry.diameter_mm` no MoM/PyNEC | `height_m = lambda/4`; `diameter_mm = 1.5`; ganho nominal `5.15 dBi`; impedância alvo aprox. `36.5 ohm`; padrão hemisférico/toroidal | `Name=Monopole_GroundPlane`; `Type=Omnidirectional vertical`; `Gmax_dBi=5.15`; `HPBW_deg=55`; `Polarization=linear vertical`; `IsDirectional=false`; `PatternModel=monopole`; `PracticalityScore=7`; `MultiDirectionScore=8` |
| `helicoidal` | `Helical_Axial` | `frequency_hz`; `geometry.turns`; `geometry.circumference_m`; `geometry.pitch_angle_deg`; orientação do nó (`azimuth_deg`, `tilt_deg`) no link budget direcional | `turns=10`; `circumference_m=lambda`; `pitch_angle_deg=14.0`; modo axial se `0.75lambda <= C <= 1.33lambda`; ganho calculado por `15*N*(C/lambda)^2*sin(pitch)`; padrão endfire `cos²(theta)` | `Name=Helical_Axial`; `Type=Directional axial-mode helix`; `Gmax_dBi=11`; `HPBW_deg=55`; `Polarization=circular/elliptical`; `IsDirectional=true`; `PatternModel=helical`; `PracticalityScore=5`; `MultiDirectionScore=3` |
| `parabolica` | `Parabolic_Dish` | `frequency_hz`; `geometry.diameter_m`; `geometry.focal_length_m`; `geometry.efficiency`; `geometry.blockage_pct`; `geometry.surface_rms_mm`; `geometry.feed_loss_db`; `geometry.radome_loss_db`; orientação do nó (`azimuth_deg`, `tilt_deg`) | No `solve()`: `diameter_m=0.6`; `focal_length_m=D*0.367`; `efficiency=0.55`; `blockage_pct=0`; `surface_rms_mm=0`; perdas passivas `0`; ganho por abertura `eta*(pi*D/lambda)^2`; HPBW `70lambda/D` | `Name=Parabolic_Dish`; `Type=Highly directional aperture`; `Gmax_dBi=20`; `HPBW_deg=18`; `Polarization=linear or circular, feed-dependent`; `IsDirectional=true`; `PatternModel=parabolic`; `PracticalityScore=2`; `MultiDirectionScore=1` |
| `pcb_compact` | `PCB_Compact` | `frequency_hz`; não exige geometria | Ganho por faixa: `<800 MHz = 0 dBi`; `800-1000 MHz = 1.5 dBi`; `>1000 MHz = 2.0 dBi`; impedância `50 ohm`; eficiência `85%`; padrão quasi-omni com penalidade de elevação | `Name=PCB_Compact`; `Type=Compact integrated antenna`; `Gmax_dBi=1`; `HPBW_deg=120`; `Polarization=linear`; `IsDirectional=false`; `PatternModel=pcb`; `PracticalityScore=10`; `MultiDirectionScore=7` |
| `commercial_omni_6dbi` | `Commercial_Omni_6dBi` | `frequency_hz`; não exige geometria; orientação pode afetar se usada via `azimuth_deg`/`tilt_deg` | Ganho fixo `6.0 dBi`; impedância `50 ohm`; eficiência `95%`; padrão colinear/omni em azimute; HPBW de elevação aproximado `20°` no solver Python | `Name=Commercial_Omni_6dBi`; `Type=Practical vertical omni`; `Gmax_dBi=6`; `HPBW_deg=35`; `Polarization=linear vertical`; `IsDirectional=false`; `PatternModel=commercial_omni_6dbi`; `PracticalityScore=9`; `MultiDirectionScore=8` |

## Campos externos que ainda não existem como campos diretos de `AntennaSpec`

Hoje eles podem ser guardados em `metadata`, `results` ou `geometry`, mas não têm schema próprio:

| Campo externo | Situação no Python |
|---|---|
| `Gmax_dBi` | Calculado pelo solver ou salvo em `results.gain_dbi`; não é campo direto da spec |
| `HPBW_deg` | Existe como cálculo/extra da parabólica e constante interna da colinear; não é campo direto comum |
| `Polarization` | Não é campo direto de `AntennaSpec`; perda de polarização está no `NodeSpec` |
| `IsDirectional` | Inferido pelo tipo/solver; não é campo direto |
| `PatternModel` | Inferido pelo `type`; não é campo direto |
| `PracticalityScore` | Existe no MATLAB externo; não está em `AntennaSpec` |
| `MultiDirectionScore` | Existe no MATLAB externo; no Python há score de robustez em `comparison.py`, mas não por cadastro de antena |
| `Notes` | Pode ir em `metadata.notes`, mas não é campo dedicado |

## Parâmetros externos de simulação que impactam antenas

O script externo `main_LoRa_AntennaComparison.m` usa:

| Campo externo | Valor no exemplo externo | Equivalente Python atual |
|---|---:|---|
| `FrequencyMHz` | `915` | `LinkScenario.frequency_hz = 915e6` |
| `TxPowerMode` | `max` | Potência vem de `NodeSpec.tx_power_dbm` ou módulo LoRa |
| `DefaultSensitivity_dBm` | `-137` para E220 | `NodeSpec.rx_sensitivity_dbm` ou biblioteca de módulos |
| `TxCableLoss_dB` | `0.5` | `node_a.cable_loss_db` |
| `RxCableLoss_dB` | `0.5` | `node_b.cable_loss_db` |
| `ExtraLoss_dB` | `8.0` | `extra_loss_db`, somado por nó |
| `FadingMargin_dB` | `10.0` | `fading_margin_db`, somado no transmissor em `compute_link_full()` |
| `PolarizationLoss_dB` | `0.0` | `polarization_loss_db`, somado no transmissor em `compute_link_full()` |
| `TxFixedAzimuth_deg` | `0` | `NodeSpec.azimuth_deg` |
| `TxFixedElevation_deg` | `0` | `NodeSpec.tilt_deg` |
| `RxFixedAzimuth_deg` | `0` | `NodeSpec.azimuth_deg` do receptor |
| `RxFixedElevation_deg` | `0` | `NodeSpec.tilt_deg` do receptor |
| `GatewayOmniName` | `Commercial_Omni_6dBi` | Antena do gateway via `antenna_id`/spec |

## Observações de consistência

1. `docs/antenna-spec-schema.md` ainda lista apenas `dipolo`, `monopolo`, `helicoidal` e `parabolica`, mas o código atual já registra `pcb_compact` e `commercial_omni_6dbi`.
2. O relatório externo `resume.md` afirma que Python tinha 4 tipos; isso ficou desatualizado depois das melhorias. O estado atual do código tem 6 tipos no registry de solvers.
3. O MATLAB externo usa `HPBW_deg=35` para `Commercial_Omni_6dBi`; o Python usa internamente HPBW aproximado de `20°` no `ColinearSolver`.
4. O MATLAB externo usa `PCB_Compact.Gmax_dBi=1`; o Python usa ganho dependente da frequência e em 915 MHz retorna `1.5 dBi`.
5. O MATLAB externo traz `PracticalityScore` e `MultiDirectionScore` por antena; o Python calcula robustez por dispersão de margens, mas não mantém esses scores no cadastro da antena.
6. O Python atual já tem ENU 3D, ganho direcional via `pattern_g()` quando `azimuth_deg` é definido e perdas extras no `NodeSpec`, então parte dos gaps antigos em `.reports/externo/resume.md` já foi implementada.

## Recomendação curta

Para alinhar o Python ao material externo, o próximo passo mais limpo é estender `AntennaSpec` com campos opcionais explícitos:

| Campo sugerido | Motivo |
|---|---|
| `gmax_dbi` | Guardar ganho máximo nominal cadastrado, não apenas resultado calculado |
| `hpbw_deg` | Unificar feixe para helicoidal, parabólica e colinear |
| `polarization` | Permitir cálculo automático de perda de polarização |
| `is_directional` | Evitar inferência dispersa por tipo |
| `pattern_model` | Separar nome comercial/tipo físico do modelo angular |
| `practicality_score` | Reproduzir ranking externo |
| `multi_direction_score` | Reproduzir penalidade externa para gateway multi-azimute |
| `notes` | Evitar esconder observações em `metadata` genérico |
