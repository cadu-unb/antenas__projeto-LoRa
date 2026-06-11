# Analise do Console do Navegador

Arquivos analisados:
- `_console/console-export-2026-6-11_15-0-10.log`
- `_console/console-export-2026-6-11_15-8-14.log`

Data da analise: 2026-06-11

## Resumo Executivo

Os logs contêm quatro classes de mensagens distintas, com três origens identificadas:

| Classe | Origem | Projeto responsável | Ação |
|--------|--------|---------------------|------|
| Bloqueio CORS `webhooks.fivetran.com` | Telemetria do Streamlit (`index.dkY5s53S.js`) | Streamlit (externo) | **Corrigido** — `gatherUsageStats = false` |
| `NetworkError when attempting to fetch` | Consequência do bloqueio CORS acima | Streamlit (externo) | **Corrigido** — mesmo fix |
| Falha ao carregar Leaflet.js (`cdn.jsdelivr.net`) | Folium carrega Leaflet por CDN | Dependência transitiva | **Anotado** — ambiente sem internet |
| `Diretiva de recursos: Desconsiderando nome de recurso` | Streamlit CSP com diretivas obsoletas (`index.dkY5s53S.js`) | Streamlit (externo) | Ruído benigno |

**Nenhum erro origina código deste projeto.** `rg -ri "fivetran\|webhook" src/` → zero resultados.

---

## Erro 1: Requisição Cross-Origin Bloqueada — `webhooks.fivetran.com`

### Mensagem

```text
Requisição cross-origin bloqueada: A diretiva Same Origin (mesma origem) não permite
a leitura do recurso remoto em https://webhooks.fivetran.com/webhooks/615b5e5c-...
(motivo: falha na requisição CORS). Código de status: (null).
```

### Origem Real

A chamada vem de `index.dkY5s53S.js` — bundle minificado do frontend do Streamlit, **não do código do projeto**. O Streamlit envia telemetria de uso para um webhook Fivetran. O segundo log confirma isso: as mensagens de `Diretiva de recursos` (Permissions-Policy) originam-se explicitamente de `index.dkY5s53S.js:2:39736` — o mesmo arquivo que dispara as chamadas Fivetran.

O navegador bloqueia a requisição por CORS porque o webhook da Fivetran não permite leitura de respostas por origens externas. O bloqueio é correto e esperado — o Streamlit ignora a falha e continua funcionando.

**O motor de simulação LoRa, o parser KML, o cálculo RF e o GIS não são afetados.**

### Correção Aplicada

Criado `.streamlit/config.toml`:

```toml
[browser]
gatherUsageStats = false
```

E adicionado ao `docker-compose.yml`:

```yaml
environment:
  - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

Após essa configuração, o Streamlit não tenta enviar telemetria e os erros CORS desaparecem.

---

## Erro 2: `Uncaught (in promise) TypeError: NetworkError`

### Mensagem

```text
Uncaught (in promise) TypeError: NetworkError when attempting to fetch resource.
```

### Origem

Consequência direta do bloqueio CORS do Erro 1. A Promise do `fetch()` interno do Streamlit rejeita sem tratamento porque é telemetria fire-and-forget — o Streamlit propositalmente não trata esse erro. **Resolvido com o mesmo fix do Erro 1.**

---

## Erro 3: Falha ao Carregar Leaflet.js via CDN

### Mensagem (segundo log, linha 102)

```text
Falha no carregamento do <script> com origem em
"https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js". index.html:1:1
Uncaught (in promise)
```

### Origem

Folium gera HTML com referência ao Leaflet.js a partir de `cdn.jsdelivr.net`. Quando o ambiente não tem acesso à internet (Docker sem rede, rede corporativa com restrições, ou CDN temporariamente indisponível), o script falha a carregar e o mapa não renderiza.

**O cálculo RF e os resultados de simulação não são afetados.** Apenas a fase visual (mapa) fica indisponível.

### Correção Aplicada

Adicionada mensagem informativa no mapa em `pages/campus.py`:

```python
st.caption(
    "O mapa requer acesso a cdn.jsdelivr.net para carregar o Leaflet.js. "
    "Em ambiente offline ou Docker sem saída para internet, o mapa pode não renderizar."
)
```

E adicionado `except Exception` para capturar erros de renderização do folium sem quebrar a página.

Para corrigir o problema de rede no Docker, garantir conectividade com `cdn.jsdelivr.net` no ambiente onde o container executa.

---

## Aviso 4: Diretiva de Recursos (Permissions-Policy)

### Mensagem

```text
Diretiva de recursos: Desconsiderando nome de recurso não suportado "accelerometer".
index.dkY5s53S.js:2:39736
```

### Origem

Streamlit define um cabeçalho `Permissions-Policy` no iframe do folium com diretivas que o Firefox não reconhece (nomes obsoletos ou de outros browsers). Firefox registra o aviso e ignora. **Ruído benigno — nenhuma ação necessária.**

---

## Aviso 5: iframe sandbox (`allow-scripts` + `allow-same-origin`)

### Mensagem (segundo log, linha 99)

```text
Um iframe que tem tanto allow-scripts como allow-same-origin no atributo sandbox pode
remover o isolamento. localhost:3953
```

### Origem

`streamlit-folium` renderiza o mapa folium em um `<iframe sandbox="allow-scripts allow-same-origin">`. Essa combinação é uma decisão de design da biblioteca para permitir que o Leaflet interaja com o DOM pai. O Firefox alerta sobre o risco teórico de escalonamento de sandbox. **Fora do escopo deste projeto — não é configurável via código Python.**

---

## Diagnóstico Consolidado

| # | Erro | Origem | Impacto | Status |
|---|------|--------|---------|--------|
| 1 | CORS `webhooks.fivetran.com` (×200+) | Telemetria Streamlit | Console poluído | **Corrigido** |
| 2 | `NetworkError` Promise (×124) | Consequência do #1 | Console poluído | **Corrigido** |
| 3 | Leaflet CDN falha | CDN sem internet | Mapa não renderiza | **Anotado** |
| 4 | Permissions-Policy warnings | Streamlit CSP | Nenhum | Benigno |
| 5 | iframe sandbox warning | streamlit-folium | Nenhum | Benigno |

---

## Arquivos Modificados

| Arquivo | Mudança |
|---------|---------|
| `.streamlit/config.toml` | **Criado** — `gatherUsageStats = false` |
| `docker-compose.yml` | Adicionado `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false` e volume `.streamlit` |
| `src/lora_antenna/pages/campus.py` | `st.caption` sobre Leaflet CDN + `except Exception` no bloco do mapa |
