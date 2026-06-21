function geometry = linkGeometry(points, gatewayIdx, options)
%linkGeometry Calcula geometria dos enlaces alarme -> gateway.
%   A convencao de theta e phi e:
%   theta = angulo polar medido a partir do eixo z local da antena;
%   phi   = azimute matematico no plano xy local, com x=leste e y=norte.

if nargin < 3
    options = struct();
end
if ~isfield(options, 'TxFixedAzimuth_deg'), options.TxFixedAzimuth_deg = 0; end
if ~isfield(options, 'TxFixedElevation_deg'), options.TxFixedElevation_deg = 0; end
if ~isfield(options, 'RxFixedAzimuth_deg'), options.RxFixedAzimuth_deg = 0; end
if ~isfield(options, 'RxFixedElevation_deg'), options.RxFixedElevation_deg = 0; end

[east, north, up] = geodeticToLocalENU(points.Lat, points.Lon, points.Alt, ...
    points.Lat(gatewayIdx), points.Lon(gatewayIdx), points.Alt(gatewayIdx));

n = height(points);
keep = setdiff((1:n).', gatewayIdx);
m = numel(keep);

pointName = cell(m, 1);
txToRx_E = zeros(m, 1);
txToRx_N = zeros(m, 1);
txToRx_U = zeros(m, 1);
distance2D = zeros(m, 1);
distance3D = zeros(m, 1);
azTx = zeros(m, 1);
elTx = zeros(m, 1);
thetaTxVertical = zeros(m, 1);
phiTxVertical = zeros(m, 1);
thetaRxVertical = zeros(m, 1);
phiRxVertical = zeros(m, 1);
thetaTxFixed = zeros(m, 1);
thetaRxFixed = zeros(m, 1);

for row = 1:m
    i = keep(row);
    pointName{row} = points.Name{i};

    % Coordenada do transmissor em relacao ao gateway.
    pTxFromGw = [east(i), north(i), up(i)];

    % Vetor transmissor -> receptor/gateway no referencial ENU.
    vTx = -pTxFromGw;
    vRx = pTxFromGw; % vetor receptor/gateway -> transmissor

    txToRx_E(row) = vTx(1);
    txToRx_N(row) = vTx(2);
    txToRx_U(row) = vTx(3);
    distance2D(row) = hypot(vTx(1), vTx(2));
    distance3D(row) = norm(vTx);

    azTx(row) = mod(atan2d(vTx(1), vTx(2)), 360);
    elTx(row) = atan2d(vTx(3), distance2D(row));

    thetaTxVertical(row) = polarThetaFromVector(vTx);
    phiTxVertical(row) = mod(atan2d(vTx(2), vTx(1)), 360);
    thetaRxVertical(row) = polarThetaFromVector(vRx);
    phiRxVertical(row) = mod(atan2d(vRx(2), vRx(1)), 360);

    boresightTx = unitVectorFromAzEl(options.TxFixedAzimuth_deg, options.TxFixedElevation_deg);
    boresightRx = unitVectorFromAzEl(options.RxFixedAzimuth_deg, options.RxFixedElevation_deg);
    thetaTxFixed(row) = angularSeparationDeg(vTx, boresightTx);
    thetaRxFixed(row) = angularSeparationDeg(vRx, boresightRx);
end

geometry = table(pointName, txToRx_E, txToRx_N, txToRx_U, distance2D, distance3D, ...
    azTx, elTx, thetaTxVertical, phiTxVertical, thetaRxVertical, phiRxVertical, ...
    thetaTxFixed, thetaRxFixed, ...
    'VariableNames', {'PointName', 'VectorTxToRx_E_m', 'VectorTxToRx_N_m', 'VectorTxToRx_U_m', ...
    'Distance2D_m', 'Distance3D_m', 'AzimuthTxToGw_deg', 'ElevationTxToGw_deg', ...
    'ThetaTxVertical_deg', 'PhiTxVertical_deg', 'ThetaRxVertical_deg', 'PhiRxVertical_deg', ...
    'ThetaTxFixedBoresight_deg', 'ThetaRxFixedBoresight_deg'});
end

function theta = polarThetaFromVector(v)
r = norm(v);
if r == 0
    theta = 0;
else
    theta = acosd(max(-1, min(1, v(3) ./ r)));
end
end

function u = unitVectorFromAzEl(az_deg, el_deg)
% Azimute geografico: 0=norte, 90=leste.
u = [cosd(el_deg) .* sind(az_deg), ...
     cosd(el_deg) .* cosd(az_deg), ...
     sind(el_deg)];
end

function ang = angularSeparationDeg(v, boresight)
if norm(v) == 0 || norm(boresight) == 0
    ang = 0;
else
    c = dot(v, boresight) ./ (norm(v) .* norm(boresight));
    ang = acosd(max(-1, min(1, c)));
end
end

