---
name: code-documentation-style
description: Apply clear, human-friendly standards for comments, docstrings, documentation, and visual organization when writing or editing Python, JavaScript, HTML, and CSS. Use whenever Codex creates or changes source code, especially when code should be maintainable, readable, well documented, visually organized, and free of redundant obvious comments.
---

# Code Documentation Style

## Objetivo

Escrever e editar código Python, JavaScript, HTML e CSS de forma legível, bem documentada e agradável para manutenção humana.

Documentar intenção, fluxo, responsabilidade e regras importantes sem poluir arquivos com comentários óbvios.

## Regras Gerais

1. Comentar apenas o que ajuda a entender intenção, fluxo, responsabilidade ou regra de negócio.
2. Evitar comentários que repetem literalmente o código.
3. Priorizar nomes claros para funções, classes, variáveis e arquivos.
4. Documentar estruturas importantes de forma proporcional à complexidade.
5. Escrever comentários e docstrings em português, salvo quando o projeto já estiver padronizado em outro idioma.
6. Não poluir arquivos pequenos com documentação excessiva.
7. Preservar o padrão existente quando houver convenção consolidada.
8. Preferir blocos bem separados e nomes claros antes de adicionar comentários.
9. Remover comentários antigos que ficaram errados após mudanças no código.
10. Não usar comentários para justificar código confuso; melhorar o código primeiro.

## Python

Use práticas compatíveis com PEP 8 e PEP 257.

### Docstrings

- Toda função pública deve ter docstring breve explicando:
  - o que a função faz;
  - parâmetros relevantes;
  - retorno, quando houver;
  - exceções importantes, quando aplicável.
- Toda classe pública deve ter docstring explicando:
  - responsabilidade da classe;
  - contexto de uso;
  - atributos relevantes, quando necessário.
- Métodos internos podem ter docstrings menores ou comentários apenas quando houver lógica não trivial.
- Módulos podem ter docstring quando concentram regra importante, API pública ou fluxo de domínio.

### Comentários

- Usar comentários inline com moderação.
- Comentar decisões, cálculos, exceções, regras de negócio e integrações pouco óbvias.
- Não comentar operações autoexplicativas.

### Organização

Organizar arquivos Python, quando fizer sentido, nesta ordem:

1. docstring de módulo;
2. imports;
3. constantes;
4. classes;
5. funções auxiliares;
6. função principal ou ponto de entrada.

Preferir type hints quando aumentarem clareza sem deixar o código artificial.

## JavaScript

Use documentação equivalente a JSDoc quando apropriado.

### JSDoc

- Funções públicas ou reutilizáveis devem receber comentário JSDoc com:
  - finalidade;
  - parâmetros;
  - retorno;
  - efeitos colaterais relevantes, quando houver.
- Classes devem ter comentário explicando:
  - responsabilidade;
  - estado interno relevante;
  - principais métodos de uso.
- Componentes, handlers e funções assíncronas devem deixar clara sua responsabilidade.

### Comentários

- Usar comentários inline apenas para decisões, regras de negócio, validações incomuns ou fluxos assíncronos relevantes.
- Evitar comentar operações óbvias, seletores simples ou manipulações diretas de DOM que já estejam claras pelo nome.

### Organização

Separar código JavaScript em blocos legíveis:

1. constantes e seletores;
2. estado local;
3. funções utilitárias;
4. chamadas de API;
5. handlers;
6. inicialização.

## HTML

Usar poucos comentários.

Comentar apenas seções estruturais importantes:

- cabeçalho;
- navegação;
- conteúdo principal;
- formulários complexos;
- rodapé;
- blocos grandes que se repetem ou têm responsabilidade clara.

Evitar comentários em elementos simples e autoexplicativos.

## CSS

Organizar CSS de forma hierárquica, agrupada e legível.

### Blocos recomendados

Separar o arquivo em blocos temáticos:

1. variáveis;
2. reset/base;
3. layout;
4. componentes;
5. estados;
6. utilitários;
7. responsividade.

### Organização de seletores

- Agrupar seletores relacionados.
- Organizar classes conforme estrutura visual ou funcional da interface.
- Usar comentários de seção para orientar leitura.
- Evitar comentários em propriedades óbvias.
- Preferir padrão próximo de BEM quando fizer sentido:
  - `.componente`
  - `.componente__elemento`
  - `.componente--modificador`

Não impor BEM quando o projeto já tiver outro padrão claro.

## Exemplos Rápidos

### Python

```python
def calcular_margem_enlace(potencia_recebida_dbm: float, sensibilidade_dbm: float) -> float:
    """Calcula a margem entre potência recebida e sensibilidade do receptor.

    Args:
        potencia_recebida_dbm: Potência estimada no receptor.
        sensibilidade_dbm: Menor potência que o receptor consegue interpretar.

    Returns:
        Margem do enlace em dB.
    """
    return potencia_recebida_dbm - sensibilidade_dbm
```

### JavaScript

```javascript
/**
 * Busca antenas salvas e atualiza a lista da biblioteca.
 *
 * @returns {Promise<void>}
 */
async function carregarBiblioteca() {
  const antenas = await api.listarAntenas();
  renderizarAntenas(antenas);
}
```

### HTML

```html
<!-- Formulário principal do sandbox -->
<form id="antenna-form">
  <label for="frequency">Frequência</label>
  <input id="frequency" name="frequency" type="number" />
</form>
```

### CSS

```css
/* Componentes */
.antenna-card {
  border: 1px solid var(--color-border);
  padding: 1rem;
}

.antenna-card__title {
  font-weight: 600;
}

.antenna-card--selected {
  border-color: var(--color-accent);
}
```

## Checklist Antes de Entregar

- Comentários explicam intenção, não sintaxe óbvia.
- Funções públicas têm documentação proporcional.
- Classes públicas explicam responsabilidade.
- Código pequeno não ficou superdocumentado.
- Nomes claros reduzem necessidade de comentário.
- CSS está separado por blocos temáticos.
- HTML usa comentários apenas em seções relevantes.
- Padrão existente do projeto foi preservado.
