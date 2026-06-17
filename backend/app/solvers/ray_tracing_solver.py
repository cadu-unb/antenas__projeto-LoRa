# Ray Tracing Solver — stub arquitetural
#
# Implementação futura. Requer modelo 3D da cena (edifícios, árvores, terreno)
# e motor de traçado de raios (ex: Embree, NVIDIA OptiX, PyEmbree).
#
# Método:
#   Para cada par tx/rx, traçar N raios; somar contribuições de
#   reflexão (coef. Fresnel), difração (UTD) e transmissão (perda por material).
#
# Limitações sem modelo 3D:
#   Resultado seria equivalente a FSPL — sem vantagem sobre solvers existentes.
#   Fora do escopo do MVP.
#
# Referência:
#   McNamara, Pistorius & Malherbe, "Introduction to the Uniform
#   Geometrical Theory of Diffraction", Artech House, 1990.
