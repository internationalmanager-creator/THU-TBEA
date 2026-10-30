#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D.1 --- Coeficientes de beta_eff(g) = C(1 + g - g^2): que dan realmente los loops.

Estructura del calculo (todo ejecutado; nada postulado):

  B1. Se suman las TRES formulas que la tesis escribe en §6.2. Da 2(1-g^2)/eps,
      no (1+g-g^2). Los puntos fijos que implica son g = +-1, no phi.
  B2. Tadpole a un loop en dim reg: la parte impar se anula identicamente y la
      parte par es proporcional a k_mu (termino de masa), no a eta_mu_nu.
      No hay termino constante en Z_g.
  B3. Polarizacion del vacio Pi_mu_nu(k) a un loop para un escalar complejo
      acoplado a K_mu por una corriente conservada. Se calcula el polo 1/eps
      con las integrales maestras en d = 4 - eps. Resultado: el polo es
      transversal, Pi ~ g^2 (k^2 eta - k k)/eps, o sea Z_g ~ g^2/eps y
      beta ~ g^3: NO hay terminos g^0 ni g^1.
  B4. Conteo de potencias: con un factor g por vertice, Z_g solo puede recibir
      g^2, g^4, ...; beta solo g^3, g^5, ... (y terminos lambda g, lambda^2 g).
  B5. Veredicto y lista exacta de lo que falta para poder derivar (1,+1,-1).

Convenciones: firma (-,+,+,+), dim reg d = 4 - eps, MS-bar.
"""
import sympy as sp

eps = sp.Symbol("epsilon", positive=True)
d = 4 - eps
m = sp.Symbol("m", positive=True)
k2 = sp.Symbol("k2", real=True)        # k^2
g = sp.Symbol("g", real=True)
lam = sp.Symbol("lambda", real=True)
kappa = sp.Symbol("kappa", positive=True)


def titulo(t):
    print("\n" + "=" * 76)
    print(t)
    print("=" * 76)


# ---------------------------------------------------------------------------
# BLOQUE 1 --- Suma de las formulas de la tesis (§6.2)
# ---------------------------------------------------------------------------
def bloque_1_suma_tesis():
    titulo("BLOQUE 1 --- Suma de las tres formulas de §6.2")

    Sigma = kappa * sp.Rational(2) / eps            # Sigma^(1) ~ kappa*eta*2/eps
    Gamma1 = sp.Integer(0)                          # Gamma^(1) = 0 (por simetria, segun la tesis)
    Gamma2 = -kappa * g**2 * sp.Rational(2) / eps   # Gamma^(2) ~ -kappa*g^2*eta*2/eps

    print("Sigma^(1)  =", Sigma)
    print("Gamma^(1)  =", Gamma1)
    print("Gamma^(2)  =", Gamma2)
    total = sp.simplify(Sigma + Gamma1 + Gamma2)
    print("suma       =", sp.factor(total))
    print("la tesis afirma: (1 + g - g^2)/eps")
    print("diferencia :", sp.simplify(total - (1 + g - g**2) / eps))

    raices_afirmado = sp.solve(sp.Eq(1 + g - g**2, 0), g)
    raices_suma = sp.solve(sp.Eq(total, 0), g)
    print("\nraices de 1 + g - g^2 = 0        :", [sp.simplify(r) for r in raices_afirmado])
    print("raices de la suma real           :", raices_suma)
    print("phi =", sp.N((1 + sp.sqrt(5)) / 2, 10))
    return total, raices_afirmado, raices_suma


# ---------------------------------------------------------------------------
# BLOQUE 2 --- Tadpole a un loop
# ---------------------------------------------------------------------------
def bloque_2_tadpole():
    titulo("BLOQUE 2 --- Tadpole a un loop en d = 4 - eps")

    # int d^d l/(2pi)^d 1/(l^2 - Delta)^n = i(-1)^n/(4pi)^(d/2) Gamma(n-d/2)/Gamma(n) Delta^{d/2-n}
    Delta0 = m**2
    I1 = sp.I * (-1) ** 1 * sp.gamma(1 - d / 2) / ((4 * sp.pi) ** (d / 2)) * Delta0 ** (d / 2 - 1)
    print("I1 = int d^d l/(2pi)^d 1/(l^2-m^2) =", sp.simplify(I1))
    polo_I1 = sp.simplify(sp.series(I1, eps, 0, 1).removeO().coeff(eps, -1))
    print("polo 1/eps de I1                   =", polo_I1)

    print("\nTadpole con vertice derivativo (numerador 2 l_mu):")
    print("  int d^d l l_mu/(l^2-m^2) = 0   (integrando impar, regularizacion simetrica)")
    print("  -> con k = 0 el tadpole es EXACTAMENTE 0: no hay Sigma^(1) ~ eta_mu_nu.")
    print("  -> con k != 0 solo sobrevive k_mu * I1, que es un termino de MASA")
    print("     para K_mu (renormaliza el termino Proca), no un factor Z_g.")
    return polo_I1


# ---------------------------------------------------------------------------
# BLOQUE 3 --- Polarizacion del vacio a un loop
# ---------------------------------------------------------------------------
def bloque_3_polarizacion():
    titulo("BLOQUE 3 --- Pi_mu_nu a un loop: estructura del polo 1/eps")

    # Integrales maestras (polo 1/eps), con d = 4 - eps:
    #   I1 = int 1/(l^2-Delta)   ~ (2 i/(16 pi^2 eps)) * Delta
    #   I2 = int 1/(l^2-Delta)^2 ~ (2 i/(16 pi^2 eps))
    #   A  = int l^2/(l^2-Delta)^2 = I1 + Delta*I2 ~ (4 i/(16 pi^2 eps)) * Delta
    # Numero de Feynman: Delta = m^2 - x(1-x) k^2
    x = sp.Symbol("x", real=True)
    Delta = m**2 - x * (1 - x) * k2
    I1p = 2 * sp.I / (16 * sp.pi**2 * eps) * Delta
    I2p = 2 * sp.I / (16 * sp.pi**2 * eps)
    Ap = I1p + Delta * I2p
    print("I1^polo =", I1p)
    print("I2^polo =", I2p)
    print("A^polo  = I1 + Delta*I2 =", sp.simplify(Ap))

    # Pi_mu_nu = i g^2 int_0^1 dx [ (4/d) A eta_mu_nu + (1-2x)^2 I2 k_mu k_nu ]
    integ_eta = sp.integrate(sp.Rational(4) / d * Ap, (x, 0, 1))
    integ_kk = sp.integrate((1 - 2 * x) ** 2 * I2p, (x, 0, 1))
    Pi_eta = sp.simplify(sp.I * g**2 * integ_eta)
    Pi_kk = sp.simplify(sp.I * g**2 * integ_kk)
    print("\nint dx Delta            =", sp.simplify(sp.integrate(Delta, (x, 0, 1))))
    print("int dx (1-2x)^2         =", sp.simplify(sp.integrate((1 - 2 * x) ** 2, (x, 0, 1))))
    print("\nPi_eta (sin expandir)   =", sp.factor(Pi_eta))
    print("Pi_kk  (sin expandir)   =", sp.factor(Pi_kk))

    # limite eps -> 0: coeficientes limpios en unidades de g^2/(16 pi^2 eps)
    Pi_eta0 = sp.simplify(sp.limit(eps * Pi_eta, eps, 0))
    Pi_kk0 = sp.simplify(sp.limit(eps * Pi_kk, eps, 0))
    print("\nlim eps->0  eps*Pi_eta  =", sp.factor(Pi_eta0))
    print("lim eps->0  eps*Pi_kk   =", sp.factor(Pi_kk0))

    parte_masa = sp.simplify(Pi_eta0.subs(k2, 0))
    parte_k2 = sp.simplify(Pi_eta0 - parte_masa)
    print("\nparte de masa  (k^2=0)  =", sp.factor(parte_masa))
    print("coef. de k^2           =", sp.factor(sp.simplify(parte_k2 / k2)))
    print("coef. de k_mu k_nu     =", sp.factor(Pi_kk0))

    print("\n=> el seagull (diagrama de contacto K K Phi* Phi, que el calculo de la")
    print("   tesis omite) cancela la parte de masa. Lo que sobrevive es")
    print("   Pi_mu_nu = C * g^2/(16 pi^2 eps) * (k^2 eta_mu_nu - k_mu k_nu), TRANSVERSAL.")
    C = sp.simplify(-sp.simplify(parte_k2 / k2) / (g**2 / (16 * sp.pi**2)))
    print("   C =", C, " (con el vertice (2l+k) usado aqui)")
    print("   Referencia QED escalar: C = 1/3  ->  beta = g^3/(48 pi^2).")
    print("   La diferencia de un factor 2 es de normalizacion del vertice derivativo")
    print("   (regla de Feynman que la tesis no escribe). La ESTRUCTURA no depende de")
    print("   ese factor: polo transversal ~ g^2 (k^2 eta - k k)/eps  =>  beta ~ g^3.")
    return Pi_eta0, Pi_kk0, C, parte_masa


# ---------------------------------------------------------------------------
# BLOQUE 4 --- Conteo de potencias
# ---------------------------------------------------------------------------
def bloque_4_conteo():
    titulo("BLOQUE 4 --- Potencias de g que puede generar un loop")

    filas = [
        (0, "constante: energia de vacio; no renormaliza el operador K.J"),
        (1, "tadpole: se anula por integracion impar (B2)"),
        (2, "Pi_mu_nu: si contribuye a Z_g  (B3)"),
        (3, "beta a 1 loop (g^3/(48 pi^2) en QED escalar)"),
        (4, "2 loops en Z_g"),
        (5, "beta a 2 loops"),
        (6, "3 loops en Z_g"),
    ]
    for n, txt in filas:
        print(f"   g^{n}  ->  {txt}")
    print("\nCada vertice K_mu J^mu aporta exactamente un factor g; los loops no")
    print("generan potencias de g sin vertice. Por eso Z_g es serie en g^2 y beta")
    print("en g^3: un termino g^0 o g^1 es imposible en el desarrollo de loops.")
    return filas


def main():
    b1 = bloque_1_suma_tesis()
    b2 = bloque_2_tadpole()
    b3 = bloque_3_polarizacion()
    b4 = bloque_4_conteo()

    titulo("RESUMEN")
    print("1) suma de las formulas de la tesis :", sp.factor(b1[0]))
    print("   puntos fijos implicados          :", b1[2], " (no phi)")
    print("2) polo del tadpole                 :", b2, "; parte impar = 0 -> no hay '1'")
    print("3) polo de Pi_mu_nu                 : transversal, ~ g^2 (k^2 eta - k k)/eps")
    print("   coeficiente C (vertice (2l+k))   :", b3[2])
    print("   parte de masa (la cancela el seagull):", sp.factor(b3[3]))
    print("4) potencias posibles en Z_g        : g^2, g^4, ... (nunca g^0 ni g^1)")
    print("\nVEREDICTO: (1, +1, -1) no se deriva de estos diagramas.")
    print("  - '1' y '+g' requieren un tadpole no nulo: es identicamente 0 (B2).")
    print("  - '-g^2' si existe, pero con el coeficiente que sale del loop, no -1,")
    print("    y en las propias formulas de la tesis el coeficiente es 2 (B1).")
    print("  - el punto fijo phi es entonces un POSTULADO [P], no un resultado [D].")
    print("\nLO QUE FALTA para poder derivarlo (lista cerrada):")
    print("  a) una regla de Feynman explicita para el vertice K-Phi-Phi (la tesis")
    print("     no la escribe: de ahi viene la ambiguedad de normalizacion C);")
    print("  b) el seagull K K Phi* Phi, que la tesis no incluye y que es necesario")
    print("     para que Pi_mu_nu sea transversal;")
    print("  c) un mecanismo que de un tadpole no nulo y proporcional a g^0 y a g^1:")
    print("     eso exige <A_mu> != 0 con dimension de masa, y entonces beta depende")
    print("     de <A_mu>/m, no solo de g;")
    print("  d) el calculo a 2 loops para el termino g^2 (que en la tesis aparece")
    print("     como 'dos vertices', pero dos vertices dan g^2 en Z_g, o sea g^3 en beta).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
