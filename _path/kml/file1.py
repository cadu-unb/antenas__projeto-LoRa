import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import contextily as ctx
from itertools import combinations
from math import atan2, cos, radians, sin, sqrt
from pathlib import Path

# =====================================================================
# 1. LEITURA NATIVA DO KML
# =====================================================================

caminho_kml = Path(__file__).with_name('mascara_campus_darcy_ribeiro.kml')

tree = ET.parse(caminho_kml)
root = tree.getroot()

lons_campus = []
lats_campus = []

for elem in root.iter():
    if 'coordinates' in str(elem.tag):
        coords_str = elem.text.strip().split()
        if len(coords_str) > 3:
            for ponto in coords_str:
                valores = ponto.split(',')
                lons_campus.append(float(valores[0]))
                lats_campus.append(float(valores[1]))
            break 

# =====================================================================
# 2. DEFINIÇÃO DOS NÓS LORA (ESP32)
# =====================================================================
lats_nos = [-15.762987, -15.765910, -15.766786, -15.768304, 
            -15.766009, -15.763774, -15.761263, -15.757649]

lons_nos = [-47.871879, -47.869717, -47.871248, -47.865723, 
            -47.866577, -47.865209, -47.867451, -47.870830]

pontos_interesse = [
    (f'P{i+1}', lat, lon)
    for i, (lat, lon) in enumerate(zip(lats_nos, lons_nos))
]


def distancia_haversine_m(lat1, lon1, lat2, lon2):
    raio_terra_m = 6_371_000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return raio_terra_m * c


def imprimir_tabela_distancias(pontos):
    print('\nDistancias entre pontos de interesse')
    print('-' * 54)
    print(f'{"Origem":<8} {"Destino":<8} {"Distancia (m)":>14} {"Distancia (km)":>16}')
    print('-' * 54)

    for origem, destino in combinations(pontos, 2):
        nome_origem, lat_origem, lon_origem = origem
        nome_destino, lat_destino, lon_destino = destino
        distancia_m = distancia_haversine_m(
            lat_origem,
            lon_origem,
            lat_destino,
            lon_destino,
        )
        print(
            f'{nome_origem:<8} {nome_destino:<8} '
            f'{distancia_m:>14.1f} {distancia_m / 1000:>16.3f}'
        )


# =====================================================================
# 3. VISUALIZAÇÃO COM MAPA DE RELEVO AO FUNDO
# =====================================================================
# Criamos a figura definindo 'ax' (eixos) para o contextily conseguir desenhar
fig, ax = plt.subplots(figsize=(12, 10))

# Desenha a fronteira do Campus extraída do KML
ax.plot(lons_campus, lats_campus, color='blue', linewidth=2, label='Fronteira do Campus')
ax.fill(lons_campus, lats_campus, color='blue', alpha=0.1)

# Plota os nós da rede LoRa
ax.scatter(lons_nos, lats_nos, color='red', marker='^', s=100, label='Nós LoRa (ESP32)', zorder=5)

# Identifica cada nó com um texto
for i, (lon, lat) in enumerate(zip(lons_nos, lats_nos)):
    ax.text(lon + 0.0002, lat, f'P{i+1}', fontsize=11, fontweight='bold', color='darkred')

# ---> ADICIONANDO O MAPA DE RELEVO <---
# O crs='EPSG:4326' é crucial: ele avisa à biblioteca que nossas coordenadas estão em Graus (Lat/Lon).
# O provedor OpenTopoMap é excelente para visualizar elevações e curvas de nível reais.
ctx.add_basemap(ax, crs='EPSG:4326', source=ctx.providers.OpenTopoMap)

# Configurações visuais
ax.set_title('Topologia LoRa sobreposta ao Mapa de Relevo', fontsize=15, fontweight='bold')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.legend()

# Força a proporção e ajusta as margens da janela gráfica
ax.set_aspect('equal', adjustable='box')
plt.tight_layout()

plt.show()

# =====================================================================
# 4. TABELA DE DISTÂNCIAS ENTRE OS PONTOS
# =====================================================================
# Esta parte roda apenas depois que a janela do plot for fechada.
imprimir_tabela_distancias(pontos_interesse)
