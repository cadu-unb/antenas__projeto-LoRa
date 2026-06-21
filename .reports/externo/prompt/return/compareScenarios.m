function results = compareScenarios(points, modules, antennas, gatewayIdx, sim)
%compareScenarios Executa cenarios A-E de comparacao modulo/antena.

if nargin < 5
    sim = struct();
end
sim = setDefaults(sim);

geometryOptions = struct('TxFixedAzimuth_deg', sim.TxFixedAzimuth_deg, ...
    'TxFixedElevation_deg', sim.TxFixedElevation_deg, ...
    'RxFixedAzimuth_deg', sim.RxFixedAzimuth_deg, ...
    'RxFixedElevation_deg', sim.RxFixedElevation_deg);
geometry = linkGeometry(points, gatewayIdx, geometryOptions);

rows = {};

% Cenario A: mesma antena no transmissor e no gateway.
for a = 1:numel(antennas)
    for m = 1:numel(modules)
        rows = appendScenarioRows(rows, 'A_SameAntenna', modules(m), antennas(a), antennas(a), ...
            geometry, sim, orientationForTx(antennas(a), 'fixed'), orientationForRx(antennas(a), 'fixed'));
    end
end

% Cenario B: gateway omnidirecional vertical e transmissores variando.
gwOmniIdx = find(~[antennas.IsDirectional]);
for gi = gwOmniIdx
    for tx = 1:numel(antennas)
        for m = 1:numel(modules)
            rows = appendScenarioRows(rows, 'B_OmniGateway_TxVaries', modules(m), antennas(tx), antennas(gi), ...
                geometry, sim, orientationForTx(antennas(tx), 'fixed'), 'vertical');
        end
    end
end

% Cenario C: transmissores diretivos apontados para o gateway; gateway omni.
gwIdx = find(strcmp({antennas.Name}, sim.GatewayOmniName), 1);
if isempty(gwIdx), gwIdx = gwOmniIdx(1); end
txDirIdx = find([antennas.IsDirectional]);
for tx = txDirIdx
    for m = 1:numel(modules)
        rows = appendScenarioRows(rows, 'C_DirectionalTxPointed', modules(m), antennas(tx), antennas(gwIdx), ...
            geometry, sim, 'pointed', 'vertical');
    end
end

% Cenario D: transmissores diretivos desalinhados; gateway omni.
for tx = txDirIdx
    for m = 1:numel(modules)
        rows = appendScenarioRows(rows, 'D_DirectionalTxMisaligned', modules(m), antennas(tx), antennas(gwIdx), ...
            geometry, sim, 'fixed', 'vertical');
    end
end

% Cenario E: comparacao direta entre modulos com antena comercial nos dois lados.
refIdx = find(strcmp({antennas.Name}, 'Commercial_Omni_6dBi'), 1);
if isempty(refIdx), refIdx = gwIdx; end
for m = 1:numel(modules)
    rows = appendScenarioRows(rows, 'E_ModuleComparison', modules(m), antennas(refIdx), antennas(refIdx), ...
        geometry, sim, 'vertical', 'vertical');
end

results = cell2table(rows, 'VariableNames', {'Scenario', 'PointName', 'ModuleName', ...
    'TxAntenna', 'GatewayAntenna', 'Distance2D_m', 'Distance3D_m', 'Azimuth_deg', ...
    'Elevation_deg', 'Gtx_dBi', 'Grx_dBi', 'Ptx_dBm', 'Sensitivity_dBm', 'FSPL_dB', ...
    'AdditionalLosses_dB', 'PolarizationLoss_dB', 'Prx_dBm', 'Margin_dB', 'LinkStatus', ...
    'TxOrientation', 'GatewayOrientation'});
end

function rows = appendScenarioRows(rows, scenarioName, module, txAnt, rxAnt, geometry, sim, txOrientation, rxOrientation)
ptx = choosePtx(module, sim);
sens = chooseSensitivity(module, sim);

for i = 1:height(geometry)
    [thetaTx, phiTx] = selectAngles(geometry(i, :), txAnt, txOrientation, 'tx');
    [thetaRx, phiRx] = selectAngles(geometry(i, :), rxAnt, rxOrientation, 'rx');

    txParams = antennaParams(txAnt);
    rxParams = antennaParams(rxAnt);
    gtx = antennaPattern(txAnt.PatternModel, thetaTx, phiTx, txParams);
    grx = antennaPattern(rxAnt.PatternModel, thetaRx, phiRx, rxParams);

    polLoss = sim.PolarizationLoss_dB + estimatePolarizationLoss(txAnt, rxAnt);
    losses = struct();
    losses.L_cabo_tx_dB = sim.TxCableLoss_dB;
    losses.L_cabo_rx_dB = sim.RxCableLoss_dB;
    losses.L_polarization_dB = polLoss;
    losses.L_extra_dB = sim.ExtraLoss_dB;
    losses.FadingMargin_dB = sim.FadingMargin_dB;

    budget = linkBudget(sim.FrequencyMHz, geometry.Distance3D_m(i) ./ 1000, ...
        ptx, sens, gtx, grx, losses);

    rows(end + 1, :) = {scenarioName, geometry.PointName{i}, module.Name, ...
        txAnt.Name, rxAnt.Name, geometry.Distance2D_m(i), geometry.Distance3D_m(i), ...
        geometry.AzimuthTxToGw_deg(i), geometry.ElevationTxToGw_deg(i), ...
        gtx, grx, ptx, sens, budget.FSPL_dB, ...
        budget.TotalLoss_dB, polLoss, budget.Prx_dBm, budget.Margin_dB, budget.Status, ...
        txOrientation, rxOrientation}; %#ok<AGROW>
end
end

function [theta, phi] = selectAngles(g, antenna, orientation, side)
if strcmpi(orientation, 'pointed')
    theta = 0;
    phi = 0;
    return;
end

if antenna.IsDirectional && strcmpi(orientation, 'fixed')
    if strcmpi(side, 'tx')
        theta = g.ThetaTxFixedBoresight_deg;
    else
        theta = g.ThetaRxFixedBoresight_deg;
    end
    phi = 0;
    return;
end

if strcmpi(side, 'tx')
    theta = g.ThetaTxVertical_deg;
    phi = g.PhiTxVertical_deg;
else
    theta = g.ThetaRxVertical_deg;
    phi = g.PhiRxVertical_deg;
end
end

function orientation = orientationForTx(antenna, fallback)
if antenna.IsDirectional
    orientation = fallback;
else
    orientation = 'vertical';
end
end

function orientation = orientationForRx(antenna, fallback)
if antenna.IsDirectional
    orientation = fallback;
else
    orientation = 'vertical';
end
end

function ptx = choosePtx(module, sim)
if isfield(sim, 'Ptx_dBm') && ~isempty(sim.Ptx_dBm)
    ptx = sim.Ptx_dBm;
elseif strcmpi(sim.TxPowerMode, 'min')
    ptx = min(module.PtxOptions_dBm);
else
    ptx = max(module.PtxOptions_dBm);
end
end

function sens = chooseSensitivity(module, sim)
options = module.SensitivityOptions_dBm;
if isempty(options) || all(isnan(options))
    sens = sim.DefaultSensitivity_dBm;
else
    sens = min(options); % modo mais sensivel para comparacao de cobertura.
end
end

function params = antennaParams(antenna)
params = struct();
params.AngleUnit = 'deg';
params.Gmax_dBi = antenna.Gmax_dBi;
params.HPBW_deg = antenna.HPBW_deg;
params.PatternModel = antenna.PatternModel;
params.Floor_dBi = -40;
end

function loss = estimatePolarizationLoss(txAnt, rxAnt)
txPol = lower(txAnt.Polarization);
rxPol = lower(rxAnt.Polarization);
txCircular = contains(txPol, 'circular') || contains(txPol, 'elliptical');
rxCircular = contains(rxPol, 'circular') || contains(rxPol, 'elliptical');

if txCircular ~= rxCircular
    loss = 3.0;
elseif contains(txPol, 'linear') && contains(rxPol, 'linear') && ...
        xor(contains(txPol, 'vertical'), contains(rxPol, 'vertical'))
    loss = 1.5;
else
    loss = 0.0;
end
end

function sim = setDefaults(sim)
defaults = struct();
defaults.FrequencyMHz = 915;
defaults.TxPowerMode = 'max';
defaults.DefaultSensitivity_dBm = -137;
defaults.TxCableLoss_dB = 0;
defaults.RxCableLoss_dB = 0;
defaults.ExtraLoss_dB = 0;
defaults.FadingMargin_dB = 0;
defaults.PolarizationLoss_dB = 0;
defaults.TxFixedAzimuth_deg = 0;
defaults.TxFixedElevation_deg = 0;
defaults.RxFixedAzimuth_deg = 0;
defaults.RxFixedElevation_deg = 0;
defaults.GatewayOmniName = 'Commercial_Omni_6dBi';

names = fieldnames(defaults);
for k = 1:numel(names)
    if ~isfield(sim, names{k}) || isempty(sim.(names{k}))
        sim.(names{k}) = defaults.(names{k});
    end
end
end

