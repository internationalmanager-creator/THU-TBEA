# -*- coding: utf-8 -*-
"""Verificacion TOTAL antes del analisis. Sin asumir NADA."""
import sys, hashlib
from pathlib import Path
import numpy as np

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
PAN = LAB / "data" / "raw" / "pantheon_plus"

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# ============================================================
# 1: Leer header completo y verificar columnas
# ============================================================
hdr("1. Header completo Pantheon+SH0ES.dat")
ph = PAN / "Pantheon+SH0ES.dat"
with open(ph) as fh:
    header = fh.readline().strip().split()
print(f"  {len(header)} columnas:")
for i, h in enumerate(header):
    print(f"    [{i:2d}] {h}")

# ============================================================
# 2: Estadisticas por subgrupo
# ============================================================
hdr("2. Estadisticas por subgrupo")

idx_z = header.index("zCMB")
idx_m = header.index("m_b_corr")
idx_err = header.index("m_b_corr_err_DIAG")
idx_cal = header.index("IS_CALIBRATOR")
idx_used = header.index("USED_IN_SH0ES_HF")

# Cargar todo con todos los indices
rows = []
with open(ph) as fh:
    fh.readline()
    for line in fh:
        p = line.split()
        if len(p) < len(header): continue
        rows.append({
            "z": float(p[idx_z]),
            "m": float(p[idx_m]),
            "err": float(p[idx_err]),
            "cal": int(p[idx_cal]),
            "used": int(p[idx_used]),
        })

def stats(rows, label):
    if not rows:
        print(f"  {label}: VACIO")
        return
    z = np.array([r["z"] for r in rows])
    m = np.array([r["m"] for r in rows])
    e = np.array([r["err"] for r in rows])
    print(f"  {label:40s}: N={len(rows):4d}, "
          f"z=[{z.min():.3f},{z.max():.3f}], "
          f"m=[{m.min():.2f},{m.max():.2f}], "
          f"err med={np.median(e):.4f}")

# Subgrupos
stats(rows, "TODAS")
stats([r for r in rows if r["z"]>0.01], "z>0.01")
stats([r for r in rows if r["cal"]==1], "IS_CALIBRATOR=1")
stats([r for r in rows if r["used"]==1], "USED_IN_SH0ES_HF=1")
stats([r for r in rows if r["cal"]==1 and r["z"]>0.01], "Calibrators con z>0.01")
stats([r for r in rows if r["z"]>0.01 and r["cal"]==0 and r["used"]==0],
      "z>0.01 & cal=0 & used=0")
stats([r for r in rows if r["z"]>0.01 and r["used"]==0],
      "z>0.01 & used=0")

# ============================================================
# 3: Verificar duplicados
# ============================================================
hdr("3. Analisis de duplicados CIDs")

idx_cid = header.index("CID")
cids = []
with open(ph) as fh:
    fh.readline()
    for line in fh:
        p = line.split()
        if len(p) < len(header): continue
        cids.append(p[idx_cid])

from collections import Counter
cnt = Counter(cids)
dupes = {k:v for k,v in cnt.items() if v > 1}
print(f"  CIDs unicos: {len(cnt)}")
print(f"  CIDs con 2+ filas: {len(dupes)}")

# Verificar: los duplicados ¿tienen mismo z, distinto survey?
print(f"\n  Primeros 5 duplicados:")
dup_cids = list(dupes.keys())[:5]
with open(ph) as fh:
    fh.readline()
    for line in fh:
        p = line.split()
        if len(p) < len(header): continue
        if p[idx_cid] in dup_cids:
            print(f"    CID={p[idx_cid]:10s}, IDSURVEY={p[1]}, z={p[idx_z]}, m={p[idx_m]}")

# ============================================================
# 4: Comparar diag de STAT+SYS con err_DIAG
# ============================================================
hdr("4. Diagonal STAT+SYS vs err_DIAG (para primeras 10 filas)")

cov_file = PAN / "Pantheon+SH0ES_STAT+SYS.cov"
with open(cov_file) as fh:
    N = int(fh.readline().strip())
    vals = np.fromfile(fh, sep="\n", dtype=np.float64)
cov = vals.reshape(N, N)
print(f"  N: {N}, cov shape: {cov.shape}")

with open(ph) as fh:
    fh.readline()
    first10 = [fh.readline().split() for _ in range(10)]

print(f"\n  {'i':>3s}  {'CID':>10s}  {'err_DIAG':>10s}  {'sqrt(cov_ii)':>14s}  {'ratio':>8s}")
for i in range(10):
    p = first10[i]
    err_diag = float(p[idx_err])
    sqrt_cov = np.sqrt(cov[i,i])
    ratio = err_diag / sqrt_cov
    print(f"  {i:3d}  {p[idx_cid]:>10s}  {err_diag:10.4f}  {sqrt_cov:14.4f}  {ratio:8.3f}")

# ============================================================
# 5: Chi2 con BAO + SNe por subgrupo (con cov correcta)
# ============================================================
hdr("5. Test chi2 con distintos filtros")

# BAO
desi = LAB / "data" / "raw" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
bao_rows = []
with open(desi) as fh:
    for l in fh:
        l = l.strip()
        if not l or l.startswith("#"): continue
        p = l.split()
        bao_rows.append((float(p[0]), float(p[1]), p[2]))
z_bao = np.array([r[0] for r in bao_rows])
val_bao = np.array([r[1] for r in bao_rows])
q_bao = [r[2] for r in bao_rows]
cov_bao = np.loadtxt(LAB / "data" / "raw" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt")

# Modelo simple LCDM
from scipy.integrate import quad
c_km_s = 299792.458
r_d = 147.46
H0 = 67.36
Om_r = 9.15e-5

def E_z_LCDM(z, Om):
    Ode = 1 - Om - Om_r
    return np.sqrt(Om*(1+z)**3 + Om_r*(1+z)**4 + Ode)

def D_M_z_LCDM(z, Om):
    return quad(lambda zp: c_km_s/(H0*E_z_LCDM(zp, Om)), 0, z)[0]

def D_H_z_LCDM(z, Om):
    return c_km_s/(H0*E_z_LCDM(z, Om))

def D_V_z_LCDM(z, Om):
    dm = D_M_z_LCDM(z, Om); dh = D_H_z_LCDM(z, Om)
    return (z*dm**2*dh)**(1/3)

def pred_bao_LCDM(Om):
    out = np.zeros(len(z_bao))
    for i, (z, q) in enumerate(zip(z_bao, q_bao)):
        if q == "DV_over_rs": out[i] = D_V_z_LCDM(z, Om)/r_d
        elif q == "DM_over_rs": out[i] = D_M_z_LCDM(z, Om)/r_d
        elif q == "DH_over_rs": out[i] = D_H_z_LCDM(z, Om)/r_d
    return out

# Chi2 BAO para Om=0.31
r = val_bao - pred_bao_LCDM(0.31)
chi2_bao = r @ np.linalg.solve(cov_bao, r)
print(f"  chi2 BAO LCDM (Om=0.31): {chi2_bao:.2f} / 13")

# Para SNe: calculo chi2 solo para subgrupos, con M_B marginalizado
def chi2_sn_subset(rows_sub, idx_orig_list):
    # Extraer cov submatriz
    cov_sub = cov[np.ix_(idx_orig_list, idx_orig_list)]
    try:
        inv = np.linalg.inv(cov_sub)
    except:
        inv = np.linalg.pinv(cov_sub)
    z = np.array([r["z"] for r in rows_sub])
    m = np.array([r["m"] for r in rows_sub])
    # Modelo LCDM
    mu = np.zeros(len(z))
    for i, zz in enumerate(z):
        dm = D_M_z_LCDM(zz, 0.31)
        dl = (1+zz)*dm
        mu[i] = 5*np.log10(dl*1e5)
    r = m - mu
    Cinv_r = inv @ r
    Cinv_1 = inv @ np.ones(len(r))
    M = np.sum(Cinv_r)/np.sum(Cinv_1)
    r_M = r - M
    return float(r_M @ inv @ r_M)

# Preparar indices para subgrupos
with open(ph) as fh:
    fh.readline()
    all_rows = []
    for i_line, line in enumerate(fh):
        p = line.split()
        if len(p) < len(header): continue
        all_rows.append((i_line, {
            "z": float(p[idx_z]),
            "m": float(p[idx_m]),
            "err": float(p[idx_err]),
            "cal": int(p[idx_cal]),
            "used": int(p[idx_used]),
        }))

subsets = {
    "z>0.01 (mi filtro)": [(i, r) for i, r in all_rows if r["z"] > 0.01],
    "z>0.01 & used=0": [(i, r) for i, r in all_rows if r["z"] > 0.01 and r["used"] == 0],
    "z>0.01 & used=0 & cal=0": [(i, r) for i, r in all_rows if r["z"] > 0.01 and r["used"] == 0 and r["cal"] == 0],
}

for label, subset in subsets.items():
    idx_list = [i for i, _ in subset]
    rows_only = [r for _, r in subset]
    try:
        c2 = chi2_sn_subset(rows_only, idx_list)
        print(f"  chi2 SN LCDM {label:30s}: {c2:.2f} / {len(rows_only)}")
    except Exception as e:
        print(f"  ERROR {label}: {e}")

print()
print("=" * 72)
print("  VERIFICACION COMPLETA")
print("=" * 72)
