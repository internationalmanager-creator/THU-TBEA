# -*- coding: utf-8 -*-
"""E.3-C7 — Backup + patch HDF5 + config para primer test."""
import sys, shutil, re, py_compile
from pathlib import Path

REPO = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto\data\raw\cosmic-birefringence-planck-act")
BM = REPO / "beta_mcmc"

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# --- 1: Backup ---
hdr("1. Backup de archivos originales")

for f in ["run_beta_mcmc.py", "config.py"]:
    src = BM / f
    dst = BM / (f + ".orig")
    if dst.exists():
        print(f"  {f}.orig ya existe, saltando")
    else:
        shutil.copy2(src, dst)
        print(f"  Backup: {f} -> {f}.orig")

# --- 2: Patch de run_beta_mcmc.py ---
hdr("2. Patch HDF5 en run_beta_mcmc.py")

run_file = BM / "run_beta_mcmc.py"
txt = run_file.read_text(encoding="utf-8")

# 2a. Insertar import de HDFBackend y CHAIN_FILE despues de imports
ANCHOR_IMPORT = "import multiprocessing\nimport numpy as np\nimport emcee"
if ANCHOR_IMPORT not in txt:
    print(f"  ERROR: anchor de import no encontrado. Abortando.")
    sys.exit(1)

NEW_IMPORTS = """import multiprocessing
import numpy as np
import emcee
from emcee.backends import HDFBackend

# === [E.3-C7] Checkpoint global ===
import os as _os
_CHAIN_FILE = _os.path.normpath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "data", "computed", "mcmc_chain.h5"))
_os.makedirs(_os.path.dirname(_CHAIN_FILE), exist_ok=True)
print(f"[E.3-C7] Checkpoint activo: {_CHAIN_FILE}")
# === fin [E.3-C7] ===
"""

txt2 = txt.replace(ANCHOR_IMPORT, NEW_IMPORTS, 1)
if txt2 == txt:
    print("  ERROR: no se pudo insertar imports")
    sys.exit(1)
txt = txt2
print(f"  OK: import HDFBackend añadido")

# 2b. Añadir backend= a las dos llamadas de EnsembleSampler
OLD_PARALLEL = """sampler = emcee.EnsembleSampler(
                n_walkers, n_params, _worker_call, pool=pool
            )"""
NEW_PARALLEL = """sampler = emcee.EnsembleSampler(
                n_walkers, n_params, _worker_call, pool=pool,
                backend=HDFBackend(_CHAIN_FILE)
            )"""

OLD_SERIAL = """sampler = emcee.EnsembleSampler(
                n_walkers, n_params, log_posterior_fn, args=log_posterior_args
            )"""
NEW_SERIAL = """sampler = emcee.EnsembleSampler(
                n_walkers, n_params, log_posterior_fn, args=log_posterior_args,
                backend=HDFBackend(_CHAIN_FILE)
            )"""

txt2 = txt.replace(OLD_PARALLEL, NEW_PARALLEL, 1)
if txt2 == txt:
    print("  ERROR: no se pudo parchear EnsembleSampler (parallel)")
    sys.exit(1)
txt = txt2
print(f"  OK: backend añadido a EnsembleSampler (parallel)")

txt2 = txt.replace(OLD_SERIAL, NEW_SERIAL, 1)
if txt2 == txt:
    print("  ERROR: no se pudo parchear EnsembleSampler (serial)")
    sys.exit(1)
txt = txt2
print(f"  OK: backend añadido a EnsembleSampler (serial)")

# 2c. Logica de resume: reemplazar el bucle de sampling
OLD_LOOP = """for _ in tqdm(sampler.sample(pos, iterations=n_steps), total=n_steps, desc="MCMC"):
            pass"""

NEW_LOOP = """# === [E.3-C7] Logica de resume ===
        _done = sampler.backend.iteration if sampler.backend is not None else 0
        if _done > 0:
            _remaining = max(0, n_steps - _done)
            print(f"[E.3-C7] RESUME: {_done} iteraciones ya completadas")
            if _remaining == 0:
                print(f"[E.3-C7] MCMC ya completa ({_done}/{n_steps}), cargando cadena")
            else:
                print(f"[E.3-C7] Continuando {_remaining} iteraciones")
                for _ in tqdm(sampler.sample(None, iterations=_remaining),
                              total=_remaining, desc="MCMC(resume)"):
                    pass
        else:
            print(f"[E.3-C7] Fresh start, {n_steps} iteraciones")
            for _ in tqdm(sampler.sample(pos, iterations=n_steps),
                          total=n_steps, desc="MCMC"):
                pass
        # === fin [E.3-C7] ==="""

txt2 = txt.replace(OLD_LOOP, NEW_LOOP, 1)
if txt2 == txt:
    print("  ERROR: no se pudo parchear el bucle de sampling")
    sys.exit(1)
txt = txt2
print(f"  OK: logica de resume insertada")

# Guardar
run_file.write_text(txt, encoding="utf-8")
print(f"  Archivo parcheado: {run_file}")

# Verificar sintaxis
try:
    py_compile.compile(str(run_file), doraise=True)
    print(f"  py_compile: OK")
except py_compile.PyCompileError as e:
    print(f"  ERROR de sintaxis: {e}")
    print(f"  Restaurando desde .orig...")
    shutil.copy2(str(BM / "run_beta_mcmc.py.orig"), str(run_file))
    sys.exit(1)

# --- 3: Patch de config.py ---
hdr("3. Patch de config.py para test")

cfg_file = BM / "config.py"
cfg_txt = cfg_file.read_text(encoding="utf-8")

# Cambiar MASK
cfg2 = cfg_txt.replace('MASK = "joint"', 'MASK = "act_dr6"', 1)
if cfg2 == cfg_txt:
    print("  ADVERTENCIA: MASK='joint' no encontrado, saltando")
else:
    cfg_txt = cfg2
    print("  MASK: joint -> act_dr6")

# Cambiar SAMPLING_MODE a beta_only para el test rapido
cfg2 = cfg_txt.replace('SAMPLING_MODE = "all"', 'SAMPLING_MODE = "beta_only"', 1)
if cfg2 == cfg_txt:
    print("  ADVERTENCIA: SAMPLING_MODE='all' no encontrado, saltando")
else:
    cfg_txt = cfg2
    print("  SAMPLING_MODE: all -> beta_only (test rapido)")

# Reducir N_STEPS para el primer test
cfg2 = cfg_txt.replace("MCMC_N_STEPS = 70000", "MCMC_N_STEPS = 3000", 1)
if cfg2 == cfg_txt:
    print("  ADVERTENCIA: MCMC_N_STEPS=70000 no encontrado, saltando")
else:
    cfg_txt = cfg2
    print("  MCMC_N_STEPS: 70000 -> 3000 (test rapido)")

cfg2 = cfg_txt.replace("MCMC_N_BURN = 1000", "MCMC_N_BURN = 500", 1)
if cfg2 == cfg_txt:
    print("  ADVERTENCIA: MCMC_N_BURN=1000 no encontrado, saltando")
else:
    cfg_txt = cfg2
    print("  MCMC_N_BURN: 1000 -> 500 (test rapido)")

cfg_file.write_text(cfg_txt, encoding="utf-8")
print(f"  Archivo parcheado: {cfg_file}")

try:
    py_compile.compile(str(cfg_file), doraise=True)
    print(f"  py_compile: OK")
except py_compile.PyCompileError as e:
    print(f"  ERROR de sintaxis: {e}")
    print(f"  Restaurando desde .orig...")
    shutil.copy2(str(BM / "config.py.orig"), str(cfg_file))
    sys.exit(1)

# --- 4: Diff summary ---
hdr("4. Resumen de cambios")

print("  run_beta_mcmc.py:")
print("    + import HDFBackend, _CHAIN_FILE")
print("    + backend=HDFBackend(_CHAIN_FILE) en 2 llamadas EnsembleSampler")
print("    + logica de resume basada en sampler.backend.iteration")
print()
print("  config.py:")
print("    MASK: joint -> act_dr6")
print("    SAMPLING_MODE: all -> beta_only")
print("    MCMC_N_STEPS: 70000 -> 3000")
print("    MCMC_N_BURN: 1000 -> 500")
print()
print("  Backups disponibles en:")
print(f"    {BM / 'run_beta_mcmc.py.orig'}")
print(f"    {BM / 'config.py.orig'}")
print()
print("  Para restaurar originales si algo falla:")
print(f"    Copy-Item '{BM / 'run_beta_mcmc.py.orig'}' '{run_file}' -Force")
print(f"    Copy-Item '{BM / 'config.py.orig'}' '{cfg_file}' -Force")

# --- 5: Verificar imports dependientes ---
hdr("5. Verificar imports del pipeline")

try:
    import sacc; print(f"  sacc: {sacc.__version__}")
except Exception as e: print(f"  sacc FALLA: {e}")
try:
    import emcee; print(f"  emcee: {emcee.__version__}")
except Exception as e: print(f"  emcee FALLA: {e}")
try:
    import h5py; print(f"  h5py: {h5py.__version__} (necesario para HDFBackend)")
except Exception as e: print(f"  h5py FALLA: {e}")

print()
print("="*72)
print("  PATCH COMPLETO")
print("="*72)
