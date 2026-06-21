function [gatewayIdx, candidateTable, ranking] = chooseGateway(points, mode, gatewayName)
%chooseGateway Escolhe o gateway manualmente ou por minimax de distancia.
%   [idx, candidateTable, ranking] = chooseGateway(points, 'manual', 'BCE')
%   [idx, candidateTable, ranking] = chooseGateway(points, 'auto')

if nargin < 2 || isempty(mode)
    mode = 'auto';
end
if nargin < 3
    gatewayName = '';
end

n = height(points);
meanDist = zeros(n, 1);
maxDist = zeros(n, 1);

for i = 1:n
    [east, north, up] = geodeticToLocalENU(points.Lat, points.Lon, points.Alt, ...
        points.Lat(i), points.Lon(i), points.Alt(i));
    d = sqrt(east.^2 + north.^2 + up.^2);
    d(i) = [];
    meanDist(i) = mean(d);
    maxDist(i) = max(d);
end

candidateTable = table(points.Name, meanDist, maxDist, ...
    'VariableNames', {'Name', 'MeanDistance_m', 'MaxDistance_m'});
[~, order] = sortrows([maxDist, meanDist], [1 2]);
ranking = candidateTable(order, :);

if strcmpi(mode, 'manual')
    gatewayIdx = find(strcmpi(points.Name, gatewayName), 1);
    if isempty(gatewayIdx)
        error('chooseGateway:UnknownGateway', 'Gateway "%s" nao encontrado na tabela de pontos.', gatewayName);
    end
else
    gatewayIdx = order(1);
end
end

