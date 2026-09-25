# -*- coding: utf-8 -*-
"""F.2b — Test de falsacion: w_Phi vs DESI DR2 + Pantheon+ (formato corregido)."""
import sys, json, hashlib, time
from pathlib import Path
import numpy as np
from scipy.optimize import minimize, approx_fprime
from scipy.integrate import quad

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
DESI_DIR = LAB / "data" / "raw" / "desi_dr2"
PAN_DIR = LAB / "data" / "raw" / "pantheon_plus"
OUT_DIR = LAB / "data" / "inventory"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TOTAL = 10
t0 = time.time()

def barra(i):
    pct = int(100 * i / TOTAL)
    filled = pct * 40 // 100
    return "=" * filled + "." * (40 - filled), pct

def paso(i, t, d=""):
    bar, pct = barra(i)
    print(); print("="*72)
    print(f"  PASO {i}/{TOTAL}  [{bar}]  {pct:3d}%")
    print(f"  {t}")
    if d: print(f"  -> {d}")
    print("="*72); sys.stdout.flush()

def sha256_file(path, chunk=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()

# ============================================================
# 1: Cargar DESI DR2 (formato: z value quantity)
# ============================================================
paso(1, "Cargar DESI DR2 BAO", "3 columnas: z, value, quantity")

desi_file = DESI_DIR / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
desi_cov_file = DESI_DIR / "desi_gaussian_bao_ALL_GCcomb_cov.txt"

# Parse manual
rows = []
with open(desi_file, encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        z = float(parts[0])
        val = float(parts[1])
        q = parts[2]
        rows.append((z, val, q))

print(f"  N mediciones: {len(rows)}")
z_bao = np.array([r[0] for r in rows])
val_bao = np.array([r[1] for r in rows])
q_bao = [r[2] for r in rows]

for z, v, q in rows:
    print(f"    z={z:.3f}  {v:.4f}  {q}")

# Cargar covarianza
cov_bao = np.loadtxt(desi_cov_file)
print(f"\n  cov shape: {cov_bao.shape}")
print(f"  SHA256 mean: {sha256_file(desi_file)[:32]}...")
print(f"  SHA256 cov:  {sha256_file(desi_cov_file)[:32]}...")

# Convertir quantities a indices
q_index = {"DV_over_rs": 0, "DM_over_rs": 1, "DH_over_rs": 2}

# ============================================================
# 2: Cargar Pantheon+ SNe
# ============================================================
paso(2, "Cargar Pantheon+ SNe", "columnas zCMB, m_b_corr, err")

ph_file = PAN_DIR / "Pantheon+SH0ES.dat"
ph_cov_file = PAN_DIR / "Pantheon+SH0ES_STAT+SYS.cov"

with open(ph_file, encoding="utf-8") as fh:
    header = fh.readline().strip().split()
print(f"  Columnas totales: {len(header)}")
print(f"  Primeras 15: {header[:15]}")

idx_z = header.index("zCMB")
idx_m = header.index("m_b_corr")
idx_err = header.index("m_b_corr_err_DIAG")
idx_is_cal = header.index("IS_CALIBRATOR")
idx_used = header.index("USED_IN_SH0ES_HF")

print(f"  idx zCMB: {idx_z}")
print(f"  idx m_b_corr: {idx_m}")
print(f"  idx m_b_corr_err_DIAG: {idx_err}")
print(f"  idx IS_CALIBRATOR: {idx_is_cal}")

# Leer datos (filtrado: USED_IN_SH0ES_HF = 1)
z_all, m_all, err_all = [], [], []
with open(ph_file, encoding="utf-8") as fh:
    fh.readline()  # skip header
    for line in fh:
        parts = line.split()
        if len(parts) < len(header):
            continue
        try:
            z = float(parts[idx_z])
            m = float(parts[idx_m])
            err = float(parts[idx_err])
            used = int(parts[idx_used])
            z_all.append(z); m_all.append(m); err_all.append(err)
        except (ValueError, IndexError):
            continue

z_all = np.array(z_all); m_all = np.array(m_all); err_all = np.array(err_all)
print(f"\n  Total SNe leidas: {len(z_all)}")

# Filtro z > 0.01 (evitar locales)
mask = z_all > 0.01
z_sn = z_all[mask]; m_sn = m_all[mask]; err_sn = err_all[mask]
print(f"  Tras corte z > 0.01: {len(z_sn)}")
print(f"  z range: {z_sn.min():.4f}..{z_sn.max():.4f}")
print(f"  SHA256 SH0ES.dat: {sha256_file(ph_file)[:32]}...")

# ============================================================
# 3: Modelo cosmologico
# ============================================================
paso(3, "Modelo w0-wa CPL", "Friedmann + distancias")

c_km_s = 299792.458
r_d_fid = 147.46  # Mpc (DESI DR2)
H0_fid = 67.36    # km/s/Mpc (Planck 2018 VI)
Om_r = 9.15e-5

def E_z(z, Om, w0, wa):
    a = 1.0 / (1.0 + z)
    f_de = (1.0 + z)**(3*(1 + w0 + wa)) * np.exp(-3*wa*z/(1.0 + z))
    Ode = 1.0 - Om - Om_r
    return np.sqrt(Om*(1+z)**3 + Om_r*(1+z)**4 + Ode*f_de)

def D_M_z(z, Om, w0, wa):
    f = lambda zp: c_km_s / (H0_fid * E_z(zp, Om, w0, wa))
    val, _ = quad(f, 0, z, limit=50)
    return val

def D_H_z(z, Om, w0, wa):
    return c_km_s / (H0_fid * E_z(z, Om, w0, wa))

def D_V_z(z, Om, w0, wa):
    dm = D_M_z(z, Om, w0, wa)
    dh = D_H_z(z, Om, w0, wa)
    return (z * dm**2 * dh)**(1.0/3.0)

def pred_bao(z_array, q_list, Om, w0, wa):
    out = np.zeros(len(z_array))
    for i, (z, q) in enumerate(zip(z_array, q_list)):
        if q == "DV_over_rs":
            out[i] = D_V_z(z, Om, w0, wa) / r_d_fid
        elif q == "DM_over_rs":
            out[i] = D_M_z(z, Om, w0, wa) / r_d_fid
        elif q == "DH_over_rs":
            out[i] = D_H_z(z, Om, w0, wa) / r_d_fid
    return out

def mu_z(z_array, Om, w0, wa):
    out = np.zeros(len(z_array))
    for i, z in enumerate(z_array):
        dm = D_M_z(z, Om, w0, wa)
        dl = (1.0 + z) * dm
        out[i] = 5.0 * np.log10(dl * 1e5)
    return out

# Test fiducial
r_bao_fid = val_bao - pred_bao(z_bao, q_bao, 0.31, -1.0, 0.0)
chi2_bao_fid = float(r_bao_fid @ np.linalg.solve(cov_bao, r_bao_fid))
print(f"  chi2 DESI fiducial: {chi2_bao_fid:.2f} / dof={len(val_bao)}")

# ============================================================
# 4: Modelo SNe
# ============================================================
paso(4, "Modelo SNe + marginalizacion M_B")

def M_best(Om, w0, wa):
    mu_th = mu_z(z_sn, Om, w0, wa)
    w = 1.0 / err_sn**2
    return np.sum(w * (m_sn - mu_th)) / np.sum(w)

def chi2_sn(Om, w0, wa):
    M = M_best(Om, w0, wa)
    mu_th = mu_z(z_sn, Om, w0, wa)
    r = m_sn - (mu_th + M)
    return float(np.sum((r / err_sn)**2))

chi2_sn_fid = chi2_sn(0.31, -1.0, 0.0)
print(f"  chi2 SNe fiducial: {chi2_sn_fid:.2f} / N={len(z_sn)}")

# ============================================================
# 5: Chi2 conjunto
# ============================================================
paso(5, "Chi2 conjunto + margenes")

def chi2_total(params):
    Om, w0, wa = params
    if not (0.15 < Om < 0.55): return 1e10
    if not (-2 < w0 < 0):      return 1e10
    if not (-3 < wa < 2):      return 1e10
    r_bao = val_bao - pred_bao(z_bao, q_bao, Om, w0, wa)
    chi2_bao = float(r_bao @ np.linalg.solve(cov_bao, r_bao))
    return chi2_bao + chi2_sn(Om, w0, wa)

chi2_lcdm = chi2_total([0.31, -1.0, 0.0])
print(f"  chi2 total LCDM: {chi2_lcdm:.2f}")

# ============================================================
# 6: Optimizacion
# ============================================================
paso(6, "Ajuste conjunto {Om, w0, wa}")

best = minimize(chi2_total, x0=[0.31, -1.0, 0.0],
                method="Nelder-Mead",
                options={"xatol": 1e-5, "fatol": 1e-4, "maxiter": 5000})
Om_best, w0_best, wa_best = best.x
chi2_best = best.fun

print(f"  Om = {Om_best:.4f}")
print(f"  w0 = {w0_best:.4f}")
print(f"  wa = {wa_best:.4f}")
print(f"  chi2 = {chi2_best:.2f}")

# ============================================================
# 7: Hessiana + sigmas
# ============================================================
paso(7, "Sigmas via Hessiana numerica")

eps = 1e-4
H = np.zeros((3, 3))
x0_arr = np.array([Om_best, w0_best, wa_best])
for i in range(3):
    for j in range(3):
        xpp = x0_arr.copy(); xpp[i] += eps; xpp[j] += eps
        xpm = x0_arr.copy(); xpm[i] += eps; xpm[j] -= eps
        xmp = x0_arr.copy(); xmp[i] -= eps; xmp[j] += eps
        xmm = x0_arr.copy(); xmm[i] -= eps; xmm[j] -= eps
        H[i,j] = (chi2_total(xpp) - chi2_total(xpm) - chi2_total(xmp) + chi2_total(xmm)) / (4*eps**2)

try:
    cov = 2 * np.linalg.inv(H)
    sigmas = np.sqrt(np.diag(cov))
    print(f"  sigma_Om = {sigmas[0]:.4f}")
    print(f"  sigma_w0 = {sigmas[1]:.4f}")
    print(f"  sigma_wa = {sigmas[2]:.4f}")
except Exception as e:
    print(f"  ERROR: {e}")
    sigmas = None
    cov = None

# ============================================================
# 8: w(z) con sigma(z)
# ============================================================
paso(8, "w(z) y test de falsacion")

z_test = np.array([0.0, 0.3, 0.5, 1.0, 1.5, 2.0])
w_test = w0_best + wa_best * z_test / (1 + z_test)

print(f"  {'z':>5s}  {'w(z)':>10s}  {'sigma_w':>10s}  {'(w+1)/sigma':>14s}")
puntos_falsacion = []
for z, w in zip(z_test, w_test):
    f_z = z / (1 + z)
    if sigmas is not None:
        var_w = sigmas[1]**2 + 2*cov[1,2]*f_z + sigmas[2]**2 * f_z**2
        sig_w = np.sqrt(max(var_w, 0))
        tension = (w + 1) / sig_w if sig_w > 0 else 0
        print(f"  {z:5.2f}  {w:10.4f}  {sig_w:10.4f}  {tension:14.4f}")
        if tension < -3:
            puntos_falsacion.append({"z": float(z), "w": float(w), "tension": float(tension)})
    else:
        print(f"  {z:5.2f}  {w:10.4f}  N/A  N/A")

# Veredicto
if puntos_falsacion:
    veredicto = "FALSACION_POTENCIAL"
elif sigmas is not None and (w0_best + 1) / sigmas[1] < -3:
    veredicto = "TENSION_SIGNIFICATIVA_w0"
else:
    veredicto = "NO_FALSACION"

print(f"\n  VEREDICTO: {veredicto}")

# ============================================================
# 9: Guardar
# ============================================================
paso(9, "Guardar resultado")

resultado = {
    "fase": "F.2b",
    "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "datos": {
        "DESI_DR2": {
            "archivo": str(desi_file.name),
            "sha256": sha256_file(desi_file),
            "n": int(len(val_bao)),
        },
        "Pantheon_plus": {
            "archivo": str(ph_file.name),
            "sha256": sha256_file(ph_file),
            "n_sne_tras_corte": int(len(z_sn)),
        },
    },
    "ajuste": {
        "modelo": "w0-wa CPL",
        "Om": float(Om_best),
        "w0": float(w0_best),
        "wa": float(wa_best),
        "sigma_Om": float(sigmas[0]) if sigmas is not None else None,
        "sigma_w0": float(sigmas[1]) if sigmas is not None else None,
        "sigma_wa": float(sigmas[2]) if sigmas is not None else None,
        "chi2": float(chi2_best),
        "chi2_LCDM": float(chi2_lcdm),
        "dof": int(len(val_bao) + len(z_sn) - 3),
    },
    "w_z": {
        "z": list(z_test),
        "w": list(w_test),
    },
    "cota_THU": "w_Phi >= -1 (PDF 14)",
    "veredicto": veredicto,
    "puntos_falsacion": puntos_falsacion,
}
out = OUT_DIR / "fase_f2b_w_phi_desi.json"
out.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"  Guardado: {out}")

# ============================================================
# 10: Resumen
# ============================================================
paso(10, "RESUMEN F.2b")

print(f"  Ajuste conjunto DESI DR2 + Pantheon+ (w0-wa CPL):")
print(f"    Om = {Om_best:.4f}" + (f" +/- {sigmas[0]:.4f}" if sigmas is not None else ""))
print(f"    w0 = {w0_best:.4f}" + (f" +/- {sigmas[1]:.4f}" if sigmas is not None else ""))
print(f"    wa = {wa_best:.4f}" + (f" +/- {sigmas[2]:.4f}" if sigmas is not None else ""))
print(f"    chi2 = {chi2_best:.2f} (LCDM: {chi2_lcdm:.2f})")
print()
print(f"  Test de falsacion THU-TBEA:")
print(f"    Cota: w_Phi >= -1")
print(f"    Puntos con w < -1 a >3 sigma: {len(puntos_falsacion)}")
print(f"    VEREDICTO: {veredicto}")
print()
print(f"  Tiempo total: {time.time()-t0:.1f}s")
