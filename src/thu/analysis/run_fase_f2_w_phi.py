# -*- coding: utf-8 -*-
"""FASE F.2 — Ajuste conjunto DESI DR2 + Pantheon+ -> w(z) -> test vs cota w_Phi >= -1."""
import sys, json, hashlib, time
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.integrate import quad

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
DESI_DIR = LAB / "data" / "raw" / "desi_dr2"
PANTHEON_DIR = LAB / "data" / "raw" / "pantheon_plus"
OUT_DIR = LAB / "data" / "inventory"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TOTAL = 9
t0 = time.time()

def barra(i):
    pct = int(100 * i / TOTAL)
    filled = pct * 40 // 100
    return "=" * filled + "." * (40 - filled), pct

def paso(i, titulo, desc=""):
    bar, pct = barra(i)
    print()
    print("=" * 72)
    print(f"  PASO {i}/{TOTAL}  [{bar}]  {pct:3d}%")
    print(f"  {titulo}")
    if desc:
        print(f"  -> {desc}")
    print("=" * 72)
    sys.stdout.flush()

def sha256_file(path, chunk=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()

# ============================================================
# 1: Verificar archivos en disco
# ============================================================
paso(1, "Verificar archivos DESI + Pantheon+",
     "Inspeccionar que existen antes de asumir")

print(f"  DESI dir:     {DESI_DIR}")
print(f"  Pantheon dir: {PANTHEON_DIR}")

for d, name in [(DESI_DIR, "DESI"), (PANTHEON_DIR, "Pantheon")]:
    print(f"\n  Contenido de {name}:")
    if not d.exists():
        print(f"    ERROR: no existe")
        continue
    for f in sorted(d.rglob("*")):
        if f.is_file():
            kb = f.stat().st_size / 1024
            print(f"    {f.relative_to(d)}  ({kb:.2f} KB)")

# ============================================================
# 2: Cargar DESI DR2 BAO
# ============================================================
paso(2, "Cargar DESI DR2 BAO",
     "mean + covarianza")

# Buscar archivos
desi_mean = None
desi_cov = None
for f in DESI_DIR.rglob("*"):
    if f.is_file():
        n = f.name.lower()
        if "mean" in n or "data" in n:
            desi_mean = f
        if "cov" in n:
            desi_cov = f

if not desi_mean:
    print(f"  ERROR: no se encontro archivo mean")
    sys.exit(1)

print(f"  mean: {desi_mean.name}")
print(f"  SHA256: {sha256_file(desi_mean)[:32]}...")

# Cargar
try:
    desi_data = np.loadtxt(desi_mean, comments="#")
    print(f"  shape: {desi_data.shape}")
    print(f"  Primeras 5 filas:")
    for row in desi_data[:5]:
        print(f"    {row}")
    print(f"  Ultimas 2 filas:")
    for row in desi_data[-2:]:
        print(f"    {row}")
except Exception as e:
    print(f"  ERROR cargando mean: {e}")
    sys.exit(1)

if desi_cov:
    print(f"\n  cov: {desi_cov.name}")
    print(f"  SHA256: {sha256_file(desi_cov)[:32]}...")
    desi_cov_mat = np.loadtxt(desi_cov, comments="#")
    print(f"  cov shape: {desi_cov_mat.shape}")
    if desi_cov_mat.ndim == 1:
        # Diagonal vector
        print(f"  cov es vector diagonal, len={len(desi_cov_mat)}")
        desi_cov_mat = np.diag(desi_cov_mat)
        print(f"  -> convertido a matriz {desi_cov_mat.shape}")
else:
    print(f"  ADVERTENCIA: sin covarianza, usando solo diagonales de sigma")
    desi_cov_mat = None

# ============================================================
# 3: Cargar Pantheon+ SNe
# ============================================================
paso(3, "Cargar Pantheon+ SNe",
     "SH0ES.dat o equivalente")

# Buscar
pantheon_data = None
pantheon_cov = None
for f in PANTHEON_DIR.rglob("*"):
    if f.is_file():
        n = f.name.lower()
        if "sh0es" in n and f.suffix in [".dat", ".txt"]:
            pantheon_data = f
        elif "pantheon" in n and f.suffix in [".dat", ".txt"] and "sh0es" not in n:
            if pantheon_data is None:
                pantheon_data = f
        if "cov" in n and f.suffix in [".txt", ".dat"]:
            pantheon_cov = f

if not pantheon_data:
    # Buscar cualquier .dat
    for f in PANTHEON_DIR.rglob("*.dat"):
        pantheon_data = f
        break

if not pantheon_data:
    print(f"  ERROR: no se encontro SH0ES.dat")
    sys.exit(1)

print(f"  data: {pantheon_data.name}")
print(f"  SHA256: {sha256_file(pantheon_data)[:32]}...")
print(f"  Tamano: {pantheon_data.stat().st_size / 1024 / 1024:.2f} MB")

# Leer header
with open(pantheon_data, encoding="utf-8", errors="replace") as fh:
    header = fh.readline().strip().split()
print(f"  Columnas ({len(header)}): {header[:15]}...")

# Cargar
try:
    # Pantheon+ suele ser whitespace-delimited con header
    pantheon_raw = np.genfromtxt(pantheon_data, names=True, encoding="utf-8",
                                  dtype=None, max_rows=None)
    print(f"  shape: {pantheon_raw.shape}")
    print(f"  Campos disponibles: {pantheon_raw.dtype.names[:15]}...")
except Exception as e:
    print(f"  ERROR: {e}")
    sys.exit(1)

# Extraer columnas necesarias
# Pantheon+ SH0ES.dat tiene: CID, IDSURVEY, zCMB, zHEL, m_b_corr, m_b_corr_err_DIAG, ...
cols = pantheon_raw.dtype.names
zcol = next((c for c in cols if "zCMB" in c or "zcmb" in c.lower()), None)
mcol = next((c for c in cols if "m_b_corr" in c or "mb_corr" in c), None)
errcol = next((c for c in cols if "err_DIAG" in c and "m_b" in c), None)
errcol2 = next((c for c in cols if "m_b_corr_err" in c and c != errcol), None)

print(f"\n  zcol   = {zcol}")
print(f"  mcol   = {mcol}")
print(f"  errcol = {errcol}")

z_sn = pantheon_raw[zcol].astype(float)
m_sn = pantheon_raw[mcol].astype(float)

if errcol:
    err_sn = pantheon_raw[errcol].astype(float)
else:
    # fallback: 0.1 mag
    print(f"  ADVERTENCIA: sin columna de error; usando sigma=0.1 mag")
    err_sn = np.full_like(z_sn, 0.1)

# Filtro: z > 0.01 (evitar SNe locales con velocidad peculiar dominante)
mask = z_sn > 0.01
z_sn = z_sn[mask]
m_sn = m_sn[mask]
err_sn = err_sn[mask]

print(f"  N SNe tras corte z>0.01: {len(z_sn)}")
print(f"  z range: {z_sn.min():.4f}..{z_sn.max():.4f}")

# ============================================================
# 4: Modelo w0-wa (CPL)
# ============================================================
paso(4, "Definir modelo w(z) = w0 + wa * z/(1+z)",
     "Friedmann + distancias")

c_km_s = 299792.458  # km/s
r_d_fid = 147.46     # Mpc (DESI DR2, COSM-002)
H0_fid = 67.36       # km/s/Mpc (Planck 2018 VI)
Om_r = 9.15e-5       # radiacion (fotones + neutrinos)

def E_z(z, Om, w0, wa):
    """H(z)/H0 para w0-wa CPL."""
    a = 1.0 / (1.0 + z)
    # DE density: rho_DE(a) = rho_DE_0 * a^(-3(1+w0+wa)) * exp(3*wa*(a-1))
    f_de = (1.0 + z)**(3*(1 + w0 + wa)) * np.exp(-3 * wa * z / (1 + z))
    Ode = 1.0 - Om - Om_r
    return np.sqrt(Om * (1 + z)**3 + Om_r * (1 + z)**4 + Ode * f_de)

def D_M_z(z, Om, w0, wa, H0=H0_fid):
    """Comoving distance en Mpc."""
    integrand = lambda zp: c_km_s / (H0 * E_z(zp, Om, w0, wa))
    val, _ = quad(integrand, 0, z, limit=50)
    return val

def D_H_z(z, Om, w0, wa, H0=H0_fid):
    """Hubble distance en Mpc."""
    return c_km_s / (H0 * E_z(z, Om, w0, wa))

def D_V_z(z, Om, w0, wa, H0=H0_fid):
    """Volume-averaged distance en Mpc."""
    dm = D_M_z(z, Om, w0, wa, H0)
    dh = D_H_z(z, Om, w0, wa, H0)
    return (z * dm**2 * dh)**(1.0/3.0)

def mu_z(z, Om, w0, wa, H0=H0_fid):
    """Distancia de luminosidad -> modulo de distancia."""
    dm = D_M_z(z, Om, w0, wa, H0)
    dl = (1 + z) * dm  # Mpc
    # mu = 5 log10(dl/10pc) = 5 log10(dl * 1e5) (con dl en Mpc)
    return 5.0 * np.log10(dl * 1e5)

# ============================================================
# 5: Chi2 DESI
# ============================================================
paso(5, "Calcular chi2 DESI DR2 BAO",
     "D_M/r_d, D_H/r_d segun bin")

# Asumir formato DESI DR2 mean.txt: z, quantity, value, sigma
# "quantity" puede ser: DV_over_rs, DM_over_rs, DH_over_rs
# La covarianza completa mezcla D_M y D_H del mismo z

# Extraer columnas
if desi_data.shape[1] >= 4:
    z_bao = desi_data[:, 0]
    q_bao = desi_data[:, 1]  # puede ser 0=DV, 1=DM, 2=DH
    val_bao = desi_data[:, 2]
    sigma_bao = desi_data[:, 3]
    print(f"  N measurements: {len(z_bao)}")
    print(f"  z: {z_bao}")
    print(f"  q (0=DV, 1=DM, 2=DH asumido): {q_bao}")
    print(f"  val/r_d: {val_bao}")
    print(f"  sigma/r_d: {sigma_bao}")
else:
    print(f"  ERROR: DESI formato no reconocido")
    sys.exit(1)

# Modelo
def model_bao(z, Om, w0, wa):
    """Devuelve D_M/r_d o D_H/r_d o D_V/r_d segun q."""
    out = []
    for i in range(len(z)):
        zz = z[i]
        qq = q_bao[i]
        dm = D_M_z(zz, Om, w0, wa)
        dh = D_H_z(zz, Om, w0, wa)
        dv = D_V_z(zz, Om, w0, wa)
        if qq == 0:      # DV
            out.append(dv / r_d_fid)
        elif qq == 1:    # DM
            out.append(dm / r_d_fid)
        elif qq == 2:    # DH
            out.append(dh / r_d_fid)
        else:
            out.append(dm / r_d_fid)
    return np.array(out)

def chi2_desi(Om, w0, wa):
    mod = model_bao(z_bao, Om, w0, wa)
    r = val_bao - mod
    if desi_cov_mat is not None and desi_cov_mat.shape == (len(r), len(r)):
        try:
            return float(r @ np.linalg.solve(desi_cov_mat, r))
        except np.linalg.LinAlgError:
            pass
    # Fallback: diagonal
    return float(np.sum((r / sigma_bao)**2))

chi2_bao = chi2_desi(0.31, -1.0, 0.0)
print(f"\n  chi2 DESI (LCDM fiducial): {chi2_bao:.2f}")
print(f"  dof: {len(val_bao)}")

# ============================================================
# 6: Chi2 Pantheon+
# ============================================================
paso(6, "Calcular chi2 Pantheon+ SNe",
     "Con marginalizacion de M_B analitica")

# Modelo mu(z) + M_B - m_sn
def chi2_sn_M(M, Om, w0, wa):
    mu_th = mu_z(z_sn, Om, w0, wa)
    r = m_sn - (mu_th + M)
    return float(np.sum((r / err_sn)**2))

# M_B optimo analiticamente para chi2 minimo
# minimize sum (m_i - mu_i - M)^2 / sigma_i^2
# dM: sum -2 (m_i - mu_i - M) / sigma_i^2 = 0
# M_best = sum((m_i - mu_i)/sigma_i^2) / sum(1/sigma_i^2)
def M_best(Om, w0, wa):
    mu_th = mu_z(z_sn, Om, w0, wa)
    w = 1.0 / err_sn**2
    M = np.sum(w * (m_sn - mu_th)) / np.sum(w)
    return M

def chi2_sn(Om, w0, wa):
    M = M_best(Om, w0, wa)
    return chi2_sn_M(M, Om, w0, wa)

chi2_sne = chi2_sn(0.31, -1.0, 0.0)
print(f"  chi2 Pantheon+ (LCDM fiducial): {chi2_sne:.2f}")
print(f"  N SNe: {len(z_sn)}")

# ============================================================
# 7: Ajuste conjunto w0-wa
# ============================================================
paso(7, "Ajuste conjunto w0-wa",
     "minimize chi2 total sobre {Om, w0, wa}")

def chi2_total(params):
    Om, w0, wa = params
    if Om < 0.15 or Om > 0.55:
        return 1e10
    if w0 < -2 or w0 > 0:
        return 1e10
    if wa < -3 or wa > 2:
        return 1e10
    return chi2_desi(Om, w0, wa) + chi2_sn(Om, w0, wa)

# Fiducial LCDM
chi2_lcdm = chi2_desi(0.31, -1.0, 0.0) + chi2_sn(0.31, -1.0, 0.0)
print(f"  chi2 total LCDM: {chi2_lcdm:.2f}")

# Optimizar
best = minimize(chi2_total, x0=[0.31, -1.0, 0.0],
                method="Nelder-Mead",
                options={"xatol": 1e-5, "fatol": 1e-4, "maxiter": 2000})
Om_best, w0_best, wa_best = best.x
chi2_best = best.fun

print(f"\n  Resultado ajuste:")
print(f"    Om   = {Om_best:.4f}")
print(f"    w0   = {w0_best:.4f}")
print(f"    wa   = {wa_best:.4f}")
print(f"    chi2 = {chi2_best:.2f}")
print(f"    dof  = {len(val_bao) + len(z_sn) - 3}")

# Sigma via Hessiana numerica
from scipy.optimize import approx_fprime
eps = 1e-4
def chi2_wrap(x):
    return chi2_total(x)

# Hessiana numerica simple
H = np.zeros((3, 3))
for i in range(3):
    for j in range(3):
        x_pp = [Om_best, w0_best, wa_best]
        x_pp[i] += eps; x_pp[j] += eps
        x_pm = [Om_best, w0_best, wa_best]
        x_pm[i] += eps; x_pm[j] -= eps
        x_mp = [Om_best, w0_best, wa_best]
        x_mp[i] -= eps; x_mp[j] += eps
        x_mm = [Om_best, w0_best, wa_best]
        x_mm[i] -= eps; x_mm[j] -= eps
        H[i, j] = (chi2_wrap(x_pp) - chi2_wrap(x_pm) - chi2_wrap(x_mp) + chi2_wrap(x_mm)) / (4 * eps**2)

try:
    cov = 2 * np.linalg.inv(H)
    sigmas = np.sqrt(np.diag(cov))
    print(f"\n  Sigmas (Hessiana numerica):")
    print(f"    sigma_Om = {sigmas[0]:.4f}")
    print(f"    sigma_w0 = {sigmas[1]:.4f}")
    print(f"    sigma_wa = {sigmas[2]:.4f}")
    print(f"    cov_w0_wa = {cov[1,2]:.6f}")
except Exception as e:
    print(f"  ERROR Hessiana: {e}")
    cov = None
    sigmas = None

# ============================================================
# 8: w(z) y test vs cota w_Phi >= -1
# ============================================================
paso(8, "Test de falsacion: w(z) vs cota w_Phi >= -1",
     "PDF §14")

print(f"  Modelo: w(z) = w0 + wa * z/(1+z)")
print(f"  w0 = {w0_best:.4f}, wa = {wa_best:.4f}")

# Puntos clave
z_test = np.array([0.0, 0.3, 0.5, 1.0, 1.5, 2.0])
w_test = w0_best + wa_best * z_test / (1 + z_test)

print(f"\n  w(z) en puntos clave:")
print(f"    {'z':>5s}  {'w(z)':>10s}")
for z, w in zip(z_test, w_test):
    print(f"    {z:5.2f}  {w:10.4f}")

# Sigma_w(z) via propagacion
if sigmas is not None:
    var_w0 = sigmas[1]**2
    var_wa = sigmas[2]**2
    cov_w0_wa = cov[1, 2] if cov is not None else 0
    print(f"\n  Sigma_w(z) via propagacion:")
    print(f"    {'z':>5s}  {'sigma_w(z)':>12s}  {'(w+1)/sigma':>12s}")
    for z in z_test:
        f_z = z / (1 + z)
        var_w = var_w0 + 2 * cov_w0_wa * f_z + var_wa * f_z**2
        sig_w = np.sqrt(max(var_w, 0))
        w_val = w0_best + wa_best * f_z
        pull = (w_val + 1) / sig_w if sig_w > 0 else 0
        print(f"    {z:5.2f}  {sig_w:12.4f}  {pull:12.4f}")

# Test de cruce fantasma
print(f"\n  Test de cruce fantasma (w < -1):")
print(f"  Cota THU-TBEA: w_Phi >= -1 (PDF §14)")
print(f"  Umbral falsacion: cruce fantasma con > 3 sigma")

# Cuantos puntos tienen w < -1 significativamente?
puntos_w_menos_1 = w_test < -1
puntos_significativos = []
if sigmas is not None:
    for z, w in zip(z_test, w_test):
        f_z = z / (1 + z)
        var_w = var_w0 + 2 * cov_w0_wa * f_z + var_wa * f_z**2
        sig_w = np.sqrt(max(var_w, 0))
        if sig_w > 0:
            tension = (w - (-1)) / sig_w  # (w - (-1))/sigma
            if tension < -3:
                puntos_significativos.append((z, w, tension))

if puntos_significativos:
    print(f"  *** FALSACION ***")
    print(f"  Puntos con w < -1 a >3 sigma:")
    for z, w, t in puntos_significativos:
        print(f"    z={z:.2f}: w={w:.4f}, tension={t:.2f} sigma")
else:
    print(f"  NO FALSACION: ningun punto con w < -1 a >3 sigma")
    print(f"  THU-TBEA sobrevive este test")

# Chequear w0
if sigmas is not None:
    tension_w0 = (w0_best + 1) / sigmas[1]
    print(f"\n  Tension en w0: (w0 + 1)/sigma_w0 = {tension_w0:.4f} sigma")

# ============================================================
# 9: Guardar y veredicto
# ============================================================
paso(9, "Guardar resultado + veredicto final")

veredicto = "NO FALSACION"
if puntos_significativos:
    veredicto = "FALSACION POTENCIAL"
elif sigmas is not None and abs((w0_best + 1) / sigmas[1]) > 3:
    veredicto = "TENSION SIGNIFICATIVA en w0"

resultado = {
    "fase": "F.2",
    "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "datos": {
        "DESI": {
            "archivo": str(desi_mean.name),
            "n_mediciones": int(len(val_bao)),
            "z_range": [float(z_bao.min()), float(z_bao.max())],
        },
        "Pantheon": {
            "archivo": str(pantheon_data.name),
            "n_sne": int(len(z_sn)),
            "z_range": [float(z_sn.min()), float(z_sn.max())],
        },
    },
    "ajuste": {
        "modelo": "w0-wa CPL",
        "Om": float(Om_best), "sigma_Om": float(sigmas[0]) if sigmas is not None else None,
        "w0": float(w0_best), "sigma_w0": float(sigmas[1]) if sigmas is not None else None,
        "wa": float(wa_best), "sigma_wa": float(sigmas[2]) if sigmas is not None else None,
        "chi2": float(chi2_best),
        "chi2_LCDM_ref": float(chi2_lcdm),
        "dof": int(len(val_bao) + len(z_sn) - 3),
    },
    "w_z": {
        "z": list(z_test),
        "w_z": list(w_test),
    },
    "cota_THU": "w_Phi >= -1 (PDF §14)",
    "veredicto": veredicto,
    "puntos_falsacion": [
        {"z": float(z), "w": float(w), "tension_sigma": float(t)}
        for z, w, t in puntos_significativos
    ],
}

out = OUT_DIR / "fase_f2_w_phi_desi.json"
out.write_text(json.dumps(resultado, indent=2), encoding="utf-8")
print(f"  Guardado: {out}")

print(f"\n  VEREDICTO: {veredicto}")
print(f"  Tiempo total: {time.time()-t0:.1f}s")

print()
print("=" * 72)
print("  RESUMEN F.2")
print("=" * 72)
print(f"  Ajuste conjunto DESI DR2 + Pantheon+ (w0-wa CPL):")
print(f"    Om = {Om_best:.4f} +/- {sigmas[0]:.4f}" if sigmas is not None else f"    Om = {Om_best:.4f}")
print(f"    w0 = {w0_best:.4f} +/- {sigmas[1]:.4f}" if sigmas is not None else f"    w0 = {w0_best:.4f}")
print(f"    wa = {wa_best:.4f} +/- {sigmas[2]:.4f}" if sigmas is not None else f"    wa = {wa_best:.4f}")
print(f"    chi2 = {chi2_best:.2f}, dof = {len(val_bao)+len(z_sn)-3}")
print()
print(f"  Test de falsacion THU-TBEA:")
print(f"    Cota teorica:  w_Phi >= -1")
print(f"    Prediccion:    sin cruce fantasma a >3 sigma")
print(f"    Resultado:     {veredicto}")
