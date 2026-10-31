#!/usr/bin/env python3
"""
Verifica numericamente el polo lider de S(1,1,1) en p=0, m=1.
Prediccion: eps^2 * S(eps) -> -3*pi^4/2 = -146.11...
"""
import numpy as np
from scipy import integrate
from scipy.special import gamma

def Delta(x, y):
    return x + y - x*x - y*y - x*y

def integrand_sub(x, y, eps):
    D = Delta(x, y)
    if D < 1e-12:
        return 0.0
    main = D ** (-2 + eps)
    # Leading behaviors at 3 corners
    c00 = (x+y) ** (-2+eps) if (x+y) > 1e-12 else 0
    c10 = (1-x) ** (-2+eps) if (1-x) > 1e-12 else 0
    c01 = (1-y) ** (-2+eps) if (1-y) > 1e-12 else 0
    return main - c00 - c10 - c01

def P_numeric(eps, npts=200):
    # Numeric integral of the subtracted integrand + analytic corners (3/eps)
    sub, _ = integrate.dblquad(
        lambda y, x: integrand_sub(x, y, eps),
        1e-4, 1 - 1e-4,
        lambda x: 1e-4,
        lambda x: max(1e-4, 1 - x - 1e-4),
        epsabs=1e-5, epsrel=1e-4
    )
    return sub + 3.0/eps

def S_numeric(eps):
    return np.pi**(4 - 2*eps) * gamma(-1 + 2*eps) * P_numeric(eps)

print("Verificacion del polo lider de S(1,1,1) en p=0, m=1")
print("Prediccion teorica: eps^2 * S -> -3*pi^4/2 =", -3*np.pi**4/2)
print()
print(f"{'eps':>6}  {'S(eps)':>15}  {'eps^2*S(eps)':>15}")
print("-" * 42)
for eps in [0.02, 0.03, 0.04, 0.05, 0.06]:
    S = S_numeric(eps)
    print(f"{eps:>6.2f}  {S:>15.4f}  {eps*eps*S:>15.4f}")
