function budget = linkBudget(f_MHz, d_km, Ptx_dBm, Sensitivity_dBm, Gtx_dBi, Grx_dBi, losses)
%linkBudget Calcula orcamento de enlace LoRa em dB/dBm.
%   FSPL_dB = 32.44 + 20*log10(f_MHz) + 20*log10(d_km)

if nargin < 7 || isempty(losses)
    losses = struct();
end

L_cabo_tx_dB = getLoss(losses, 'L_cabo_tx_dB', 0);
L_cabo_rx_dB = getLoss(losses, 'L_cabo_rx_dB', 0);
L_polarization_dB = getLoss(losses, 'L_polarization_dB', 0);
L_extra_dB = getLoss(losses, 'L_extra_dB', 0);
FadingMargin_dB = getLoss(losses, 'FadingMargin_dB', 0);

d_km = max(d_km, 1e-6);
FSPL_dB = 32.44 + 20 .* log10(f_MHz) + 20 .* log10(d_km);
TotalLoss_dB = L_cabo_tx_dB + L_cabo_rx_dB + L_polarization_dB + L_extra_dB + FadingMargin_dB;
Prx_dBm = Ptx_dBm + Gtx_dBi + Grx_dBi - FSPL_dB - TotalLoss_dB;
Margin_dB = Prx_dBm - Sensitivity_dBm;

if Margin_dB < 0
    status = 'Falha';
elseif Margin_dB < 10
    status = 'Critico';
else
    status = 'Confortavel';
end

budget = struct();
budget.FSPL_dB = FSPL_dB;
budget.TotalLoss_dB = TotalLoss_dB;
budget.L_cabo_tx_dB = L_cabo_tx_dB;
budget.L_cabo_rx_dB = L_cabo_rx_dB;
budget.L_polarization_dB = L_polarization_dB;
budget.L_extra_dB = L_extra_dB;
budget.FadingMargin_dB = FadingMargin_dB;
budget.Prx_dBm = Prx_dBm;
budget.Margin_dB = Margin_dB;
budget.Status = status;
end

function value = getLoss(losses, name, fallback)
if isfield(losses, name)
    value = losses.(name);
else
    value = fallback;
end
end

