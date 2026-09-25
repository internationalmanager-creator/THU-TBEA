# -*- coding: utf-8 -*-
"""F.2c-recon — Inspeccionar TODOS los formatos ANTES de escribir analisis."""
import sys
from pathlib import Path
import numpy as np

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
DESI_DIR = LAB / "data" / "raw" / "desi_dr2"
PAN_DIR = LAB / "data" / "raw" / "pantheon_plus"

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# 1: DESI mean (ya conocido)
hdr("1. DESI mean.txt — confirmar formato")
f = DESI_DIR / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
lines = f.read_text().splitlines()
print(f"  Lineas: {len(lines)}")
for i, l in enumerate(lines[:5]):
    print(f"    L{i}: {l!r}")

# 2: DESI cov
hdr("2. DESI cov.txt — confirmar formato")
f = DESI_DIR / "desi_gaussian_bao_ALL_GCcomb_cov.txt"
lines = f.read_text().splitlines()
print(f"  Lineas: {len(lines)}")
print(f"  Primera linea tiene {len(lines[0].split())} tokens")
for i, l in enumerate(lines[:3]):
    print(f"    L{i}: {l[:150]}")

# 3: Pantheon+ .cov — formato real
hdr("3. Pantheon+ .cov — formato completo")
f = PAN_DIR / "Pantheon+SH0ES_STAT+SYS.cov"
with open(f) as fh:
    lines = [fh.readline().strip() for _ in range(5)]
    # Contar total
    total = 5
    for _ in fh:
        total += 1

print(f"  Total lineas: {total}")
print(f"  L0 (header?): {lines[0]!r}")
print(f"  L1:           {lines[1]!r}")
print(f"  L2:           {lines[2]!r}")
print(f"  L3:           {lines[3]!r}")
print(f"  L4:           {lines[4]!r}")
print()
N_header = int(lines[0])
print(f"  N del header: {N_header}")
print(f"  N^2: {N_header**2}")
print(f"  Lineas - 1: {total - 1}")
print(f"  Coincide: {N_header**2 == total - 1}")
print()
print(f"  ==> Formato: header con N, luego N^2 valores en lineas separadas")

# 4: Pantheon+ SH0ES.dat — confirmar columnas
hdr("4. Pantheon+ SH0ES.dat")
f = PAN_DIR / "Pantheon+SH0ES.dat"
with open(f) as fh:
    header = fh.readline().strip().split()
    first_data = fh.readline().strip().split()
print(f"  N columnas: {len(header)}")
for i, (h, v) in enumerate(zip(header[:12], first_data[:12])):
    print(f"    [{i:2d}] {h:25s}  = {v}")

# 5: Cuantos SNe tienen USED_IN_SH0ES_HF=1 vs 0
hdr("5. Distribucion de IS_CALIBRATOR y USED_IN_SH0ES_HF")
idx_cal = header.index("IS_CALIBRATOR")
idx_used = header.index("USED_IN_SH0ES_HF")
idx_z = header.index("zCMB")
n_total = 0; n_used = 0; n_cal = 0; n_z_gt_01 = 0
with open(f) as fh:
    fh.readline()
    for line in fh:
        parts = line.split()
        if len(parts) < len(header): continue
        n_total += 1
        if int(parts[idx_used]) == 1: n_used += 1
        if int(parts[idx_cal]) == 1: n_cal += 1
        if float(parts[idx_z]) > 0.01: n_z_gt_01 += 1
print(f"  Total SNe: {n_total}")
print(f"  USED_IN_SH0ES_HF=1: {n_used}")
print(f"  IS_CALIBRATOR=1: {n_cal}")
print(f"  z > 0.01: {n_z_gt_01}")
