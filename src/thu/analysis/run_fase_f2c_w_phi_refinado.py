# -*- coding: utf-8 -*-
"""F.2c — Cierre A-15 + refinamiento con covarianza Pantheon+ completa."""
import sys, json, hashlib, time, re
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.integrate import quad

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
DESI_DIR = LAB / "data" / "raw" / "desi_dr2"
PAN_DIR = LAB / "data" / "raw" / "pantheon_plus"
REG = LAB / "registry" / "thu"
OUT_DIR = LAB / "data" / "inventory"
REG.mkdir(parents=True, exist_ok=True)
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
# PASO 1-2: Cerrar F.2b -> registrar A-15
# ============================================================
paso(1, "Cerrar F.2b: registrar A-15 en registry/thu/")

a15_estado = {
    "id": "A-15",
    "titulo": "Falsabilidad w_phi < -1 (sector de coherencia escalar)",
    "estatus": "[F] observacion activa",
    "fecha_actualizacion": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "prediccion_THU": {
        "cota": "w_Phi(z) >= -1 para todo z <= 10^4",
        "fuente": "PDF v5.3 §14, Teorema 1",
    },
    "observacion_actual": {
        "datos": "DESI DR2 BAO (13 mediciones) + Pantheon+ (1588 SNe, z>0.01)",
        "modelo": "w0-wa CPL (Chevallier-Polarski-Linder)",
        "resultado": {
            "Om": 0.3135,
            "sigma_Om": 0.0117,
            "w0": -0.8115,
            "sigma_w0": 0.0562,
            "wa": -0.6209,
            "sigma_wa": 0.4196,
            "chi2_w0wa": 730.82,
            "chi2_LCDM": 767.09,
            "delta_chi2": 36.27,
            "dof": 1598,
        },
        "test_falsacion": {
            "umbral_3sigma": "cruce fantasma w < -1 a >3 sigma",
            "maxima_tension_con_cota": -0.97,
            "unidad": "sigma",
            "puntos_con_falsacion": 0,
        },
        "veredicto": "NO_FALSACION",
        "tension_residual": "w0 = -0.81 +/- 0.06 (compatible con -1 a 3.35 sigma en direccion opuesta)",
    },
    "limitaciones": [
        "Analisis aproximado, no oficial de DESI",
        "Covarianza Pantheon+ solo diagonal en F.2b (mejorado en F.2c)",
        "Sin marginalizacion sobre r_d",
        "Sin BAO Lyman-alpha",
        "Sin priors BBN explicitos",
    ],
    "proximo_decisor": "DESI DR3 (~2027) + Euclid",
    "riesgo_estimado": "MODERADO-ALTO",
    "nota": "Resultado central cruza w=-1 entre z=0.3 y z=0.5. No significativo (>1 sigma) pero cualitativamente en tension con cota THU.",
}

a15_path = REG / "A-15_w_phi_falsabilidad.json"
a15_path.write_text(json.dumps(a15_estado, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"  Guardado: {a15_path}")
print(f"  Tamano: {a15_path.stat().st_size} B")

# ============================================================
# PASO 2: Verificar formato .cov de Pantheon+
# ============================================================
paso(2, "Inspeccionar formato Pantheon+SH0ES_STAT+SYS.cov")

cov_file = PAN_DIR / "Pantheon+SH0ES_STAT+SYS.cov"
print(f"  Archivo: {cov_file.name}")
print(f"  Tamano: {cov_file.stat().st_size / 1024 / 1024:.2f} MB")
print(f"  SHA256: {sha256_file(cov_file)[:32]}...")

# Leer primeras lineas para ver estructura
with open(cov_file, encoding="utf-8", errors="replace") as fh:
    for i, line in enumerate(fh):
        if i >= 3: break
        l_disp = line.strip()
        if len(l_disp) > 200:
            l_disp = l_disp[:200] + "..."
        print(f"  L{i}: {l_disp}")

# Contar lineas y columnas de la primera linea
with open(cov_file, encoding="utf-8") as fh:
    first_line = fh.readline().strip()
    ncols = len(first_line.split())
    nlines = 1
    for _ in fh:
        nlines += 1

print(f"\n  Filas: {nlines}")
print(f"  Columnas de primera linea: {ncols}")
print(f"  Esperado: matriz cuadrada N x N")

# Determinar formato
if ncols == nlines:
    formato = "matriz_completa"
elif ncols * 2 - 1 == nlines:
    formato = "triangular_superior"
else:
    formato = "desconocido"
print(f"  Formato detectado: {formato}")

# ============================================================
# PASO 3: Cargar covarianza Pantheon+ completa
# ============================================================
paso(3, "Cargar covarianza Pantheon+ completa")

# Cargar como matriz (esto puede tardar)
print(f"  Cargando {nlines} x {ncols} ... (puede tardar 10-30s)")
t_load = time.time()

# np.loadtxt es lento; usar np.fromfile + reshape
try:
    # Intentar carga directa
    cov_mat = np.loadtxt(cov_file)
    print(f"  OK: matriz {cov_mat.shape} en {time.time()-t_load:.1f}s")
except Exception as e:
    print(f"  ERROR: {e}")
    # Fallback: leer como texto parseado manual
    rows = []
    with open(cov_file, encoding="utf-8") as fh:
        for line in fh:
            vals = [float(v) for v in line.strip().split()]
            rows.append(vals)
    cov_mat = np.array(rows)
    print(f"  Cargado manual: {cov_mat.shape}")

# Si es triangular superior, hacer simetrica
if cov_mat.shape[0] != cov_mat.shape[1]:
    print(f"  Matriz no cuadrada {cov_mat.shape}, rellenando simetrica")
    N = max(cov_mat.shape)
    full = np.zeros((N, N))
    for i in range(cov_mat.shape[0]):
        for j in range(cov_mat.shape[1]):
            full[i, j] = cov_mat[i, j]
            if i != j:
                full[j, i] = cov_mat[i, j]
    cov_mat = full
    print(f"  -> {cov_mat.shape}")

print(f"  Rango: [{cov_mat.min():.3e}, {cov_mat.max():.3e}]")
print(f"  Diagonal media: {np.diag(cov_mat).mean():.4e}")

# ============================================================
# PASO 4: Cargar datos con filtro coherente
# ============================================================
paso(4, "Cargar datos coherentes con covarianza")

# DESI
desi_file = DESI_DIR / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
desi_cov_file = DESI_DIR / "desi_gaussian_bao_ALL_GCcomb_cov.txt"
rows = []
with open(desi_file, encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line or line.startswith("#"): continue
        parts = line.split()
        rows.append((float(parts[0]), float(parts[1]), parts[2]))
z_bao = np.array([r[0] for r in rows])
val_bao = np.array([r[1] for r in rows])
q_bao = [r[2] for r in rows]
cov_bao = np.loadtxt(desi_cov_file)
print(f"  DESI: {len(z_bao)} mediciones")

# Pantheon+
ph_file = PAN_DIR / "Pantheon+SH0ES.dat"
with open(ph_file, encoding="utf-8") as fh:
    header = fh.readline().strip().split()
idx_z = header.index("zCMB")
idx_m = header.index("m_b_corr")
idx_err = header.index("m_b_corr_err_DIAG")
idx_used = header.index("USED_IN_SH0ES_HF")

z_all, m_all, err_all, idx_all = [], [], [], []
with open(ph_file, encoding="utf-8") as fh:
    fh.readline()
    for i_line, line in enumerate(fh):
        parts = line.split()
        if len(parts) < len(header): continue
        try:
            z = float(parts[idx_z])
            m = float(parts[idx_m])
            err = float(parts[idx_err])
            z_all.append(z); m_all.append(m); err_all.append(err)
            idx_all.append(i_line)
        except (ValueError, IndexError):
            continue

z_all = np.array(z_all); m_all = np.array(m_all); err_all = np.array(err_all)
idx_all = np.array(idx_all)
print(f"  Pantheon+ total: {len(z_all)}")

# Filtro z>0.01 y que idx_all esten dentro de cov_mat
mask = (z_all > 0.01) & (idx_all < cov_mat.shape[0])
z_sn = z_all[mask]; m_sn = m_all[mask]; err_sn = err_all[mask]
idx_sn = idx_all[mask]
print(f"  Tras corte z>0.01 y dentro de cov: {len(z_sn)}")

# Extraer submatriz de covarianza
cov_sn = cov_mat[np.ix_(idx_sn, idx_sn)]
print(f"  cov_sn shape: {cov_sn.shape}")
print(f"  Diag[min,max]: {cov_sn.diagonal().min():.4e}, {cov_sn.diagonal().max():.4e}")
print(f"  vs err_sn^2 min/max: {err_sn.min()**2:.4e}, {err_sn.max()**2:.4e}")

# Verificar simetria
asim = np.max(np.abs(cov_sn - cov_sn.T))
print(f"  max|cov - cov.T|: {asim:.4e}")

# Invertir
print(f"  Invirtiendo {cov_sn.shape}...")
t_inv = time.time()
try:
    cov_sn_inv = np.linalg.inv(cov_sn)
    print(f"  Invertida en {time.time()-t_inv:.1f}s")
except np.linalg.LinAlgError:
    cov_sn_inv = np.linalg.pinv(cov_sn)
    print(f"  Pseudo-inversa (singular)")

# ============================================================
# PASO 5: Modelo
# ============================================================
paso(5, "Modelo w0-wa CPL")

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

def M_best(Om, w0, wa):
    mu_th = mu_z(z_sn, Om, w0, wa)
    r = m_sn - mu_th
    # M = (r^T C^-1 1) / (1^T C^-1 1)
    Cinv_r = cov_sn_inv @ r
    Cinv_1 = cov_sn_inv @ np.ones(len(r))
    M = np.sum(Cinv_r) / np.sum(Cinv_1)
    return M

def chi2_sn(Om, w0, wa):
    M = M_best(Om, w0, wa)
    mu_th = mu_z(z_sn, Om, w0, wa)
    r = m_sn - (mu_th + M)
    return float(r @ cov_sn_inv @ r)

def chi2_total(params):
    Om, w0, wa = params
    if not (0.15 < Om < 0.55): return 1e10
    if not (-2 < w0 < 0):      return 1e10
    if not (-3 < wa < 2):      return 1e10
    return chi2_bao(Om, w0, wa) + chi2_sn(Om, w0, wa)

# Test fiducial
chi2_lcdm = chi2_total([0.31, -1.0, 0.0])
print(f"  chi2 LCDM (con cov completa): {chi2_lcdm:.2f}")

# ============================================================
# PASO 6: Ajuste
# ============================================================
paso(6, "Ajuste conjunto con covarianza Pantheon+ completa")

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

# ============================================================
# PASO 7: Hessiana
# ============================================================
paso(7, "Sigmas via Hessiana")

eps = 1e-4
H = np.zeros((3, 3))
x0_arr = np.array([Om_best, w0_best, wa_best])
for i in range(3):
    for j in range(3):
        xpp = x0_arr.copy(); xpp[i]+=eps; xpp[j]+=eps
        xpm = x0_arr.copy(); xpm[i]+=eps; xpm[j]-=eps
        xmp = x0_arr.copy(); xmp[i]-=eps; xmp[j]+=eps
        xmm = x0_arr.copy(); xmm[i]-=eps; xmm[j]-=eps
        H[i,j] = (chi2_total(xpp)-chi2_total(xpm)-chi2_total(xmp)+chi2_total(xmm))/(4*eps**2)

try:
    cov = 2 * np.linalg.inv(H)
    sigmas = np.sqrt(np.diag(cov))
    print(f"  sigma_Om = {sigmas[0]:.4f}")
    print(f"  sigma_w0 = {sigmas[1]:.4f}")
    print(f"  sigma_wa = {sigmas[2]:.4f}")
except Exception as e:
    print(f"  ERROR: {e}")
    sigmas = None; cov = None

# ============================================================
# PASO 8: w(z) + falsacion
# ============================================================
paso(8, "Test de falsacion con covarianza completa")

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
# PASO 9: Comparacion F.2b vs F.2c
# ============================================================
paso(9, "Comparacion F.2b (diagonal) vs F.2c (completa)")

print(f"  {'Cantidad':20s}  {'F.2b':>15s}  {'F.2c':>15s}")
print(f"  {'Om':20s}  {'0.3135+/-0.0117':>15s}  {f'{Om_best:.4f}+/-{sigmas[0]:.4f}':>15s}")
print(f"  {'w0':20s}  {'-0.8115+/-0.0562':>15s}  {f'{w0_best:.4f}+/-{sigmas[1]:.4f}':>15s}")
print(f"  {'wa':20s}  {'-0.6209+/-0.4196':>15s}  {f'{wa_best:.4f}+/-{sigmas[2]:.4f}':>15s}")
print(f"  {'chi2':20s}  {'730.82':>15s}  {f'{chi2_best:.2f}':>15s}")
print(f"  {'chi2_LCDM':20s}  {'767.09':>15s}  {f'{chi2_lcdm:.2f}':>15s}")

# Actualizar A-15 con resultado refinado
a15_estado["observacion_refinada_F2c"] = {
    "datos": "DESI DR2 + Pantheon+ (covarianza completa STAT+SYS)",
    "modelo": "w0-wa CPL",
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
a15_path.write_text(json.dumps(a15_estado, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\n  A-15 actualizado con resultado refinado")

# ============================================================
# PASO 10: Guardar + resumen
# ============================================================
paso(10, "Guardar y resumen final")

resultado_final = {
    "fase": "F.2c (refinado)",
    "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "datos": {
        "DESI_DR2": {"n": int(len(val_bao)), "sha256": sha256_file(desi_file)},
        "Pantheon_plus": {"n": int(len(z_sn)), "sha256": sha256_file(ph_file),
                          "cov_sha256": sha256_file(cov_file)},
    },
    "ajuste_F2c": {
        "Om": float(Om_best), "w0": float(w0_best), "wa": float(wa_best),
        "sigma_Om": float(sigmas[0]) if sigmas is not None else None,
        "sigma_w0": float(sigmas[1]) if sigmas is not None else None,
        "sigma_wa": float(sigmas[2]) if sigmas is not None else None,
        "chi2": float(chi2_best), "chi2_LCDM": float(chi2_lcdm),
    },
    "comparacion_F2b": {
        "Om_F2b": 0.3135, "w0_F2b": -0.8115, "wa_F2b": -0.6209,
        "chi2_F2b": 730.82, "sigma_w0_F2b": 0.0562,
    },
    "veredicto": veredicto,
}
out = OUT_DIR / "fase_f2c_w_phi_refinado.json"
out.write_text(json.dumps(resultado_final, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"  Guardado: {out}")

print()
print("="*72)
print("  RESUMEN F.2c")
print("="*72)
print(f"  Ajuste conjunto (covarianza completa Pantheon+):")
print(f"    Om = {Om_best:.4f} +/- {sigmas[0]:.4f}")
print(f"    w0 = {w0_best:.4f} +/- {sigmas[1]:.4f}")
print(f"    wa = {wa_best:.4f} +/- {sigmas[2]:.4f}")
print(f"    chi2 = {chi2_best:.2f} (LCDM: {chi2_lcdm:.2f}, dchi2 = {chi2_lcdm-chi2_best:.2f})")
print()
print(f"  Test de falsacion THU-TBEA:")
print(f"    Veredicto: {veredicto}")
print()
print(f"  Registrado en registry/thu/A-15_w_phi_falsabilidad.json")
print(f"  Tiempo total: {time.time()-t0:.1f}s")
