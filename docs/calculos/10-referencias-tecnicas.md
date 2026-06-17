# Referências Técnicas

Referências bibliográficas verificáveis usadas nos solvers e modelos do sistema.

---

## Antenas — Teoria e Projeto

**[1]** C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed.
Wiley, 2016. ISBN 978-1-118-64206-1.
> Referência principal para dipolo analítico (Cap. 4, Eq. 4-79), monopolo (Cap. 4), helicoidal (Cap. 11), abertura (Cap. 15).

**[2]** W. L. Stutzman & G. A. Thiele, *Antenna Theory and Design*, 3rd ed.
Wiley, 2012. ISBN 978-0-470-57664-9.
> Fundamentação alternativa para SWR, impedância de entrada e padrões de irradiação.

**[3]** J. D. Kraus, "Helical Beam Antenna",
*Electronics*, vol. 20, pp. 109–111, April 1947.
> Fórmula original de ganho para helicoidal em modo axial: G ≈ 15·N·(C/λ)²·sin(α).

**[4]** S. Silver, *Microwave Antenna Theory and Design*, MIT Radiation Lab Series, Vol. 12.
MIT, 1949. Disponível via archive.org.
> Abertura efetiva e eficiência de abertura η para refletores parabólicos.

---

## NEC-2 — Method of Moments

**[5]** G. J. Burke & A. J. Poggio, *Numerical Electromagnetics Code (NEC) — Method of Moments*.
LLNL Tech. Doc. UCID-18834, Lawrence Livermore National Laboratory, 1981.
> Formulação original do NEC-2. Disponível em: https://www.nec2.org/

**[6]** A. J. Burke, *NEC-2 User's Manual*.
LLNL, 1992.
> Manual de uso das cards (GW, EX, FR, RP) usadas na interface PyNEC.

---

## Propagação — Okumura-Hata

**[7]** M. Hata, "Empirical Formula for Propagation Loss in Land Mobile Radio Services",
*IEEE Transactions on Vehicular Technology*, vol. 29, no. 3, pp. 317–325, August 1980.
DOI: 10.1109/T-VT.1980.23859.
> Fórmulas exatas implementadas: L_u, a(h_m), correções suburban e open.

**[8]** Y. Okumura, E. Ohmori, T. Kawano & K. Fukuda,
"Field Strength and Its Variability in VHF and UHF Land-Mobile Radio Service",
*Review of the Electrical Communication Laboratory*, vol. 16, no. 9–10, pp. 825–873, 1968.
> Dados de campo originais das campanhas em Tóquio que Hata reformulou.

**[9]** COST Action 231, *Digital Mobile Radio Towards Future Generation Systems — Final Report*.
European Commission, 1999.
> Extensão COST-231 de Hata para 1500–2000 MHz (não implementada nesta versão).

---

## Propagação — Longley-Rice ITM

**[10]** A. G. Longley & P. L. Rice,
*Prediction of Tropospheric Radio Transmission Loss over Irregular Terrain*.
ESSA Technical Report ERL 79-ITS 67, Institute for Telecommunication Sciences, 1968.
> Formulação original do ITM. Disponível via NTIA.

**[11]** G. A. Hufford, A. G. Longley & W. A. Kissick,
*A Guide to the Use of the ITS Irregular Terrain Model (Longley-Rice Method)*.
NTIA Report 82-100, 1982.
> Parâmetros de terreno (Δh), raio efetivo da Terra (k=4/3), variabilidade estatística.

**[12]** L. Boithias, *Radio Wave Propagation*.
McGraw-Hill, 1992. ISBN 978-0-07-006433-4.
> Atenuação de faca knife-edge J(ν) — aprovação de Boithias/Sadiku usada na implementação.

---

## Free-Space Path Loss e Link Budget

**[13]** H. T. Friis, "A Note on a Simple Transmission Formula",
*Proceedings of the IRE*, vol. 34, no. 5, pp. 254–256, May 1946.
DOI: 10.1109/JRPROC.1946.234568.
> Fórmula de Friis: fórmula base para FSPL e link budget.

**[14]** ITU-R P.525-4, *Calculation of Free-Space Attenuation*.
International Telecommunication Union, 2019.
> Padronização ITU da fórmula FSPL usada no cálculo de link budget.

---

## LoRa / LPWAN

**[15]** LoRa Alliance, *LoRaWAN Regional Parameters*, v1.0.3.
LoRa Alliance, 2018. Disponível em: https://lora-alliance.org/
> Parâmetros de frequência (915 MHz BR/AU, 868 MHz EU), sensibilidades por SF, EIRP máximo.

**[16]** A. F. Molisch, *Wireless Communications*, 2nd ed.
Wiley-IEEE Press, 2011. ISBN 978-0-470-74187-0.
> Link budget, fade margin, modelos de canal — capítulos 5 e 6.

---

## Ferramentas de referência externas

| Ferramenta | Uso | URL |
|---|---|---|
| splat! | ITM completo com DEM real | https://www.qsl.net/kd2bd/splat.html |
| NTIA/ITS ITM (C++) | Implementação de referência do ITM | https://github.com/NTIA/itm |
| 4nec2 | NEC-2 GUI com visualização 3D | https://www.qsl.net/4nec2/ |
| PyNEC | Wrapper Python para NEC-2 | https://pypi.org/project/PyNEC/ |
