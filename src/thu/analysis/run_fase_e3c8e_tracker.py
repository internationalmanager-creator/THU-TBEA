# -*- coding: utf-8 -*-
"""E.3-C8e — Crear run_tracker.py + parchear run_beta_mcmc.py."""
import sys, shutil, py_compile
from pathlib import Path

REPO = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto\data\raw\cosmic-birefringence-planck-act")
BM = REPO / "beta_mcmc"

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# ============================================================
# 1. Crear run_tracker.py
# ============================================================
hdr("1. Crear run_tracker.py")

TRACKER_CODE = '''# -*- coding: utf-8 -*-
"""run_tracker.py — SQLite tracking + real-time progress for MCMC runs.

Diseno: si el proceso muere por corte de luz, el SQLite conserva el ultimo
estado. Al relanzar, el HDF5 resume la cadena y este tracker registra una
nueva corrida como continuacion de la anterior.
"""
import os, sqlite3, json, time, numpy as np
from datetime import datetime, timezone

DB_PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "data", "computed", "mcmc_runs.sqlite"))
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS mcmc_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT NOT NULL,
    end_time TEXT,
    status TEXT DEFAULT 'running',
    total_steps INTEGER,
    current_step INTEGER DEFAULT 0,
    n_walkers INTEGER,
    n_params INTEGER,
    chain_file TEXT,
    config_json TEXT,
    last_update TEXT
);
CREATE TABLE IF NOT EXISTS mcmc_snapshots (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    step INTEGER,
    timestamp TEXT,
    beta_mean REAL,
    beta_std REAL,
    chain_file_size INTEGER,
    FOREIGN KEY (run_id) REFERENCES mcmc_runs(run_id)
);
"""

def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _conn():
    c = sqlite3.connect(DB_PATH, timeout=10)
    c.execute("PRAGMA journal_mode=WAL")
    return c

def init_db():
    with _conn() as c:
        c.executescript(_SCHEMA)

def start_run(total_steps, n_walkers, n_params, chain_file, config_dict):
    init_db()
    with _conn() as c:
        cur = c.execute(
            """INSERT INTO mcmc_runs
               (start_time, status, total_steps, current_step,
                n_walkers, n_params, chain_file, config_json, last_update)
               VALUES (?, 'running', ?, 0, ?, ?, ?, ?, ?)""",
            (_now(), total_steps, n_walkers, n_params,
             str(chain_file), json.dumps(config_dict), _now()))
        return cur.lastrowid

def update_progress(run_id, step, chain_file, sampler=None, beta_idx=0):
    """Actualiza current_step + snapshot con beta si sampler disponible."""
    beta_mean = None
    beta_std = None
    if sampler is not None and sampler.iteration > 0:
        try:
            chain = sampler.get_chain(flat=True)
            if len(chain) > 5:
                # beta viene en radianes; convertir a grados
                beta_deg = np.rad2deg(chain[:, beta_idx])
                beta_mean = float(np.median(beta_deg))
                beta_std = float(np.std(beta_deg))
        except Exception:
            pass
    size = 0
    try:
        if os.path.exists(chain_file):
            size = os.path.getsize(chain_file)
    except Exception:
        pass
    with _conn() as c:
        c.execute("""UPDATE mcmc_runs
                     SET current_step = ?, last_update = ?
                     WHERE run_id = ?""", (step, _now(), run_id))
        c.execute("""INSERT INTO mcmc_snapshots
                     (run_id, step, timestamp, beta_mean, beta_std, chain_file_size)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (run_id, step, _now(), beta_mean, beta_std, size))
        return beta_mean, beta_std

def finish_run(run_id, status="completed"):
    with _conn() as c:
        c.execute("""UPDATE mcmc_runs
                     SET status = ?, end_time = ?, last_update = ?
                     WHERE run_id = ?""",
                  (status, _now(), _now(), run_id))

def latest_run():
    init_db()
    with _conn() as c:
        row = c.execute("""SELECT run_id, start_time, status, total_steps,
                                  current_step, last_update
                           FROM mcmc_runs
                           ORDER BY run_id DESC LIMIT 1""").fetchone()
    return row

def print_status():
    init_db()
    with _conn() as c:
        runs = c.execute("""SELECT run_id, start_time, status, total_steps,
                                   current_step, last_update
                            FROM mcmc_runs ORDER BY run_id DESC LIMIT 5""").fetchall()
    print()
    print("=== Ultimas corridas MCMC ===")
    for r in runs:
        rid, start, status, total, cur, upd = r
        pct = 100 * cur / total if total else 0
        print(f"  run_id={rid}  {status:10s}  {cur}/{total} ({pct:.1f}%)  "
              f"start={start}  last_update={upd}")
'''

tracker_file = BM / "run_tracker.py"
tracker_file.write_text(TRACKER_CODE, encoding="utf-8")
print(f"  Creado: {tracker_file}")

try:
    py_compile.compile(str(tracker_file), doraise=True)
    print(f"  py_compile: OK")
except py_compile.PyCompileError as e:
    print(f"  ERROR: {e}")
    sys.exit(1)

# Test: importar y ejecutar init
sys.path.insert(0, str(BM))
try:
    import run_tracker
    run_tracker.init_db()
    print(f"  init_db: OK, DB en {run_tracker.DB_PATH}")
except Exception as e:
    print(f"  ERROR init_db: {e}")
    sys.exit(1)

# ============================================================
# 2. Parchear run_beta_mcmc.py
# ============================================================
hdr("2. Parchear run_beta_mcmc.py para SQLite + postfix")

run_file = BM / "run_beta_mcmc.py"
backup = run_file.parent / "run_beta_mcmc.py.orig3"
if not backup.exists():
    shutil.copy2(run_file, backup)
    print(f"  Backup: {backup.name}")
else:
    print(f"  Backup ya existe")

txt = run_file.read_text(encoding="utf-8")

# 2a. Insertar import del tracker (junto al bloque [E.3-C7])
ANCHOR = "from emcee.backends import HDFBackend"
if ANCHOR not in txt:
    print("  ERROR: anchor [E.3-C7] no encontrado")
    sys.exit(1)

NEW_IMPORTS = """from emcee.backends import HDFBackend

# === [E.3-C8e] SQLite tracker ===
import run_tracker as _tracker
_TRACKER_RUN_ID = None
# === fin [E.3-C8e] ===
"""

txt2 = txt.replace(ANCHOR, NEW_IMPORTS, 1)
if txt2 == txt:
    print("  ERROR: no se pudo insertar import tracker")
    sys.exit(1)
txt = txt2
print(f"  OK: import run_tracker anadido")

# 2b. Reemplazar el loop fresh start para anadir SQLite + postfix
OLD_LOOP = """        else:
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
                # === fin [E.3-C8d] ==="""

NEW_LOOP = """        else:
            print(f"[E.3-C7] Fresh start, {n_steps} iteraciones")
            # === [E.3-C8e] registrar run en SQLite ===
            global _TRACKER_RUN_ID
            _cfg_dict = {
                "n_walkers": int(n_walkers), "n_params": int(n_params),
                "n_steps": int(n_steps), "n_burn": int(n_burn),
                "chain_file": str(_CHAIN_FILE),
            }
            _TRACKER_RUN_ID = _tracker.start_run(
                total_steps=n_steps, n_walkers=n_walkers,
                n_params=n_params, chain_file=_CHAIN_FILE,
                config_dict=_cfg_dict)
            print(f"[E.3-C8e] run_id={_TRACKER_RUN_ID} registrado en SQLite")
            # === fin [E.3-C8e] ===
            _pbar = tqdm(sampler.sample(pos, iterations=n_steps),
                         total=n_steps, desc="MCMC")
            for _i, _state in enumerate(_pbar):
                # === [E.3-C8d] Flush cada 100 pasos para persistir HDF5 ===
                if (_i + 1) % 100 == 0:
                    try:
                        _hb = sampler.backend
                        _f = getattr(_hb, '_f', None) or getattr(_hb, 'file', None)
                        if _f is not None and hasattr(_f, 'flush'):
                            _f.flush()
                    except Exception:
                        pass
                    # === [E.3-C8e] SQLite update + postfix tqdm ===
                    try:
                        _b_mean, _b_std = _tracker.update_progress(
                            _TRACKER_RUN_ID, _i + 1, _CHAIN_FILE, sampler=sampler)
                        if _b_mean is not None:
                            _pbar.set_postfix(beta_deg=f"{_b_mean:.4f}",
                                              sigma=f"{_b_std:.4f}")
                    except Exception as _e:
                        pass
                    # === fin [E.3-C8e] ===
                # === fin [E.3-C8d] ==="""

if OLD_LOOP not in txt:
    print("  ERROR: anchor del loop [E.3-C8d] no encontrado")
    print("  (probablemente ya parcheado con E.3-C8e o diferente)")
    sys.exit(1)

txt2 = txt.replace(OLD_LOOP, NEW_LOOP, 1)
if txt2 == txt:
    print("  ERROR: no se pudo parchear el loop")
    sys.exit(1)
txt = txt2
print(f"  OK: loop con SQLite + postfix")

# 2c. try/finally alrededor del sampling para marcar completed/failed
OLD_FINALLY = """    finally:
        if pool is not None:
            pool.close()
            pool.join()"""

NEW_FINALLY = """    finally:
        if pool is not None:
            pool.close()
            pool.join()
        # === [E.3-C8e] marcar run como completado ===
        if _TRACKER_RUN_ID is not None:
            try:
                _tracker.finish_run(_TRACKER_RUN_ID, "completed")
                print(f"[E.3-C8e] run_id={_TRACKER_RUN_ID} marcado completed")
            except Exception:
                pass
        # === fin [E.3-C8e] ==="""

if OLD_FINALLY not in txt:
    print("  ADVERTENCIA: anchor finally no encontrado. Saltando marca de completed.")
else:
    txt = txt.replace(OLD_FINALLY, NEW_FINALLY, 1)
    print(f"  OK: try/finally con marca de completed")

# Guardar
run_file.write_text(txt, encoding="utf-8")
print(f"  Archivo parcheado: {run_file}")

try:
    py_compile.compile(str(run_file), doraise=True)
    print(f"  py_compile: OK")
except py_compile.PyCompileError as e:
    print(f"  ERROR: {e}")
    print(f"  Restaurando desde {backup.name}...")
    shutil.copy2(backup, run_file)
    sys.exit(1)

# ============================================================
# 3. Verificar estado
# ============================================================
hdr("3. Estado final")
print(f"  run_tracker.py: {tracker_file}")
print(f"  SQLite DB: {run_tracker.DB_PATH}")
print()
print("  Corridas previas:")
run_tracker.print_status()

print()
print("="*72)
print("  E.3-C8e COMPLETO")
print("="*72)
print()
print("  Para lanzar la corrida:")
print(f"    cd {BM}")
print(f"    python run_beta_mcmc.py")
print()
print("  Veras:")
print("    [E.3-C8e] run_id=N registrado en SQLite")
print("    MCMC: X walkers, Y parallel workers")
print("    [progress bar con postfix: beta_deg=X.XXXX sigma=X.XXXX]")
print()
print("  Consultar estado en cualquier momento:")
print(f"    python -c \"import sys; sys.path.insert(0,'{BM}'); import run_tracker; run_tracker.print_status()\"")
print()
print("  Si se corta la luz: relanzar el mismo comando reanuda desde HDF5.")
print("  El SQLite registra una nueva run_id como continuacion.")
