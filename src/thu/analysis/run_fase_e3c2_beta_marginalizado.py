# -*- coding: utf-8 -*-
"""
FASE E.3-C2 — Ajuste riguroso de beta con marginalizacion cosmologica.
Metodo: expansion Taylor + prior Gaussiano Planck 2018.
"""
import sys, json, time
from pathlib import Path
import numpy as np
import camb
from camb import model as camb_model

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
ACT = LAB / "data" / "raw" / "act_dr6" / "act_dr6.02_spectra_and_cov_xtra" / "xtra"
OUT = LAB / "data" / "inventory"

TOTAL = 8
t0 = time.time()

def barra(i):
    pct = int(100 * i / TOTAL)
    filled = pct * 40 // 100
    return "=" * filled + "." * (40 - filled), pct

def paso(i, t, d):
    bar, pct = barra(i)
    print()
    print("=" * 72)
    print(f"  PASO {i}/{TOTAL}  [{bar}]  {pct:3d}%")
    print(f"  {t}")
    print(f"  -> {d}")
    print("=" * 72)
    sys.stdout.flush()

# Fiducial Planck 2018 VI
FID = dict(H0=67.36, ombh2=0.02237, omch2=0.1200,
           tau=0.0544, mnu=0.06, ns=0.9649, As=2.100e-9)
SIGMA = dict(H0=0.54, ombh2=0.00015, omch2=0.0012,
             ns=0.0042, As=0.030e-9)
MARG = ["As", "ns", "H0", "ombh2", "omch2"]

LMAX = 8000

def run_camb(p):
    pars = camb_model.CAMBparams()
    pars.set_cosmology(H0=p["H0"], ombh2=p["ombh2"], omch2=p["omch2"],
                       tau=p["tau"], mnu=p["mnu"], omk=0, nnu=3.046)
    pars.InitPower.set_params(As=p["As"], ns=p["ns"], r=0)
    pars.set_for_lmax(LMAX, lens_potential_accuracy=1)
    pars.set_accuracy(AccuracyBoost=0.5)
    res = camb.get_results(pars)
    powers = res.get_cmb_power_spectra(pars, CMB_unit="muK")
    ell = np.arange(powers["total"].shape[0])
    return ell, powers["total"][:, 0], powers["total"][:, 1], \
           powers["total"][:, 2], powers["total"][:, 3]

# -- 1: Cargar datos ACT --
paso(1, "Cargar EB y TB de ACT DR6", "47 bins por espectro")

eb_data = np.loadtxt(ACT / "opt_weight_fg_subtracted_EB.dat", comments="#")
tb_data = np.loadtxt(ACT / "opt_weight_fg_subtracted_TB.dat", comments="#")
ell_obs = eb_data[:, 0]
dl_eb = eb_data[:, 1]
dl_tb = tb_data[:, 1]
n_bins = len(ell_obs)
print(f"  n_bins = {n_bins}, ell {ell_obs.min():.1f}..{ell_obs.max():.1f}")

cov_eb = np.load(ACT / "cov_opt_weight_EB.npy")
cov_tb = np.load(ACT / "cov_opt_weight_TB.npy")
inv_cov_eb = np.linalg.inv(cov_eb)
inv_cov_tb = np.linalg.inv(cov_tb)
print(f"  cov_EB: {cov_eb.shape}, cov_TB: {cov_tb.shape}")
print(f"  Nota: NO hay archivo de covarianza conjunta EB-TB en xtra/")
print(f"  Usando block-diagonal (aproximacion)")

# -- 2: CAMB fiducial + derivadas --
paso(2, "CAMB: fiducial + derivadas numericas",
     f"1 + 2*{len(MARG)} = {1+2*len(MARG)} runs a lmax={LMAX}")

t_camb = time.time()
print(f"  Corre fiducial...", flush=True)
ell_c, tt_0, ee_0, bb_0, te_0 = run_camb(FID)
print(f"    OK en {time.time()-t_camb:.1f}s, ell_max={ell_c.max()}")

def interp_cl(cl):
    return np.interp(ell_obs, ell_c, cl)

EE_0 = interp_cl(ee_0); BB_0 = interp_cl(bb_0); TE_0 = interp_cl(te_0)

dEE_dp = {}; dBB_dp = {}; dTE_dp = {}
for p_name in MARG:
    print(f"  Derivada {p_name}...", end=" ", flush=True)
    t_p = time.time()
    dp = SIGMA[p_name]
    p_plus = dict(FID); p_plus[p_name] += dp
    p_minus = dict(FID); p_minus[p_name] -= dp
    _, _, ee_p, bb_p, te_p = run_camb(p_plus)
    _, _, ee_m, bb_m, te_m = run_camb(p_minus)
    dEE_dp[p_name] = (interp_cl(ee_p) - interp_cl(ee_m)) / (2*dp)
    dBB_dp[p_name] = (interp_cl(bb_p) - interp_cl(bb_m)) / (2*dp)
    dTE_dp[p_name] = (interp_cl(te_p) - interp_cl(te_m)) / (2*dp)
    print(f"({time.time()-t_p:.1f}s)")

print(f"  CAMB total: {time.time()-t_camb:.1f}s")

# -- 3: chi2 y ajuste parabolic --
paso(3, "Definir chi2(beta) y ajuste", "Parabolico con 3 puntos")

def chi2_at_beta(beta_deg, EE, BB, TE):
    b = np.radians(beta_deg)
    model_eb = 0.5 * np.sin(4*b) * (EE - BB)
    model_tb = np.sin(2*b) * TE
    r_eb = dl_eb - model_eb
    r_tb = dl_tb - model_tb
    return float(r_eb @ inv_cov_eb @ r_eb) + float(r_tb @ inv_cov_tb @ r_tb)

def fit_beta_parabolic(EE, BB, TE, delta=0.5):
    c0 = chi2_at_beta(0.0, EE, BB, TE)
    c_p = chi2_at_beta(delta, EE, BB, TE)
    c_m = chi2_at_beta(-delta, EE, BB, TE)
    a = (c_p + c_m - 2*c0) / (2*delta**2)
    b_coef = (c_p - c_m) / (2*delta)
    if a <= 0:
        return 0.0, float("nan")
    beta_best = -b_coef / (2*a)
    sigma = 1.0 / np.sqrt(a)
    return beta_best, sigma

# Test al fiducial
b_test, s_test = fit_beta_parabolic(EE_0, BB_0, TE_0)
print(f"  Fiducial (sin marginalizar): beta={b_test:.4f}, sigma={s_test:.4f} deg")

# -- 4: Muestreo --
paso(4, "Muestreo de theta_cosmo (Planck 2018)",
     "500 samples Gaussianos")

np.random.seed(20260921)
N_SAMPLES = 500
samples = {p: np.random.normal(0, 1, N_SAMPLES) for p in MARG}
print(f"  N = {N_SAMPLES}")
print(f"  Parametros marginalizados: {MARG}")
print(f"  Semilla: 20260921 (reproducible)")

# -- 5: Ajuste por sample --
paso(5, "Ajuste de beta para cada sample", f"N={N_SAMPLES}")

betas = np.zeros(N_SAMPLES)
sigmas = np.zeros(N_SAMPLES)

for i in range(N_SAMPLES):
    dEE = np.zeros(n_bins)
    dBB = np.zeros(n_bins)
    dTE = np.zeros(n_bins)
    for p in MARG:
        dp = SIGMA[p] * samples[p][i]
        dEE += dEE_dp[p] * dp
        dBB += dBB_dp[p] * dp
        dTE += dTE_dp[p] * dp
    EE_i = EE_0 + dEE
    BB_i = BB_0 + dBB
    TE_i = TE_0 + dTE
    beta_i, sigma_i = fit_beta_parabolic(EE_i, BB_i, TE_i)
    betas[i] = beta_i
    sigmas[i] = sigma_i

print(f"  Completado")
print(f"  beta: media={betas.mean():.4f}, std={betas.std():.4f} deg")

# -- 6: Posterior marginalizado --
paso(6, "Posterior marginalizado", "Combinacion within + between")

beta_mean = float(betas.mean())
var_within = float(np.nanmean(sigmas**2))
var_between = float(betas.var())
beta_std = float(np.sqrt(var_within + var_between))

print(f"  beta_marginalized = {beta_mean:.4f} deg")
print(f"  sigma_within      = {np.sqrt(var_within):.4f} deg (conditional)")
print(f"  sigma_between     = {np.sqrt(var_between):.4f} deg (cosmological)")
print(f"  sigma_total       = {beta_std:.4f} deg")

# -- 7: Tension vs THU --
paso(7, "Tension vs beta_THU = 0.3803 +/- 0.040", "")

beta_thu = 0.3803
sigma_thu = 0.040
sigma_comb = np.sqrt(beta_std**2 + sigma_thu**2)
tension = abs(beta_mean - beta_thu) / sigma_comb

print(f"  beta_ACT_marg = {beta_mean:.4f} +/- {beta_std:.4f} deg")
print(f"  beta_THU      = {beta_thu:.4f} +/- {sigma_thu:.4f} deg")
print(f"  Delta         = {beta_thu - beta_mean:.4f} deg")
print(f"  sigma_comb    = {sigma_comb:.4f} deg")
print(f"  Tension       = {tension:.3f} sigma")
print()
if tension < 1:
    print(f"  VEREDICTO: COMPATIBLE a < 1 sigma")
elif tension < 2:
    print(f"  VEREDICTO: COMPATIBLE a < 2 sigma")
elif tension < 3:
    print(f"  VEREDICTO: TENSION MARGINAL (2-3 sigma)")
else:
    print(f"  VEREDICTO: TENSION SIGNIFICATIVA (> 3 sigma)")

# -- 8: Guardar --
paso(8, "Guardar resultado", "")

result = {
    "beta_marginalized_deg": beta_mean,
    "sigma_total_deg": beta_std,
    "sigma_within_deg": float(np.sqrt(var_within)),
    "sigma_between_deg": float(np.sqrt(var_between)),
    "n_samples": N_SAMPLES,
    "params_marginalized": MARG,
    "param_sigmas": SIGMA,
    "lmax_camb": LMAX,
    "beta_thu_deg": beta_thu,
    "sigma_thu_deg": sigma_thu,
    "tension_sigma": float(tension),
    "metodo": "Taylor linear expansion + Planck 2018 Gaussian prior",
    "cov_note": "Block-diagonal EB/TB (no hay archivo conjunto en xtra/)",
    "seed": 20260921,
    "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
}
out = OUT / "resultado_beta_act_dr6_marginalizado.json"
out.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(f"  Guardado: {out}")

t_total = time.time() - t0
print()
print("=" * 72)
print(f"  FIN E.3-C2  (duracion total: {t_total:.1f}s)")
print("=" * 72)
print()
print("  Interpretacion:")
print("  - sigma_within: incertidumbre estadistica del ajuste de beta")
print("  - sigma_between: incertidumbre por variacion de cosmologia")
print("  - sigma_total: combinacion, es la que se reporta")
