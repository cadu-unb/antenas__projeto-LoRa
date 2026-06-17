# Modelo Okumura-Hata

## Conceito

Modelo empírico de perda de percurso para sistemas móveis terrestres. Baseado em medições extensivas de Okumura em Tóquio (1968) e reformulado analiticamente por Hata (1980).

Amplamente usado para enlace LoRa em 868/915 MHz em ambientes urbanos e rurais.

## Intervalo de validade

| Parâmetro | Intervalo |
|---|---|
| Frequência | 150–1500 MHz |
| Distância | 1–20 km |
| Altura da base | 30–200 m |
| Altura do terminal | 1–10 m |

## Fórmula (urbano, cidade grande)

```
L_u = 69.55 + 26.16·log(f) − 13.82·log(h_b) − a(h_m)
      + (44.9 − 6.55·log(h_b))·log(d)
```

Onde `f` em MHz, `h_b` e `h_m` em metros, `d` em km.

**Fator de correção `a(h_m)` para cidade grande (f ≥ 300 MHz):**
```
a(h_m) = 3.2·(log(11.75·h_m))² − 4.97
```

## Correções por ambiente

| Ambiente | Correção aplicada |
|---|---|
| `urban_large` | Nenhuma (base) |
| `urban_small` | Nenhuma (fórmula usa a(h_m) de cidade pequena) |
| `suburban` | `L = L_u − 2·(log(f/28))² − 5.4` |
| `open` | `L = L_u − 4.78·(log f)² + 18.33·log f − 40.94` |

## Valor de referência (documentado em `tests/test_solvers.py`)

```
f=900 MHz, h_b=30 m, h_m=1.5 m, d=1 km, urban_large
Esperado: 126.43 dB  (tolerância ±1 dB)
```

Cálculo:
- a(h_m) = 3.2·(log 17.625)² − 4.97 ≈ 0.0
- L_u = 69.55 + 77.27 − 20.39 − 0.0 + 0.0 = 126.43 dB

## Limitações

- Assume terreno plano equivalente — não modela relevo
- Sem efeitos de difração por edifícios específicos
- Fora do intervalo de validade: sistema emite `warning` mas calcula mesmo assim
- Não aplicável para roteadores indoor ou enlaces < 1 km
- Para terrenos irregulares: usar Longley-Rice

## Extensão COST-231

Para 1500–2000 MHz (não implementada nesta versão):
```
L_COST = 46.3 + 33.9·log(f) − 13.82·log(h_b) − a(h_m)
         + (44.9 − 6.55·log(h_b))·log(d) + C_m
```
Onde C_m = 0 dB (médias cidades) ou 3 dB (centros metropolitanos).

## Referências

- M. Hata, "Empirical Formula for Propagation Loss in Land Mobile Radio Services",
  *IEEE Trans. Veh. Technol.*, vol. 29, pp. 317–325, 1980.
- Y. Okumura et al., "Field Strength and Its Variability in VHF and UHF Land-Mobile
  Radio Service", *Rev. Elec. Commun. Lab.*, vol. 16, 1968.
- COST Action 231, *Digital Mobile Radio Towards Future Generation Systems*, EU, 1999.
