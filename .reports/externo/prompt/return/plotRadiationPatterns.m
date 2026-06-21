function plotRadiationPatterns(antennas)
%plotRadiationPatterns Plota cortes em theta, phi e padroes 3D simplificados.

theta = linspace(0, 180, 721);
phiFixed = zeros(size(theta));
phi = linspace(0, 360, 721);
thetaHorizon = 90 .* ones(size(phi));

figure('Name', 'Cortes em theta dos diagramas de radiacao', 'NumberTitle', 'off');
hold on; grid on;
for k = 1:numel(antennas)
    params = antennaParams(antennas(k));
    g = antennaPattern(antennas(k).PatternModel, theta, phiFixed, params);
    plot(theta, g, 'LineWidth', 1.5, 'DisplayName', antennas(k).Name);
end
xlabel('\theta (graus)');
ylabel('Ganho (dBi)');
title('Corte em \theta, com \phi = 0 grau');
legend('Location', 'best');
hold off;

figure('Name', 'Cortes em phi dos diagramas de radiacao', 'NumberTitle', 'off');
hold on; grid on;
for k = 1:numel(antennas)
    params = antennaParams(antennas(k));
    g = antennaPattern(antennas(k).PatternModel, thetaHorizon, phi, params);
    plot(phi, g, 'LineWidth', 1.5, 'DisplayName', antennas(k).Name);
end
xlabel('\phi (graus)');
ylabel('Ganho (dBi)');
title('Corte em \phi, com \theta = 90 graus');
legend('Location', 'best');
hold off;

figure('Name', 'Padroes 3D simplificados', 'NumberTitle', 'off');
nAnt = numel(antennas);
nRows = ceil(nAnt / 3);
nCols = min(3, nAnt);
[Phi, Theta] = meshgrid(linspace(0, 360, 91), linspace(0, 180, 61));

for k = 1:nAnt
    params = antennaParams(antennas(k));
    G = antennaPattern(antennas(k).PatternModel, Theta, Phi, params);
    radius = 10.^((G - antennas(k).Gmax_dBi) ./ 20);
    radius = max(radius, 0.02);
    X = radius .* sind(Theta) .* cosd(Phi);
    Y = radius .* sind(Theta) .* sind(Phi);
    Z = radius .* cosd(Theta);

    subplot(nRows, nCols, k);
    surf(X, Y, Z, G, 'EdgeColor', 'none');
    axis equal tight;
    view(35, 25);
    colormap turbo;
    title(strrep(antennas(k).Name, '_', '\_'));
    xlabel('x'); ylabel('y'); zlabel('z');
    camlight headlight;
    lighting gouraud;
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

