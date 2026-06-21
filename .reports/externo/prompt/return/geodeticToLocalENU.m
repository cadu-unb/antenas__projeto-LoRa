function [east_m, north_m, up_m] = geodeticToLocalENU(lat, lon, alt, lat0, lon0, alt0)
%geodeticToLocalENU Converte coordenadas geograficas para ENU local.
%   Usa Mapping Toolbox quando disponivel; caso contrario, usa aproximacao
%   local adequada para a escala do campus.

if exist('geodetic2enu', 'file') == 2 && exist('wgs84Ellipsoid', 'file') == 2
    try
        ellipsoid = wgs84Ellipsoid('meter');
        [east_m, north_m, up_m] = geodetic2enu(lat, lon, alt, lat0, lon0, alt0, ellipsoid);
        return;
    catch
        % Se a toolbox existir mas falhar por versao/assinatura, usa fallback.
    end
end

lat = lat(:);
lon = lon(:);
alt = alt(:);
avgLat = (lat + lat0) ./ 2;

metersPerDegLat = 111132.92 - 559.82 .* cosd(2 .* avgLat) + ...
    1.175 .* cosd(4 .* avgLat) - 0.0023 .* cosd(6 .* avgLat);
metersPerDegLon = 111412.84 .* cosd(avgLat) - 93.5 .* cosd(3 .* avgLat) + ...
    0.118 .* cosd(5 .* avgLat);

east_m = (lon - lon0) .* metersPerDegLon;
north_m = (lat - lat0) .* metersPerDegLat;
up_m = alt - alt0;
end

