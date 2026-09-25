# -*- coding: utf-8 -*-
"""F.2a — Inspeccionar formato exacto de DESI DR2 y Pantheon+."""
import sys
from pathlib import Path

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
DESI_DIR = LAB / "data" / "raw" / "desi_dr2"
PANTHEON_DIR = LAB / "data" / "raw" / "pantheon_plus"

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# --- 1: DESI mean (completo) ---
hdr("1. DESI DR2 mean.txt (completo, primeras 30 lineas)")

for fname in ["desi_gaussian_bao_ALL_GCcomb_mean.txt",
              "desi_2024_gaussian_bao_ALL_GCcomb_mean.txt"]:
    f = DESI_DIR / fname
    print(f"\n  --- {fname} ---")
    if not f.exists():
        print(f"    NO EXISTE")
        continue
    lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
    print(f"  Total lineas: {len(lines)}")
    for i, l in enumerate(lines[:30], 1):
        print(f"    L{i:3d}: {l}")
    if len(lines) > 30:
        print(f"    ... ({len(lines)-30} mas)")

# --- 2: DESI cov (primeras lineas) ---
hdr("2. DESI DR2 cov.txt (primeras 5 lineas)")

for fname in ["desi_gaussian_bao_ALL_GCcomb_cov.txt",
              "desi_2024_gaussian_bao_ALL_GCcomb_cov.txt"]:
    f = DESI_DIR / fname
    print(f"\n  --- {fname} ---")
    if not f.exists():
        print(f"    NO EXISTE")
        continue
    lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
    print(f"  Total lineas: {len(lines)}")
    for i, l in enumerate(lines[:8], 1):
        # Truncar cada linea si es larga
        l_disp = l if len(l) < 200 else l[:200] + "..."
        print(f"    L{i}: {l_disp}")

# --- 3: Manifest DESI ---
hdr("3. DESI _manifest.json")
mf = DESI_DIR / "_manifest.json"
if mf.exists():
    print(mf.read_text(encoding="utf-8"))

# --- 4: Pantheon+ SH0ES.dat header (primeras 3 lineas) ---
hdr("4. Pantheon+SH0ES.dat (header + 3 filas)")

ph = PANTHEON_DIR / "Pantheon+SH0ES.dat"
if ph.exists():
    with open(ph, encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            if i >= 4:
                break
            # Truncar
            l_disp = line.rstrip()
            if len(l_disp) > 200:
                l_disp = l_disp[:200] + "... (truncado)"
            print(f"  L{i}: {l_disp}")

# --- 5: Pantheon manifest ---
hdr("5. Pantheon _manifest.json")
mf = PANTHEON_DIR / "_manifest.json"
if mf.exists():
    print(mf.read_text(encoding="utf-8"))
