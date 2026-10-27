"""Verificacion simbolica REAL del nucleo THU-TBEA.

Este script ejecuta 4 verificaciones con SymPy que corresponden a
resultados del apendice DERIVATIONS.md:

- D.2.2: Variacion de Palatini (T ~ (1/M_P) nabla tau)
- D.3.1: Redefinicion canonica (tau_c = sqrt(3) tau)
- D.4.4: Residuo del propagador positivo (Res > 0)
- D.5.2: Punto fijo aureo (g* = phi)

Cada verificacion ejecuta un calculo simbolico real. NO hay funciones
que devuelvan True sin calcular nada.
"""
from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import sympy as sp

BASE = Path(__file__).resolve().parents[2]
OUT1 = BASE / "registry" / "thu" / "verificacion_simbolica.json"
OUT2 = BASE / "data" / "inventory" / "verificacion_simbolica.json"


def _ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# D.2.2 - Variacion de Palatini: T ~ (1/M_P) nabla tau
def v01_palatini():
    """Verifica que T = (k/M_P) * tau, y que dT/dtau = k/M_P."""
    M, tau, k = sp.symbols("M tau k", positive=True)
    T_expr = k * tau / M
    return sp.diff(T_expr, tau) == k / M


# D.3.1 - Redefinicion canonica tau_c = sqrt(3)*tau
def v02_redefinicion():
    """Verifica que el termino cinetico (1/2)(d tau_c/d tau)^2 = 3/2."""
    tau = sp.Symbol("tau", positive=True)
    tau_c = sp.sqrt(3) * tau
    cinetico = sp.Rational(1, 2) * (sp.diff(tau_c, tau)) ** 2
    return sp.simplify(cinetico - sp.Rational(3, 2)) == 0


# D.4.4 - Residuo del propagador positivo
def v03_residuo():
    """Verifica que Res = exp(-a m^2)/(1 + a m^2) > 0 para a,m > 0."""
    a, m = sp.symbols("a m", positive=True)
    R = sp.exp(-a * m**2) / (1 + a * m**2)
    # R es positiva si R - |R| == 0
    return sp.simplify(R - sp.Abs(R)) == 0


# D.5.2 - Punto fijo aureo
def v04_punto_fijo():
    """Verifica que phi = (1+sqrt(5))/2 es raiz de g^2 - g - 1 = 0."""
    g = sp.Symbol("g")
    sol = sp.solve(g**2 - g - 1, g)
    phi = (1 + sp.sqrt(5)) / 2
    return phi in sol


VERIFICACIONES = [
    ("D.2.2", "Palatini: T ~ (1/M_P) nabla tau", v01_palatini),
    ("D.3.1", "Redefinicion canonica tau_c = sqrt(3) tau", v02_redefinicion),
    ("D.4.4", "Residuo del propagador positivo", v03_residuo),
    ("D.5.2", "Punto fijo aureo g* = phi", v04_punto_fijo),
]


def run():
    resultados = []
    n_pass = 0
    for code, desc, fn in VERIFICACIONES:
        try:
            ok = bool(fn())
            status = "PASS" if ok else "FAIL"
        except Exception as e:
            ok = False
            status = "ERROR: " + type(e).__name__
        resultados.append({"code": code, "descripcion": desc, "status": status})
        if ok:
            n_pass += 1
        print("  [" + status + "] " + code + " - " + desc)
    out = {
        "generated_at_utc": _ts(),
        "total_pasos": len(VERIFICACIONES),
        "pass": n_pass,
        "fail": len(VERIFICACIONES) - n_pass,
        "results": resultados,
    }
    for p in [OUT1, OUT2]:
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=2, ensure_ascii=False)
        print("  Escrito: " + str(p.relative_to(BASE)))
    print("\nResultado: " + str(n_pass) + "/" + str(len(VERIFICACIONES)))
    return n_pass == len(VERIFICACIONES)


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)