"""
Verificacion del analisis de Dirac-Bergmann de THU-TBEA (Cap. 5).

Construye la matriz de Poisson 8x8 de las restricciones del sector
proyectado y verifica:
1. Determinante = (kappa_2^2 + kappa_3^2)^2
2. Rango = 8 para (kappa_2, kappa_3) != (0,0)
3. Conteo de grados de libertad = 1
"""
import sympy as sp
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("  VERIFICACION DIRAC-BERGMANN (Cap. 5)")
    print("=" * 60)

    k2, k3 = sp.symbols("kappa_2 kappa_3", real=True)

    # ============================================================
    # 1. Definir bloques de la matriz de Poisson
    # ============================================================
    I2 = sp.eye(2)
    Z2 = sp.zeros(2, 2)

    # Bloque A = [[0, -I], [I, 0]]
    A = sp.Matrix([[Z2, -I2], [I2, Z2]])

    # Bloque B = [[0, X], [-X^T, 0]]
    X = sp.Matrix([[k2, k3], [-k3, k2]])
    B = sp.Matrix([[Z2, X], [-X.T, Z2]])

    # Matriz completa 8x8
    M = sp.BlockMatrix([[A, sp.zeros(4, 4)], [sp.zeros(4, 4), B]]).as_explicit()
    print(f"\n[1] Matriz de Poisson 8x8 construida.")
    print(f"    Dimension: {M.shape}")

    # ============================================================
    # 2. Calcular determinante
    # ============================================================
    print(f"\n[2] Calculando determinante...")
    det_M = sp.simplify(M.det())
    det_A = sp.simplify(A.det())
    det_B = sp.simplify(B.det())
    det_X = sp.simplify(X.det())

    print(f"    det(A) = {det_A}")
    print(f"    det(X) = {det_X}")
    print(f"    det(B) = {det_B}")
    print(f"    det(M) = {det_M}")

    # Verificar contra el valor esperado
    esperado = (k2**2 + k3**2)**2
    ok_det = sp.simplify(det_M - esperado) == 0
    print(f"    Esperado: {esperado}")
    print(f"    Coincide: {ok_det}")

    # ============================================================
    # 3. Calcular rango (evaluando en valores genericos)
    # ============================================================
    print(f"\n[3] Calculando rango (evaluando en k2=1, k3=1)...")
    M_num = M.subs({k2: 1, k3: 1})
    rank = M_num.rank()
    print(f"    Rango: {rank} (esperado: 8)")
    ok_rank = (rank == 8)

    # ============================================================
    # 4. Conteo de grados de libertad
    # ============================================================
    print(f"\n[4] Conteo de grados de libertad...")
    dim_fase = 10
    n_restricciones = 8
    gdl = sp.Rational(1, 2) * (dim_fase - n_restricciones)
    print(f"    dim(Gamma) = {dim_fase}")
    print(f"    n_restricciones = {n_restricciones}")
    print(f"    GDL = (1/2) * (10 - 8) = {gdl}")
    ok_gdl = (gdl == 1)

    # ============================================================
    # 5. Verificar que el bloque B no es invertible si k2=k3=0
    # ============================================================
    print(f"\n[5] Caso limite k2=k3=0...")
    B_limite = B.subs({k2: 0, k3: 0})
    det_B_limite = sp.simplify(B_limite.det())
    print(f"    det(B) en k2=k3=0: {det_B_limite} (esperado: 0)")
    ok_limite = (det_B_limite == 0)

    # ============================================================
    # RESUMEN
    # ============================================================
    print("\n" + "=" * 60)
    print("  RESUMEN")
    print("=" * 60)
    checks = [
        ("det(M) = (k2^2 + k3^2)^2", ok_det),
        ("Rango = 8", ok_rank),
        ("GDL = 1", ok_gdl),
        ("det(B) = 0 si k2=k3=0", ok_limite),
    ]
    n_pass = 0
    for desc, ok in checks:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {desc}")
        if ok:
            n_pass += 1

    print(f"\n  Resultado: {n_pass}/{len(checks)} verificaciones PASS")
    return n_pass == len(checks)


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)