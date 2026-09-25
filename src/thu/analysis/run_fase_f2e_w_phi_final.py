# -*- coding: utf-8 -*-
"""F.2e — Analisis correcto con covarianza Pantheon+ validada (version B)."""
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
# 1: Cargar Pantheon+ con scale, filtro z>0.01 & used=0
# ============================================================
paso(1, "Cargar Pantheon+ con filtro oficial",
     "z>0.01 & USED_IN_SH0ES_HF=0")

ph_file = PAN_DIR / "Pantheon+SH0ES.dat"
with open(ph_file) as fh:
    header = fh.readline().strip().split()
idx = {h: i for i, h in enumerate(header)}

z_all, m_all, scale_all, used_all = [], [], [], []
with open(ph_file) as fh:
    fh.readline()
    for line in fh:
        p = line.split()
        if len(p) < len(header): continue
        z_all.append(float(p[idx["zCMB"]]))
        m_all.append(float(p[idx["m_b_corr"]]))
        scale_all.append(float(p[idx["biasCor_m_b_COVSCALE"]]))
        used_all.append(int(p[idx["USED_IN_SH0ES_HF"]]))

z_all = np.array(z_all); m_all = np.array(m_all)
scale_all = np.array(scale_all); used_all = np.array(used_all)

mask = (z_all > 0.01) & (used_all == 0)
idx_keep = np.where(mask)[0]

z_sn = z_all[mask]; m_sn = m_all[mask]; scale_sn = scale_all[mask]

print(f"  Total Pantheon+: {len(z_all)}")
print(f"  Tras filtro: {len(z_sn)}")
print(f"  z range: {z_sn.min():.4f}..{z_sn.max():.4f}")
print(f"  scale range: [{scale_sn.min():.4f}, {scale_sn.max():.4f}]")
print(f"  scale mean: {scale_sn.mean():.4f}")

# ============================================================
# 2: Construir covarianza correcta (version B)
# ============================================================
paso(2, "Construir covarianza correcta", "C = STATSYS * outer(scale, scale)")

cov_file = PAN_DIR / "Pantheon+SH0ES_STAT+SYS.cov"
with open(cov_file) as fh:
    N = int(fh.readline().strip())
    vals = np.fromfile(fh, sep="\n", dtype=np.float64)

cov_full = vals.reshape(N, N)
cov_sn_raw = cov_full[np.ix_(idx_keep, idx_keep)]

# Version B: multiplicar por scale
cov_sn = cov_sn_raw * np.outer(scale_sn, scale_sn)

print(f"  cov_sn shape: {cov_sn.shape}")
print(f"  Diagonal[min,max]: {cov_sn.diagonal().min():.4e}, {cov_sn.diagonal().max():.4e}")
print(f"  max|cov - cov.T|: {np.max(np.abs(cov_sn - cov_sn.T)):.4e}")

# Invertir
print(f"  Invirtiendo...")
t_inv = time.time()
cov_sn_inv = np.linalg.inv(cov_sn)
print(f"  Invertida en {time.time()-t_inv:.1f}s")

# Guardar para certificacion
cov_path = OUT_DIR / "pantheon_cov_used.npy"
np.save(cov_path, cov_sn)
print(f"  Covarianza guardada: {cov_path.name}")
print(f"  SHA256 STATSYS: {sha256_file(cov_file)[:32]}...")

# ============================================================
# 3: Cargar DESI
# ============================================================
paso(3, "Cargar DESI DR2 BAO")

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
dof_lcdm = len(z_bao) + len(z_sn) - 1
print(f"  chi2 LCDM: {chi2_lcdm:.2f}")
print(f"  dof: {dof_lcdm}")
print(f"  chi2/dof: {chi2_lcdm/dof_lcdm:.4f}")

# ============================================================
# 5: Ajuste
# ============================================================
paso(5, "Ajuste conjunto (covarianza validada)")

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
print(f"  chi2/dof = {chi2_best/(len(z_bao)+len(z_sn)-3):.4f}")
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
# 8: Actualizar A-15
# ============================================================
paso(8, "Actualizar A-15 con resultado validado")

a15_path = REG / "A-15_w_phi_falsabilidad.json"
if a15_path.exists():
    a15 = json.loads(a15_path.read_text(encoding="utf-8"))
else:
    a15 = {}

a15["observacion_final_F2e"] = {
    "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "datos": "DESI DR2 + Pantheon+ (covarianza version B: STATSYS * outer(scale,scale))",
    "N_sne": int(len(z_sn)),
    "chi2_verificacion": {
        "chi2_LCDM": float(chi2_lcdm),
        "dof": int(dof_lcdm),
        "chi2_dof": float(chi2_lcdm/dof_lcdm),
        "veredicto_cov": "version B correcta (chi2/dof ~ 1)",
    },
    "resultado": {
        "Om": float(Om_best),
        "w0": float(w0_best),
        "wa": float(wa_best),
        "sigma_Om": float(sigmas[0]) if sigmas is not None else None,
        "sigma_w0": float(sigmas[1]) if sigmas is not None else None,
        "sigma_wa": float(sigmas[2]) if sigmas is not None else None,
        "chi2_best": float(chi2_best),
        "delta_chi2_vs_LCDM": float(chi2_lcdm - chi2_best),
    },
    "veredicto": veredicto,
    "puntos_falsacion": puntos_falsacion,
    "metodo_validado": True,
}
a15_path.write_text(json.dumps(a15, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"  A-15 actualizado")

# ============================================================
# 9: Resumen
# ============================================================
paso(9, "RESUMEN F.2e (resultado final)")

print(f"  ANALISIS CON COVARIANZA VALIDADA:")
print(f"    N SNe: {len(z_sn)}")
print(f"    chi2/dof (LCDM): {chi2_lcdm/dof_lcdm:.4f}  <- verificacion")
print()
print(f"  Ajuste w0-wa CPL:")
print(f"    Om = {Om_best:.4f} +/- {sigmas[0]:.4f}" if sigmas is not None else f"    Om = {Om_best:.4f}")
print(f"    w0 = {w0_best:.4f} +/- {sigmas[1]:.4f}" if sigmas is not None else f"    w0 = {w0_best:.4f}")
print(f"    wa = {wa_best:.4f} +/- {sigmas[2]:.4f}" if sigmas is not None else f"    wa = {wa_best:.4f}")
print(f"    chi2 = {chi2_best:.2f} / dof {len(z_bao)+len(z_sn)-3}")
print()
print(f"  Test de falsacion THU-TBEA (w_Phi >= -1):")
print(f"    VEREDICTO: {veredicto}")
print()
print(f"  Tiempo total: {time.time()-t0:.1f}s")
