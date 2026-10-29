"""Ajuste cosmologico profundo THU vs LCDM con BAO + SNe."""
import numpy as np
from scipy.optimize import minimize
from scipy.integrate import quad
from pathlib import Path
import json
from datetime import datetime

BASE = Path(__file__).resolve().parents[1]
BAO_MEAN = BASE / "data" / "raw" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
BAO_COV = BASE / "data" / "raw" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt"
SNE_FILE = BASE / "data" / "raw" / "pantheon_plus" / "Pantheon+SH0ES.dat"
OUT_FILE = BASE / "registry" / "thu" / "ajuste_cosmologico_profundo.json"

C_KMS = 299792.458


def cargar_bao():
    z_list, val_list, qty_list = [], [], []
    with open(BAO_MEAN, "r") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            z_list.append(float(parts[0]))
            val_list.append(float(parts[1]))
            qty_list.append(parts[2])
    
    z = np.array(z_list)
    val = np.array(val_list)
    qty = qty_list
    cov_frac = np.loadtxt(BAO_COV, comments="#")
    cov_abs = cov_frac * np.outer(val, val)
    return z, val, qty, cov_abs


def cargar_sne():
    """Carga Pantheon+ SNe (z, mu, mu_err)."""
    z, mu, mu_err = [], [], []
    with open(SNE_FILE, "r") as fh:
        header = fh.readline()
        for line in fh:
            parts = line.split()
            if len(parts) < 10:
                continue
            try:
                z_val = float(parts[2])  # zCMB
                mu_val = float(parts[10])  # MU_SH0ES
                mu_err_val = float(parts[11])  # MU_SH0ES_ERR_DIAG
                if z_val > 0.01 and mu_err_val > 0:
                    z.append(z_val)
                    mu.append(mu_val)
                    mu_err.append(mu_err_val)
            except (ValueError, IndexError):
                continue
    return np.array(z), np.array(mu), np.array(mu_err)


def E_LCDM(z, Om):
    OL = 1.0 - Om
    return np.sqrt(Om * (1+z)**3 + OL)


def E_THU(z, Om, Otau):
    OL = 1.0 - Om - Otau
    return np.sqrt(Om * (1+z)**3 + Otau * (1+z)**6 + OL)


def predecir_observables(z_arr, E_func, params, rd):
    DM_over_rd = np.zeros_like(z_arr)
    DH_over_rd = np.zeros_like(z_arr)
    DV_over_rd = np.zeros_like(z_arr)
    for i, zi in enumerate(z_arr):
        integral, _ = quad(lambda zp: 1.0/E_func(zp, *params), 0, zi)
        DM = C_KMS / 100.0 * integral
        DH = C_KMS / 100.0 / E_func(zi, *params)
        DV = (zi * DM**2 * DH)**(1/3)
        DM_over_rd[i] = DM / rd
        DH_over_rd[i] = DH / rd
        DV_over_rd[i] = DV / rd
    return DM_over_rd, DH_over_rd, DV_over_rd


def chi2_bao(z, val, qty, cov_abs, E_func, params, rd):
    DM_over_rd, DH_over_rd, DV_over_rd = predecir_observables(z, E_func, params, rd)
    pred = np.zeros_like(val)
    for i, q in enumerate(qty):
        if "DM" in q:
            pred[i] = DM_over_rd[i]
        elif "DH" in q:
            pred[i] = DH_over_rd[i]
        elif "DV" in q:
            pred[i] = DV_over_rd[i]
    delta = val - pred
    cov_inv = np.linalg.inv(cov_abs)
    return delta @ cov_inv @ delta


def chi2_sne(z_sne, mu_sne, mu_err_sne, E_func, params, H0):
    """Calcula chi2 de SNe con H0 ajustable."""
    c_over_H0 = C_KMS / H0
    mu_pred = np.zeros_like(z_sne)
    for i, zi in enumerate(z_sne):
        integral, _ = quad(lambda zp: 1.0/E_func(zp, *params), 0, zi)
        DL = c_over_H0 * (1+zi) * integral  # Mpc
        mu_pred[i] = 5 * np.log10(DL) + 25  # mag
    delta = mu_sne - mu_pred
    return np.sum((delta / mu_err_sne)**2)


def main():
    print("=" * 70)
    print("  AJUSTE COSMOLOGICO PROFUNDO - BAO + SNe")
    print("=" * 70)
    
    z_bao, val_bao, qty_bao, cov_bao = cargar_bao()
    z_sne, mu_sne, mu_err_sne = cargar_sne()
    print(f"BAO: {len(z_bao)} puntos")
    print(f"SNe: {len(z_sne)} puntos")
    
    # === LCDM ===
    print("\n[1] Ajuste Lambda-CDM (BAO + SNe)...")
    def neg_chi2_lcdm(p):
        Om, rd, H0 = p
        if Om < 0.15 or Om > 0.45 or rd < 130 or rd > 165 or H0 < 60 or H0 > 80:
            return 1e10
        try:
            c_bao = chi2_bao(z_bao, val_bao, qty_bao, cov_bao, E_LCDM, [Om], rd)
            c_sne = chi2_sne(z_sne, mu_sne, mu_err_sne, E_LCDM, [Om], H0)
            return c_bao + c_sne
        except:
            return 1e10
    
    res_lcdm = minimize(neg_chi2_lcdm, x0=[0.3, 147.5, 70], method="Nelder-Mead",
                        options={"xatol": 1e-5, "fatol": 1e-5, "maxiter": 20000})
    Om_l, rd_l, H0_l = res_lcdm.x
    c_bao_l = chi2_bao(z_bao, val_bao, qty_bao, cov_bao, E_LCDM, [Om_l], rd_l)
    c_sne_l = chi2_sne(z_sne, mu_sne, mu_err_sne, E_LCDM, [Om_l], H0_l)
    n_data_l = len(z_bao) + len(z_sne)
    dof_l = n_data_l - 3
    print(f"  Om = {Om_l:.4f}, rd = {rd_l:.2f}, H0 = {H0_l:.2f}")
    print(f"  chi2_BAO = {c_bao_l:.2f}, chi2_SNe = {c_sne_l:.2f}, total = {res_lcdm.fun:.2f}")
    print(f"  chi2/dof = {res_lcdm.fun/dof_l:.3f}")
    
    # === THU ===
    print("\n[2] Ajuste THU (BAO + SNe)...")
    def neg_chi2_thu(p):
        Om, Otau, rd, H0 = p
        if Om < 0.15 or Om > 0.45 or Otau < 0 or Otau > 0.2 or rd < 130 or rd > 165 or H0 < 60 or H0 > 80:
            return 1e10
        if Om + Otau > 0.95:
            return 1e10
        try:
            c_bao = chi2_bao(z_bao, val_bao, qty_bao, cov_bao, E_THU, [Om, Otau], rd)
            c_sne = chi2_sne(z_sne, mu_sne, mu_err_sne, E_THU, [Om, Otau], H0)
            return c_bao + c_sne
        except:
            return 1e10
    
    mejor = None
    for x0 in [[0.3, 0.01, 147.5, 70], [0.3, 0.05, 147.5, 70], [0.35, 0.02, 147.5, 70], [0.25, 0.01, 147.5, 70]]:
        res = minimize(neg_chi2_thu, x0=x0, method="Nelder-Mead",
                       options={"xatol": 1e-5, "fatol": 1e-5, "maxiter": 30000})
        if mejor is None or res.fun < mejor.fun:
            mejor = res
    res_thu = mejor
    Om_t, Otau_t, rd_t, H0_t = res_thu.x
    c_bao_t = chi2_bao(z_bao, val_bao, qty_bao, cov_bao, E_THU, [Om_t, Otau_t], rd_t)
    c_sne_t = chi2_sne(z_sne, mu_sne, mu_err_sne, E_THU, [Om_t, Otau_t], H0_t)
    dof_t = n_data_l - 4
    print(f"  Om = {Om_t:.4f}, Otau = {Otau_t:.4f}, rd = {rd_t:.2f}, H0 = {H0_t:.2f}")
    print(f"  chi2_BAO = {c_bao_t:.2f}, chi2_SNe = {c_sne_t:.2f}, total = {res_thu.fun:.2f}")
    print(f"  chi2/dof = {res_thu.fun/dof_t:.3f}")
    
    # === Comparacion ===
    print("\n[3] Comparacion:")
    aic_l = res_lcdm.fun + 2*3
    aic_t = res_thu.fun + 2*4
    delta_aic = aic_t - aic_l
    print(f"  chi2_LCDM = {res_lcdm.fun:.2f} (k=3), AIC = {aic_l:.2f}")
    print(f"  chi2_THU  = {res_thu.fun:.2f} (k=4), AIC = {aic_t:.2f}")
    print(f"  Delta AIC = {delta_aic:.2f}")
    
    # === Perfil de Otau ===
    print("\n[4] Perfil de chi2 en funcion de Otau (fijando Om, rd, H0)...")
    Otau_vals = np.linspace(0, 0.1, 11)
    chi2_profile = []
    for ot in Otau_vals:
        def neg_profile(p):
            Om, rd, H0 = p
            if Om + ot > 0.95:
                return 1e10
            try:
                c_bao = chi2_bao(z_bao, val_bao, qty_bao, cov_bao, E_THU, [Om, ot], rd)
                c_sne = chi2_sne(z_sne, mu_sne, mu_err_sne, E_THU, [Om, ot], H0)
                return c_bao + c_sne
            except:
                return 1e10
        r = minimize(neg_profile, x0=[0.3, 147.5, 70], method="Nelder-Mead",
                     options={"xatol": 1e-4, "fatol": 1e-4, "maxiter": 5000})
        chi2_profile.append(r.fun)
        print(f"  Otau = {ot:.3f}: chi2 = {r.fun:.2f} (Delta chi2 = {r.fun - res_lcdm.fun:+.2f})")
    
    # Guardar
    resultado = {
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "datos": "DESI DR2 BAO (13) + Pantheon+ SNe (" + str(len(z_sne)) + ")",
        "modelo_LCDM": {
            "Om": float(Om_l), "rd": float(rd_l), "H0": float(H0_l),
            "chi2_BAO": float(c_bao_l), "chi2_SNe": float(c_sne_l),
            "chi2_total": float(res_lcdm.fun), "chi2_dof": float(res_lcdm.fun/dof_l),
            "k": 3, "AIC": float(aic_l),
        },
        "modelo_THU": {
            "Om": float(Om_t), "Otau": float(Otau_t), "rd": float(rd_t), "H0": float(H0_t),
            "chi2_BAO": float(c_bao_t), "chi2_SNe": float(c_sne_t),
            "chi2_total": float(res_thu.fun), "chi2_dof": float(res_thu.fun/dof_t),
            "k": 4, "AIC": float(aic_t),
        },
        "delta_AIC": float(delta_aic),
        "perfil_Otau": {
            "Otau": [float(x) for x in Otau_vals],
            "chi2": [float(x) for x in chi2_profile],
        },
        "veredicto": "THU preferido" if delta_aic < -2 else ("LCDM preferido" if delta_aic > 2 else "Equivalentes"),
    }
    
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as fh:
        json.dump(resultado, fh, indent=2, ensure_ascii=False)
    print(f"\nGuardado: {OUT_FILE}")


if __name__ == "__main__":
    main()