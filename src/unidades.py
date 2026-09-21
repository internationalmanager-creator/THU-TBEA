"""Conversiones de unidades explicitas.

Regla PIR: NUNCA se convierte implicitamente. Toda conversion debe:
    1. Estar declarada aqui con su factor exacto.
    2. Citar la definicion (SI, CODATA, IAU).
    3. Registrar el factor en el payload del evento.

Unidades base del proyecto: Hz (frecuencia).
"""
from typing import Optional


# Definiciones exactas (SI o CODATA)
C_LUZ           = 299_792_458.0          # m/s (exacto por definicion SI)
PARSEC          = 3.0856775814913673e16  # m (IAU 2015)
MEGAPARSEC      = 1e6 * PARSEC           # m
KM              = 1000.0                 # m
MINUTO          = 60.0                   # s
HORA            = 3600.0                 # s
DIA             = 86400.0                # s
ANO_JULIANO     = 365.25 * DIA           # s


def a_hz(valor: float, unidad: str) -> Optional[float]:
    """Convierte un valor a Hz. Devuelve None si la unidad no es convertible.

    Reglas:
        - Si la unidad es adimensional o no es frecuencia, devuelve None.
        - Si la unidad ya es Hz, devuelve el valor.
        - La conversion de km/s/Mpc usa C_LUZ / MEGAPARSEC.
    """
    u = unidad.strip().lower().replace(" ", "")

    # Frecuencias directas
    if u in ("hz", "1/s", "s^-1"):
        return float(valor)
    if u == "mhz":   return float(valor) * 1e-3
    if u == "khz":   return float(valor) * 1e3
    if u == "ghz":   return float(valor) * 1e9
    if u == "thz":   return float(valor) * 1e12
    if u in ("1/min", "rpm"):
        return float(valor) / MINUTO
    if u == "1/dia":
        return float(valor) / DIA
    if u == "1/ano":
        return float(valor) / ANO_JULIANO

    # Constante de Hubble: H0 en km/s/Mpc -> Hz
    if u in ("km/s/mpc",):
        return float(valor) * KM / MEGAPARSEC

    # Palabras por minuto: se interpreta a nivel de "evento linguistico"
    if u in ("palabras/minuto", "wpm"):
        return float(valor) / MINUTO

    # Tasas por generacion / por base: requieren tiempo de generacion
    if "generacion" in u or "mutaciones" in u:
        return None

    # Adimensional (constante de estructura fina, etc.): no es frecuencia
    if u in ("adimensional", "dimensionless", ""):
        return None

    return None


def factor_conversion(unidad: str) -> Optional[float]:
    """Devuelve el factor multiplicativo para ir a Hz, o None."""
    return a_hz(1.0, unidad)


def unidades_soportadas():
    return [
        ("Hz",          1.0),
        ("mHz",         1e-3),
        ("kHz",         1e3),
        ("MHz",         1e6),
        ("GHz",         1e9),
        ("THz",         1e12),
        ("1/min",       1/MINUTO),
        ("1/dia",       1/DIA),
        ("1/ano",       1/ANO_JULIANO),
        ("km/s/Mpc",    KM / MEGAPARSEC),
        ("palabras/minuto", 1/MINUTO),
    ]


if __name__ == "__main__":
    # Auto-test: verificar conversiones conocidas
    print("=== Test unidades.py ===")
    casos = [
        (100.0, "Hz",       100.0),
        (100.0, "kHz",      100_000.0),
        (67.4,  "km/s/Mpc", 67.4 * KM / MEGAPARSEC),
        (150.0, "palabras/minuto", 150.0 / 60.0),
        (0.309494, "mHz",   0.309494 * 1e-3),
        (1.0,   "adimensional", None),
    ]
    from tqdm import tqdm
    for v, u, esperado in tqdm(casos, desc="Test", ncols=80):
        r = a_hz(v, u)
        if esperado is None:
            assert r is None, f"Esperaba None para {u}, dio {r}"
        else:
            assert abs(r - esperado) < 1e-20, f"Falló {v} {u}: {r} != {esperado}"
    print("=== TEST OK ===")