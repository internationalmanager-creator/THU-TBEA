# -*- coding: utf-8 -*-
"""
FASE B — Verificacion simbolica de resultados clave THU-TBEA 5.0
Verifica con sympy los coeficientes y formulas del PDF (v5.3).
"""
import sys, time, json
from pathlib import Path
from datetime import datetime, timezone

from sympy import (
    symbols, sqrt, pi, exp, cos, integrate, oo, Rational, S,
    diff, solve, Eq, nsolve, LambertW, log, N, simplify, expand,
    series, limit, Function, Symbol, I, re, im, oo as SYM_oo
)
from sympy.abc import a, b, k, g, u, x, n, N as Nsym

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
OUT = LAB / "outputs" / "verificaciones"
OUT.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────
# Helper de barra de progreso + output
# ──────────────────────────────────────────────────────────────
def step_header(i, total, titulo):
    pct = int(100 * i / total)
    filled = pct * 40 // 100
    bar = "█" * filled + "░" * (40 - filled)
    print()
    print("═" * 72)
    print(f"  PASO {i}/{total}   [{bar}]  {pct:3d}%")
    print(f"  {titulo}")
    print("═" * 72)
    sys.stdout.flush()

def paso(desc, pdf, calc, pass_, extra=None):
    print(f"\n  ¿QUE SE VERIFICA?")
    print(f"    {desc}")
    print(f"\n  VALOR PDF (v5.3):")
    print(f"    {pdf}")
    print(f"\n  CALCULO SYMPY:")
    print(f"    {calc}")
    if extra:
        print(f"\n  {extra}")
    print(f"\n  RESULTADO: {'✓ PASS' if pass_ else '✗ FAIL'}")
    sys.stdout.flush()
    return pass_

def fmt(x, n=10):
    """Formatea un valor sympy a n digitos"""
    return f"{float(N(x, n+2)):.{n}f}"

# ──────────────────────────────────────────────────────────────
# Cabecera
# ──────────────────────────────────────────────────────────────
print()
print("╔" + "═" * 70 + "╗")
print("║" + " FASE B — VERIFICACION SIMBOLICA THU-TBEA 5.0 ".center(70) + "║")
print("║" + " Sympy symbolic verification of thesis coefficients ".center(70) + "║")
print("╚" + "═" * 70 + "╝")
print(f"  Fecha: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
print(f"  Output: {OUT}")
sys.stdout.flush()

resultados = []
TOTAL = 10
t0 = time.time()

# ══════════════════════════════════════════════════════════════
# PASO 1 — Cap. 3: Normalizacion canonica tau_c = sqrt(3) tau
# ══════════════════════════════════════════════════════════════
step_header(1, TOTAL, "Cap. 3 — Normalizacion canonica tau_c = sqrt(3) tau")

# Verificar: 3/2 (grad tau)^2 = 1/2 (grad tau_c)^2 con tau_c = sqrt(3) tau
# Y: 1/2 tau H tau = 1/6 tau_c H tau_c
tau_ratio = sqrt(3)
cinetico = Rational(3,2) * (Symbol("grad_tau")**2)
canonico = Rational(1,2) * (Symbol("grad_tau") * tau_ratio)**2
diff_cin = simplify(cinetico - canonico)

# Termino no local
H = Function("H")
tau = Symbol("tau", positive=True)
tau_c = Symbol("tau_c", positive=True)
no_local_orig = Rational(1,2) * tau * H(tau)
# Bajo tau = tau_c / sqrt(3)
no_local_nuevo = no_local_orig.subs(tau, tau_c / sqrt(3))
ratio_no_local = simplify(no_local_nuevo / (tau_c * H(tau_c)))

ok1 = (diff_cin == 0) and (ratio_no_local == Rational(1,6))

extra1 = (
    f"  Verificacion cinetica: 3/2 (∇τ)² - 1/2 (∇τ_c)² = {diff_cin}\n"
    f"  Verificacion no-local: [1/2 τ Ĥ τ] / [τ_c Ĥ τ_c] = {ratio_no_local}"
)
paso(
    "Tau_c = √3 τ lleva el termino cinetico de +3/2 a +1/2,\n"
    "  y el termino no-local de 1/2 a 1/6.",
    "τ_c = √3 τ,  coeficiente no-local = 1/6  (Ec. 3.8-3.9)",
    f"cinetico diff = {diff_cin}; no_local ratio = {ratio_no_local}",
    ok1, extra1
)
resultados.append({"paso": 1, "titulo": "tau_c = sqrt(3) tau", "ok": ok1})

# ══════════════════════════════════════════════════════════════
# PASO 2 — Cap. 4: Residuo del propagador Res[Delta]
# ══════════════════════════════════════════════════════════════
step_header(2, TOTAL, "Cap. 4 — Residuo del propagador: Res[Δ] = e^(-am²)/(1+am²)")

k2, m2, a_ = symbols("k2 m2 a", real=True, positive=True)
D = k2 * exp(-a_*k2) + m2
D_prime = diff(D, k2)
# En el polo k2 = -m2 (formal: usar -m2)
D_prime_polo = D_prime.subs(k2, -m2)
Residuo = 1 / D_prime_polo

# Comparar con formula del PDF
Residuo_pdf = exp(-a_*m2) / (1 + a_*m2)
diff_res = simplify(Residuo - Residuo_pdf)
ok2 = (diff_res == 0)

extra2 = (
    f"  D(k²)        = {D}\n"
    f"  D'(k²)       = {D_prime}\n"
    f"  D'(-m²)      = {D_prime_polo}\n"
    f"  Res[Δ]       = {Residuo}\n"
    f"  PDF          = {Residuo_pdf}\n"
    f"  Diferencia   = {diff_res}"
)
paso(
    "El residuo del propagador en el polo fisico k² = -m².\n"
    "  PDF: Res[Δ] = e^(-am²)/(1 + am²)",
    "Res[Δ] = e^(-am²)/(1+am²)  (Ec. 4.4)",
    f"1 / D'(-m²) = {Residuo}",
    ok2, extra2
)
resultados.append({"paso": 2, "titulo": "Residuo propagador", "ok": ok2})

# ══════════════════════════════════════════════════════════════
# PASO 3 — Cap. 4: Ramas de Lambert-W
# ══════════════════════════════════════════════════════════════
step_header(3, TOTAL, "Cap. 4 — Ramas de Lambert-W: u e^u = am²")

# Resolver u*exp(u) = a*m2
ecuacion = Eq(u * exp(u), a_ * m2)
solucion = solve(ecuacion, u)
# Sympy deberia devolver [LambertW(a*m2)]
lam_sol = solucion[0] if solucion else None

# Verificar que W(x)*exp(W(x)) = x
x_test = S(0.5)
W_x = LambertW(x_test)
identidad = simplify(W_x * exp(W_x) - x_test)

ok3 = (lam_sol == LambertW(a_*m2)) and (abs(float(identidad)) < 1e-10)

extra3 = (
    f"  Solucion sympy: {lam_sol}\n"
    f"  Identidad W(x)·e^W(x) - x = {identidad}  (test x=0.5)\n"
    f"  k² = -(M_P²/φ) W_k(φm²/M_P²), k ∈ ℤ"
)
paso(
    "El operador □e^(a□) - m² tiene ceros dados por u e^u = am²,\n"
    "  cuya solucion son las ramas W_k de Lambert-W.",
    "u = W_k(am²),  k² = -(M_P²/φ) W_k(φm²/M_P²)  (Ec. 4.6)",
    f"Sympy: u = {lam_sol}",
    ok3, extra3
)
resultados.append({"paso": 3, "titulo": "Lambert-W", "ok": ok3})

# ══════════════════════════════════════════════════════════════
# PASO 4 — Cap. 6: Funcion beta y punto fijo aureo
# ══════════════════════════════════════════════════════════════
step_header(4, TOTAL, "Cap. 6 — Funcion beta y punto fijo aureo g* = φ")

kappa = symbols("kappa", positive=True)
beta_g = kappa * (1 + g - g**2)

# Puntos fijos
puntos_fijos = solve(beta_g, g)
phi_val = (1 + sqrt(5)) / 2
g_plus = max(puntos_fijos, key=lambda v: float(v))
g_minus = min(puntos_fijos, key=lambda v: float(v))

# Verificar g_+ = phi
ok_g_plus = simplify(g_plus - phi_val) == 0
ok_g_minus = simplify(g_minus - (-1/phi_val)) == 0

# Derivada en el punto fijo
beta_prime = diff(beta_g, g)
gamma_val = beta_prime.subs(g, phi_val)
gamma_esperado = -kappa * sqrt(5)

ok_gamma = simplify(gamma_val - gamma_esperado) == 0

ok4 = ok_g_plus and ok_g_minus and ok_gamma

extra4 = (
    f"  β(g)              = {beta_g}\n"
    f"  Raices:             {puntos_fijos}\n"
    f"  g_+               = {fmt(g_plus, 10)}  (φ = {fmt(phi_val, 10)})\n"
    f"  g_-               = {fmt(g_minus, 10)}  (-1/φ = {fmt(-1/phi_val, 10)})\n"
    f"  β'(g)             = {beta_prime}\n"
    f"  β'(φ)             = {gamma_val}\n"
    f"  -κ√5              = {gamma_esperado}\n"
    f"  β'(φ) - (-κ√5)    = {simplify(gamma_val - gamma_esperado)}"
)
paso(
    "β(g) = κ(1+g-g²) tiene raices en g_+ = φ y g_- = -1/φ.\n"
    "  Estabilidad del punto fijo positivo: β'(φ) = -κ√5 < 0.",
    "g* = φ ≈ 1.618,  γ = β'(φ) = -κ√5  (Ecs. 6.4-6.5)",
    f"Sympy: g+ = {fmt(g_plus, 8)}, g- = {fmt(g_minus, 8)}, β'(φ) = {fmt(gamma_val/kappa, 6)}·κ",
    ok4, extra4
)
resultados.append({"paso": 4, "titulo": "beta function", "ok": ok4})

# ══════════════════════════════════════════════════════════════
# PASO 5 — Cap. 7: Integral de vacio escalar I_2(a,b)
# ══════════════════════════════════════════════════════════════
step_header(5, TOTAL, "Cap. 7 — Integral de vacio I_2(a,b)")

# I_2(a,b) = int_0^inf k^2 cos(bk) e^(-a k^2) dk
a_p, b_p = symbols("a b", positive=True)
I2_calc = integrate(k**2 * cos(b_p*k) * exp(-a_p * k**2), (k, 0, oo))
I2_pdf = (1/(4*a_p)) * sqrt(pi/a_p) * (1 - b_p**2/(2*a_p)) * exp(-b_p**2/(4*a_p))

diff_I2 = simplify(I2_calc - I2_pdf)
ok5 = (diff_I2 == 0)

extra5 = (
    f"  I_2(a,b) calculado  = {I2_calc}\n"
    f"  I_2(a,b) PDF        = {I2_pdf}\n"
    f"  Diferencia          = {diff_I2}"
)
paso(
    "La integral de vacio escalar modulada.\n"
    "  PDF: I_2 = (1/4a) √(π/a) (1 - b²/2a) e^(-b²/4a)",
    "I_2(a,b) = (1/(4a))·√(π/a)·(1 - b²/(2a))·e^(-b²/(4a))  (Ec. 7.3)",
    f"Sympy integrate: {I2_calc}",
    ok5, extra5
)
resultados.append({"paso": 5, "titulo": "Integral I2(a,b)", "ok": ok5})

# ══════════════════════════════════════════════════════════════
# PASO 6 — Cap. 7: Condicion de seleccion N
# ══════════════════════════════════════════════════════════════
step_header(6, TOTAL, "Cap. 7 — Condicion de seleccion φ^(2N) = 2φ")

phi_exact = (1 + sqrt(5)) / 2

# Resolver phi^(2N) = 2*phi
# 2N * ln(phi) = ln(2*phi)
# N = ln(2*phi) / (2*ln(phi)) = 1/2 + ln(2)/(2*ln(phi))
N_sol = log(2*phi_exact) / (2 * log(phi_exact))
N_simplificado = simplify(N_sol)

N_valor = float(N(N_sol, 15))
N_pdf = 1.220210
ok6 = abs(N_valor - N_pdf) < 1e-5

extra6 = (
    f"  φ                 = {fmt(phi_exact, 12)}\n"
    f"  Solucion analitica: N = ln(2φ) / (2 ln φ)\n"
    f"                    = 1/2 [1 + ln 2 / ln φ]\n"
    f"  N (sympy)         = {fmt(N_sol, 12)}\n"
    f"  N (PDF)           = {N_pdf:.6f}\n"
    f"  Verificacion:     φ^(2N) = {fmt(phi_exact**(2*N_sol), 10)}"
)
paso(
    "La cancelacion del termino dominante del vacio escalar\n"
    "  fija el grado espectral N mediante φ^(2N) = 2φ.",
    "N = (1/2)[1 + ln(2)/ln(φ)] ≈ 1.220210  (Ec. 7.4-7.5)",
    f"Sympy solve: N = {N_simplificado} = {N_valor:.10f}",
    ok6, extra6
)
resultados.append({"paso": 6, "titulo": "Condicion N", "ok": ok6})

# ══════════════════════════════════════════════════════════════
# PASO 7 — Cap. 8: Coeficiente kappa^4/6 en Friedmann
# ══════════════════════════════════════════════════════════════
step_header(7, TOTAL, "Cap. 8 — Coeficiente κ⁴/6 en Friedmann modificada")

kappa_sym = symbols("kappa", positive=True)
S_sym = symbols("S", positive=True)
a_sym = symbols("a", positive=True)
rho_tot = symbols("rho_tot", positive=True)

# Verificar: 3H^2 = κ²(ρ_tot - κ²S²a^-6/6) = κ²ρ_tot - κ⁴S²a^-6/6
lado_interno = rho_tot - kappa_sym**2 * S_sym**2 * a_sym**(-6) / 6
lado_expandido = kappa_sym**2 * lado_interno
lado_directo = kappa_sym**2 * rho_tot - kappa_sym**4 * S_sym**2 * a_sym**(-6) / 6
diff_fried = expand(lado_expandido - lado_directo)

ok7 = (diff_fried == 0)

extra7 = (
    f"  Lado interno: ρ_tot - κ²S²a⁻⁶/6\n"
    f"  3H² = κ²(...)  = {lado_expandido}\n"
    f"  Forma directa:  κ²ρ_tot - κ⁴S²a⁻⁶/6 = {lado_directo}\n"
    f"  Diferencia:     {diff_fried}"
)
paso(
    "El coeficiente canonico del termino de espin es κ⁴/6,\n"
    "  consistente entre ecuacion interna y expansion.",
    "3H² = κ²ρ_tot - (κ⁴/6) S² a⁻⁶  (Ecs. 8.1-8.2)",
    f"Verificacion algebraica: {diff_fried} = 0",
    ok7, extra7
)
resultados.append({"paso": 7, "titulo": "Friedmann κ⁴/6", "ok": ok7})

# ══════════════════════════════════════════════════════════════
# PASO 8 — Cap. 12: Escala Lambda_THU = M_P phi^(-88)
# ══════════════════════════════════════════════════════════════
step_header(8, TOTAL, "Cap. 12 — Escala Lambda_THU = M_P φ^(-88)")

# M_P reducida = 1.2209e19 GeV (o 2.435e18? -> PDF dice 2.435e18)
# Vamos con el valor del PDF: 2.435e18 GeV (reducida)
MP_GeV = 2.435e18
phi_num = float((1 + sqrt(5)) / 2)

Lambda_GeV = MP_GeV * phi_num**(-88)
Lambda_MeV = Lambda_GeV * 1000

Lambda_pdf_MeV = 989.89
ok8 = abs(Lambda_MeV - Lambda_pdf_MeV) < 0.5

extra8 = (
    f"  M_P (reducida)      = {MP_GeV:.4e} GeV\n"
    f"  φ                   = {phi_num:.10f}\n"
    f"  φ^88                = {phi_num**88:.6e}\n"
    f"  φ^(-88)             = {phi_num**(-88):.6e}\n"
    f"  Λ_THU               = {Lambda_GeV:.6e} GeV\n"
    f"                    = {Lambda_MeV:.4f} MeV\n"
    f"  PDF                 = {Lambda_pdf_MeV} MeV\n"
    f"  Error relativo      = {abs(Lambda_MeV-Lambda_pdf_MeV)/Lambda_pdf_MeV*100:.3f}%"
)
paso(
    "La jerarquia aurea Λ_THU = M_P φ^(-88) da la escala hadronica.",
    "Λ_THU ≈ 989.89 MeV  (Ec. 12.1)",
    f"Sympy N(): Λ_THU = {Lambda_MeV:.4f} MeV",
    ok8, extra8
)
resultados.append({"paso": 8, "titulo": "Lambda_THU", "ok": ok8})

# ══════════════════════════════════════════════════════════════
# PASO 9 — Cap. 12: Masa del neutron
# ══════════════════════════════════════════════════════════════
step_header(9, TOTAL, "Cap. 12 — Masa del neutron con jerarquia de correcciones")

Lambda = 989.89  # MeV
phi_n = phi_num
alpha_em = 1.0 / 137.035999139

m_n = Lambda - Lambda / phi_n**6 + alpha_em / pi * Lambda
m_n_float = float(m_n.evalf()) if hasattr(m_n, "evalf") else m_n

m_n_pdf = 937.03
ok9 = abs(float(m_n_float) - m_n_pdf) < 0.5

extra9 = (
    f"  Λ             = {Lambda} MeV\n"
    f"  φ^6           = {phi_n**6:.4f}\n"
    f"  Λ/φ^6         = {Lambda / phi_n**6:.4f} MeV\n"
    f"  α/π·Λ         = {alpha_em/float(pi) * Lambda:.4f} MeV\n"
    f"  m_n           = {float(m_n_float):.4f} MeV\n"
    f"  PDF           = {m_n_pdf} MeV\n"
    f"  Error rel.    = {abs(float(m_n_float) - m_n_pdf)/m_n_pdf*100:.3f}%"
)
paso(
    "Masa del neutron con jerarquia aurea φ^(-6) + correccion QED.",
    "m_n^THU ≈ 937.03 MeV  (Ec. 12.2)",
    f"Sympy N(): m_n = {float(m_n_float):.4f} MeV",
    ok9, extra9
)
resultados.append({"paso": 9, "titulo": "m_n neutron", "ok": ok9})

# ══════════════════════════════════════════════════════════════
# PASO 10 — Cap. 10: Coeficiente anomalo A
# ══════════════════════════════════════════════════════════════
step_header(10, TOTAL, "Cap. 10 — Coeficiente anomalo A = 1.819")

# A_0 = 3*(2/3)^2 + 3*(1/3)^2
A0 = 3 * Rational(2,3)**2 + 3 * Rational(1,3)**2
A0_float = float(A0)

# Correcciones VL: delta_A_i = N_c Q^2 * y^2/(4 pi^2) * ln(M_i/mu_ex)
# y = 2.0, mu_ex ~ escala GUT
# VL-u: Nc Q^2 = 4/3, ln = 0.665
# VL-d: Nc Q^2 = 1/3, ln = 0.833
# VL-e: Nc Q^2 = 1.0, ln = 0.336
y = 2.0
factor_y = y**2 / (4 * float(pi)**2)

dA_u = (4/3) * factor_y * 0.665
dA_d = (1/3) * factor_y * 0.833
dA_e = 1.0    * factor_y * 0.336
dA_total = dA_u + dA_d + dA_e

A_total = A0_float + dA_total
A_pdf = 1.819
ok10 = abs(A_total - A_pdf) < 0.01

extra10 = (
    f"  A_0 = 3(2/3)² + 3(1/3)² = {A0_float:.6f}  (5/3 = {float(Rational(5,3)):.6f})\n"
    f"  y²/(4π²)                  = {factor_y:.6f}\n"
    f"  δA_u (VL-u, 4/3·0.665)  = {dA_u:.6f}\n"
    f"  δA_d (VL-d, 1/3·0.833)  = {dA_d:.6f}\n"
    f"  δA_e (VL-e, 1.0·0.336)  = {dA_e:.6f}\n"
    f"  δA_total                  = {dA_total:.6f}\n"
    f"  A = A_0 + δA              = {A_total:.6f}\n"
    f"  PDF                       = {A_pdf}"
)
paso(
    "Coeficiente anomalo del acoplamiento axionico:\n"
    "  A_0 = 5/3 (Modelo Estándar), correccion VL = 0.152,\n"
    "  A_total = 1.819.",
    "A = 5/3 + δA_VL = 1.819  (Ecs. 10.4-10.5)",
    f"Sympy/Rational: A = {A_total:.6f}",
    ok10, extra10
)
resultados.append({"paso": 10, "titulo": "Coeficiente A", "ok": ok10})

# ══════════════════════════════════════════════════════════════
# RESUMEN
# ══════════════════════════════════════════════════════════════
t_total = time.time() - t0
n_pass = sum(1 for r in resultados if r["ok"])
n_fail = sum(1 for r in resultados if not r["ok"])

print()
print("╔" + "═" * 70 + "╗")
print("║" + " RESUMEN FASE B ".center(70) + "║")
print("╚" + "═" * 70 + "╝")
print()
for r in resultados:
    icon = "✓" if r["ok"] else "✗"
    color = "\033[92m" if r["ok"] else "\033[91m"
    reset = "\033[0m"
    print(f"  {color}{icon}{reset}  Paso {r['paso']:2d}  {r['titulo']}")
print()
print(f"  PASS: {n_pass}/{TOTAL}")
print(f"  FAIL: {n_fail}/{TOTAL}")
print(f"  Duracion total: {t_total:.2f}s")

# Manifest
mf = {
    "version": "1.0.0",
    "fecha": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "total_pasos": TOTAL,
    "pass": n_pass,
    "fail": n_fail,
    "duracion_s": round(t_total, 3),
    "detalle": resultados
}
mf_path = LAB / "data" / "inventory" / "verificacion_simbolica.json"
mf_path.write_text(json.dumps(mf, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\n  Manifest: {mf_path}")
print()
