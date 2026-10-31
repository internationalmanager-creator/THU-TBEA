#!/usr/bin/env python3
"""
Verifica analiticamente la identidad:
    S(2,1,1) = (1-eps)/(3*m^2) * S(1,1,1)   (a p=0, masas iguales)

La identidad viene de:  m * d/dm S(1,1,1) = 6 m^2 S(2,1,1)
y de que S(1,1,1) = (m^2)^(1-eps) * f(eps).
"""
import sympy as sp

m2, eps, f = sp.symbols('m2 eps f', positive=True)

# S(1,1,1) = (m^2)^(1-eps) * f(eps)
S111 = m2**(1 - eps) * f

# m * d/dm: como m2 = m^2, d/dm = 2m d/dm2, y m*d/dm = 2 m2 d/dm2
m_dS_dm = 2 * m2 * sp.diff(S111, m2)

# Identidad: m*dS111/dm = 6*m2*S211  ->  S211 = m_dS_dm/(6*m2)
S211_via_deriv = sp.simplify(m_dS_dm / (6 * m2))

# Lo que queremos verificar:
S211_esperado = sp.simplify((1 - eps) / (3 * m2) * S111)

print("m*dS111/dm      =", sp.simplify(m_dS_dm))
print("S211 via deriv  =", S211_via_deriv)
print("S211 esperado   =", S211_esperado)
print()
print("Identidad se cumple:", sp.simplify(S211_via_deriv - S211_esperado) == 0)
