# -*- coding: utf-8 -*-
"""
FASE E.1 — Reconocimiento.
Lista archivos, lee metadata.json, identifica data vectors y covarianzas.
SIN asumir nada. Si algo no está, se reporta.
"""
import sys, json, time
from pathlib import Path
import numpy as np

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
EXT = LAB / "data" / "extracted" / "zen_runtime"

TOTAL = 6
t0 = time.time()

def barra(i):
    pct = int(100 * i / TOTAL)
    filled = pct * 40 // 100
    return "█" * filled + "░" * (40 - filled), pct

def paso(i, titulo, desc):
    bar, pct = barra(i)
    print()
    print("═" * 72)
    print(f"  PASO {i}/{TOTAL}  [{bar}]  {pct:3d}%")
    print(f"  {titulo}")
    print(f"  → {desc}")
    print("═" * 72)
    sys.stdout.flush()

def listar_arbol(d, max_depth=3):
    """Lista archivos con tamaño, hasta max_depth niveles."""
    if not d.exists():
        print(f"  NO EXISTE: {d}")
        return []
    items = []
    for p in sorted(d.rglob("*")):
        if p.is_file():
            rel = p.relative_to(d)
            depth = len(rel.parts)
            if depth <= max_depth:
                items.append((str(rel), p.stat().st_size))
    return items

def leer_metadata(d):
    """Lee el primer metadata.json que encuentre."""
    mds = list(d.rglob("metadata.json"))
    if not mds:
        return None
    try:
        return json.loads(mds[0].read_text(encoding="utf-8"))
    except Exception as e:
        return {"__error__": str(e)}

def explorar_likelihood(nombre, ruta):
    """Explora un directorio de likelihood y reporta estructura."""
    print(f"\n  ─── {nombre} ───")
    if not ruta.exists():
        print(f"  ✗ NO EXISTE: {ruta}")
        return None

    archivos = listar_arbol(ruta, max_depth=4)
    print(f"  Archivos ({len(archivos)}):")
    for rel, sz in archivos[:30]:
        kb = sz / 1024
        if kb > 1024:
            print(f"    {rel:65s}  {kb/1024:.2f} MB")
        else:
            print(f"    {rel:65s}  {kb:.1f} KB")

    if len(archivos) > 30:
        print(f"    ... ({len(archivos)-30} más)")

    md = leer_metadata(ruta)
    if md:
        print(f"\n  Metadata keys: {list(md.keys())[:10]}")
        for k in list(md.keys())[:6]:
            v = md[k]
            if isinstance(v, (str, int, float, bool)):
                print(f"    {k}: {v}")
            elif isinstance(v, list):
                print(f"    {k}: [list de {len(v)}]")
            elif isinstance(v, dict):
                print(f"    {k}: {{dict con keys {list(v.keys())[:5]}}}")

    return {"archivos": archivos, "metadata": md}

resultados = {}

# ── 1: CamSpec PR4 TTTEEE ──
paso(1, "CamSpec PR4 TTTEEE (Planck NPIPE)",
    "Verificar qué archivos hay: data vector, covariance, metadata")
ruta = EXT / "Planck_NPIPE_CamSpec_PR4_TTTEEE_likelihood_runtime" / "CamSpec_PR4_TTTEEE_v1_20260919"
resultados["camspec_pr4"] = explorar_likelihood("CamSpec PR4", ruta)

# ── 2: ACT DR6 TTTEEE ──
paso(2, "ACT DR6 TTTEEE",
    "Verificar estructura del likelihood ACT")
ruta = EXT / "ACT_DR6_full_multifrequency_TT_TE_EE_likelihood_ru" / "ACT_DR6_TTTEEE_v1_20260917"
resultados["act_dr6"] = explorar_likelihood("ACT DR6 TTTEEE", ruta)

# ── 3: SPT-3G D1 T&E ──
paso(3, "SPT-3G D1 T&E",
    "Verificar estructura de la likelihood SPT más pequeña")
ruta = EXT / "SPT_3G_D1_T_E_likelihood_runtime_data_for_SPTLikel" / "SPT3G_D1_TnE_v0_20260917"
resultados["spt3g_d1"] = explorar_likelihood("SPT-3G D1", ruta)

# ── 4: JointCMB planck ──
paso(4, "JointCMB Planck PR4",
    "Runtime data conjunto para JointCMBLikelihoods.jl")
ruta = EXT / "Joint_Planck_PR4_likelihood_runtime_data_for_Joint" / "JointCMB_planck_v1_20260919"
resultados["jointcmb_planck"] = explorar_likelihood("JointCMB Planck", ruta)

# ── 5: cmblite ──
paso(5, "CMB Lite CamSpec",
    "Versión lite del likelihood CamSpec")
ruta = EXT / "CMB_Lite_Likelihood_Data" / "cmblite_data" / "cmblite_data"
resultados["cmblite"] = explorar_likelihood("CMB Lite", ruta)

# ── 6: Buscar TODOS los .npy del proyecto ──
paso(6, "Todos los .npy en el proyecto",
    "Mapa completo de matrices/arrays disponibles")

print("\n  Escaneando todos los .npy...")
npy_files = []
for p in EXT.rglob("*.npy"):
    sz = p.stat().st_size
    npy_files.append((str(p.relative_to(EXT)), sz))

npy_files.sort(key=lambda x: -x[1])
print(f"  Total .npy: {len(npy_files)}")
print("\n  Top 15 por tamaño:")
for rel, sz in npy_files[:15]:
    mb = sz / 1024 / 1024
    print(f"    {rel:70s}  {mb:6.2f} MB")
    try:
        arr = np.load(EXT / rel, mmap_mode="r")
        print(f"      shape={arr.shape}  dtype={arr.dtype}")
    except Exception as e:
        print(f"      ERROR: {e}")

# Guardar reporte completo
reporte = {
    "likelihoods": {k: {"archivos": v["archivos"][:50] if v else None,
                        "metadata_keys": list(v["metadata"].keys()) if v and v["metadata"] else None}
                    for k, v in resultados.items()},
    "npy_files": [{"path": r, "bytes": s} for r, s in npy_files[:30]]
}

rep_path = LAB / "data" / "inventory" / "recon_fase_e.json"
rep_path.write_text(json.dumps(reporte, indent=2, ensure_ascii=False), encoding="utf-8")

t_total = time.time() - t0
print()
print("╔" + "═" * 70 + "╗")
print("║" + " RESUMEN FASE E.1 ".center(70) + "║")
print("╚" + "═" * 70 + "╝")
print(f"  Duración: {t_total:.2f}s")
print(f"  Reporte:  {rep_path}")
print()
print("  → Con este mapa decidimos qué likelihood usar y cómo cargarla.")
