% ========================================================================
% SIMULAÇÃO DE REDE LORA: COBERTURA OMNIDIRECIONAL E MATRIZ DE ENLACES
% ========================================================================
clear; clc; close all;

% 1. Banco de dados com os 10 nós (8 originais + 2 novos)
lats = [-15.762987, -15.765910, -15.766786, -15.768304, ...
        -15.766009, -15.763774, -15.761263, -15.757649, ...
        -15.764483, -15.772472];

lons = [-47.871879, -47.869717, -47.871248, -47.865723, ...
        -47.866577, -47.865209, -47.867451, -47.870830, ...
        -47.859878, -47.867381];

num_nos = length(lats);

% Parâmetro de alcance LoRa (em metros)
raio_lora_metros = 600; % Ajuste este valor para testar conexões com alcances maiores ou menores

% 2. Configurar o Gráfico Geográfico
figure('Name', 'Topologia da Rede e Enlaces', 'NumberTitle', 'off');
geoplot(lats, lons, 'r^', 'MarkerSize', 8, 'MarkerFaceColor', 'r');
hold on;
geobasemap('streets');

% 3. Desenhar a Cobertura Omnidirecional para cada ponto
theta = linspace(0, 2*pi, 100);
metros_por_grau_lat = 111320;

for i = 1:num_nos
    metros_por_grau_lon = 111320 * cosd(lats(i));
    
    dx_metros = raio_lora_metros * cos(theta);
    dy_metros = raio_lora_metros * sin(theta);
    
    lat_circulo = lats(i) + (dy_metros / metros_por_grau_lat);
    lon_circulo = lons(i) + (dx_metros / metros_por_grau_lon);
    
    % Plota o círculo de alcance de cada nó (Translúcido/Tracejado)
    geoplot(lat_circulo, lon_circulo, 'b--', 'LineWidth', 0.5, 'Color', [0 0 1 0.3]);
    
    % Identificar visualmente os pontos no mapa (P1, P2...)
    text(lats(i) + 0.0002, lons(i), sprintf('P%d', i), 'FontSize', 10, 'FontWeight', 'bold');
end

% 4. Cálculo de Distâncias e Enlaces
% Cria uma matriz vazia para registrar quem conecta com quem
conexoes = false(num_nos, num_nos); 

for i = 1:num_nos
    for j = 1:num_nos
        if i ~= j
            % Cálculo da distância entre o nó 'i' e o nó 'j'
            avg_lat = (lats(i) + lats(j)) / 2;
            metros_por_grau_lon = 111320 * cosd(avg_lat);
            
            dx = (lons(j) - lons(i)) * metros_por_grau_lon;
            dy = (lats(j) - lats(i)) * metros_por_grau_lat;
            distancia = sqrt(dx^2 + dy^2);
            
            % Se a distância for menor ou igual ao alcance da antena, há enlace!
            if distancia <= raio_lora_metros
                conexoes(i, j) = true;
            end
        end
    end
end

% 5. Desenhar as linhas de conexão (Enlaces) no mapa
for i = 1:num_nos
    for j = (i+1):num_nos % (i+1) garante que desenhamos a linha entre dois nós apenas uma vez
        if conexoes(i,j)
            geoplot([lats(i), lats(j)], [lons(i), lons(j)], '-', ...
                    'LineWidth', 2, 'Color', [0.2 0.8 0.2]); % Linha Verde
        end
    end
end

% 6. Exibir o Relatório de Conexões no Terminal (Estilo MIMO/Mesh)
fprintf('\n==================================================\n');
fprintf('RELATÓRIO DE ENLACES (ALCANCE DA ANTENA: %dm)\n', raio_lora_metros);
fprintf('==================================================\n');

for i = 1:num_nos
    % Busca quais índices da matriz deram 'true' para a linha 'i'
    vizinhos_conectados = find(conexoes(i, :));
    
    if isempty(vizinhos_conectados)
        fprintf('P%d -> (Sem conexões. Nó Isolado)\n', i);
    else
        % Formata a string para imprimir "P1, P2, P3" etc.
        str_vizinhos = sprintf('P%d, ', vizinhos_conectados);
        str_vizinhos = str_vizinhos(1:end-2); % Remove a última vírgula e o espaço
        
        fprintf('P%d -> %s\n', i, str_vizinhos);
    end
end
fprintf('==================================================\n\n');

% Ajuste de Zoom
geolimits('auto');
title(sprintf('Topologia de Rede LoRa - Cobertura: %dm', raio_lora_metros));
hold off;