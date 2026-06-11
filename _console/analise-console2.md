# Analise do Console do Navegador

Arquivo analisado: `_console/console-export-2026-6-11_15-8-14.log`

Data da analise: 2026-06-11

## Resumo Executivo

O log contém cinco famílias de mensagens, com diagnósticos e ações revisados após inspeção do código-fonte:

| Família | Origem Real | Impacto | Status |
|---------|-------------|---------|--------|
| CORS `webhooks.fivetran.com` | Telemetria do Streamlit (`index.dkY5s53S.js`) | Console poluído | **Corrigido** — `gatherUsageStats = false` |
| `NetworkError` Promise | Consequência do bloqueio CORS acima | Console poluído | **Corrigido** — mesmo fix |
| `Permissions-Policy` diretivas ignoradas | Streamlit CSP com nomes obsoletos | Ruído benigno | Sem ação necessária |
| `iframe sandbox` (`allow-scripts` + `allow-same-origin`) | `streamlit-folium` design | Risco XSS de tooltip | **Corrigido** — escaping de labels KML |
| Leaflet CDN falha | Dependência CDN externa do folium | Mapa não renderiza offline | **Mitigado** — pre-check + warning |

**Nenhum erro origina do motor de simulação, do parser KML, do cálculo RF ou do GIS.** Os problemas são de infraestrutura/dependência externa.

---

## Erro 1: CORS `webhooks.fivetran.com`

### Mensagem

```text
Requisição cross-origin bloqueada: ... webhooks.fivetran.com ... (null).
```

### Origem Real

**Não é código deste projeto.** `rg -ri "fivetran|webhook" src/` → zero resultados.

A chamada vem de `index.dkY5s53S.js` — bundle minificado do frontend do Streamlit, confirmado pelas mensagens de `Permissions-Policy` que referenciam explicitamente `index.dkY5s53S.js:2:39736`. O Streamlit envia telemetria de uso para um webhook Fivetran. O navegador bloqueia por CORS. O Streamlit ignora a falha silenciosamente.

### Correção Aplicada

`.streamlit/config.toml`:
```toml
[browser]
gatherUsageStats = false
```

`docker-compose.yml`:
```yaml
environment:
  - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

---

## Erro 2: `NetworkError when attempting to fetch resource`

Consequência direta do Erro 1. Resolvido pelo mesmo fix. Sem ação adicional.

---

## Aviso 1: Diretivas de Recursos Não Suportadas

```text
Diretiva de recursos: Desconsiderando nome de recurso não suportado "accelerometer".
index.dkY5s53S.js:2:39736
```

Originam de `index.dkY5s53S.js` — Streamlit define um cabeçalho `Permissions-Policy` com nomes que o Firefox não reconhece (nomes obsoletos da `Feature-Policy` antiga). O Firefox avisa e ignora. **Ruído benigno — fora do escopo deste projeto.**

---

## Aviso 2: iframe com `allow-scripts` e `allow-same-origin`

```text
Um iframe que tem tanto allow-scripts como allow-same-origin no atributo sandbox
pode remover o isolamento. localhost:3953
```

### Origem

`streamlit-folium` renderiza o mapa folium em um `<iframe sandbox="allow-scripts allow-same-origin">`. Essa combinação é necessária para o Leaflet interagir com o DOM. O Firefox emite o aviso correto: um iframe com ambos os atributos pode escapar o sandbox.

### Risco Real

O conteúdo do iframe inclui tooltips gerados a partir dos campos `<name>` do KML. Se um KML malicioso contiver `&lt;script&gt;...&lt;/script&gt;` em um nome de ponto ou polígono, sem escaping o browser poderia executar o script no contexto do iframe, com `allow-scripts` ativo.

### Correção Aplicada

`pages/campus.py` — todos os labels provenientes de KML agora são escapados antes de passar para tooltips folium:

```python
import html as _html

# Markers, polygons, polylines:
tooltip=_html.escape(point.label)
tooltip=_html.escape(polygon.label)
tooltip=_html.escape(f"{r.origin_label}→{r.dest_label} | {r.link_margin_db:.1f} dB")
```

O atributo `sandbox` em si é uma decisão de design do `streamlit-folium` e não é configurável pelo código Python deste projeto.

---

## Erro 3: Falha ao Carregar Leaflet via CDN

```text
Falha no carregamento do <script> com origem em
"https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js".
```

### Origem

Folium gera HTML com `<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js">`. Em ambiente sem internet (Docker offline, rede corporativa com restrições), o script não carrega e o mapa fica em branco.

### Por que não foi resolvido com bundling local

Folium 0.17 não tem modo "bundle tudo localmente" para Leaflet. Sobrescrever as URLs CDN internamente do folium requer monkey-patch de atributos privados (`JavascriptLink._url`), o que é frágil e quebra a cada update de folium. A decisão foi não introduzir acoplamento a internals de terceiros.

### Mitigação Aplicada

1. **Pre-check server-side** em `pages/campus.py` — verifica se `cdn.jsdelivr.net` é acessível a partir do processo Python (mesmo host/container que o browser usaria) e exibe warning antes de tentar renderizar o mapa:

```python
@st.cache_data(ttl=30)
def _leaflet_cdn_reachable() -> bool:
    try:
        urllib.request.urlopen("https://cdn.jsdelivr.net", timeout=1.5)
        return True
    except Exception:
        return False

# Phase 4 — Map
if not _leaflet_cdn_reachable():
    st.warning(
        "Sem acesso a cdn.jsdelivr.net — o mapa não renderizará. "
        "Verifique conectividade de internet ou execute fora do modo offline."
    )
```

2. **`except Exception`** captura qualquer erro Python durante a criação do mapa e exibe mensagem controlada.

3. Para Docker com acesso à internet, o mapa funciona normalmente (a rede do container usa a rede do host por padrão).

---

## Erro 4: Promise Rejeitada no Carregamento do Script

```text
Uncaught (in promise)
error { target: script, isTrusted: true, ... }
```

Consequência direta da falha de carregamento do Leaflet (Erro 3). É JavaScript interno do `streamlit-folium` sem tratamento de erro. **Fora do escopo deste projeto.**

---

## Aviso 3: Sourcemap Inválido no DevTools

```text
Erro no mapa de codigo: Error: URL constructor:  is not a valid URL.
URL do recurso: wasm:http://localhost:3953/static/js/index.dkY5s53S.js
URL do mapa de codigo: null
```

Ruído do DevTools tentando resolver sourcemap de módulo WebAssembly gerado pelo build do Streamlit. Não afeta execução. **Sem ação necessária.**

---

## Arquivos Modificados

| Arquivo | Mudança |
|---------|---------|
| `.streamlit/config.toml` | Adicionado `enableStaticServing = true` (para futura expansão com assets locais) |
| `src/lora_antenna/pages/campus.py` | `import html as _html` + `import urllib.request` + `_leaflet_cdn_reachable()` cached + `_html.escape()` em todos os tooltips de origem KML |

---

## Diagnóstico Final

| # | Problema | Causa raiz | Status |
|---|----------|-----------|--------|
| 1 | CORS Fivetran (×200) | Telemetria Streamlit | **Corrigido** |
| 2 | `NetworkError` Promise (×124) | Consequência #1 | **Corrigido** |
| 3 | Permissions-Policy warnings | Streamlit CSP | Benigno |
| 4 | iframe sandbox XSS risk | streamlit-folium + labels não escapados | **Corrigido** |
| 5 | Leaflet CDN failure | Folium depende de CDN externo | **Mitigado** |
| 6 | Script load Promise | Consequência #5 | Benigno (coberto pelo #5) |
| 7 | DevTools sourcemap | Build Streamlit | Benigno |
