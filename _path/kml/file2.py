import requests
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# =====================================================================
# 1. COORDENADAS DOS NÓS
# =====================================================================
lats_nos = [-15.762987, -15.765910, -15.766786, -15.768304, 
            -15.766009, -15.763774, -15.761263, -15.757649]

lons_nos = [-47.871879, -47.869717, -47.871248, -47.865723, 
            -47.866577, -47.865209, -47.867451, -47.870830]

# =====================================================================
# 2. CONSULTA DO RELEVO (API SRTM 30m)
# =====================================================================
print("Consultando a altitude real do terreno via satélite...")

# Formata as coordenadas para a URL da API (lat,lon|lat,lon...)
coords_str = "|".join([f"{lat},{lon}" for lat, lon in zip(lats_nos, lons_nos)])
url_api = f"https://api.opentopodata.org/v1/srtm30m?locations={coords_str}"

# Faz a requisição e extrai as altitudes em metros
resposta = requests.get(url_api).json()
elevacoes = [item['elevation'] for item in resposta['results']]

# =====================================================================
# 3. VISUALIZAÇÃO 3D DO RELEVO
# =====================================================================
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Define uma base visual para as "torres" (10 metros abaixo do ponto mais baixo)
z_base = min(elevacoes) - 10 

# Plota cada nó de rede
for i, (lon, lat, elev) in enumerate(zip(lons_nos, lats_nos, elevacoes)):
    # Desenha uma linha vertical simulando a altura desde a base até o relevo
    ax.plot([lon, lon], [lat, lat], [z_base, elev], color='gray', linestyle='--', linewidth=1.5)
    
    # Adiciona o texto com a identificação e a altitude exata
    ax.text(lon, lat, elev + 1.5, f"P{i+1}\n({elev:.1f}m)", 
            color='black', fontsize=9, fontweight='bold', ha='center')

# Plota as antenas no topo do relevo
ax.scatter(lons_nos, lats_nos, elevacoes, color='red', marker='^', s=100, label='Nós (Altitude Real)')

# Configurações visuais do ambiente 3D
ax.set_title('Diferença de Relevo entre os Nós da Rede', fontsize=14, fontweight='bold')
ax.set_xlabel('\nLongitude')
ax.set_ylabel('\nLatitude')
ax.set_zlabel('\nAltitude (metros)')
ax.legend()

# Ajusta o ângulo de visão inicial da câmera 3D (elevação, azimute)
ax.view_init(elev=20, azim=-45)

plt.show()