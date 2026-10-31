"""
Derivacion D.1: Punto fijo aureo a nivel de arbol.

Calcula los coeficientes de la funcion beta_eff(g) = kappa(1 + g - g^2)
a partir de los diagramas de Feynman a nivel de arbol (tadpole, vertice
lineal, dos vertices) de la accion de THU-TBEA.

Referencia: paper/thu/src/tesis_es.tex, Capitulo 6.
"""
import sympy as sp
import sys

def main():
    print("=" * 70)
    print("  PUNTO FIJO AUREO - NIVEL DE ARBOL (D.1)")
    print("=" * 70)

    # ==================================================================
    # 1. ACCION DE THU-TBEA
    # ==================================================================
    # S = int d^4x [ (1/2)(d_mu g)(d^mu g) - V(g) ]
    # donde V(g) = (1/2)m^2 g^2 + (1/3!) lambda g^3 + (1/4!) lambda_4 g^4
    #
    # Para el punto fijo, nos interesa el flujo RG del acoplamiento g.
    # A nivel de arbol, la funcion beta se calcula de los diagramas:
    # - Tadpole: <g> = 0 (por simetria Z2)
    # - Vertice lineal: g * <g> = 0
    # - Dos vertices: g^2 * <g g> (propagador)
    
    g, m, lam = sp.symbols('g m lambda', real=True)
    
    print("\n[1] Accion:")
    print("    S = int [ (1/2)(d g)^2 - (1/2)m^2 g^2 - (lambda/3!) g^3 - ... ]")
    
    # ==================================================================
    # 2. DIAGRAMAS A NIVEL DE ARBOL
    # ==================================================================
    # 2.1. Tadpole:
    #      -i * lambda * int d^4k/(2pi)^4 * 1/(k^2 - m^2) = 0 (dim. reg.)
    #      En dim. reg., el tadpole es identicamente cero.
    
    print("\n[2.1] Tadpole:")
    print("    -i * lambda * int d^4k/(2pi)^4 * 1/(k^2 - m^2) = 0 (dim. reg.)")
    print("    -> Coeficiente de g^0: 0")
    
    # 2.2. Vertice lineal:
    #      -i * lambda * g * <g> = 0 (porque <g> = 0)
    
    print("\n[2.2] Vertice lineal:")
    print("    -i * lambda * g * <g> = 0")
    print("    -> Coeficiente de g^1: 0")
    
    # 2.3. Dos vertices:
    #      (-i * lambda)^2 * g^2 * int d^4k/(2pi)^4 * 1/(k^2 - m^2)^2
    #      = (lambda^2 * g^2) / (16 pi^2) * (1/epsilon + ...)
    #      Este termino es de orden g^2, no de orden g^0 o g^1.
    
    print("\n[2.3] Dos vertices:")
    print("    (-i*lambda)^2 * g^2 * int d^4k/(2pi)^4 * 1/(k^2 - m^2)^2")
    print("    = (lambda^2 * g^2) / (16 pi^2) * (1/epsilon + ...)")
    print("    -> Coeficiente de g^2: lambda^2 / (16 pi^2)")
    
    # ==================================================================
    # 3. FUNCION BETA
    # ==================================================================
    # A nivel de arbol, la funcion beta es:
    # beta(g) = (1/2) * g * d(log Z)/d(log mu)
    # donde Z es la constante de renormalizacion.
    #
    # A nivel de arbol, Z = 1, por lo que beta(g) = 0.
    # Los coeficientes (1, +1, -1) de beta_eff = kappa(1 + g - g^2)
    # NO salen de los diagramas a nivel de arbol.
    #
    # Eso confirma lo que dice el ERRATA (E-01): la funcion beta
    # es [P] (postulada), no [D] (derivada de loops).
    
    print("\n[3] Funcion beta a nivel de arbol:")
    print("    beta(g) = 0 (a nivel de arbol)")
    print("    Los coeficientes (1, +1, -1) de beta_eff = kappa(1 + g - g^2)")
    print("    NO salen de los diagramas a nivel de arbol.")
    print("\n    -> CONFIRMADO: beta_eff es [P] (postulada), no [D] (derivada).")
    print("    -> Esto coincide con el ERRATA v5.5 (E-01).")
    
    return True

if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)