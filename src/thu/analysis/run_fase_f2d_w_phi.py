# -*- coding: utf-8 -*-
"""F.2d — Analisis refinado con covarianza Pantheon+ completa (formato verificado)."""
import sys, json, hashlib, time
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.integrate import quad

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
DESI_DIR = LAB / "data" / "raw" / "desi_dr2"
PAN_DIR = LAB / "data" / "raw" / "pantheon_plus"
REG = LAB / "registry" / "thu"
OUT_DIR = LAB / "data" / "inventory"

TOTAL = 9
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
# 1: Cargar covarianza Pantheon+ completa (formato confirmado)
# ============================================================
paso(1, "Cargar Pantheon+ cov completa", "header N + N^2 valores")

cov_file = PAN_DIR / "Pantheon+SH0ES_STAT+SYS.cov"
print(f"  Cargando... (32 MB, formato header + N^2 lineas)")

t_load = time.time()
with open(cov_file) as fh:
    N_cov = int(fh.readline().strip())
    values = np.fromfile(fh, sep="\n", dtype=np.float64)

print(f"  N del header: {N_cov}")
print(f"  Valores leidos: {len(values)}")
print(f"  Esperado N^2: {N_cov**2}")
assert len(values) == N_cov**2, "Mismatch N^2"

cov_full = values.reshape(N_cov, N_cov)
print(f"  cov shape: {cov_full.shape}")
print(f"  Diagonal[min,max]: {cov_full.diagonal().min():.4e}, {cov_full.diagonal().max():.4e}")
print(f"  max|cov - cov.T|: {np.max(np.abs(cov_full - cov_full.T)):.4e}")
print(f"  Cargado en {time.time()-t_load:.1f}s")
print(f"  SHA256: {sha256_file(cov_file)[:32]}...")

# ============================================================
# 2: Cargar Pantheon+ data + filtrar coherentemente
# ============================================================
paso(2, "Cargar Pantheon+ data + filtro z>0.01")

ph_file = PAN_DIR / "Pantheon+SH0ES.dat"
with open(ph_file) as fh:
    header = fh.readline().strip().split()
idx_z = header.index("zCMB")
idx_m = header.index("m_b_corr")

z_all, m_all = [], []
with open(ph_file) as fh:
    fh.readline()
    for i_line, line in enumerate(fh):
        parts = line.split()
        if len(parts) < len(header):
            continue
        z_all.append(float(parts[idx_z]))
        m_all.append(float(parts[idx_m]))

z_all = np.array(z_all); m_all = np.array(m_all)
print(f"  Total SNe leidas: {len(z_all)}")

# Aplicar filtro z>0.01 preservando indices
mask = z_all > 0.01
z_sn = z_all[mask]
m_sn = m_all[mask]
idx_sn = np.where(mask)[0]  # indices originales 0..1700

print(f"  Tras corte z>0.01: {len(z_sn)}")
print(f"  Indices: {idx_sn[:5]}...{idx_sn[-3:]}")
print(f"  z range: {z_sn.min():.4f}..{z_sn.max():.4f}")

# Extraer submatriz
cov_sn = cov_full[np.ix_(idx_sn, idx_sn)]
print(f"  cov_sn shape: {cov_sn.shape}")

# Invertir
print(f"  Invirtiendo {cov_sn.shape}...")
t_inv = time.time()
try:
    cov_sn_inv = np.linalg.inv(cov_sn)
    print(f"  Invertida en {time.time()-t_inv:.1f}s")
except np.linalg.LinAlgError as e:
    print(f"  ERROR: {e}")
    cov_sn_inv = np.linalg.pinv(cov_sn)
    print(f"  Usando pseudo-inversa")

# ============================================================
# 3: Cargar DESI
# ============================================================
paso(3, "Cargar DESI DR2")

desi_file = DESI_DIR / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
desi_cov_file = DESI_DIR / "desi_gaussian_bao_ALL_GCcomb_cov.txt"

rows = []
with open(desi_file) as fh:
    for line in fh:
        line = line.strip()
        if not line or line.startswith("#"): continue
        parts = line.split()
        rows.append((float(parts[0]), float(parts[1]), parts[2]))

z_bao = np.array([r[0] for r in rows])
val_bao = np.array([r[1] for r in rows])
q_bao = [r[2] for r in rows]
cov_bao = np.loadtxt(desi_cov_file)
print(f"  N BAO: {len(z_bao)}")
print(f"  cov_bao shape: {cov_bao.shape}")
print(f"  SHA256 mean: {sha256_file(desi_file)[:32]}...")

# ============================================================
# 4: Modelo
# ============================================================
paso(4, "Modelo w0-wa CPL")

c_km_s = 299792.458
r_d_fid = 147.46
H0_fid = 67.36
Om_r = 9.15e-5

def E_z(z, Om, w0, wa):
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
    dm = D_M_z(z, Om, w0, wa); dh = D_H_z(z, Om, w0, wa)
    return (z * dm**2 * dh)**(1.0/3.0)

def pred_bao(z_array, q_list, Om, w0, wa):
    out = np.zeros(len(z_array))
    for i, (z, q) in enumerate(zip(z_array, q_list)):
        if q == "DV_over_rs": out[i] = D_V_z(z, Om, w0, wa) / r_d_fid
        elif q == "DM_over_rs": out[i] = D_M_z(z, Om, w0, wa) / r_d_fid
        elif q == "DH_over_rs": out[i] = D_H_z(z, Om, w0, wa) / r_d_fid
    return out

def mu_z(z_array, Om, w0, wa):
    out = np.zeros(len(z_array))
    for i, z in enumerate(z_array):
        dm = D_M_z(z, Om, w0, wa)
        dl = (1.0 + z) * dm
        out[i] = 5.0 * np.log10(dl * 1e5)
    return out

def chi2_bao(Om, w0, wa):
    r = val_bao - pred_bao(z_bao, q_bao, Om, w0, wa)
    return float(r @ np.linalg.solve(cov_bao, r))

def chi2_sn(Om, w0, wa):
    mu_th = mu_z(z_sn, Om, w0, wa)
    r = m_sn - mu_th
    # M_B con covarianza completa
    Cinv_r = cov_sn_inv @ r
    Cinv_1 = cov_sn_inv @ np.ones(len(r))
    M = float(np.sum(Cinv_r) / np.sum(Cinv_1))
    r_M = r - M
    return float(r_M @ cov_sn_inv @ r_M)

def chi2_total(params):
    Om, w0, wa = params
    if not (0.15 < Om < 0.55): return 1e10
    if not (-2 < w0 < 0):      return 1e10
    if not (-3 < wa < 2):      return 1e10
    return chi2_bao(Om, w0, wa) + chi2_sn(Om, w0, wa)

chi2_lcdm = chi2_total([0.31, -1.0, 0.0])
print(f"  chi2 LCDM (cov completa): {chi2_lcdm:.2f}")

# ============================================================
# 5: Ajuste
# ============================================================
paso(5, "Ajuste conjunto con covarianza completa")

t_fit = time.time()
best = minimize(chi2_total, x0=[0.31, -1.0, 0.0],
                method="Nelder-Mead",
                options={"xatol": 1e-5, "fatol": 1e-4, "maxiter": 5000})
Om_best, w0_best, wa_best = best.x
chi2_best = best.fun
print(f"  Tiempo ajuste: {time.time()-t_fit:.1f}s")
print(f"  Om = {Om_best:.4f}")
print(f"  w0 = {w0_best:.4f}")
print(f"  wa = {wa_best:.4f}")
print(f"  chi2 = {chi2_best:.2f}")
print(f"  dchi2 vs LCDM: {chi2_lcdm - chi2_best:.2f}")

# ============================================================
# 6: Hessiana
# ============================================================
paso(6, "Sigmas via Hessiana")

eps = 1e-4
H = np.zeros((3, 3))
x0_arr = np.array([Om_best, w0_best, wa_best])
t_h = time.time()
for i in range(3):
    for j in range(3):
        xpp = x0_arr.copy(); xpp[i]+=eps; xpp[j]+=eps
        xpm = x0_arr.copy(); xpm[i]+=eps; xpm[j]-=eps
        xmp = x0_arr.copy(); xmp[i]-=eps; xmp[j]+=eps
        xmm = x0_arr.copy(); xmm[i]-=eps; xmm[j]-=eps
        H[i,j] = (chi2_total(xpp)-chi2_total(xpm)-chi2_total(xmp)+chi2_total(xmm))/(4*eps**2)
print(f"  Hessiana en {time.time()-t_h:.1f}s")

try:
    cov = 2 * np.linalg.inv(H)
    sigmas = np.sqrt(np.diag(cov))
    print(f"  sigma_Om = {sigmas[0]:.4f}")
    print(f"  sigma_w0 = {sigmas[1]:.4f}")
    print(f"  sigma_wa = {sigmas[2]:.4f}")
    print(f"  corr(w0,wa) = {cov[1,2]/(sigmas[1]*sigmas[2]):.4f}")
except Exception as e:
    print(f"  ERROR: {e}")
    sigmas = None; cov = None

# ============================================================
# 7: Test falsacion
# ============================================================
paso(7, "Test de falsacion w_Phi >= -1")

z_test = np.array([0.0, 0.3, 0.5, 1.0, 1.5, 2.0])
print(f"  {'z':>5s}  {'w(z)':>10s}  {'sigma_w':>10s}  {'(w+1)/sigma':>14s}")

puntos_falsacion = []
for z in z_test:
    w = w0_best + wa_best * z / (1 + z)
    f_z = z / (1 + z)
    if sigmas is not None:
        var_w = sigmas[1]**2 + 2*cov[1,2]*f_z + sigmas[2]**2*f_z**2
        sig_w = np.sqrt(max(var_w, 0))
        tension = (w + 1) / sig_w if sig_w > 0 else 0
        print(f"  {z:5.2f}  {w:10.4f}  {sig_w:10.4f}  {tension:14.4f}")
        if tension < -3:
            puntos_falsacion.append({"z": float(z), "w": float(w), "tension": float(tension)})

if puntos_falsacion:
    veredicto = "FALSACION_POTENCIAL"
elif sigmas is not None and (w0_best + 1) / sigmas[1] < -3:
    veredicto = "TENSION_SIGNIFICATIVA_w0"
else:
    veredicto = "NO_FALSACION"

print(f"\n  VEREDICTO: {veredicto}")

# ============================================================
# 8: Comparacion F.2b vs F.2d
# ============================================================
paso(8, "Comparacion F.2b (diagonal) vs F.2d (cov completa)")

print(f"  {'Cantidad':14s}  {'F.2b':>22s}  {'F.2d':>22s}  {'Cambio':>10s}")
def fmt(v, s): return f"{v:.4f} +/- {s:.4f}"
print(f"  {'Om':14s}  {fmt(0.3135, 0.0117):>22s}  {fmt(Om_best, sigmas[0]):>22s}")
print(f"  {'w0':14s}  {fmt(-0.8115, 0.0562):>22s}  {fmt(w0_best, sigmas[1]):>22s}  {((w0_best+0.8115)/0.0562):>+9.2f}s")
print(f"  {'wa':14s}  {fmt(-0.6209, 0.4196):>22s}  {fmt(wa_best, sigmas[2]):>22s}")
print(f"  {'chi2':14s}  {730.82:>22.2f}  {chi2_best:>22.2f}")

# Actualizar A-15
a15_path = REG / "A-15_w_phi_falsabilidad.json"
if a15_path.exists():
    a15 = json.loads(a15_path.read_text(encoding="utf-8"))
else:
    a15 = {}
a15["observacion_refinada_F2d"] = {
    "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "datos": "DESI DR2 + Pantheon+ (covarianza completa STAT+SYS)",
    "N_sne": int(len(z_sn)),
    "resultado": {
        "Om": float(Om_best), "sigma_Om": float(sigmas[0]) if sigmas is not None else None,
        "w0": float(w0_best), "sigma_w0": float(sigmas[1]) if sigmas is not None else None,
        "wa": float(wa_best), "sigma_wa": float(sigmas[2]) if sigmas is not None else None,
        "chi2": float(chi2_best), "chi2_LCDM": float(chi2_lcdm),
        "delta_chi2": float(chi2_lcdm - chi2_best),
    },
    "veredicto": veredicto,
    "puntos_falsacion": puntos_falsacion,
}
a15_path.write_text(json.dumps(a15, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\n  A-15 actualizado: {a15_path}")

# Guardar resultado final
res = {
    "fase": "F.2d",
    "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "datos": {
        "DESI_DR2": {"n": int(len(z_bao)), "sha256": sha256_file(desi_file)},
        "Pantheon_plus": {"n": int(len(z_sn)), "sha256": sha256_file(ph_file),
                          "cov_sha256": sha256_file(cov_file)},
    },
    "ajuste": {
        "Om": float(Om_best), "w0": float(w0_best), "wa": float(wa_best),
        "sigma_Om": float(sigmas[0]) if sigmas is not None else None,
        "sigma_w0": float(sigmas[1]) if sigmas is not None else None,
        "sigma_wa": float(sigmas[2]) if sigmas is not None else None,
        "chi2": float(chi2_best), "chi2_LCDM": float(chi2_lcdm),
    },
    "veredicto": veredicto,
}
out = OUT_DIR / "fase_f2d_w_phi_refinado.json"
out.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")

# ============================================================
# 9: Resumen
# ============================================================
paso(9, "RESUMEN F.2d")

print(f"  Ajuste con covarianza Pantheon+ completa:")
print(f"    Om = {Om_best:.4f} +/- {sigmas[0]:.4f}")
print(f"    w0 = {w0_best:.4f} +/- {sigmas[1]:.4f}")
print(f"    wa = {wa_best:.4f} +/- {sigmas[2]:.4f}")
print(f"    chi2 = {chi2_best:.2f} (LCDM: {chi2_lcdm:.2f})")
print()
print(f"  Test falsacion THU-TBEA (cota w_Phi >= -1):")
print(f"    VEREDICTO: {veredicto}")
print()
print(f"  Tiempo total: {time.time()-t0:.1f}s")
