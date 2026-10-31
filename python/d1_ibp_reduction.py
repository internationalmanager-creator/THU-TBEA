#!/usr/bin/env python3
"""
d1_ibp_reduction.py
Reduccion IBP del sunset p=0 con masas iguales.

    S(a,b,c) = integral d^d k1 d^d k2 / (D1^a D2^b D3^c)

con D_i = k_i^2 - m^2.

Objetivo: expresar S(2,1,1) en terminos de integrales maestras
(S(1,1,1) y productos de tadpoles) usando las identidades IBP.

Identidades (derivadas a mano en el chat anterior):
   0 = (d - 2a - c) S(a,b,c) - 2a m^2 S(a+1,b,c)
       - c S(a-1,b,c+1) + c S(a,b-1,c+1) - c m^2 S(a,b,c+1)
y la simetrica con a<->b.
"""

import json
import sympy as sp
from sympy import Symbol, symbols, linear_eq_to_matrix

d, m2 = symbols('d m2', positive=True)


def S(a, b, c):
    return Symbol(f"S_{a}_{b}_{c}")


def ibp1(a, b, c):
    return ((d - 2*a - c) * S(a, b, c)
            - 2*a*m2 * S(a + 1, b, c)
            - c * S(a - 1, b, c + 1)
            + c * S(a, b - 1, c + 1)
            - c*m2 * S(a, b, c + 1))


def ibp2(a, b, c):
    return ((d - 2*b - c) * S(a, b, c)
            - 2*b*m2 * S(a, b + 1, c)
            - c * S(a, b - 1, c + 1)
            + c * S(a - 1, b, c + 1)
            - c*m2 * S(a, b, c + 1))


def main(N_max=3):
    print("=" * 64)
    print(f"REDUCCION IBP DEL SUNSET p=0 (masas iguales), N_max={N_max}")
    print("=" * 64)

    eqs = []
    for a in range(1, N_max + 1):
        for b in range(1, N_max + 1):
            for c in range(1, N_max + 1):
                eqs.append(ibp1(a, b, c))
                eqs.append(ibp2(a, b, c))

    unknowns = set()
    for e in eqs:
        for s in e.free_symbols:
            if str(s).startswith('S_'):
                unknowns.add(s)
    unknowns = sorted(unknowns, key=str)

    print(f"Ecuaciones generadas : {len(eqs)}")
    print(f"Incognitas S(a,b,c)  : {len(unknowns)}")

    A, b_vec = linear_eq_to_matrix(eqs, unknowns)
    rango = A.rank()
    kernel_dim = len(unknowns) - rango
    print(f"Matriz               : {A.shape}")
    print(f"Rango                : {rango}")
    print(f"Master integrals libres: {kernel_dim}")

    print("\n--- Aislando S(2,1,1) (dejando S(1,1,1) como maestra) ---")
    free = S(1, 1, 1)
    to_solve = [u for u in unknowns if u != free]
    sol = sp.solve(eqs, to_solve, dict=True)

    resultado = {"N_max": N_max,
                 "rank": int(rango),
                 "kernel_dim": int(kernel_dim),
                 "S211": None}

    if sol:
        sol = sol[0]
        print(f"\nNumero de incognitas resueltas: {len(sol)}")
        if S(2, 1, 1) in sol:
            expr = sp.simplify(sol[S(2, 1, 1)])
            print(f"\nS(2,1,1) = {expr}")
            resultado["S211"] = str(expr)
        else:
            print("\nS(2,1,1) no se puede aislar solo con S(1,1,1).")
            print("Muestra de lo que si se resolvio:")
            for k in [S(3, 1, 1), S(2, 1, 2), S(2, 2, 1)]:
                if k in sol:
                    print(f"  {k} = {sp.simplify(sol[k])}")
    else:
        print("\nSin solucion unica. Probar N_max mayor o agregar IBP extras.")

    out = "/mnt/c/temp_thu_resultados/d1_ibp_reduction.json"
    try:
        with open(out, "w") as f:
            json.dump(resultado, f, indent=2)
        print(f"\nResultado guardado en: {out}")
    except FileNotFoundError:
        print(f"\n(No se pudo guardar en {out} — carpeta no existe)")


if __name__ == "__main__":
    import sys
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    main(N_max=N)
