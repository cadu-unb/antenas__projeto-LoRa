function energy = estimateEnergyConsumption(module, Ptx_dBm, airtime_s, voltage_V, txPerDay)
%estimateEnergyConsumption Estima consumo simples por transmissao.
%   A estimativa usa somente corrente de transmissao, tensao e tempo de ar.
%   Nao modela toda a pilha LoRaWAN.

if nargin < 3 || isempty(airtime_s), airtime_s = 1; end
if nargin < 4 || isempty(voltage_V), voltage_V = mean([module.VoltageMin_V, module.VoltageMax_V], 'omitnan'); end
if nargin < 5 || isempty(txPerDay), txPerDay = 1; end

txCurrent_mA = lookupTxCurrent(module, Ptx_dBm);

if isnan(txCurrent_mA) || isnan(voltage_V)
    energyPerTx_J = NaN;
    dailyEnergy_J = NaN;
else
    energyPerTx_J = voltage_V .* (txCurrent_mA ./ 1000) .* airtime_s;
    dailyEnergy_J = energyPerTx_J .* txPerDay;
end

energy = struct();
energy.ModuleName = module.Name;
energy.Ptx_dBm = Ptx_dBm;
energy.TxCurrent_mA = txCurrent_mA;
energy.Voltage_V = voltage_V;
energy.Airtime_s = airtime_s;
energy.TransmissionsPerDay = txPerDay;
energy.EnergyPerTx_J = energyPerTx_J;
energy.DailyEnergy_J = dailyEnergy_J;
end

function txCurrent_mA = lookupTxCurrent(module, Ptx_dBm)
options = module.TxCurrentOptions_mA;
if isempty(options) || any(isnan(options(:)))
    txCurrent_mA = NaN;
    return;
end

if size(options, 2) ~= 2
    txCurrent_mA = NaN;
    return;
end

[~, idx] = min(abs(options(:, 1) - Ptx_dBm));
txCurrent_mA = options(idx, 2);
end

