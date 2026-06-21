function G_dBi = antennaPattern(antennaType, theta, phi, params)
%antennaPattern Ganho aproximado de antena em dBi.
%   G_dBi = antennaPattern(antennaType, theta, phi, params)
%
%   theta e phi podem estar em graus ou radianos. Por padrao a funcao usa
%   graus quando algum valor excede 2*pi; caso contrario assume radianos.
%   Para evitar ambiguidade, defina params.AngleUnit = 'deg' ou 'rad'.
%
%   Convencao: theta e o angulo polar a partir do eixo z local. Para modelos
%   diretivos, o boresight coincide com theta=0.

if nargin < 4 || isempty(params)
    params = struct();
end
if nargin < 3 || isempty(phi)
    phi = zeros(size(theta));
end

thetaDeg = toDegrees(theta, params);
phiDeg = toDegrees(phi, params);
thetaDeg = mod(thetaDeg, 360);
thetaDeg(thetaDeg > 180) = 360 - thetaDeg(thetaDeg > 180);

model = lower(char(antennaType));
if isfield(params, 'PatternModel') && ~isempty(params.PatternModel)
    model = lower(char(params.PatternModel));
end

floor_dBi = getParam(params, 'Floor_dBi', -40);
Gmax = getParam(params, 'Gmax_dBi', defaultGmax(model));
HPBW = getParam(params, 'HPBW_deg', defaultHPBW(model));

switch model
    case {'dipole', 'dipole_halfwave', 'dipole_half_wave'}
        power = max(sind(thetaDeg).^2, 1e-12);
        G_dBi = Gmax + 10 .* log10(power);

    case {'monopole', 'monopole_groundplane', 'monopole_ground_plane'}
        power = max(sind(thetaDeg).^3, 1e-12);
        lowerHemispherePenalty = zeros(size(thetaDeg));
        below = thetaDeg > 90;
        lowerHemispherePenalty(below) = 20 .* ((thetaDeg(below) - 90) ./ 90).^2;
        G_dBi = Gmax + 10 .* log10(power) - lowerHemispherePenalty;

    case {'helical', 'helical_axial'}
        halfBeam = max(HPBW ./ 2, 1);
        mainLobe = Gmax - 3 .* (thetaDeg ./ halfBeam).^2;
        sideLobe = Gmax - 22 - 8 .* abs(sind(2 .* thetaDeg));
        G_dBi = max(mainLobe, sideLobe);

    case {'parabolic', 'parabolic_dish', 'dish'}
        halfBeam = max(HPBW ./ 2, 0.5);
        mainLobe = Gmax - 3 .* (thetaDeg ./ halfBeam).^2;
        sideLobe = Gmax - 32 + 2 .* cosd(4 .* phiDeg);
        G_dBi = max(mainLobe, sideLobe);

    case {'pcb', 'pcb_compact'}
        variation = -1.5 .* cosd(thetaDeg).^2 + ...
            0.8 .* sind(3 .* phiDeg) .* sind(thetaDeg).^2 + ...
            0.4 .* cosd(2 .* thetaDeg + phiDeg);
        G_dBi = min(Gmax, Gmax - 0.6 + variation);

    case {'commercial_omni_6dbi', 'commercial_omni', 'omni_6dbi'}
        power = max(sind(thetaDeg).^5, 1e-12);
        G_dBi = Gmax + 10 .* log10(power);

    otherwise
        power = max(sind(thetaDeg).^2, 1e-12);
        G_dBi = Gmax + 10 .* log10(power);
end

G_dBi = max(G_dBi, floor_dBi);
end

function degrees = toDegrees(angle, params)
if isfield(params, 'AngleUnit')
    unit = lower(char(params.AngleUnit));
else
    if isempty(angle) || max(abs(angle(:))) <= 2*pi + 1e-9
        unit = 'rad';
    else
        unit = 'deg';
    end
end

if strcmp(unit, 'rad') || strcmp(unit, 'radian') || strcmp(unit, 'radians')
    degrees = rad2deg(angle);
else
    degrees = angle;
end
end

function value = getParam(params, name, fallback)
if isfield(params, name) && ~isempty(params.(name)) && ~isnan(params.(name))
    value = params.(name);
else
    value = fallback;
end
end

function g = defaultGmax(model)
switch model
    case {'dipole', 'dipole_halfwave', 'dipole_half_wave'}
        g = 2.15;
    case {'monopole', 'monopole_groundplane', 'monopole_ground_plane'}
        g = 5.15;
    case {'helical', 'helical_axial'}
        g = 11;
    case {'parabolic', 'parabolic_dish', 'dish'}
        g = 20;
    case {'pcb', 'pcb_compact'}
        g = 1;
    case {'commercial_omni_6dbi', 'commercial_omni', 'omni_6dbi'}
        g = 6;
    otherwise
        g = 0;
end
end

function h = defaultHPBW(model)
switch model
    case {'helical', 'helical_axial'}
        h = 55;
    case {'parabolic', 'parabolic_dish', 'dish'}
        h = 18;
    case {'commercial_omni_6dbi', 'commercial_omni', 'omni_6dbi'}
        h = 35;
    otherwise
        h = 90;
end
end

