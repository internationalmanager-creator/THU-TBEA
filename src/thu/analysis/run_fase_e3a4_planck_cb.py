# -*- coding: utf-8 -*-
"""FASE E.3-A4 — Leer CSV de planck_pr4 (Cosmic Birefringence)."""
import sys
from pathlib import Path

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
PP4 = LAB / "data" / "raw" / "planck_pr4"

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# -- 1: beta_planck_pr4.csv --
hdr("1. beta_planck_pr4.csv")
f = PP4 / "beta_planck_pr4.csv"
print(f"  Path: {f}")
print(f"  Existe: {f.exists()}")
if f.exists():
    print(f"  Contenido COMPLETO:")
    for line in f.read_text(encoding="utf-8").splitlines():
        print(f"    {line}")

# -- 2: cb_spectra/NPIPE_CB_spectra.csv --
hdr("2. cb_spectra/NPIPE_CB_spectra.csv")
f = PP4 / "cb_spectra" / "NPIPE_CB_spectra.csv"
print(f"  Path: {f}")
print(f"  Existe: {f.exists()}")
if f.exists():
    lines = f.read_text(encoding="utf-8").splitlines()
    print(f"  Total lineas: {len(lines)}")
    print(f"  Primeras 5 lineas:")
    for line in lines[:5]:
        print(f"    {line}")
    print(f"  Ultimas 3 lineas:")
    for line in lines[-3:]:
        print(f"    {line}")
    # Intentar inferir columnas
    header = lines[0]
    ncols = len(header.split())
    print(f"  N columnas (header split): {ncols}")

# -- 3: cb_spectra/PR3_CB_spectra.csv --
hdr("3. cb_spectra/PR3_CB_spectra.csv")
f = PP4 / "cb_spectra" / "PR3_CB_spectra.csv"
print(f"  Existe: {f.exists()}")
if f.exists():
    lines = f.read_text(encoding="utf-8").splitlines()
    print(f"  Total lineas: {len(lines)}")
    print(f"  Primeras 5:")
    for line in lines[:5]:
        print(f"    {line}")

# -- 4: cb_spectra/NPIPE_alpha_CMB_cc.csv --
hdr("4. cb_spectra/NPIPE_alpha_CMB_cc.csv")
f = PP4 / "cb_spectra" / "NPIPE_alpha_CMB_cc.csv"
print(f"  Existe: {f.exists()}")
if f.exists():
    lines = f.read_text(encoding="utf-8").splitlines()
    print(f"  Total lineas: {len(lines)}")
    for line in lines[:10]:
        print(f"    {line}")

# -- 5: litebird forecast --
hdr("5. litebird/forecast/litebird_forecast_beta.txt")
f = LAB / "data" / "raw" / "litebird" / "forecast" / "litebird_forecast_beta.txt"
print(f"  Existe: {f.exists()}")
if f.exists():
    lines = f.read_text(encoding="utf-8").splitlines()
    print(f"  Total lineas: {len(lines)}")
    for line in lines[:20]:
        print(f"    {line}")

# -- 6: Intentar leer NPIPE_CB_spectra.csv con numpy --
hdr("6. Parseo numerico de NPIPE_CB_spectra.csv")
f = PP4 / "cb_spectra" / "NPIPE_CB_spectra.csv"
if f.exists():
    import numpy as np
    # Intentar detectar separador y header
    lines = f.read_text(encoding="utf-8").splitlines()
    # Skip lineas de comentario
    data_lines = [l for l in lines if not l.strip().startswith("#") and l.strip()]
    print(f"  Lineas no-comentario: {len(data_lines)}")
    if data_lines:
        # Detectar separador
        first = data_lines[0]
        if "," in first:
            sep = ","
        elif "\t" in first:
            sep = "\t"
        else:
            sep = None
        print(f"  Separador detectado: '{sep}'")
        print(f"  Primera linea no-comentario: {first[:200]}")
        # Intentar cargar
        try:
            data = np.genfromtxt(f, delimiter=sep, comments="#", skip_header=0)
            print(f"  Shape cargado: {data.shape}")
            print(f"  Primeras 3 filas x 6 cols:")
            print(data[:3, :min(6, data.shape[1])])
        except Exception as e:
            print(f"  No se pudo cargar como array: {e}")

# -- 7: Resumen y siguiente paso --
hdr("7. Resumen")
print(f"  beta_planck_pr4.csv:      {'OK' if (PP4/'beta_planck_pr4.csv').exists() else 'NO'}")
print(f"  NPIPE_CB_spectra.csv:     {'OK' if (PP4/'cb_spectra'/'NPIPE_CB_spectra.csv').exists() else 'NO'}")
print(f"  PR3_CB_spectra.csv:       {'OK' if (PP4/'cb_spectra'/'PR3_CB_spectra.csv').exists() else 'NO'}")
print(f"  NPIPE_alpha_CMB_cc.csv:   {'OK' if (PP4/'cb_spectra'/'NPIPE_alpha_CMB_cc.csv').exists() else 'NO'}")
print()
print("  Siguiente paso:")
print("  - Si los CSV contienen EB y TB -> E.3-B: chi^2 -> beta")
print("  - Si contienen beta directamente -> comparar contra beta_0 = 0.3803 deg")
