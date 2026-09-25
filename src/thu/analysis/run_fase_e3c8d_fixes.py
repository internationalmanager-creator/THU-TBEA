# -*- coding: utf-8 -*-
"""E.3-C8d — Fix mk_chi2 + HDF5 flush + config SAMPLING_MODE='all'."""
import sys, shutil, py_compile
from pathlib import Path

REPO = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto\data\raw\cosmic-birefringence-planck-act")
BM = REPO / "beta_mcmc"

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# ============================================================
# FIX 1: mk_chi2 (bug L202)
# ============================================================
hdr("FIX 1: mk_chi2 L202")

bl_file = BM / "birefringence_likelihood.py"
backup = bl_file.parent / "birefringence_likelihood.py.orig"
if not backup.exists():
    shutil.copy2(bl_file, backup)
    print(f"  Backup: {backup.name}")
else:
    print(f"  Backup ya existe")

txt = bl_file.read_text(encoding="utf-8")

OLD = """            v_batch = v_all[np.ix_(bin_idx, active_idx)]
            M_batch = M_full[np.ix_(bin_idx, active_idx, active_idx)]
            M_inv_v = np.linalg.solve(M_batch, v_batch)
            chi2_total += float(np.einsum('bi,bi->', v_batch, M_inv_v))
            n_data += len(bin_idx) * len(active_idx)"""

NEW = """            v_batch = v_all[np.ix_(bin_idx, active_idx)]
            M_batch = M_full[np.ix_(bin_idx, active_idx, active_idx)]
            # === [E.3-C8d] Fix shape: v_batch puede ser (N,1) y solve lo interpreta mal.
            # Solucion: anadir dim extra y quitar despues.
            # solve(M(N,N), v(N,1)) falla porque numpy ve (N,1) como (M=N, K=1).
            # solve(M(N,N), v(N,1,1)) funciona porque (1,) se interpreta como K=1.
            M_inv_v = np.linalg.solve(M_batch, v_batch[..., None])[..., 0]
            # === fin [E.3-C8d] ===
            chi2_total += float(np.einsum('bi,bi->', v_batch, M_inv_v))
            n_data += len(bin_idx) * len(active_idx)"""

if OLD not in txt:
    print(f"  ADVERTENCIA: anchor no encontrado. Verificar si ya parcheado.")
else:
    txt = txt.replace(OLD, NEW, 1)
    bl_file.write_text(txt, encoding="utf-8")
    print(f"  OK: parche aplicado")

try:
    py_compile.compile(str(bl_file), doraise=True)
    print(f"  py_compile: OK")
except py_compile.PyCompileError as e:
    print(f"  ERROR: {e}")
    shutil.copy2(backup, bl_file)
    sys.exit(1)

# ============================================================
# FIX 2: HDF5 flush periodico en _run_mcmc
# ============================================================
hdr("FIX 2: HDF5 flush en run_beta_mcmc.py")

run_file = BM / "run_beta_mcmc.py"
backup2 = run_file.parent / "run_beta_mcmc.py.orig2"
if not backup2.exists():
    shutil.copy2(run_file, backup2)
    print(f"  Backup: {backup2.name}")
else:
    print(f"  Backup ya existe")

txt = run_file.read_text(encoding="utf-8")

# Reemplazar el loop fresh start para que flushee cada 100 pasos
OLD_LOOP = """        else:
            print(f"[E.3-C7] Fresh start, {n_steps} iteraciones")
            for _ in tqdm(sampler.sample(pos, iterations=n_steps),
                          total=n_steps, desc="MCMC"):
                pass
        # === fin [E.3-C7] ==="""

NEW_LOOP = """        else:
            print(f"[E.3-C7] Fresh start, {n_steps} iteraciones")
            for _i, _state in enumerate(tqdm(
                    sampler.sample(pos, iterations=n_steps),
                    total=n_steps, desc="MCMC")):
                # === [E.3-C8d] Flush cada 100 pasos para persistir HDF5 ===
                if (_i + 1) % 100 == 0:
                    try:
                        _hb = sampler.backend
                        # h5py.File objeto interno
                        _f = getattr(_hb, '_f', None) or getattr(_hb, 'file', None)
                        if _f is not None and hasattr(_f, 'flush'):
                            _f.flush()
                    except Exception:
                        pass
                # === fin [E.3-C8d] ===
        # === fin [E.3-C7] ==="""

if OLD_LOOP not in txt:
    print(f"  ADVERTENCIA: anchor del loop no encontrado. Saltando FIX 2.")
else:
    txt = txt.replace(OLD_LOOP, NEW_LOOP, 1)
    run_file.write_text(txt, encoding="utf-8")
    print(f"  OK: flush cada 100 pasos anadido")

try:
    py_compile.compile(str(run_file), doraise=True)
    print(f"  py_compile: OK")
except py_compile.PyCompileError as e:
    print(f"  ERROR: {e}")
    shutil.copy2(backup2, run_file)
    sys.exit(1)

# ============================================================
# FIX 3: config.py -> SAMPLING_MODE='all', pasos realistas
# ============================================================
hdr("FIX 3: config.py -> modo all + 3000 pasos test")

cfg_file = BM / "config.py"
txt = cfg_file.read_text(encoding="utf-8")

# Cambiar a modo 'all' (paper mode, marginaliza alphas)
txt2 = txt.replace('SAMPLING_MODE = "beta_only"', 'SAMPLING_MODE = "all"', 1)
if txt2 != txt:
    txt = txt2
    print("  SAMPLING_MODE: beta_only -> all")
else:
    # Puede estar ya en 'all' o no haber sido cambiado
    if 'SAMPLING_MODE = "all"' in txt:
        print("  SAMPLING_MODE ya es 'all'")
    else:
        print("  ADVERTENCIA: SAMPLING_MODE no encontrado")

# Dejar 3000 pasos para el test (o subir si ya fue cambiado)
if 'MCMC_N_STEPS = 50' in txt:
    txt = txt.replace('MCMC_N_STEPS = 50', 'MCMC_N_STEPS = 3000', 1)
    print("  MCMC_N_STEPS: 50 -> 3000")
elif 'MCMC_N_STEPS = 3000' in txt:
    print("  MCMC_N_STEPS ya es 3000")
else:
    print("  ADVERTENCIA: MCMC_N_STEPS no encontrado")

if 'MCMC_N_BURN = 20' in txt:
    txt = txt.replace('MCMC_N_BURN = 20', 'MCMC_N_BURN = 500', 1)
    print("  MCMC_N_BURN: 20 -> 500")
elif 'MCMC_N_BURN = 500' in txt:
    print("  MCMC_N_BURN ya es 500")

cfg_file.write_text(txt, encoding="utf-8")
try:
    py_compile.compile(str(cfg_file), doraise=True)
    print("  py_compile: OK")
except py_compile.PyCompileError as e:
    print(f"  ERROR: {e}")
    sys.exit(1)

# ============================================================
# FIX 4: limpiar HDF5 anterior si existe
# ============================================================
hdr("FIX 4: limpiar HDF5 previo (si existe)")

h5 = REPO / "data" / "computed" / "mcmc_chain.h5"
if h5.exists():
    size = h5.stat().st_size
    h5.unlink()
    print(f"  Eliminado: {h5.name} ({size} bytes)")
else:
    print(f"  No existe (limpio)")

print()
print("="*72)
print("  E.3-C8d: FIXES APLICADOS")
print("="*72)
print()
print("  Para lanzar la corrida de test (3000 pasos):")
print(f"    cd {BM}")
print(f"    python run_beta_mcmc.py")
print()
print("  Comportamiento esperado:")
print("    - Sampler con 18 walkers (2*workers) o similar")
print("    - N_params: 1 (beta) + 5 (alphas) + 3 (dust) = 9")
print("    - Tiempo estimado: 5-15 min")
print("    - Si se corta la luz: relanzar el comando reanuda")
print()
print("  Backups para rollback:")
print(f"    {backup}")
print(f"    {backup2}")
