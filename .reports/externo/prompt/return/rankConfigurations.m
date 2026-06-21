function rankings = rankConfigurations(results, modules, antennas)
%rankConfigurations Cria rankings por modulo, antena e combinacao.

combKeys = unique(strcat(results.Scenario, '|', results.ModuleName, '|', ...
    results.TxAntenna, '|', results.GatewayAntenna));
combRows = cell(numel(combKeys), 13);

for k = 1:numel(combKeys)
    parts = splitKey(combKeys{k});
    idx = strcmp(results.Scenario, parts{1}) & strcmp(results.ModuleName, parts{2}) & ...
        strcmp(results.TxAntenna, parts{3}) & strcmp(results.GatewayAntenna, parts{4});
    sub = results(idx, :);
    metrics = summarizeResults(sub);
    practicality = antennaScore(antennas, parts{3}, 'PracticalityScore') + ...
        antennaScore(antennas, parts{4}, 'PracticalityScore');
    robustness = mean([antennaScore(antennas, parts{3}, 'MultiDirectionScore'), ...
        antennaScore(antennas, parts{4}, 'MultiDirectionScore')]);
    txCurrent = estimateModuleCurrent(modules, parts{2}, mean(sub.Ptx_dBm));
    score = metrics.MinMargin_dB + 0.25 .* metrics.MeanMargin_dB - ...
        25 .* metrics.Failures - 10 .* metrics.CriticalLinks + ...
        1.5 .* robustness + 0.8 .* practicality - currentPenalty(txCurrent);

    combRows(k, :) = {parts{1}, parts{2}, parts{3}, parts{4}, metrics.MinMargin_dB, ...
        metrics.MeanMargin_dB, metrics.Failures, metrics.CriticalLinks, ...
        metrics.ComfortableLinks, robustness, practicality, txCurrent, score};
end

combinationRanking = cell2table(combRows, 'VariableNames', {'Scenario', 'ModuleName', ...
    'TxAntenna', 'GatewayAntenna', 'MinMargin_dB', 'MeanMargin_dB', 'Failures', ...
    'CriticalLinks', 'ComfortableLinks', 'RobustnessScore', 'PracticalityScore', ...
    'TxCurrent_mA', 'Score'});
combinationRanking = sortrows(combinationRanking, {'Score', 'MinMargin_dB', 'MeanMargin_dB'}, {'descend', 'descend', 'descend'});

moduleRanking = rankOneDimension(results, 'ModuleName', modules, antennas);
txAntennaRanking = rankOneDimension(results, 'TxAntenna', modules, antennas);
gatewayAntennaRanking = rankOneDimension(results, 'GatewayAntenna', modules, antennas);

rankings = struct();
rankings.CombinationRanking = combinationRanking;
rankings.ModuleRanking = moduleRanking;
rankings.TxAntennaRanking = txAntennaRanking;
rankings.GatewayAntennaRanking = gatewayAntennaRanking;
end

function ranking = rankOneDimension(results, columnName, modules, antennas)
values = unique(results.(columnName));
rows = cell(numel(values), 8);

for k = 1:numel(values)
    value = values{k};
    idx = strcmp(results.(columnName), value);
    sub = results(idx, :);
    metrics = summarizeResults(sub);
    extraScore = 0;
    txCurrent = NaN;

    if strcmp(columnName, 'ModuleName')
        txCurrent = estimateModuleCurrent(modules, value, mean(sub.Ptx_dBm));
        extraScore = -currentPenalty(txCurrent);
    elseif contains(columnName, 'Antenna')
        extraScore = antennaScore(antennas, value, 'MultiDirectionScore') + ...
            0.5 .* antennaScore(antennas, value, 'PracticalityScore');
    end

    score = metrics.MinMargin_dB + 0.25 .* metrics.MeanMargin_dB - ...
        25 .* metrics.Failures - 10 .* metrics.CriticalLinks + extraScore;

    rows(k, :) = {value, metrics.MinMargin_dB, metrics.MeanMargin_dB, ...
        metrics.Failures, metrics.CriticalLinks, metrics.ComfortableLinks, txCurrent, score};
end

ranking = cell2table(rows, 'VariableNames', {columnName, 'MinMargin_dB', ...
    'MeanMargin_dB', 'Failures', 'CriticalLinks', 'ComfortableLinks', ...
    'TxCurrent_mA', 'Score'});
ranking = sortrows(ranking, {'Score', 'MinMargin_dB', 'MeanMargin_dB'}, {'descend', 'descend', 'descend'});
end

function metrics = summarizeResults(sub)
metrics = struct();
metrics.MinMargin_dB = min(sub.Margin_dB);
metrics.MeanMargin_dB = mean(sub.Margin_dB);
metrics.Failures = sum(strcmp(sub.LinkStatus, 'Falha'));
metrics.CriticalLinks = sum(strcmp(sub.LinkStatus, 'Critico'));
metrics.ComfortableLinks = sum(strcmp(sub.LinkStatus, 'Confortavel'));
end

function parts = splitKey(key)
parts = regexp(key, '\|', 'split');
end

function score = antennaScore(antennas, name, fieldName)
idx = find(strcmp({antennas.Name}, name), 1);
if isempty(idx) || ~isfield(antennas, fieldName)
    score = 0;
else
    score = antennas(idx).(fieldName);
end
end

function current_mA = estimateModuleCurrent(modules, moduleName, ptx_dBm)
idx = find(strcmp({modules.Name}, moduleName), 1);
if isempty(idx)
    current_mA = NaN;
    return;
end
options = modules(idx).TxCurrentOptions_mA;
if isempty(options) || any(isnan(options(:)))
    current_mA = NaN;
else
    [~, nearest] = min(abs(options(:, 1) - ptx_dBm));
    current_mA = options(nearest, 2);
end
end

function penalty = currentPenalty(current_mA)
if isnan(current_mA)
    penalty = 0;
else
    penalty = 0.03 .* current_mA;
end
end

