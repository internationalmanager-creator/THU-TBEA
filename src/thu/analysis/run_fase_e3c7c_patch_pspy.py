# -*- coding: utf-8 -*-
"""E.3-C7c — Hacer pspy import opcional en tools/data_loading.py."""
import sys, shutil, py_compile
from pathlib import Path

REPO = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto\data\raw\cosmic-birefringence-planck-act")
DL = REPO / "tools" / "data_loading.py"

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

hdr("1. Backup")
backup = DL.parent / "data_loading.py.orig"
if backup.exists():
    print(f"  Ya existe: {backup}")
else:
    shutil.copy2(DL, backup)
    print(f"  Backup creado: {backup}")

hdr("2. Aplicar patch")

txt = DL.read_text(encoding="utf-8")

# --- Patch 1: hacer el import de pspy opcional ---
OLD_IMPORT = "import os\n\nimport numpy as np\nfrom astropy.io import fits\nfrom pspy import pspy_utils\n"
NEW_IMPORT = """import os

import numpy as np
from astropy.io import fits

# === [E.3-C7c] pspy es opcional ===
# pspy requiere compilador Fortran, no disponible en este entorno.
# Solo se necesita para load_act_beam() y load_npipe_beam().
# Para el modo MASK='act_dr6' del beta_mcmc, no se invoca.
try:
    from pspy import pspy_utils
    _HAS_PSPY = True
except ImportError:
    pspy_utils = None
    _HAS_PSPY = False
# === fin [E.3-C7c] ===
"""

if OLD_IMPORT not in txt:
    print("  ERROR: anchor de import no encontrado")
    sys.exit(1)

txt2 = txt.replace(OLD_IMPORT, NEW_IMPORT, 1)
if txt2 == txt:
    print("  ERROR: no se pudo reemplazar imports")
    sys.exit(1)
txt = txt2
print("  OK: pspy import hecho opcional")

# --- Patch 2: guardia en load_act_beam ---
OLD_LAB = '''    _, bl = pspy_utils.read_beam_file(act_beam_path(array_band), lmax=lmax)
    return bl'''
NEW_LAB = '''    if not _HAS_PSPY:
        raise ImportError(
            "[E.3-C7c] load_act_beam requiere pspy (compilador Fortran). "
            "No disponible en este entorno. No se usa en modo MASK='act_dr6'."
        )
    _, bl = pspy_utils.read_beam_file(act_beam_path(array_band), lmax=lmax)
    return bl'''

if OLD_LAB not in txt:
    print("  ADVERTENCIA: anchor load_act_beam no encontrado (quizas ya parcheado)")
else:
    txt = txt.replace(OLD_LAB, NEW_LAB, 1)
    print("  OK: guardia en load_act_beam")

# --- Patch 3: guardia en load_npipe_beam (no usa pspy_utils directamente, pero verificar) ---
# load_npipe_beam usa fits, no pspy. Saltamos.

# Guardar
DL.write_text(txt, encoding="utf-8")
print(f"  Archivo parcheado: {DL}")

# --- Verificar sintaxis ---
hdr("3. Verificar sintaxis")
try:
    py_compile.compile(str(DL), doraise=True)
    print(f"  py_compile: OK")
except py_compile.PyCompileError as e:
    print(f"  ERROR: {e}")
    print(f"  Restaurando...")
    shutil.copy2(backup, DL)
    sys.exit(1)

# --- Test de import ---
hdr("4. Test: importar data_loading desde el repo")
sys.path.insert(0, str(REPO))
try:
    # Limpiar cache previo si existe
    for mod in list(sys.modules.keys()):
        if "data_loading" in mod or mod == "tools":
            del sys.modules[mod]
    from tools import data_loading
    print(f"  OK: tools.data_loading importado")
    print(f"  _HAS_PSPY = {data_loading._HAS_PSPY}")
    print(f"  NPIPE_TIME_SPLIT_FREQS = {data_loading.NPIPE_TIME_SPLIT_FREQS}")
    print(f"  NPIPE_DUST_FREQS = {data_loading.NPIPE_DUST_FREQS}")
except Exception as e:
    print(f"  ERROR al importar: {e}")
    import traceback
    traceback.print_exc()

# --- Test: importar birefringence_likelihood (que importa las constantes) ---
hdr("5. Test: importar birefringence_likelihood")
sys.path.insert(0, str(REPO / "beta_mcmc"))
try:
    for mod in list(sys.modules.keys()):
        if "birefringence_likelihood" in mod:
            del sys.modules[mod]
    from birefringence_likelihood import _is_hfi_label
    print(f"  OK: birefringence_likelihood importado")
    print(f"  _is_hfi_label(217) = {_is_hfi_label(217)}")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*72)
print("  PATCH E.3-C7c COMPLETO")
print("="*72)
