% main_LoRa_AntennaComparison
% Simulacao educacional de enlaces LoRa/LoRaWAN com modelos aproximados de
% antenas para pontos de alarme no Campus Darcy Ribeiro da UnB.

clear; clc; close all;

fprintf('\n============================================================\n');
fprintf('SIMULACAO LORA / ANTENAS - CAMPUS DARCY RIBEIRO UnB\n');
fprintf('============================================================\n\n');

points = loadCampusPoints();

% O E220-900T22D nao traz sensibilidade nos dados fornecidos. Para permitir
% comparacoes automaticas, usamos uma hipotese ajustavel de -137 dBm.
defaultSensitivityE220_dBm = -137;
modules = loadLoRaModules(defaultSensitivityE220_dBm);
antennas = loadAntennaModels();

gatewayMode = 'auto';   % 'auto' ou 'manual'
manualGatewayName = 'BCE';
[gatewayIdx, gatewayCandidates, gatewayRanking] = chooseGateway(points, gatewayMode, manualGatewayName);

fprintf('Gateway escolhido: %s (modo: %s)\n\n', points.Name{gatewayIdx}, gatewayMode);
fprintf('Ranking de candidatos a gateway:\n');
disp(gatewayRanking);

[east_m, north_m, up_m] = geodeticToLocalENU(points.Lat, points.Lon, points.Alt, ...
    points.Lat(gatewayIdx), points.Lon(gatewayIdx), points.Alt(gatewayIdx));
localCoordinates = table(points.Name, east_m, north_m, up_m, ...
    'VariableNames', {'Name', 'East_m', 'North_m', 'Up_m'});

fprintf('Coordenadas locais ENU, com origem no gateway:\n');
disp(localCoordinates);

geometry = linkGeometry(points, gatewayIdx);
fprintf('Geometria dos enlaces alarme -> gateway:\n');
disp(geometry(:, {'PointName', 'Distance2D_m', 'Distance3D_m', ...
    'AzimuthTxToGw_deg', 'ElevationTxToGw_deg', 'ThetaTxVertical_deg', 'ThetaRxVertical_deg'}));

plotRadiationPatterns(antennas);

sim = struct();
sim.FrequencyMHz = 915;
sim.TxPowerMode = 'max';
sim.DefaultSensitivity_dBm = defaultSensitivityE220_dBm;
sim.TxCableLoss_dB = 0.5;
sim.RxCableLoss_dB = 0.5;
sim.ExtraLoss_dB = 8.0;        % perdas medias por instalacao/obstaculos leves
sim.FadingMargin_dB = 10.0;    % margem conservadora embutida como perda
sim.PolarizationLoss_dB = 0.0; % perdas extras alem da estimativa automatica
sim.TxFixedAzimuth_deg = 0;    % norte geografico
sim.TxFixedElevation_deg = 0;
sim.RxFixedAzimuth_deg = 0;    % gateway diretivo fixo para norte, se usado
sim.RxFixedElevation_deg = 0;
sim.GatewayOmniName = 'Commercial_Omni_6dBi';

results = compareScenarios(points, modules, antennas, gatewayIdx, sim);

fprintf('\nAmostra da tabela de calculo de enlace:\n');
disp(results(1:min(18, height(results)), :));

rankings = rankConfigurations(results, modules, antennas);

fprintf('\nRanking de combinacoes modulo-antena:\n');
disp(rankings.CombinationRanking(1:min(15, height(rankings.CombinationRanking)), :));

fprintf('\nRanking por modulo LoRa:\n');
disp(rankings.ModuleRanking);

fprintf('\nRanking por antena transmissora:\n');
disp(rankings.TxAntennaRanking);

fprintf('\nRanking por antena do gateway:\n');
disp(rankings.GatewayAntennaRanking);

top = rankings.CombinationRanking(1, :);
idxTop = strcmp(results.Scenario, top.Scenario{1}) & ...
    strcmp(results.ModuleName, top.ModuleName{1}) & ...
    strcmp(results.TxAntenna, top.TxAntenna{1}) & ...
    strcmp(results.GatewayAntenna, top.GatewayAntenna{1});
plotCampusMap(points, gatewayIdx, results(idxTop, :), ...
    sprintf('Campus UnB - %s / %s -> %s', top.ModuleName{1}, top.TxAntenna{1}, top.GatewayAntenna{1}));

fprintf('\n============================================================\n');
fprintf('DISCUSSAO AUTOMATICA\n');
fprintf('============================================================\n');

bestTx = rankings.TxAntennaRanking(1, :);
bestGw = rankings.GatewayAntennaRanking(1, :);
bestModuleMargin = rankings.ModuleRanking(1, :);

fprintf('Melhor antena para os nos transmissores pelo ranking agregado: %s.\n', bestTx.TxAntenna{1});
fprintf('Melhor antena para o gateway pelo ranking agregado: %s.\n', bestGw.GatewayAntenna{1});
fprintf('Modulo com melhor margem agregada: %s.\n', bestModuleMargin.ModuleName{1});

fprintf('\nEstimativa simples de energia por transmissao (quando ha dados de corrente):\n');
airtime_s = 1.0;
txPerDay = 24;
energyRows = cell(numel(modules), 5);
for k = 1:numel(modules)
    ptx = max(modules(k).PtxOptions_dBm);
    voltage = mean([modules(k).VoltageMin_V, modules(k).VoltageMax_V], 'omitnan');
    e = estimateEnergyConsumption(modules(k), ptx, airtime_s, voltage, txPerDay);
    energyRows{k, 1} = modules(k).Name;
    energyRows{k, 2} = ptx;
    energyRows{k, 3} = e.TxCurrent_mA;
    energyRows{k, 4} = e.EnergyPerTx_J;
    energyRows{k, 5} = e.DailyEnergy_J;
end
energyTable = cell2table(energyRows, 'VariableNames', ...
    {'ModuleName', 'Ptx_dBm', 'TxCurrent_mA', 'EnergyPerTx_J', 'DailyEnergy_J'});
disp(energyTable);

validEnergy = ~isnan(cell2mat(energyRows(:, 5)));
if any(validEnergy)
    validIdx = find(validEnergy);
    [~, localBest] = min(cell2mat(energyRows(validEnergy, 5)));
    bestEnergyIdx = validIdx(localBest);
    fprintf('Melhor modulo em consumo com dados disponiveis: %s.\n', modules(bestEnergyIdx).Name);
else
    fprintf('Nao ha dados completos de corrente para comparar consumo entre todos os modulos.\n');
end

fprintf(['Antenas muito diretivas, como helicoidal axial e parabolica, so entregam seu ganho maximo ', ...
    'quando o boresight esta apontado para o gateway. Em um gateway unico recebendo de muitos azimutes, ', ...
    'isso tende a reduzir a robustez, salvo com setorizacao, multiplas antenas ou apontamento controlado.\n']);
fprintf(['O cenario D isola esse efeito: transmissores diretivos desalinhados perdem margem porque ', ...
    'Gtx(theta,phi) cai rapidamente fora do eixo de apontamento.\n']);

fprintf('\nVariaveis principais no workspace: points, modules, antennas, geometry, results, rankings, energyTable.\n');

