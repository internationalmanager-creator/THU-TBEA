# -*- coding: utf-8 -*-
"""E.3-C8c-bis — Diagnostico completo con API sacc corregida."""
import sys, traceback
from pathlib import Path
import numpy as np

REPO = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto\data\raw\cosmic-birefringence-planck-act")
BM = REPO / "beta_mcmc"
SACC = REPO / "data" / "act_dr6" / "v1.0" / "dr6_data.fits"

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# --- 1: ells por data_type usando API sacc correcta ---
hdr("1. Rangos ell por data_type (via API sacc)")

import sacc as sacc_mod
s = sacc_mod.Sacc.load_fits(str(SACC))

from collections import Counter
types = Counter()
for d in s.data:
    types[d.data_type] += 1

for dt in sorted(types):
    ells = []
    for d in s.data:
        if d.data_type == dt:
            try:
                ell = d.get_ell()
                if hasattr(ell, '__iter__'):
                    ells.extend(ell)
                else:
                    ells.append(ell)
            except Exception:
                pass
    if ells:
        arr = np.array(ells)
        print(f"  {dt:8s}: n={len(arr)}, ell=[{arr.min():.1f}, {arr.max():.1f}], unique={len(np.unique(arr))}")

# --- 2: data_dict ---
hdr("2. Cargar data_dict via pipeline Eskilt")

sys.path.insert(0, str(BM))
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "beta_mcmc" / "act_dr6"))

from act_dr6.core import load_act_sacc_data
bands = ["pa4_f220", "pa5_f090", "pa5_f150", "pa6_f090", "pa6_f150"]
data_dict = load_act_sacc_data(bands)
print(f"  data_dict keys: {list(data_dict.keys())}")
print(f"  n_bins: {data_dict['n_bins']}")
print(f"  n_cross: {len(data_dict['cross_spec_list'])}")
print(f"  alpha_labels: {data_dict['alpha_labels']}")

lc = data_dict['likelihood_cache']
print(f"\n  likelihood_cache:")
for k, v in lc.items():
    if hasattr(v, 'shape'):
        print(f"    {k}: shape={v.shape}")
    else:
        print(f"    {k}: {type(v).__name__}")

# --- 3: bin_groups ---
hdr("3. bin_groups (estructura clave del bug)")

if 'bin_groups' in data_dict:
    bg = data_dict['bin_groups']
    print(f"  Total grupos: {len(bg)}")
    for i, (active_idx, bin_idx) in enumerate(bg):
        active_idx = np.asarray(active_idx)
        bin_idx = np.asarray(bin_idx)
        print(f"    grupo {i}: active_idx.shape={active_idx.shape}, bin_idx.shape={bin_idx.shape}")
    print(f"\n  Interpretacion: cada grupo tiene los indices activos y los bins por resolver")
else:
    print(f"  NO HAY bin_groups")

# --- 4: Reproducir bug L202 ---
hdr("4. Reproducir bug np.linalg.solve(M_batch, v_batch)")

from birefringence_likelihood import (
    _compute_residuals_and_covariance, mk_chi2
)

n_cross = len(data_dict['cross_spec_list'])
beta = 0.19
alpha_i = np.zeros(n_cross)
alpha_j = np.zeros(n_cross)

print(f"  Simulando beta={beta}, alpha_i.shape={alpha_i.shape}, alpha_j.shape={alpha_j.shape}")

v_all, M_full = _compute_residuals_and_covariance(
    alpha_i, alpha_j, beta, data_dict['likelihood_cache'], f_ell=None)
print(f"  v_all.shape = {v_all.shape}")
print(f"  M_full.shape = {M_full.shape}")

# Loop del bug
print(f"\n  Reproduciendo loop sobre bin_groups:")
if 'bin_groups' in data_dict:
    for k, (active_idx, bin_idx) in enumerate(data_dict['bin_groups']):
        active_idx = np.asarray(active_idx)
        bin_idx = np.asarray(bin_idx)
        try:
            v_batch = v_all[np.ix_(bin_idx, active_idx)]
            M_batch = M_full[np.ix_(bin_idx, active_idx, active_idx)]
            print(f"    grupo {k}: active_idx={active_idx.shape}, bin_idx={bin_idx.shape}")
            print(f"      v_batch.shape={v_batch.shape}, M_batch.shape={M_batch.shape}")
            M_inv_v = np.linalg.solve(M_batch, v_batch)
            print(f"      solve OK: M_inv_v.shape={M_inv_v.shape}")
        except Exception as e:
            print(f"    grupo {k}: ERROR -> {e}")
            print(f"      v_batch: shape={v_batch.shape if 'v_batch' in dir() else '?'}")
            print(f"      M_batch: shape={M_batch.shape if 'M_batch' in dir() else '?'}")
            print(f"      np.linalg.solve requiere M_batch (..., n, n) y v_batch (..., n)")
            if 'M_batch' in dir() and 'v_batch' in dir():
                print(f"      -> M_batch.shape[-2:] = {M_batch.shape[-2:]}")
                print(f"      -> v_batch.shape[-1] = {v_batch.shape[-1]}")
            break

# --- 5: Test HDF5 ---
hdr("5. Test escritura HDF5 en data/computed/")

COMPUTED = REPO / "data" / "computed"
print(f"  data/computed/ existe: {COMPUTED.exists()}")
print(f"  Es directorio: {COMPUTED.is_dir()}")
print(f"  Contenido: {[x.name for x in COMPUTED.iterdir()]}")

import h5py
import emcee

test_h5 = COMPUTED / "_test_h5.h5"
try:
    with h5py.File(test_h5, "w") as f:
        f.create_dataset("test", data=np.array([1,2,3]))
    print(f"  h5py escribe: OK ({test_h5.stat().st_size} bytes)")
    test_h5.unlink()
except Exception as e:
    print(f"  h5py escribe: ERROR -> {e}")

test_chain = COMPUTED / "_test_chain.h5"
try:
    backend = emcee.backends.HDFBackend(str(test_chain))
    print(f"  HDFBackend instanciado: OK")
    print(f"  Archivo existe inmediatamente: {test_chain.exists()}")
    if test_chain.exists():
        print(f"  Tamano: {test_chain.stat().st_size} bytes")
    # Test escritura real
    def logp(x):
        return -0.5 * np.sum(x**2)
    sampler = emcee.EnsembleSampler(2, 2, logp, backend=backend)
    sampler.run_mcmc(np.random.randn(2, 2), 5, progress=False)
    print(f"  run_mcmc OK, iteracion final: {sampler.iteration}")
    if test_chain.exists():
        print(f"  Archivo tras run: {test_chain.stat().st_size} bytes")
    test_chain.unlink()
except Exception as e:
    print(f"  emcee HDFBackend: ERROR -> {e}")
    traceback.print_exc()

# --- 6: Test solve con shapes correctas ---
hdr("6. Test fix candidato para el bug")

if 'bin_groups' in data_dict:
    # Tomar primer grupo
    active_idx, bin_idx = data_dict['bin_groups'][0]
    active_idx = np.asarray(active_idx)
    bin_idx = np.asarray(bin_idx)
    
    v_batch = v_all[np.ix_(bin_idx, active_idx)]
    M_batch = M_full[np.ix_(bin_idx, active_idx, active_idx)]
    
    print(f"  Shapes actuales:")
    print(f"    v_batch.shape = {v_batch.shape}")
    print(f"    M_batch.shape = {M_batch.shape}")
    print()
    print(f"  np.linalg.solve espera:")
    print(f"    M_batch (..., N, N)")
    print(f"    v_batch (..., N)")
    print()
    
    # Intento 1: squeeze de v_batch
    if v_batch.ndim == 3 and v_batch.shape[-1] == 1:
        v_sq = v_batch.squeeze(-1)
        print(f"  Fix candidato 1: v_batch.squeeze(-1) -> shape={v_sq.shape}")
        try:
            r = np.linalg.solve(M_batch, v_sq)
            print(f"    OK: resultado shape={r.shape}")
        except Exception as e:
            print(f"    FALLA: {e}")
    
    # Intento 2: broadcasting
    print(f"\n  Fix candidato 2: interpretar como batch")
    print(f"    v_all.shape = {v_all.shape}")
    print(f"    M_full.shape = {M_full.shape}")
    print(f"    -> Si v_all es (n_bins, n_cross) y M_full es (n_bins, n_cross, n_cross)")
    print(f"       entonces el solve correcto seria por bin:")
    # Test: por bin
    bin_0 = bin_idx[0]
    v_0 = v_all[bin_0, active_idx]   # shape (n_active,)
    M_0 = M_full[bin_0][np.ix_(active_idx, active_idx)]  # shape (n_active, n_active)
    print(f"    v_all[bin_0, active_idx] = {v_0.shape}")
    print(f"    M_full[bin_0][active_idx, active_idx] = {M_0.shape}")
    try:
        r = np.linalg.solve(M_0, v_0)
        print(f"    solve OK: shape={r.shape}")
    except Exception as e:
        print(f"    FALLA: {e}")

# --- 7: Inspeccionar _compute_residuals_and_covariance ---
hdr("7. Codigo de _compute_residuals_and_covariance")
import inspect
src = inspect.getsource(_compute_residuals_and_covariance)
for i, l in enumerate(src.splitlines()[:100], 1):
    print(f"  L{i:3d}: {l}")
