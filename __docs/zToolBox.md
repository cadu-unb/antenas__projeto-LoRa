<link rel="stylesheet" type="text/css" href=".css/style.css">

# ToolBox Manual

## ⚠️ Atualizar a instalação global

Se você alterar ou adicionar módulos na `toolbox`, reinstale a ferramenta:

```pwsh
    :: Caminho Relativo
    $TOOLBOX_DIR = "..\toolbox"
    :: ou Caminho Absoluto
    $TOOLBOX_DIR = "C:\Users\anton\OneDrive\Documentos\GitHub\toolbox"
    uv tool install --reinstall $TOOLBOX_DIR
```

## Caminhos úteis

- Direitório atual
```pwsh
    :: Caminho Relativo
    $REPO_ALVO = "..\antenas__projeto-LoRa"
    :: ou Caminho Absoluto
    $REPO_ALVO = "C:\Users\[...]\antenas__projeto-LoRa"
```
- Direitório da ToolBox
```pwsh
    :: Caminho Relativo
    $TOOLBOX_DIR = "..\toolbox"
    :: ou Caminho Absoluto
    $TOOLBOX_DIR = "C:\Users\[...]\toolbox"
```
- Path filtro:
```pwsh
    :: Caminho Absoluto
    $CONFIG_FILE = "..\antenas__projeto-LoRa\__docs\zFilter.py"
    $CONFIG_FILE = "C:\Users\anton\OneDrive\Documentos\GitHub\antenas__projeto-LoRa\__docs\zFilter.py"
```


## Tree

- Fluxo mínimo recomendado:

```pwsh
    $TOOLBOX_DIR = "C:\Users\anton\OneDrive\Documentos\GitHub\toolbox"   # substitua pelo seu caminho
    cd $TOOLBOX_DIR
    uv sync
    uv run toolbox list
    uv tool install $TOOLBOX_DIR
    cd $REPO_ALVO
```

- Exemplo de Uso
```pwsh
    toolbox run file_tree -- $REPO_ALVO --config $CONFIG_FILE
```

