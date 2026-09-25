# -*- coding: utf-8 -*-
"""
FASE E.3a — Reconocimiento del data vector SPT-3G D1.

Objetivo unico: determinar si este likelihood contiene espectros
que puedan medir birefringencia (EB, TB) o solo T&E.

NO se calcula chi^2. NO se asume contenido.
Solo se reporta lo que hay.
"""
import sys, json, time
from pathlib import Path
import numpy as np

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")

# Path segun handoff (se verifica, no se asume)
SPT_ROOT = (LAB / "data" / "extracted" / "zen_runtime" /
            "SPT_3G_D1_T_E_likelihood_runtime_data_for_SPTLikel" /
            "SPT3G_D1_TnE_v0_20260917")

TOTAL = 6
t0 = time.time()

def barra(i):
    pct = int(100 * i / TOTAL)
    filled = pct * 40 // 100
    return "=" * filled + "." * (40 - filled), pct

def paso(i, titulo, desc):
    bar, pct = barra(i)
    print()
    print("=" * 72)
    print(f"  PASO {i}/{TOTAL}  [{bar}]  {pct:3d}%")
    print(f"  {titulo}")
    print(f"  -> {desc}")
    print("=" * 72)
    sys.stdout.flush()

# -- 1 --
paso(1, "Verificar path SPT-3G D1",
     "El path del handoff puede estar desactualizado. Verificar primero.")

print(f"  Path objetivo: {SPT_ROOT}")
print(f"  Existe: {SPT_ROOT.exists()}")

if not SPT_ROOT.exists():
    print()
    print("  ERROR: path no existe. Buscando alternativas...")
    alt_root = LAB / "data" / "extracted" / "zen_runtime"
    if alt_root.exists():
        candidatos = [d for d in alt_root.iterdir() if d.is_dir()
                      and "spt" in d.name.lower()]
        print(f"  Directorios con 'spt' encontrados en {alt_root}:")
        for c in candidatos:
            print(f"    {c}")
            for sub in c.iterdir():
                if sub.is_dir():
                    print(f"      -> {sub.name}")
    sys.exit(1)

# -- 2 --
paso(2, "Listar archivos del directorio",
     "Que hay realmente. Sin filtros, todo.")

files = sorted([f for f in SPT_ROOT.rglob("*") if f.is_file()])
print(f"  Total archivos: {len(files)}")
print(f"  Listado completo:")
for f in files:
    rel = f.relative_to(SPT_ROOT)
    size_kb = f.stat().st_size / 1024
    print(f"    {str(rel):60s}  {size_kb:10.2f} KB")

# -- 3 --
paso(3, "Leer metadata.json literal",
     "Sin interpretar. Reportar tal cual.")

meta_path = SPT_ROOT / "metadata.json"
if meta_path.exists():
    raw = meta_path.read_text(encoding="utf-8")
    try:
        meta = json.loads(raw)
        print(f"  metadata.json (pretty-printed):")
        print(json.dumps(meta, indent=4, ensure_ascii=False))
    except json.JSONDecodeError as e:
        print(f"  metadata.json no es JSON valido: {e}")
        print(f"  Contenido crudo:")
        print(raw)
else:
    print(f"  metadata.json NO EXISTE en {SPT_ROOT}")
    # Buscar en subdirectorios
    metas = list(SPT_ROOT.rglob("metadata*.json"))
    print(f"  metadata*.json encontrados recursivamente: {len(metas)}")
    for m in metas:
        print(f"    {m}")

# -- 4 --
paso(4, "Inspeccionar data_vector.npy y covariance.npy",
     "Shape, dtype, rango de valores")

dv_path = SPT_ROOT / "data_vector.npy"
cov_path = SPT_ROOT / "covariance.npy"

if dv_path.exists():
    dv = np.load(dv_path)
    print(f"  data_vector.npy:")
    print(f"    shape  = {dv.shape}")
    print(f"    dtype  = {dv.dtype}")
    print(f"    min    = {dv.min():.6e}")
    print(f"    max    = {dv.max():.6e}")
    print(f"    media  = {dv.mean():.6e}")
    print(f"    n_nan  = {np.sum(np.isnan(dv))}")
    print(f"    n_inf  = {np.sum(np.isinf(dv))}")
    print(f"    primeros 5: {dv.ravel()[:5]}")
    print(f"    ultimos 5:  {dv.ravel()[-5:]}")
else:
    print(f"  data_vector.npy NO EXISTE")

if cov_path.exists():
    cov = np.load(cov_path)
    print()
    print(f"  covariance.npy:")
    print(f"    shape  = {cov.shape}")
    print(f"    dtype  = {cov.dtype}")
    # Simetria
    if cov.ndim == 2 and cov.shape[0] == cov.shape[1]:
        asim = np.max(np.abs(cov - cov.T))
        print(f"    max|cov - cov.T| = {asim:.6e}")
        print(f"    diagonal min/max = {cov.diagonal().min():.6e} / {cov.diagonal().max():.6e}")
        # Verificar positivo definido via autovalores
        try:
            eigs = np.linalg.eigvalsh(cov)
            print(f"    autovalor min = {eigs.min():.6e}")
            print(f"    autovalor max = {eigs.max():.6e}")
            print(f"    cond number   = {eigs.max()/eigs.min():.6e}")
        except Exception as e:
            print(f"    no se pudo diagonalizar: {e}")
else:
    print(f"  covariance.npy NO EXISTE")

# -- 5 --
paso(5, "Buscar spectrum_metadata.tsv o similar",
     "Aqui deberia estar el mapeo de indices -> espectros")

candidatos_meta = [
    "spectrum_metadata.tsv",
    "spectrum_metadata.txt",
    "spectra.txt",
    "bandpowers.txt",
    "fields.txt"
]
encontrados = []
for c in candidatos_meta:
    p = SPT_ROOT / c
    if p.exists():
        encontrados.append(p)

# Tambien buscar recursivamente
encontrados += [m for m in SPT_ROOT.rglob("*.tsv") if m not in encontrados]
encontrados += [m for m in SPT_ROOT.rglob("spectrum*") if m.is_file() and m not in encontrados]

if encontrados:
    print(f"  Archivos de metadata encontrados: {len(encontrados)}")
    for m in encontrados:
        print()
        print(f"  --- {m.relative_to(SPT_ROOT)} ---")
        try:
            lines = m.read_text(encoding="utf-8").splitlines()
            print(f"  ({len(lines)} lineas totales, mostrando primeras 30)")
            for line in lines[:30]:
                print(f"    {line}")
            if len(lines) > 30:
                print(f"    ... ({len(lines)-30} lineas mas)")
        except Exception as e:
            print(f"  no se pudo leer: {e}")
else:
    print(f"  NO se encontro archivo de metadata de espectros")
    print(f"  Archivos .tsv/.txt en el directorio:")
    for f in SPT_ROOT.rglob("*.tsv"):
        print(f"    {f}")
    for f in SPT_ROOT.rglob("*.txt"):
        print(f"    {f}")

# -- 6 --
paso(6, "Conclusion: puede medir beta?",
     "Diagnostico honesto basado en la evidencia anterior")

# Heuristica basada en la razon n_data / n_espectros_posibles
# Si lmin=2, lmax=4095 -> 4094 multipolos por espectro
# Si data_vector tiene ~1360 elementos -> probablemente un solo espectro binned
if dv_path.exists():
    n_dv = dv.size
    print(f"  Elementos en data_vector: {n_dv}")
    print()
    print(f"  Analisis estructural:")
    print(f"    - Si contuviera TT,TE,EE full (2<=l<=4095):")
    print(f"      esperariamos ~3*4094 = 12282 elementos")
    print(f"    - Si contuviera TT,TE,EE,BB,EB,TB full:")
    print(f"      esperariamos ~6*4094 = 24564 elementos")
    print(f"    - Elementos reales: {n_dv}")
    print()
    if n_dv < 3000:
        print(f"  INTERPRETACION: data_vector es demasiado pequeno para")
        print(f"                  contener TT,TE,EE full. Posibilidades:")
        print(f"    (a) Contiene solo un espectro binned")
        print(f"    (b) Contiene rango l reducido")
        print(f"    (c) Esta comprimido/procesado")
        print()
        print(f"  Sin el spectrum_metadata legible, NO se puede determinar")
        print(f"  si hay EB/TB.")
    else:
        print(f"  data_vector tiene tamano suficiente para varios espectros.")
        print(f"  Ver spectrum_metadata.tsv para mapeo exacto.")
else:
    print(f"  No hay data_vector, no se puede concluir")

# Chequeo final de nombres de archivo
print()
print(f"  Busqueda en nombres de archivo por 'EB' o 'TB':")
hay_eb_tb = False
for f in SPT_ROOT.rglob("*"):
    name_upper = f.name.upper()
    if "EB" in name_upper or "TB" in name_upper:
        print(f"    ENCONTRADO: {f.relative_to(SPT_ROOT)}")
        hay_eb_tb = True
if not hay_eb_tb:
    print(f"    NINGUN archivo con 'EB' o 'TB' en el nombre")
    print(f"    (evidencia indirecta: probablemente solo T&E)")

t_total = time.time() - t0
print()
print("=" * 72)
print(f"  FIN E.3a   (duracion: {t_total:.2f}s)")
print("=" * 72)
print()
print("  Pega este output completo. Con esa informacion se decide:")
print("    - Si SPT-3G D1 sirve para medir beta -> E.3 directo")
print("    - Si no -> redirigir a CamSpec PR4 o ACT DR6")
