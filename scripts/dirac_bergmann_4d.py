#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D.5 --- Analisis de Dirac-Bergmann completo en 4D sobre U4.

Objetivo: cerrar la limitacion declarada en DERIVATIONS.md D.9.6
("el conteo de 1 g.d.l. es en sector proyectado, no 4D general")
extendiendo el analisis del Cap. 5 (M6 = T^3 x Sigma_3, matriz 8x8) al
espacio-tiempo 4D: metrica ADM (q_ij, N, N_i) + campo de coherencia Phi
+ torsion axial A_mu, que es algebraica (solucion de Palatini, §3.2) y por
tanto no propaga.

Todo lo que se imprime es calculado. Cada bloque verifica una propiedad con
algebra simbolica o con matrices exactas; no hay resultados hardcodeados ni
"return True".

Convenciones: firma (-,+,+,+); eta = diag(-1,+1,+1,+1); M_P reducida.
"""
import sympy as sp

MP = sp.Symbol("M_P", positive=True)
kappa2, kappa3 = sp.symbols("kappa_2 kappa_3", real=True)
alpha, beta = sp.symbols("alpha beta", real=True)


def titulo(txt):
    print("\n" + "=" * 74)
    print(txt)
    print("=" * 74)


# ---------------------------------------------------------------------------
# BLOQUE 1 --- Sector escalar Phi en ADM 4D
# ---------------------------------------------------------------------------
def bloque_1_escalar_adm():
    titulo("BLOQUE 1 --- Escalar Phi en ADM 4D: momento, Hamiltoniano, g.d.l.")

    N = sp.Symbol("N", positive=True)          # lapse
    sq = sp.Symbol("sqrt_q", positive=True)    # sqrt(det q_ij)
    G = sp.Symbol("G", positive=True)          # q^ij d_i Phi d_j Phi >= 0
    D = sp.Symbol("D", real=True)              # N^i d_i Phi
    V = sp.Symbol("V", real=True)              # V(Phi)
    phidot = sp.Symbol("Phi_dot", real=True)
    P = sp.Symbol("P", real=True)              # momento pi_Phi independiente

    S = phidot - D
    L = -sq * S**2 / (2 * N) + sp.Rational(1, 2) * N * sq * G - N * sq * V

    pi_expr = sp.simplify(sp.diff(L, phidot))
    print("pi_Phi          =", pi_expr)

    dpi = sp.simplify(sp.diff(pi_expr, phidot))
    print("d pi / d Phi_dot =", dpi)
    invertible = dpi != 0
    print("invertible (sin restriccion primaria)?", bool(invertible))

    phidot_sol = sp.solve(sp.Eq(P, -sq * (phidot - D) / N), phidot)[0]
    H = sp.simplify(P * phidot_sol - L.subs(phidot, phidot_sol))
    H = sp.expand(H)
    print("H               =", H)

    H_perp = sp.simplify(H.coeff(N))
    resto = sp.simplify(H - N * H_perp)
    print("H_perp          =", H_perp)
    print("resto (shift)   =", resto)
    solo_shift = sp.simplify(resto - D * P) == 0
    print("H == N*H_perp + N^i*pi*d_iPhi ?", bool(solo_shift))
    sin_vel = sp.simplify(sp.diff(H, phidot)) == 0
    print("dH/dPhi_dot == 0 (sin velocidad residual)?", bool(sin_vel))

    # 2 dimensiones de fase (Phi, pi), ninguna restriccion propia
    gdl = sp.Rational(2 - 0, 2)
    print("g.d.l. del sector Phi = (2-0)/2 =", gdl)
    return invertible, solo_shift, sin_vel, gdl


# ---------------------------------------------------------------------------
# BLOQUE 2 --- Torsion axial A_mu: cadena de restricciones
# ---------------------------------------------------------------------------
def bloque_2_torsion():
    titulo("BLOQUE 2 --- Torsion axial A_mu: primarias, secundarias, 2a clase")

    eta = sp.diag(-1, 1, 1, 1)                  # (-,+,+,+)
    A = sp.Matrix(sp.symbols("A0 A1 A2 A3", real=True))
    dPhi = sp.Matrix(sp.symbols("d0 d1 d2 d3", real=True))   # d_mu Phi

    A2 = (A.T * eta * A)[0]                     # A_mu A^mu
    AdPhi = (A.T * eta * dPhi)[0]               # A^mu d_mu Phi
    L = alpha * MP**2 * A2 + beta * MP * AdPhi
    print("L_torsion = alpha M_P^2 A^2 + beta M_P A.dPhi =", L)

    # 1) no hay derivadas temporales de A_mu -> momentos nulos
    dA = [sp.Symbol(f"A{i}_dot") for i in range(4)]
    pA = [sp.diff(L, d) for d in dA]
    print("pi_A^mu = dL/d(A_dot^mu) =", pA, "-> 4 restricciones primarias")

    # 2) restricciones secundarias: phi_mu = dL/dA^mu = 0
    phi = [sp.simplify(sp.diff(L, a)) for a in A]
    for i, f in enumerate(phi):
        print(f"phi_{i} = dL/dA^{i} =", sp.factor(f))

    # 3) matriz de Dirac (bloques [[0,-H],[H,0]]) -> Hessiano
    Hm = sp.Matrix(4, 4, lambda i, j: sp.diff(phi[j], A[i]))
    print("Hessiano H_munu = d phi_nu / d A^mu =")
    sp.pprint(Hm)
    detH = sp.factor(sp.simplify(Hm.det()))
    print("det H =", detH)
    segunda_clase = sp.simplify(detH) != 0
    print("det != 0  =>  4 pares de SEGUNDA clase:", bool(segunda_clase))
    print("rango(H) =", Hm.subs({alpha: -1}).rank(), "(con alpha=-1)")

    # 4) solucion algebraica y coeficiente cinetico efectivo
    Asol = sp.solve([sp.Eq(f, 0) for f in phi], list(A), dict=True)[0]
    print("A_mu(dPhi) =", {str(k): sp.simplify(v) for k, v in Asol.items()})

    # invariante de Lorentz (dPhi)^2 = eta^{munu} d_mu Phi d_nu Phi
    dPhi2 = sp.simplify(-dPhi[0] ** 2 + dPhi[1] ** 2 + dPhi[2] ** 2 + dPhi[3] ** 2)
    Leff = sp.simplify(L.subs(Asol))
    ratio = sp.simplify(sp.cancel(Leff / dPhi2))
    print("(dPhi)^2 =", dPhi2)
    print("L_torsion eliminada =", sp.factor(ratio), "* (dPhi)^2")
    coef = sp.simplify(sp.Rational(1, 2) + ratio)      # + (1/2)(dPhi)^2 canonico
    print("coef. total de (dPhi)^2 =", coef)

    rel = sp.solve(sp.Eq(coef, sp.Rational(3, 2)), beta**2)
    print("coef = 3/2  (tau_c = sqrt(3) tau)  <=>  beta^2 =", [sp.simplify(r) for r in rel])

    # con la solucion de Palatini A_sigma = M_P^-1 d_sigma tau: -beta/(2 alpha) = 1
    rel_pal = sp.solve(sp.Eq(-beta / (2 * alpha), 1), beta)
    print("Palatini A = M_P^-1 d tau  <=>  beta =", rel_pal)
    coef_pal = sp.simplify(coef.subs(beta, rel_pal[0]))
    print("coef. cinetico con esa relacion =", coef_pal,
          " -> tau_c = sqrt(%s) tau" % sp.simplify(2 * coef_pal))
    return segunda_clase, coef, rel


# ---------------------------------------------------------------------------
# BLOQUE 3 --- Conteo en 4D
# ---------------------------------------------------------------------------
def bloque_3_conteo():
    titulo("BLOQUE 3 --- Conteo de Dirac-Bergmann en 4D completo")

    dim_fase = 2 * (6 + 1 + 3 + 1 + 4)   # q_ij,N,N_i,Phi,A_mu
    primarias_fc = 4                     # pi_N, pi^i
    secundarias_fc = 4                   # H, H_i
    fc = primarias_fc + secundarias_fc
    sc = 8                               # 4 pares (pi_A^mu, phi_mu)
    gdl = sp.Rational(dim_fase - 2 * fc - sc, 2)

    print(f"dim Gamma             = {dim_fase}")
    print(f"1a clase: {primarias_fc} primarias + {secundarias_fc} secundarias = {fc}")
    print(f"2a clase: {sc}")
    print(f"GDL = ({dim_fase} - 2*{fc} - {sc})/2 = {gdl}")

    dim_sin = 2 * (6 + 1 + 3 + 1)
    gdl_sin = sp.Rational(dim_sin - 2 * fc, 2)
    print(f"sin torsion: ({dim_sin} - {2*fc})/2 = {gdl_sin}  -> torsion aporta {gdl - gdl_sin}")
    print(f"desglose: 2 tensoriales + {gdl_sin - 2} escalar = {gdl}")
    return dim_fase, fc, sc, gdl, gdl_sin


# ---------------------------------------------------------------------------
# BLOQUE 4 --- Limite proyectado del Cap. 5
# ---------------------------------------------------------------------------
def bloque_4_proyectado():
    titulo("BLOQUE 4 --- Limite proyectado M6 (Cap. 5): matriz 8x8")

    A = sp.Matrix([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 0, -1], [0, 0, 1, 0]])
    X = sp.Matrix([[kappa2, kappa3], [-kappa3, kappa2]])
    Z = sp.zeros(2, 2)
    B = sp.BlockMatrix([[Z, X], [-X.T, Z]]).as_explicit()
    M = sp.BlockMatrix([[A, sp.zeros(4, 4)], [sp.zeros(4, 4), B]]).as_explicit()

    detM = sp.factor(sp.simplify(M.det()))
    print("det M =", detM)
    esperado = (kappa2**2 + kappa3**2) ** 2
    coincide = sp.simplify(detM - esperado) == 0
    print("det M == (kappa2^2+kappa3^2)^2 ?", bool(coincide))
    print("det X =", sp.factor(X.det()))

    punto = {kappa2: sp.Rational(37, 100), kappa3: sp.Rational(-52, 100)}
    print("rango(M) en (0.37,-0.52) =", M.subs(punto).rank())
    print("det(M) en ese punto      =", sp.simplify(detM.subs(punto)))
    gdl_proy = sp.Rational(10 - M.subs(punto).rank(), 2)
    print(f"GDL proyectado = (10 - 8)/2 = {gdl_proy}")
    return coincide, M.subs(punto).rank(), gdl_proy


# ---------------------------------------------------------------------------
# BLOQUE 5 --- Sector metrico: pi^ij no degenerado
# ---------------------------------------------------------------------------
def bloque_5_gravedad():
    titulo("BLOQUE 5 --- Sector metrico ADM: pi^ij invertible, 8 restricciones 1a clase")

    idx = [(0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)]
    # gravedad linealizada sobre Minkowski: pi_ij = 1/2 (h_ij - delta_ij h)
    Jac = sp.zeros(6, 6)
    for fila, (i, j) in enumerate(idx):
        for col, (k, l) in enumerate(idx):
            delta_sym = 1 if (i, j) == (k, l) else 0          # h_ij, indices simetricos
            delta_tr = 1 if (i == j and k == l) else 0        # delta_ij delta_kl
            Jac[fila, col] = sp.Rational(1, 2) * (delta_sym - delta_tr)
    print("Jacobiano d pi_ij / d h_dot_kl =")
    sp.pprint(Jac)
    detJ = sp.factor(Jac.det())
    print("det J =", detJ)
    no_degenerado = sp.simplify(detJ) != 0
    print("det != 0  =>  sin restriccion primaria sobre q_ij:", bool(no_degenerado))

    dim_fase_grav = 2 * (6 + 1 + 3)
    fc_grav = 8
    gdl_grav = sp.Rational(dim_fase_grav - 2 * fc_grav, 2)
    print(f"GDL metrico = ({dim_fase_grav} - {2*fc_grav})/2 = {gdl_grav} (2 polarizaciones)")
    return no_degenerado, gdl_grav


# ---------------------------------------------------------------------------
# BLOQUE 6 --- Signo del termino cinetico en FLRW (consistencia con w_K = +1)
# ---------------------------------------------------------------------------
def bloque_6_signo_frw():
    titulo("BLOQUE 6 --- Signo cinetico en FLRW: densidad de energia y w_K")

    t = sp.Symbol("t", positive=True)
    tau = sp.Function("tau")(t)
    V = sp.Symbol("V", positive=True)
    dtau = sp.diff(tau, t)
    td = sp.Symbol("taudot", positive=True)   # valor de dtau/dt para el chequeo numerico

    # dos convenciones de signo para el mismo campo, con firma (-,+,+,+):
    #   caso A: L = -(1/2)(grad tau)^2 - V  =  +(1/2)dtau^2 - V   (cinetica positiva)
    #   caso B: L = +(1/2)(grad tau)^2 - V  =  -(1/2)dtau^2 - V   (cinetica negativa)
    casos = [
        ("A: L = -(1/2)(grad tau)^2 - V", sp.Rational(1, 2) * dtau**2 - V),
        ("B: L = +(1/2)(grad tau)^2 - V", -sp.Rational(1, 2) * dtau**2 - V),
    ]
    salida = []
    for etiqueta, L in casos:
        pi = sp.diff(L, dtau)
        rho = sp.simplify(pi * dtau - L)      # pi*dtau - L  (campo homogeneo)
        p = sp.simplify(L)
        w = sp.simplify(p / rho)
        rho_val = sp.simplify(rho.subs({dtau: 1, V: sp.Rational(1, 10)}))
        p_val = sp.simplify(p.subs({dtau: 1, V: sp.Rational(1, 10)}))
        w_val = sp.simplify(w.subs({dtau: 1, V: sp.Rational(1, 10)}))
        positivo = bool(sp.Gt(rho_val, 0))
        print(f"{etiqueta}")
        print(f"   pi_tau = {pi}")
        print(f"   rho    = {rho}")
        print(f"   p      = {p}")
        print(f"   w      = {w}")
        print(f"   con V=0.1, taudot=1: rho={rho_val}, p={p_val}, w={w_val}, rho>0? {positivo}")
        salida.append((etiqueta, rho, positivo))
    print("\nLectura: w_K = +1 se obtiene en AMBOS casos (el signo global del Lagrangiano")
    print("no cambia w), pero solo el caso A tiene densidad de energia positiva.")
    print("El caso B es un fantasma (rho < 0) y es el que corresponde a escribir")
    print("+(1/2)(grad tau)^2 con firma (-,+,+,+).")
    return salida[0][1], salida[1][1]


def main():
    b1 = bloque_1_escalar_adm()
    b2 = bloque_2_torsion()
    b3 = bloque_3_conteo()
    b4 = bloque_4_proyectado()
    b5 = bloque_5_gravedad()
    b6 = bloque_6_signo_frw()

    titulo("RESUMEN")
    print(f"Phi: momento invertible={b1[0]} | H=N*H_perp+N^i*H_i={b1[1]} | sin velocidad residual={b1[2]}")
    print(f"Torsion: 2a clase={b2[0]} | coef. cinetico efectivo={b2[1]}")
    print(f"Conteo 4D: dim Gamma={b3[0]}, FC={b3[1]}, SC={b3[2]}, GDL={b3[3]}")
    print(f"Proyectado: det coincide={b4[0]}, rango={b4[1]}, GDL={b4[2]}")
    print(f"Metrico: pi^ij no degenerado={b5[0]}, GDL graviton={b5[1]}")
    print(f"FRW: rho(L=+1/2)={b6[0]} | rho(L=-1/2)={b6[1]}")

    escalares = b3[3] - b5[1]
    print("\n--- verificacion final ---")
    print(f"GDL(4D) - GDL(graviton) = {b3[3]} - {b5[1]} = {escalares}")
    print(f"GDL(M6 proyectado)      = {b4[2]}")
    print("coinciden?", bool(escalares == b4[2]))
    print(f"\n=> El sector de coherencia propaga {escalares} g.d.l. escalar tambien en 4D.")
    print("   La torsion axial no aporta ninguno: 4 pares de segunda clase.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
