#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba de la hipotesis "Escalera Aurea" para beta_0 (Cap. 10).

Hipotesis: las masas de los tres estados vector-like no se ajustan a mano;
se derivan de la escalera geometrica m_n = M_P * phi^(-n), con phi el numero
aureo y n entero. Se calcula la correccion de umbral

    delta A = sum_i  N_c^i Q_i^2 y_i^2/(4 pi^2) * ln(M_i / mu_ex)

con y_i = 2, mu_ex = T_ex = 1e16 GeV (los valores de la tesis), y

    beta_0 = 0.20906 * (5/3 + delta A)   [grados]

Se compara con beta_0 = 0.3803 deg.

Bloques:
  B1  tabla para n = 8..12 con los tres estados en el mismo nivel n
  B2  criterio del 2%
  B3  barrido de las 125 combinaciones (n_u, n_d, n_e) en 8..12: cuantas caen
      en la ventana del 2% (test de "look-elsewhere")
  B4  sensibilidad a mu_ex = T_ex (que solo se conoce a factor ~2)
  B5  veredicto

Todo calculado; nada postulado.
"""
import sympy as sp

# --- constantes y parametros declarados en la tesis ------------------------
MP = sp.Float("2.435e18")          # GeV, M_P reducida
PHI = (1 + sp.sqrt(5)) / 2         # numero aureo
MU = sp.Float("1e16")              # mu_ex = T_ex
Y = sp.Float("2.0")                # Yukawa VL declarado
A0 = sp.Rational(5, 3)             # u,d: 3(2/3)^2 + 3(1/3)^2
COEF = sp.Float("0.20906")         # alpha_em/2 en grados
BETA_REF = sp.Float("0.3803")      # valor reportado

ESTADOS = [("VL-u", 3, sp.Rational(2, 3)), ("VL-d", 3, sp.Rational(1, 3)), ("VL-e", 1, -1)]


def titulo(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


def delta_a(M, mu=MU, y=Y):
    """Correccion de umbral al coeficiente anomalo A."""
    return sum(sp.N(nc * q**2 * y**2 / (4 * sp.pi**2) * sp.log(M / mu), 8) for _, nc, q in ESTADOS)


def beta0(dA):
    return sp.N(COEF * (A0 + dA), 8)


def dev(beta):
    return sp.N((beta - BETA_REF) / BETA_REF * 100, 6)


def masa(n):
    return sp.N(MP * PHI ** (-n), 8)


# ---------------------------------------------------------------------------
def bloque_1_tabla():
    titulo("BLOQUE 1 --- Escalera aurea: los tres estados VL en el nivel n")
    print("phi =", sp.N(PHI, 8), " | M_P = 2.435e18 GeV | mu_ex = 1e16 GeV | y = 2")
    print()
    print(f"{'n':>2} {'M_n [GeV]':>12} {'dA_u':>8} {'dA_d':>8} {'dA_e':>8} "
          f"{'dA':>8} {'A':>8} {'beta_0 [deg]':>13} {'dev':>7}")
    print("-" * 78)
    filas = []
    for n in range(8, 13):
        M = masa(n)
        partes = [sp.N(nc * q**2 * Y**2 / (4 * sp.pi**2) * sp.log(M / MU), 6) for _, nc, q in ESTADOS]
        dA = sum(partes)
        A = sp.N(A0 + dA, 6)
        b = beta0(dA)
        d = dev(b)
        filas.append((n, M, partes, dA, A, b, d))
        print(f"{n:>2} {float(M):>12.4e} {float(partes[0]):>8.4f} {float(partes[1]):>8.4f} "
              f"{float(partes[2]):>8.4f} {float(dA):>8.4f} {float(A):>8.4f} "
              f"{float(b):>13.5f} {float(d):>6.2f}%")
    return filas


def bloque_2_criterio(filas):
    titulo("BLOQUE 2 --- Criterio: |beta_0 - 0.3803| / 0.3803 < 2 %")
    pasan = [(n, b, d) for n, _, _, _, _, b, d in filas if abs(d) < 2]
    for n, b, d in pasan:
        print(f"  n = {n}: beta_0 = {float(b):.5f} deg, desviacion = {float(d):+.2f} %  -> PASA")
    if not pasan:
        print("  ningun n pasa el criterio del 2 %.")
    # cual es el n mas cercano aunque no pase
    mejor = min(filas, key=lambda f: abs(f[6]))
    print(f"\n  mas cercano: n = {mejor[0]}, beta_0 = {float(mejor[5]):.5f}, "
          f"desviacion = {float(mejor[6]):+.2f} %")
    return pasan


def bloque_3_barrido():
    titulo("BLOQUE 3 --- Barrido de las 125 combinaciones (n_u, n_d, n_e)")
    niveles = range(8, 13)
    resultados = []
    for nu in niveles:
        for nd in niveles:
            for ne in niveles:
                dA = (sp.N(3 * sp.Rational(4, 9) * Y**2 / (4 * sp.pi**2) * sp.log(masa(nu) / MU), 8)
                      + sp.N(3 * sp.Rational(1, 9) * Y**2 / (4 * sp.pi**2) * sp.log(masa(nd) / MU), 8)
                      + sp.N(1 * Y**2 / (4 * sp.pi**2) * sp.log(masa(ne) / MU), 8))
                resultados.append(((nu, nd, ne), beta0(dA), dev(beta0(dA))))

    ventana = [r for r in resultados if abs(r[2]) < 2]
    print(f"combinaciones totales           : {len(resultados)}")
    print(f"dentro de +-2 % de 0.3803       : {len(ventana)}  ({100*len(ventana)/len(resultados):.1f} %)")
    mejor = min(resultados, key=lambda r: abs(r[2]))
    print(f"mejor combinacion               : (n_u,n_d,n_e) = {mejor[0]}, "
          f"beta_0 = {float(mejor[1]):.5f}, desv = {float(mejor[2]):+.2f} %")
    print("\nlas 6 combinaciones mas cercanas:")
    for (comb, b, d) in sorted(resultados, key=lambda r: abs(r[2]))[:6]:
        print(f"   {comb}  beta_0 = {float(b):.5f}  desv = {float(d):+.2f} %")
    return resultados, ventana


def bloque_4_mu():
    titulo("BLOQUE 4 --- Sensibilidad a mu_ex = T_ex (conocido a factor ~2)")
    print("n = 10 en los tres estados; se varia mu_ex:")
    print(f"{'mu_ex [GeV]':>12} {'dA':>8} {'beta_0 [deg]':>13} {'dev':>8}")
    salida = []
    for mu in ["5e15", "1e16", "2e16", "4e16"]:
        dA = sum(sp.N(nc * q**2 * Y**2 / (4 * sp.pi**2) * sp.log(masa(10) / sp.Float(mu)), 8)
                 for _, nc, q in ESTADOS)
        b = beta0(dA)
        salida.append((mu, dA, b, dev(b)))
        print(f"{mu:>12} {float(dA):>8.4f} {float(b):>13.5f} {float(dev(b)):>7.2f}%")
    print("\n=> un factor 2 en T_ex mueve beta_0 entre",
          f"{float(salida[0][2]):.3f} y {float(salida[-1][2]):.3f} grados,",
          "es decir ~", f"{abs(float(salida[-1][3] - salida[0][3])):.0f} % de rango.")
    return salida


def main():
    filas = bloque_1_tabla()
    pasan = bloque_2_criterio(filas)
    res, ventana = bloque_3_barrido()
    mu = bloque_4_mu()

    titulo("VEREDICTO")
    print(f"1) n = 10 con los tres estados en el mismo nivel da beta_0 = "
          f"{float(filas[2][5]):.5f} deg (desv {float(filas[2][6]):+.2f} %):")
    print("   ", "PASA el criterio del 2 %." if abs(filas[2][6]) < 2 else "NO pasa el criterio.")
    print("2) pero el barrido muestra que", len(ventana), "de 125 combinaciones discretas",
          f"({100*len(ventana)/125:.0f} %) caen en esa misma ventana.")
    print("3) y un factor 2 en mu_ex = T_ex mueve beta_0 ~",
          f"{abs(float(mu[-1][3] - mu[0][3])):.0f} %,",
          "mas que la ventana del 2 %.")
    print("\nCONCLUSION: la escalera NO es una derivacion de beta_0 = 0.3803.")
    print("El acierto de n = 10 es (a) marginal (1.8 %), (b) facil de reproducir por")
    print("combinatoria discreta, y (c) no robusto frente a T_ex. Es una eleccion")
    print("motivada, no una prediccion. Si se quiere usar, hay que declararla [P]")
    print("con T_ex fijado por otro sector.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
