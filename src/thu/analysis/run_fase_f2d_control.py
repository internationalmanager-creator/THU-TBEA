# -*- coding: utf-8 -*-
"""Control: verificar filtro de SNe."""
import numpy as np
from pathlib import Path

PAN = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto\data\raw\pantheon_plus")
ph = PAN / "Pantheon+SH0ES.dat"

with open(ph) as fh:
    header = fh.readline().strip().split()
idx_z = header.index("zCMB")
idx_m = header.index("m_b_corr")
idx_err = header.index("m_b_corr_err_DIAG")
idx_cal = header.index("IS_CALIBRATOR")
idx_used = header.index("USED_IN_SH0ES_HF")

# Cargar todo
z_all, m_all, err_all, cal_all, used_all = [], [], [], [], []
with open(ph) as fh:
    fh.readline()
    for line in fh:
        p = line.split()
        if len(p) < len(header): continue
        z_all.append(float(p[idx_z]))
        m_all.append(float(p[idx_m]))
        err_all.append(float(p[idx_err]))
        cal_all.append(int(p[idx_cal]))
        used_all.append(int(p[idx_used]))

z = np.array(z_all); m = np.array(m_all); err = np.array(err_all)
cal = np.array(cal_all); used = np.array(used_all)

print("=== ANALISIS DE FILTROS ===")
print(f"Total SNe: {len(z)}")
print()

# Filtros
print("Escenario A — mi filtro actual (z > 0.01):")
mask_A = z > 0.01
print(f"  N: {mask_A.sum()}")
print(f"  Incluye calibradoras: {cal[mask_A].sum()}")
print(f"  Incluye USED_IN_SH0ES_HF=1: {used[mask_A].sum()}")

print()
print("Escenario B — filtro oficial Pantheon+ cosmologia:")
mask_B = (used == 0) & (cal == 0) & (z > 0.01)
print(f"  N: {mask_B.sum()}")
print(f"  z range: {z[mask_B].min():.4f}..{z[mask_B].max():.4f}")

print()
print("Escenario C — solo cosmologicas (USED_IN_SH0ES_HF=0):")
mask_C = (used == 0)
print(f"  N: {mask_C.sum()}")

print()
print("=== DISTRIBUCION DE ERRORES ===")
for label, mask in [("Todo", np.ones_like(z, bool)),
                     ("A (mi filtro)", mask_A),
                     ("B (oficial)", mask_B)]:
    e = err[mask]
    print(f"  {label:20s}: min={e.min():.4f}, med={np.median(e):.4f}, max={e.max():.4f}")

print()
print("=== ESTADISTICAS DE m_b_corr ===")
for label, mask in [("A", mask_A), ("B", mask_B)]:
    mm = m[mask]
    print(f"  {label}: media={mm.mean():.3f}, std={mm.std():.3f}, "
          f"min={mm.min():.3f}, max={mm.max():.3f}")

# Chequear duplicados
print()
print("=== DUPLICADOS (CID repetidos) ===")
with open(ph) as fh:
    header_full = fh.readline().strip().split()
idx_cid = header_full.index("CID")
cids = []
with open(ph) as fh:
    fh.readline()
    for line in fh:
        p = line.split()
        if len(p) < len(header_full): continue
        cids.append(p[idx_cid])

from collections import Counter
cnt = Counter(cids)
dupes = {k: v for k, v in cnt.items() if v > 1}
print(f"  CIDs unicos: {len(cnt)}")
print(f"  CIDs duplicados: {len(dupes)}")
print(f"  Total filas duplicadas: {sum(v-1 for v in dupes.values())}")
if dupes:
    for k, v in list(dupes.items())[:5]:
        print(f"    {k}: {v} veces")
