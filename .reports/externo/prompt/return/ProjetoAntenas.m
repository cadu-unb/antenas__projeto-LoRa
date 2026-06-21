% ========================================================================
% ALINHAMENTO DE LINK DIRECIONAL ENTRE COORDENADAS
% ========================================================================
clear; clc; close all;

% 1. Definição das coordenadas reais
lat_antena = -15.764483;
lon_antena = -47.859878;

lat_central = -15.772472;
lon_central = -47.867381;

% 2. Cálculo dinâmico de distância e ângulo de apontamento
metros_por_grau_lat = 111320;
avg_lat = (lat_antena + lat_central) / 2;
metros_por_grau_lon = 111320 * cosd(avg_lat);

% Deslocamentos em metros nos eixos X (Longitude) e Y (Latitude)
dx = (lon_central - lon_antena) * metros_por_grau_lon;
dy = (lat_central - lat_antena) * metros_por_grau_lat;

% Distância real de visada entre os dois pontos
distancia_link = sqrt(dx^2 + dy^2); 

% Ângulo matemático de apontamento (em radianos)
angulo_apontamento = atan2(dy, dx); 

% 3. Configuração dos parâmetros do feixe direcional
abertura_deg = 25; % Abertura estreita para simular antena direcional/parabólica
abertura_rad = deg2rad(abertura_deg);

% Define o limite do feixe para que ultrapasse um pouco a central (margem de 15%)
raio_feixe_metros = distancia_link * 1.15; 

% Gerar o arco do feixe direcionado
theta = linspace(angulo_apontamento - abertura_rad/2, angulo_apontamento + abertura_rad/2, 50);

dx_feixe = raio_feixe_metros * cos(theta);
dy_feixe = raio_feixe_metros * sin(theta);

lat_borda = lat_antena + (dy_feixe / metros_por_grau_lat);
lon_borda = lon_antena + (dx_feixe / metros_por_grau_lon);

% Fechar a geometria do lóbulo (Origem -> Arco -> Origem)
lat_setor = [lat_antena, lat_borda, lat_antena];
lon_setor = [lon_antena, lon_borda, lon_antena];

% 4. Plotagem no Mapa Geográfico
figure('Name', 'Alinhamento de Link Direcional', 'NumberTitle', 'off');

% Plota a Antena Transmissora (Triângulo Vermelho)
geoplot(lat_antena, lon_antena, 'r^', 'MarkerSize', 12, 'MarkerFaceColor', 'r');
hold on;

% Plota a Central de Recepção (Círculo Verde)
geoplot(lat_central, lon_central, 'go', 'MarkerSize', 12, 'MarkerFaceColor', 'g');

% Desenha o contorno do feixe direcional em azul
geoplot(lat_setor, lon_setor, 'b-', 'LineWidth', 1.5);

% Desenha uma linha tracejada preta representando a linha de visada direta (LoS)
geoplot([lat_antena, lat_central], [lon_antena, lon_central], 'k:', 'LineWidth', 2);

% Carrega o mapa de fundo
geobasemap('streets'); 

% Adiciona identificadores de texto na tela
text(lat_antena + 0.0003, lon_antena, ' Antena Direcional', 'FontWeight', 'bold', 'FontSize', 10);
text(lat_central + 0.0003, lon_central, ' Central de Recepção', 'FontWeight', 'bold', 'FontSize', 10, 'Color', [0 0.5 0]);

% Ajusta os limites de visualização dinamicamente com uma margem de contorno
margem = 0.003;
geolimits([min([lat_antena, lat_central]) - margem, max([lat_antena, lat_central]) + margem], ...
          [min([lon_antena, lon_central]) - margem, max([lon_antena, lon_central]) + margem]);

title(sprintf('Link Direcional Configurado — Distância: %.2f metros', distancia_link));
hold off;