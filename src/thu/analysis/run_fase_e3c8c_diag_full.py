# -*- coding: utf-8 -*-
"""E.3-C8c — Diagnostico completo: datos, analisis, ecuaciones."""
import sys, json, traceback
from pathlib import Path
import numpy as np

REPO = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto\data\raw\cosmic-birefringence-planck-act")
BM = REPO / "beta_mcmc"
SACC = REPO / "data" / "act_dr6" / "v1.0" / "dr6_data.fits"

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# ============================================================
# PARTE 1: DATOS
# ============================================================
hdr("PARTE 1 — DATOS: verificacion de integridad del SACC")

import sacc as sacc_mod
s = sacc_mod.Sacc.load_fits(str(SACC))
print(f"  SACC cargado: {len(s.data)} entries")

from collections import Counter
types = Counter()
for d in s.data:
    types[d.data_type] += 1
print(f"  Data types:")
for dt in sorted(types):
    print(f"    {dt:8s} x{types[dt]}")

# Verificar covarianza
cov = s.covariance.covmat
print(f"\n  Covarianza: shape={cov.shape}, dtype={cov.dtype}")
print(f"  Simetria max|cov-cov.T| = {np.max(np.abs(cov - cov.T)):.4e}")
try:
    eigvals = np.linalg.eigvalsh(cov)
    print(f"  Autovalores: min={eigvals.min():.4e}, max={eigvals.max():.4e}")
    print(f"  Condicionamiento: {eigvals.max()/max(eigvals.min(), 1e-300):.4e}")
    print(f"  Positivo definido: {eigvals.min() > 0}")
except Exception as e:
    print(f"  Error eigvalsh: {e}")

# Tracers
tracers = sorted(set(t for d in s.data for t in d.tracers))
print(f"\n  {len(tracers)} tracers unicos:")
for t in tracers:
    print(f"    {t}")

# Mapear data_type -> ell_range
hdr("PARTE 1b — Rango ell por data_type")
for dt in sorted(types):
    ells = []
    for d in s.data:
        if d.data_type == dt:
            ells.extend(d.get_ell())
    ells = np.array(ells)
    if len(ells):
        print(f"    {dt:8s}: ell=[{ells.min():.1f}, {ells.max():.1f}], n={len(ells)}, unique={len(np.unique(ells))}")

# ============================================================
# PARTE 2: ANALISIS — extraer data_dict como lo hace el pipeline
# ============================================================
hdr("PARTE 2 — ANALISIS: cargar data_dict via load_act_sacc_data")

sys.path.insert(0, str(BM))
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "beta_mcmc" / "act_dr6"))

try:
    from act_dr6.core import load_act_sacc_data
    bands = ["pa4_f220", "pa5_f090", "pa5_f150", "pa6_f090", "pa6_f150"]
    print(f"  Llamando load_act_sacc_data(bands={bands})...")
    data_dict = load_act_sacc_data(bands)
    print(f"  OK: data_dict cargado")
    print(f"  Keys: {list(data_dict.keys())}")
except Exception as e:
    print(f"  ERROR cargando data_dict: {e}")
    traceback.print_exc()
    sys.exit(1)

# Inspeccionar shapes
hdr("PARTE 2b — Inspeccionar shapes internas")
lc = data_dict['likelihood_cache']
print(f"  likelihood_cache keys: {list(lc.keys())}")
for k, v in lc.items():
    if hasattr(v, 'shape'):
        print(f"    {k}: shape={v.shape}, dtype={v.dtype}")
    else:
        print(f"    {k}: {type(v).__name__}")

print(f"\n  data_dict['n_bins']: {data_dict.get('n_bins')}")
print(f"  data_dict['ell']: shape={data_dict['ell'].shape}")
print(f"  data_dict['cross_spec_list']: {len(data_dict['cross_spec_list'])} pares")
print(f"  data_dict['alpha_labels']: {data_dict.get('alpha_labels')}")

# Inspeccionar bin_groups si existe
if 'bin_groups' in data_dict:
    bg = data_dict['bin_groups']
    print(f"\n  bin_groups: {len(bg)} grupos")
    for i, (active_idx, bin_idx) in enumerate(bg[:5]):
        print(f"    grupo {i}: active_idx={np.array(active_idx).shape}, bin_idx={np.array(bin_idx).shape}")
    if len(bg) > 5:
        print(f"    ... ({len(bg)-5} mas)")
else:
    print(f"\n  'bin_groups' NO esta en data_dict")

# ============================================================
# PARTE 3: ECUACIONES — formula de rotacion
# ============================================================
hdr("PARTE 3 — ECUACIONES: verificar formula de rotacion MK")

import inspect
from birefringence_likelihood import (
    _compute_residuals_and_covariance, mk_chi2
)

# Ver firma y primeras lineas
print("  _compute_residuals_and_covariance:")
sig = inspect.signature(_compute_residuals_and_covariance)
print(f"    signature: {sig}")
src = inspect.getsource(_compute_residuals_and_covariance)
print(f"    source (primeras 80 lineas):")
for i, l in enumerate(src.splitlines()[:80], 1):
    print(f"      L{i:3d}: {l}")

# ============================================================
# PARTE 4: REPRODUCIR BUG
# ============================================================
hdr("PARTE 4 — REPRODUCIR BUG DE L202 paso a paso")

# Simular parametros
n_alpha = len(data_dict.get('alpha_labels', []))
beta = 0.19  # grados
alpha_i = np.zeros(len(data_dict['cross_spec_list']))
alpha_j = np.zeros(len(data_dict['cross_spec_list']))

print(f"  Simulando: beta={beta}, n_alpha={n_alpha}")
print(f"  alpha_i shape: {alpha_i.shape}")
print(f"  alpha_j shape: {alpha_j.shape}")

try:
    v_all, M_full = _compute_residuals_and_covariance(
        alpha_i, alpha_j, beta, data_dict['likelihood_cache'], f_ell=None)
    print(f"  v_all: shape={v_all.shape}")
    print(f"  M_full: shape={M_full.shape}")
except Exception as e:
    print(f"  ERROR en _compute_residuals_and_covariance: {e}")
    traceback.print_exc()
    sys.exit(1)

# Reproducir el loop de L199-204
if 'bin_groups' in data_dict:
    print(f"\n  Reproduciendo loop sobre bin_groups:")
    for k, (active_idx, bin_idx) in enumerate(data_dict['bin_groups']):
        active_idx = np.asarray(active_idx)
        bin_idx = np.asarray(bin_idx)
        try:
            v_batch = v_all[np.ix_(bin_idx, active_idx)]
            M_batch = M_full[np.ix_(bin_idx, active_idx, active_idx)]
            print(f"    grupo {k}: active_idx={active_idx.shape}, bin_idx={bin_idx.shape}")
            print(f"      v_batch shape: {v_batch.shape}")
            print(f"      M_batch shape: {M_batch.shape}")
            M_inv_v = np.linalg.solve(M_batch, v_batch)
            print(f"      solve OK, M_inv_v shape: {M_inv_v.shape}")
        except Exception as e:
            print(f"    grupo {k}: ERROR -> {e}")
            print(f"      active_idx={active_idx[:10]}")
            print(f"      bin_idx={bin_idx[:10]}")
            print(f"      M_batch expected (batch, n, n), v_batch expected (batch, n)")
            print(f"      M_batch.shape={M_batch.shape}, v_batch.shape={v_batch.shape}")
            if M_batch.ndim >= 2 and v_batch.ndim >= 2:
                print(f"      -> M_batch[-2:]={M_batch.shape[-2:]}, v_batch[-1]={v_batch.shape[-1]}")
            break
else:
    print(f"  Sin bin_groups, ejecutando np.linalg.solve(M_full, v_all) directo")
    print(f"  M_full shape: {M_full.shape}, v_all shape: {v_all.shape}")
    try:
        result = np.linalg.solve(M_full, v_all)
        print(f"  solve OK: {result.shape}")
    except Exception as e:
        print(f"  ERROR: {e}")

# ============================================================
# PARTE 5: TEST DE ESCRITURA HDF5
# ============================================================
hdr("PARTE 5 — TEST: escritura HDF5 en data/computed/")

COMPUTED = REPO / "data" / "computed"
print(f"  Existe data/computed/: {COMPUTED.exists()}")
print(f"  Es directorio: {COMPUTED.is_dir()}")

# Test de escritura
test_file = COMPUTED / "_test_h5.h5"
try:
    import h5py
    with h5py.File(test_file, "w") as f:
        f.create_dataset("test", data=np.array([1,2,3]))
    print(f"  OK: h5py escribio {test_file.name}")
    size = test_file.stat().st_size
    print(f"  Tamano: {size} bytes")
    test_file.unlink()  # limpiar
    print(f"  Test limpio: eliminado")
except Exception as e:
    print(f"  ERROR: {e}")
    traceback.print_exc()

# Test emcee HDFBackend
test_chain = COMPUTED / "_test_chain.h5"
try:
    import emcee
    backend = emcee.backends.HDFBackend(str(test_chain))
    print(f"  emcee HDFBackend instanciado OK en {test_chain.name}")
    print(f"  Archivo existe tras instanciacion: {test_chain.exists()}")
    if test_chain.exists():
        print(f"  Tamano: {test_chain.stat().st_size} bytes")
        test_chain.unlink()
        print(f"  Test limpio: eliminado")
except Exception as e:
    print(f"  ERROR: {e}")
    traceback.print_exc()

# ============================================================
# PARTE 6: TEST MODO ALL vs BETA_ONLY
# ============================================================
hdr("PARTE 6 — Comparar modo beta_only vs all")

# En modo beta_only, n_params = 1
# En modo all, n_params = 1 + n_alpha
n_params_beta_only = 1
n_params_all = 1 + n_alpha

print(f"  beta_only: n_params = {n_params_beta_only}")
print(f"  all: n_params = {n_params_all}")

# Inspeccionar como se construye el pos inicial en el codigo
print(f"\n  Buscando inicializacion de pos en run_beta_mcmc.py...")
run_file = BM / "run_beta_mcmc.py"
lines = run_file.read_text(encoding="utf-8").splitlines()
for i, l in enumerate(lines, 1):
    if "SAMPLING_MODE" in l or "n_params" in l or "pos" in l and "=" in l:
        if "SAMPLING_MODE" in l or "n_params =" in l:
            print(f"    L{i}: {l}")

# ============================================================
# PARTE 7: RESUMEN
# ============================================================
hdr("PARTE 7 — Resumen de diagnostico")

print("  DATOS:")
print(f"    SACC entries: {len(s.data)}")
print(f"    Data types: {dict(types)}")
print(f"    Covarianza positiva definida: {eigvals.min() > 0 if 'eigvals' in dir() else 'N/A'}")
print()
print("  ANALISIS:")
print(f"    n_cross (pares): {len(data_dict['cross_spec_list'])}")
print(f"    n_bins (ell): {data_dict['n_bins']}")
print(f"    bin_groups: {len(data_dict.get('bin_groups', []))}")
print()
print("  ECUACIONES:")
print(f"    Formula de rotacion en _compute_residuals_and_covariance")
print(f"    Chi2 via np.linalg.solve por bin_group")
print()
print("  BUGS:")
print(f"    - HDF5 no se creo (ver Parte 5)")
print(f"    - Crash L202 en modo beta_only (ver Parte 4)")
