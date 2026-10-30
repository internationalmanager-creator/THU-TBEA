#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D.3 --- beta_0 = 0.3803 deg desde el acoplamiento pseudoescalar-foton.

QUE SE CALCULA AQUI (todo ejecutado):
  B1. La conversion rad -> grados: 0.20906 = (alpha_em/2)*(180/pi). Se verifica
      numericamente y se reproduce beta_0 = 0.20906 * A para A = 5/3 y 1.819.
  B2. El coeficiente anomalo A = sum_i N_c Q_i^2 para los espectros declarados
      (doblete u,d; con leptones; con el termino hadronico -1.92 de un axion
      de QCD). Se compara el beta_0 que da cada uno.
  B3. La rotacion de la polarizacion: derivacion simbolica de la relacion de
      dispersion para las dos helicidades circulares en un fondo a(t) con
      L_int = (1/4) g a F F~, hasta O(g). Se obtiene omega_+- = k -+ g adot/2
      y beta = (1/2) g Delta a.
  B4. Las correcciones de umbral: delta A_i = N_c Q^2 y^2/(4 pi^2) ln(M_i/mu),
      con los numeros de la tesis; se verifica 0.090+0.028+0.034 = 0.152 y se
      cuantifica la degeneracion (cuanto hay que mover las masas / el Yukawa
      para cambiar beta_0).
  B5. Veredicto: que esta derivado, que esta postulado, que falta.

NO se deriva aqui el coeficiente de la anomalia ABJ desde el diagrama triangulo:
se usa el resultado estandar y se verifica el factor de grupo. Eso se declara.
"""
import sympy as sp

alpha_em = 1 / sp.Float("137.035999")
grados = 180 / sp.pi


def titulo(t):
    print("\n" + "=" * 76)
    print(t)
    print("=" * 76)


# ---------------------------------------------------------------------------
# BLOQUE 1 --- De radianes a grados y reproduccion de beta_0
# ---------------------------------------------------------------------------
def bloque_1_conversion():
    titulo("BLOQUE 1 --- Conversion 0.20906 y reproduccion de beta_0")

    coef = sp.N(alpha_em / 2 * grados, 8)
    print("alpha_em                =", sp.N(alpha_em, 8))
    print("(alpha_em/2)*(180/pi)   =", coef, " grados")
    dif_rel = abs(float(coef) - 0.20906) / 0.20906
    print("valor usado en la tesis = 0.20906  -> dif. relativa =", f"{dif_rel:.2e}",
          " (coincide a 4 cifras:", dif_rel < 1e-4, ")")
    print("  nota: el valor exacto es 0.209054; 0.20906 esta redondeado al alza en la")
    print("  quinta cifra. El efecto en beta_0 es ~3e-5 grados: despreciable.")

    A0 = sp.Rational(5, 3)
    A = sp.Float("1.819")
    print("\nbeta_0(A=5/3)   = 0.20906 * 5/3   =", sp.N(coef * A0, 6), "grados")
    print("beta_0(A=1.819) = 0.20906 * 1.819 =", sp.N(coef * A, 6), "grados")
    print("valor reportado = 0.3803 grados  -> coincide:",
          abs(float(sp.N(coef * A)) - 0.3803) < 1e-4)

    # A que hay que llegar para beta_0 = 0.3803 exacto
    A_necesario = sp.N(sp.Float("0.3803") / coef, 6)
    print("\nA necesario para beta_0 = 0.3803 :", A_necesario, " (la tesis usa 1.819)")
    return coef, A0, A


# ---------------------------------------------------------------------------
# BLOQUE 2 --- Coeficiente anomalo A
# ---------------------------------------------------------------------------
def bloque_2_A():
    titulo("BLOQUE 2 --- Coeficiente anomalo A = sum N_c Q^2")

    espectros = {
        "doblete u,d (declarado)": [(3, sp.Rational(2, 3)), (3, sp.Rational(1, 3))],
        "u,d + electron": [(3, sp.Rational(2, 3)), (3, sp.Rational(1, 3)), (1, -1)],
    }
    res = {}
    for nombre, ferm in espectros.items():
        A = sum(nc * q**2 for nc, q in ferm)
        res[nombre] = A
        print(f"{nombre:28s}: A = {A} = {sp.N(A, 6)}")
    print("\nnota: la tesis solo declara el doblete u,d, por eso A_0 = 5/3.")
    print("Si el electron tuviera la misma carga PQ, A_0 seria 8/3 (beta_0 = 0.558 deg).")

    # termino hadronico estandar de un axion de QCD (mezcla con pi0, eta)
    A_qcd = sp.Rational(5, 3) - sp.Float("1.92")
    res["con -1.92 (axion de QCD)"] = A_qcd
    print(f"\ncon el termino hadronico -1.92: A = {sp.N(A_qcd, 5)}")
    print("  -> beta_0 = 0.20906 * A =", sp.N(0.20906 * A_qcd, 5), " grados (SIGNO OPUESTO)")
    return res


# ---------------------------------------------------------------------------
# BLOQUE 3 --- Rotacion de la polarizacion desde L_int = (1/4) g a F F~
# ---------------------------------------------------------------------------
def eps_up(idx):
    """epsilon^{mu nu rho sigma} con eps^{0123} = +1 (indices arriba)."""
    if len(set(idx)) < 4:
        return 0
    perm = list(idx)
    sign = 1
    for i in range(4):
        for j in range(i + 1, 4):
            if perm[i] > perm[j]:
                sign = -sign
    return sign


def bloque_3_rotacion():
    titulo("BLOQUE 3 --- Dispersion de las helicidades y beta = (1/2) g Delta a")

    w, k, g, adot = sp.symbols("omega k g adot", real=True)
    ex, ey = sp.symbols("eps_x eps_y", real=True)

    # A_mu = (0, eps_x, eps_y, 0) e^{i(kz - omega t)}
    # F_{mu nu} no nulo:
    F = {}
    F[(0, 1)] = -sp.I * w * ex
    F[(1, 0)] = sp.I * w * ex
    F[(0, 2)] = -sp.I * w * ey
    F[(2, 0)] = sp.I * w * ey
    F[(1, 3)] = -sp.I * k * ex
    F[(3, 1)] = sp.I * k * ex
    F[(2, 3)] = -sp.I * k * ey
    F[(3, 2)] = sp.I * k * ey
    print("F_01 =", F[(0, 1)], " | F_02 =", F[(0, 2)])
    print("F_13 =", F[(1, 3)], " | F_23 =", F[(2, 3)])

    def Ft(mu, nu):
        return sp.Rational(1, 2) * sum(
            eps_up((mu, nu, r, s)) * F.get((r, s), 0) for r in range(4) for s in range(4)
        )

    print("\nF~^{01} =", sp.simplify(Ft(0, 1)))
    print("F~^{02} =", sp.simplify(Ft(0, 2)))

    # EoM linealizada:  -i k_mu F^{mu nu} - g adot F~^{0 nu} = 0
    # F^{mu nu} = eta^{mu a} eta^{nu b} F_{a b}, con eta = diag(-1,+1,+1,+1):
    # los componentes con un indice temporal cambian de signo.
    eta = [-1, 1, 1, 1]

    def Fup(mu, nu):
        return eta[mu] * eta[nu] * F.get((mu, nu), 0)

    def eom(nu):
        lhs = -sp.I * ((-w) * Fup(0, nu) + k * Fup(3, nu))
        return sp.simplify(lhs - g * adot * Ft(0, nu))

    e1 = sp.simplify(eom(1))
    e2 = sp.simplify(eom(2))
    print("\nEoM nu=1:", sp.simplify(e1))
    print("EoM nu=2:", sp.simplify(e2))

    Mmat = sp.Matrix([[sp.simplify(e1.coeff(ex)), sp.simplify(e1.coeff(ey))],
                      [sp.simplify(e2.coeff(ex)), sp.simplify(e2.coeff(ey))]])
    det = sp.simplify(Mmat.det())
    print("\nmatriz 2x2 =\n", Mmat)
    print("det =", sp.factor(det))

    # dispersion: w^2 = k^2 -+ g adot k
    sol = sp.solve(sp.Eq(det, 0), w**2)
    print("soluciones w^2 =", [sp.factor(s) for s in sol])

    # a primer orden en g: w_+- = k -+ g adot/2
    wp = sp.series(sp.sqrt(sol[0]).subs(k, sp.Symbol("k", positive=True)), g, 0, 2).removeO()
    wm = sp.series(sp.sqrt(sol[1]).subs(k, sp.Symbol("k", positive=True)), g, 0, 2).removeO()
    print("\nw_+ =", sp.simplify(wp))
    print("w_- =", sp.simplify(wm))
    dw = sp.simplify(wm - wp)
    print("w_- - w_+ =", dw)

    # fase acumulada en un intervalo T con adot constante: Delta phi = |dw| T = g Delta a
    T = sp.Symbol("T", positive=True)
    dphi = sp.simplify(dw * T)
    print("Delta phi =", dphi, " = g * (adot*T) = g * Delta a")
    beta = sp.simplify(dphi / 2)
    print("\nbeta = Delta phi / 2 =", beta, "  ->  beta = (1/2) g Delta a  [confirmado]")
    return beta


# ---------------------------------------------------------------------------
# BLOQUE 4 --- Correcciones de umbral y su degeneracion
# ---------------------------------------------------------------------------
def bloque_4_umbral():
    titulo("BLOQUE 4 --- Umbrales VL: 0.152 y cuanto esta ajustado")

    mu = sp.Float("1e16")           # T_ex
    y = sp.Float("2.0")
    estados = [
        ("VL-u", 3, sp.Rational(2, 3), sp.Float("1.94e16"), sp.Float("0.090")),
        ("VL-d", 3, sp.Rational(1, 3), sp.Float("2.30e16"), sp.Float("0.028")),
        ("VL-e", 1, -sp.Integer(1), sp.Float("1.40e16"), sp.Float("0.034")),
    ]
    total = 0
    for nombre, nc, q, M, declarado in estados:
        dA = sp.N(nc * q**2 * y**2 / (4 * sp.pi**2) * sp.log(M / mu), 5)
        total += dA
        print(f"{nombre}: N_c Q^2 = {sp.N(nc*q**2,4):5}, M = {M:.3g} GeV, "
              f"delta A = {dA} (tesis: {declarado})")
    print("\nsuma delta A =", sp.N(total, 5), " (tesis: 0.152)")
    print("A = 5/3 +", sp.N(total, 5), "=", sp.N(sp.Rational(5, 3) + total, 6))
    print("beta_0 =", sp.N(0.20906 * (sp.Rational(5, 3) + total), 6), "grados")

    # sensibilidad: d deltaA / d ln M_i
    print("\nsensibilidad (coef. de ln M_i), por estado:")
    for nombre, nc, q, M, _ in estados:
        print(f"  {nombre}: {sp.N(nc*q**2*y**2/(4*sp.pi**2), 4)}")

    # cuanto hay que mover las masas para cambiar beta_0 un 5%
    der = sum(sp.N(nc * q**2 * y**2 / (4 * sp.pi**2), 6) for _, nc, q, _, _ in estados)
    print("\ndelta A por e-fold comun en las masas =", sp.N(der, 5))
    print("=> un factor e en todas las masas mueve beta_0 de 0.3803 a",
          sp.N(0.20906 * (sp.Rational(5, 3) + total + der), 5), "grados")
    print("   es decir, beta_0 cambia ~", sp.N(100 * der / (sp.Rational(5, 3) + total), 4), "% por e-fold.")

    # con Yukawa perturbativo y = 1, que masa haria falta para deltaA = 0.152
    objetivo = sp.Float("0.1520")
    base = sum(sp.N(nc * q**2 * 1.0**2 / (4 * sp.pi**2), 6) for _, nc, q, _, _ in estados)
    lnM = sp.N(objetivo / base, 6)
    print("\ncon y = 1 (perturbativo): delta A =", base, "* ln(M/mu);")
    print("  para delta A = 0.152 hace falta ln(M/mu) =", lnM,
          " => M ~", sp.N(mu * sp.exp(lnM), 4), "GeV")
    return total, der


# ---------------------------------------------------------------------------
# BLOQUE 5 --- Que pasa si las masas VL se fijan con la escalera m_n = M_P phi^-n
# ---------------------------------------------------------------------------
def bloque_5_escalera():
    titulo("BLOQUE 5 --- Masas VL desde la escalera m_n = M_P phi^(-n)")

    MP = sp.Float("2.435e18")
    phi = (1 + sp.sqrt(5)) / 2
    mu = sp.Float("1e16")
    y = sp.Float("2.0")
    suma_ncQ2 = 3 * sp.Rational(4, 9) + 3 * sp.Rational(1, 9) + 1   # u, d, e

    print("phi =", sp.N(phi, 8), "| M_P =", MP)
    print(f"{'n':>3} {'M_n [GeV]':>12} {'delta A':>9} {'A':>8} {'beta_0 [deg]':>12}")
    salida = []
    for n in range(8, 13):
        M = MP * phi ** (-n)
        dA = sp.N(suma_ncQ2 * y**2 / (4 * sp.pi**2) * sp.log(M / mu), 5)
        A = sp.N(sp.Rational(5, 3) + dA, 6)
        beta = sp.N(0.20906 * A, 6)
        salida.append((n, M, dA, A, beta))
        print(f"{n:>3} {sp.N(M,4)!s:>12} {dA!s:>9} {A!s:>8} {beta!s:>12}")
    print("\nSi los tres estados VL se colocan en el mismo nivel n, beta_0 no tiene")
    print("parametros libres (salvo y). El valor observado 0.3803 corresponde a n ~ 10")
    print("(delta A ~ 0.185 en la escalera, frente a 0.152 elegido a mano).")
    print("=> la escalera es una via para convertir el +0.152 en PREDICCION; hoy no se usa.")
    return salida


# ---------------------------------------------------------------------------
# BLOQUE 5 --- Veredicto
# ---------------------------------------------------------------------------
def main():
    c = bloque_1_conversion()
    A = bloque_2_A()
    beta = bloque_3_rotacion()
    umbral = bloque_4_umbral()
    esc = bloque_5_escalera()

    titulo("RESUMEN")
    print("1) conversion            : 0.20906 deg = (alpha_em/2)*(180/pi)  [verificado]")
    print("2) A(5/3) y A(1.819)     :", A["doblete u,d (declarado)"], "/", sp.N(sp.Float("1.819"), 6))
    print("3) rotacion              :", beta, "  [derivado de la dispersion]")
    print("4) umbrales              : delta A =", sp.N(umbral[0], 5),
          "(tesis 0.152); beta_0 =", sp.N(0.20906 * (sp.Rational(5, 3) + umbral[0]), 6))
    print("\nVEREDICTO")
    print(" - El acoplamiento pseudoescalar-foton NO existe a nivel de arbol: el")
    print("   termino g a F F~ es la anomalia ABJ (1 loop, exacta). Lo que se puede")
    print("   derivar es el coeficiente de grupo sum N_c Q^2 y la cinematica.")
    print(" - La cinematica beta = (1/2) g Delta a SI se deriva (B3), y con")
    print("   Delta a = 2 pi f_a N_DW y g = alpha A/(2 pi f_a) da beta_0 = (alpha/2) A N_DW.")
    print(" - La aritmetica 0.20906 * 1.819 = 0.3803 es correcta.")
    print(" - NO esta derivado: (a) A_0 = 5/3 supone omitir leptones por construccion;")
    print("   (b) el termino hadronico -1.92, obligatorio si el campo es un axion de QCD,")
    print("   cambia A a -0.253 y beta_0 a -0.053 grados;")
    print("   (c) el +0.152 sale de 3 masas + y = 2, elegidos; con y = 1 (perturbativo)")
    print("   harian falta masas ~9,5e16 GeV. Es un ajuste de 4 parametros a 1 numero:")
    print("   retrodiccion, no prediccion.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
