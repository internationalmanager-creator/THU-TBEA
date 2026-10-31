#!/usr/bin/env python3
"""
Verifica la identidad S(2,1,1) = (d-3)/(3 m^2) * S(1,1,1)
usando d como simbolo (independiente de la convencion de dim reg).
"""
import sympy as sp

d, m2, f = sp.symbols('d m2 f', positive=True)

# S(1,1,1) = (m^2)^(d-3) * f(d)   <- analisis dimensional exacto
S111 = m2**(d - 3) * f

# m * d/dm = 2 * m2 * d/dm2
m_dS_dm = 2 * m2 * sp.diff(S111, m2)

# Identidad: m*dS/dm = 6*m2*S211  ->  S211 = m_dS_dm/(6*m2)
S211_via_deriv = sp.simplify(m_dS_dm / (6 * m2))

# Esperado: S(2,1,1) = (d-3)/(3*m2) * S(1,1,1)
S211_esperado = sp.simplify((d - 3) / (3 * m2) * S111)

print("m * dS111/dm   =", sp.simplify(m_dS_dm))
print("S211 via deriv =", S211_via_deriv)
print("S211 esperado  =", S211_esperado)
print()
print("Identidad cumple (version d-explicita):", sp.simplify(S211_via_deriv - S211_esperado) == 0)
print()
# Sustituyendo d = 4 - 2*eps
eps = sp.Symbol('eps', positive=True)
print("Con d = 4 - 2*eps, el factor (d-3)/(3 m^2) =",
      sp.simplify((d - 3)/(3*m2)).subs(d, 4 - 2*eps))
