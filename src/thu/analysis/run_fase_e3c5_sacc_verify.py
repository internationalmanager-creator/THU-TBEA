# -*- coding: utf-8 -*-
"""E.3-C5 — Verificar si el SACC de ACT DR6 contiene EB/BE/TB."""
import sys, hashlib
from pathlib import Path

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
PKG = LAB / "data" / "raw" / "act_dr6_packages"

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

def sha256_file(path, chunk=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()

# --- 1: Localizar dr6_data.fits ---
hdr("1. Buscar dr6_data.fits en el arbol de packages")
sacc_files = list(PKG.rglob("dr6_data.fits"))
print(f"  Archivos encontrados: {len(sacc_files)}")
for f in sacc_files:
    size_mb = f.stat().st_size / 1024 / 1024
    print(f"    {f.relative_to(PKG)}  ({size_mb:.2f} MB)")

if not sacc_files:
    print("  NO ENCONTRADO. Buscando alternativas:")
    for f in PKG.rglob("*.fits"):
        print(f"    {f.relative_to(PKG)}  ({f.stat().st_size/1024/1024:.2f} MB)")
    sys.exit(1)

sacc_path = sacc_files[0]

# --- 2: SHA-256 ---
hdr("2. Certificacion SHA-256")
sha = sha256_file(sacc_path)
print(f"  Archivo:  {sacc_path}")
print(f"  SHA-256:  {sha}")
print(f"  Tamano:   {sacc_path.stat().st_size / 1024 / 1024:.2f} MB")

# --- 3: Cargar con sacc ---
hdr("3. Cargar SACC y listar data_types")
try:
    import sacc as sacc_mod
    s = sacc_mod.Sacc.load_fits(str(sacc_path))
    print(f"  OK: SACC cargado")
except Exception as e:
    print(f"  ERROR: {e}")
    sys.exit(1)

from collections import Counter
types = Counter()
for d in s.data:
    types[d.data_type] += 1

print(f"  Total entries: {len(s.data)}")
print()
print(f"  Data types presentes:")
for dt, n in sorted(types.items()):
    mark = "  <-- birefringence" if dt in ("cl_eb", "cl_be", "cl_tb") else ""
    print(f"    {dt:15s}  x{n:6d}{mark}")

# --- 4: Veredicto ---
hdr("4. Veredicto: sirve para birefringencia?")

tiene_eb = "cl_eb" in types
tiene_be = "cl_be" in types
tiene_tb = "cl_tb" in types

print(f"  cl_eb presente: {tiene_eb}")
print(f"  cl_be presente: {tiene_be}  (BE(i,j) = EB(j,i) transpuesto)")
print(f"  cl_tb presente: {tiene_tb}")
print()
if tiene_eb or tiene_be:
    print("  ***** SI SIRVE PARA BIREFRINGENCIA *****")
    print("  El SACC contiene EB/BE.")
    print("  Siguiente paso: correr beta_mcmc/run_beta_mcmc.py con MASK='act_dr6'")
elif tiene_tb:
    print("  ***** SOLO TB *****")
    print("  Solo permite medir beta con TB (menos preciso).")
else:
    print("  ***** NO SIRVE *****")
    print("  El SACC solo contiene TT/TE/EE. No hay EB/BE/TB.")
    print("  Opciones:")
    print("    - contactar a J.R. Eskilt para SACC de birefringencia")
    print("    - cerrar FASE E con E.3-C2 (beta = 0.288 +/- 0.047 deg)")

# --- 5: Tracers y metadatos ---
hdr("5. Metadatos del SACC")
tracers = set()
for d in s.data:
    tracers.update(d.tracers)
print(f"  {len(tracers)} tracers unicos")
for t in sorted(tracers)[:40]:
    print(f"    {t}")

# Guardar reporte
import json, time
report = {
    "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "archivo": str(sacc_path),
    "sha256": sha,
    "size_mb": round(sacc_path.stat().st_size / 1024 / 1024, 2),
    "url_origen": "https://lambda.gsfc.nasa.gov/data/act/pspipe/sacc_files/dr6_data.tar.gz",
    "data_types": dict(types),
    "tiene_eb": tiene_eb,
    "tiene_be": tiene_be,
    "tiene_tb": tiene_tb,
    "sirve_birefringencia": tiene_eb or tiene_be or tiene_tb,
}
out = LAB / "data" / "inventory" / "certificacion_act_dr6_sacc.json"
out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\n  Reporte guardado: {out}")
