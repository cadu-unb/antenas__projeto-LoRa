function plotCampusMap(points, gatewayIdx, linkResults, figureTitle)
%plotCampusMap Plota pontos do campus e enlaces coloridos por margem.

if nargin < 4
    figureTitle = 'Mapa do campus com enlaces ao gateway';
end

figure('Name', figureTitle, 'NumberTitle', 'off');
useGeo = exist('geoplot', 'file') == 2;

if useGeo
    geoplot(points.Lat, points.Lon, 'ko', 'MarkerFaceColor', [0.85 0.85 0.85], 'MarkerSize', 6);
    hold on;
    geoplot(points.Lat(gatewayIdx), points.Lon(gatewayIdx), 'kp', ...
        'MarkerFaceColor', 'c', 'MarkerSize', 14);
    if exist('geobasemap', 'file') == 2
        geobasemap('streets');
    end

    for i = 1:height(points)
        text(points.Lat(i), points.Lon(i), ['  ' points.Name{i}], 'FontWeight', 'bold');
    end

    for r = 1:height(linkResults)
        idx = find(strcmp(points.Name, linkResults.PointName{r}), 1);
        if isempty(idx), continue; end
        geoplot([points.Lat(idx), points.Lat(gatewayIdx)], [points.Lon(idx), points.Lon(gatewayIdx)], ...
            '-', 'Color', statusColor(linkResults.LinkStatus{r}), 'LineWidth', 2);
    end
    geolimits([min(points.Lat)-0.001, max(points.Lat)+0.001], [min(points.Lon)-0.001, max(points.Lon)+0.001]);
else
    [east, north] = geodeticToLocalENU(points.Lat, points.Lon, points.Alt, ...
        points.Lat(gatewayIdx), points.Lon(gatewayIdx), points.Alt(gatewayIdx));
    plot(east, north, 'ko', 'MarkerFaceColor', [0.85 0.85 0.85], 'MarkerSize', 6);
    hold on; grid on; axis equal;
    plot(east(gatewayIdx), north(gatewayIdx), 'kp', 'MarkerFaceColor', 'c', 'MarkerSize', 14);
    for i = 1:height(points)
        text(east(i), north(i), ['  ' points.Name{i}], 'FontWeight', 'bold');
    end
    for r = 1:height(linkResults)
        idx = find(strcmp(points.Name, linkResults.PointName{r}), 1);
        if isempty(idx), continue; end
        plot([east(idx), east(gatewayIdx)], [north(idx), north(gatewayIdx)], ...
            '-', 'Color', statusColor(linkResults.LinkStatus{r}), 'LineWidth', 2);
    end
    xlabel('Leste (m)');
    ylabel('Norte (m)');
end

title(figureTitle);
hold off;
end

function c = statusColor(status)
switch lower(status)
    case 'falha'
        c = [0.85 0.1 0.1];
    case 'critico'
        c = [0.95 0.75 0.05];
    otherwise
        c = [0.1 0.65 0.2];
end
end

