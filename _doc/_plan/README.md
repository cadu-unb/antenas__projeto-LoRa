# Resumo do Projeto

O projeto consiste no desenvolvimento de uma aplicação científica e visual para análise de antenas e enlaces LoRa/LoRaWAN, com foco em aplicações de Internet das Coisas (IoT) de longo alcance e baixo consumo energético.

A plataforma será construída em Python (3.11/3.12), utilizando Streamlit para a interface gráfica, `uv` para gerenciamento de dependências e Docker para distribuição em rede local (LAN) pela porta padrão 3953.

---

# Objetivo Principal

Criar uma ferramenta que permita:

- Projetar e analisar diferentes tipos de antenas;
- Calcular parâmetros eletromagnéticos fundamentais;
- Visualizar geometrias e padrões de radiação;
- Simular enlaces entre transmissor e receptor;
- Estimar cobertura geográfica em mapas reais;
- Gerar relatórios técnicos automáticos.

---

# Conceito Central

O núcleo da aplicação será o objeto `Antenna`, que representará uma antena como uma entidade reproduzível e serializável, contendo:

- Frequência de operação;
- Tipo e geometria;
- Dimensões físicas;
- Ganho e diretividade;
- Impedância;
- VSWR;
- Eficiência;
- Polarização;
- Área efetiva;
- Padrão de radiação;
- Localização geográfica.

Esses objetos poderão ser salvos, reutilizados e comparados em diferentes simulações.

---

# Cenário 1 — Antena Standalone

Neste cenário, o usuário poderá analisar uma única antena em detalhes.

## Funcionalidades

- Seleção de frequência (~~433 MHz~~ (Fora da faixa definida pela ANATEL), ~~868 MHz~~ (Fora da faixa definida pela ANATEL), 915 MHz ou personalizada);
- Escolha do tipo de antena (Monopole, Dipole, Patch, Yagi, etc.);
- Cálculo automático das dimensões;
- Cálculo de comprimento de onda;
- Ganho, impedância, VSWR e área efetiva;
- Visualização da geometria da antena;
- Diagramas de radiação 2D e 3D;
- Comparação entre diferentes frequências.

---

# Cenário 2 — Sistema com Duas Antenas

Neste cenário, será possível modelar um enlace completo entre uma antena transmissora e uma receptora.

## Funcionalidades

- Criação das antenas Tx e Rx;
- Definição da distância entre elas;
- Cálculo da perda em espaço livre (FSPL);
- Aplicação da equação de Friis;
- Estimativa da potência recebida;
- Cálculo da margem de enlace;
- Visualização das zonas de Fresnel;
- Gráficos de potência versus distância;
- Simulação de cobertura.

---

# Cobertura Geográfica

A aplicação utilizará dados geográficos oficiais (como shapefiles do IBGE) para:

- Recortar a área de interesse (por exemplo, um campus);
- Gerar uma grade espacial;
- Calcular a potência recebida em cada ponto;
- Produzir mapas de cobertura e heatmaps.

---

# Modelos Matemáticos

Serão utilizados modelos analíticos e aproximações clássicas da literatura, incluindo:

- Comprimento de onda;
- Área efetiva da antena;
- Coeficiente de reflexão;
- VSWR;
- Return Loss;
- EIRP;
- FSPL;
- Equação de Friis.

O objetivo é fornecer estimativas de engenharia confiáveis, sem implementar simulações eletromagnéticas completas (como FDTD ou FEM).

---

# Persistência e Reprodutibilidade

Os projetos serão armazenados em:

- JSON (serialização científica);
- SQLite (biblioteca e histórico);
- Pydantic (validação e versionamento de esquema).

Cada antena e simulação poderá ser salva, recarregada e comparada posteriormente.

---

# Interface e Visualização

A interface será desenvolvida com Streamlit e incluirá:

- Formulários interativos;
- Gráficos com Plotly;
- Diagramas polares;
- Visualizações 3D;
- Mapas geográficos com Folium.

---

# Infraestrutura e Deploy

O projeto utilizará:

- `uv` para gerenciamento de ambiente e dependências;
- Docker para empacotamento;
- Docker Compose para execução;
- Acesso via navegador em rede local na porta 3953.

Exemplo de acesso:

```text
http://IP_DO_SERVIDOR:3953