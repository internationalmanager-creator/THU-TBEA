"""Orquestador unico. Ejecuta TODO el repositorio de forma observable.

Fases (numeradas, secuenciales, salida en vivo):
    01. Entorno          - verifica python, deps, cwd
    02. Schema           - migrations.py (init/migrate)
    03. Integridad       - chronolog.py verificar
    04. Tests            - pytest tests/ -v
    05. Semilla          - registra TEST-001 si no hay entidades (--seed)
    06. Manifest         - hash_manifest.py --anchor
    07. Analisis         - analisis.py
    08. Cronolog export  - chronolog.py exportar
    09. Audit report     - audit_report.py
    10. Resumen final    - last_run.json + banner

Cada fase imprime:
    [PHASE N] <<titulo>>
    $ <comando>
    <salida en vivo>
    [PHASE N] OK <tiempo>
    o
    [PHASE N] FAIL (rc=<rc>) <tiempo>

Al final:
    - outputs/last_run.json con todo el detalle
    - outputs/run_log_<ts>.txt con el log completo
    - el audit report (via fase 09)

Uso:
    python src/run_all.py                    # secuencia completa
    python src/run_all.py --dry-run          # muestra plan sin ejecutar
    python src/run_all.py --skip-tests       # salta pytest
    python src/run_all.py --seed             # crea TEST-001 si vacio
    python src/run_all.py --dashboard        # arranca streamlit al final
    python src/run_all.py --stop-on-fail     # aborta al primer fallo
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent
PY = sys.executable
OUTPUTS = BASE / "outputs"
LAST_RUN = OUTPUTS / "last_run.json"
RUN_LOG = None
RUN_LOG_PATH = None
WIDTH = 100


def _ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ts_compact():
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def _line(ch="=", n=WIDTH):
    return ch * n


def _log(msg, also_print=True):
    if also_print:
        print(msg, flush=True)
    if RUN_LOG:
        RUN_LOG.write(msg + "\n")
        RUN_LOG.flush()


def _log_block(title):
    _log("")
    _log(_line("="))
    _log(title)
    _log(_line("="))


def _run(cmd, cwd=None):
    """Ejecuta comando con stdio heredado (salida en vivo).
    Devuelve (rc, segundos).
    """
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    _log(f"$ {' '.join(str(c) for c in cmd)}")
    t0 = time.time()
    try:
        rc = subprocess.run(cmd, cwd=str(cwd or BASE), env=env).returncode
    except Exception as e:
        _log(f"[subprocess error] {e}")
        rc = -1
    return rc, time.time() - t0


def _has_entities():
    import sqlite3
    db = BASE / "data" / "pir.sqlite"
    if not db.exists():
        return False
    try:
        c = sqlite3.connect(str(db))
        try:
            n = c.execute("SELECT COUNT(*) FROM entidades").fetchone()[0]
            return n > 0
        except sqlite3.OperationalError:
            return False
        finally:
            c.close()
    except Exception:
        return False


def _write_seed_input():
    """Crea data/inputs/TEST-001.json si no existe."""
    p = BASE / "data" / "inputs" / "TEST-001.json"
    if p.exists():
        return False
    p.parent.mkdir(parents=True, exist_ok=True)
    datos = {
        "id": "TEST-001",
        "categoria": "test",
        "titulo": "TEST-001 (semilla run_all)",
        "valor_principal": 100.0,
        "incertidumbre": 0.5,
        "unidad": "Hz",
        "fuente": "Example2024",
        "origen": "observado",
        "estatus": "D",
        "notas": "Entidad semilla generada por run_all.",
        "provenance": {
            "cita_completa": "Example, A. Test entity for pipeline validation. Journal of Tests, 1, 1-10 (2024).",
            "doi": "10.0000/test.2024.001",
            "tipo_publicacion": "revista indexada",
            "ano": 2024,
            "instrumento": "Osciloscopio calibrado",
            "condiciones": "Temperatura ambiente, 1 atm",
            "reproducibilidad": "Confirmado en laboratorio independiente",
            "extracto": "The measured frequency was 100.0 Hz with uncertainty 0.5 Hz.",
            "hash_pdf": None,
            "fecha_descarga_utc": None,
            "notas": ""
        }
    }
    p.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n",
                 encoding="utf-8", newline="\n")
    return True


# ============================================================
# FASES
# ============================================================

def fase_01_entorno(args, estado):
    _log_block("[PHASE 01] ENTORNO")
    _log(f"  python:          {PY}")
    v = sys.version_info
    _log(f"  python_version:  {v.major}.{v.minor}.{v.micro}")
    _log(f"  cwd:             {Path.cwd()}")
    _log(f"  repo_root:       {BASE}")

    faltantes = []
    for mod in ("numpy", "scipy", "pandas", "matplotlib",
                "streamlit", "plotly", "tqdm", "pytest"):
        try:
            __import__(mod)
        except ImportError:
            faltantes.append(mod)
    if faltantes:
        _log(f"  AVISO: faltan dependencias: {faltantes}")
        return ("WARN", {"faltan": faltantes})
    _log("  deps:            OK")
    return ("OK", {"faltan": []})


def fase_02_schema(args, estado):
    _log_block("[PHASE 02] SCHEMA")
    rc1, t1 = _run([PY, "src/migrations.py", "--status"])
    if rc1 != 0:
        return ("FAIL", {"rc_status": rc1, "t": round(t1, 2)})
    rc2, t2 = _run([PY, "src/migrations.py"])
    if rc2 != 0:
        return ("FAIL", {"rc_migrate": rc2, "t": round(t2, 2)})
    return ("OK", {"t_status": round(t1, 2), "t_migrate": round(t2, 2)})


def fase_03_integridad(args, estado):
    _log_block("[PHASE 03] INTEGRIDAD (cadena de eventos)")
    rc, t = _run([PY, "src/chronolog.py", "verificar"])
    return ("OK" if rc == 0 else "FAIL", {"rc": rc, "t": round(t, 2)})


def fase_04_tests(args, estado):
    _log_block("[PHASE 04] TESTS (pytest)")
    if args.skip_tests:
        _log("  --skip-tests: fase omitida")
        return ("SKIP", {})
    rc, t = _run([PY, "-m", "pytest", "tests/", "-v", "--no-header", "-q"])
    return ("OK" if rc == 0 else "FAIL", {"rc": rc, "t": round(t, 2)})

# === PARTE 2 se agrega a continuacion ===

def fase_05_semilla(args, estado):
    _log_block("[PHASE 05] SEMILLA")
    if not args.seed:
        _log("  --seed no especificado; solo se reporta el estado")
        tiene = _has_entities()
        _log(f"  entidades presentes: {tiene}")
        return ("OK", {"entidades": tiene})

    if _has_entities():
        _log("  Ya hay entidades; no se crea semilla.")
        return ("OK", {"creada": False})

    creada = _write_seed_input()
    _log(f"  data/inputs/TEST-001.json creado: {creada}")
    rc, t = _run([PY, "src/registrar_entidad.py", "TEST-001"])
    return ("OK" if rc == 0 else "FAIL",
            {"rc": rc, "t": round(t, 2), "archivo_creado": creada})


def fase_06_manifest(args, estado):
    _log_block("[PHASE 06] MANIFEST + ANCLAJE")
    version = "0.7.0"
    meta_p = BASE / "registry" / "project_metadata.json"
    if meta_p.exists():
        try:
            version = json.loads(meta_p.read_text(encoding="utf-8")).get("version", version)
        except Exception:
            pass
    rc, t = _run([PY, "src/hash_manifest.py", version, "--anchor"])
    return ("OK" if rc == 0 else "FAIL",
            {"rc": rc, "t": round(t, 2), "version": version})


def fase_07_analisis(args, estado):
    _log_block("[PHASE 07] ANALISIS EXPLORATORIO")
    rc, t = _run([PY, "src/analisis.py"])
    return ("OK" if rc == 0 else "FAIL", {"rc": rc, "t": round(t, 2)})


def fase_08_cronolog(args, estado):
    _log_block("[PHASE 08] EXPORTAR CRONOLOG")
    rc, t = _run([PY, "src/chronolog.py", "exportar"])
    return ("OK" if rc == 0 else "FAIL", {"rc": rc, "t": round(t, 2)})


def fase_09_audit(args, estado):
    _log_block("[PHASE 09] AUDIT REPORT")
    rc, t = _run([PY, "src/audit_report.py"])
    return ("OK" if rc == 0 else "FAIL", {"rc": rc, "t": round(t, 2)})


def fase_10_resumen(args, estado):
    _log_block("[PHASE 10] RESUMEN FINAL")
    _log(f"  audit report:      {OUTPUTS / 'audit_report_latest.txt'}")
    _log(f"  last_run.json:     {LAST_RUN}")
    _log(f"  log completo:      {RUN_LOG_PATH}")
    _log(f"  cronolog md:       {BASE / 'registry' / 'chronolog.md'}")
    seeds = sorted((BASE / "seeds").glob("seed_v*.json"))
    if seeds:
        _log(f"  ultimo manifest:   {seeds[-1].name}")
    return ("OK", {})


FASES = [
    ("01", "Entorno",            fase_01_entorno),
    ("02", "Schema",             fase_02_schema),
    ("03", "Integridad",         fase_03_integridad),
    ("04", "Tests",              fase_04_tests),
    ("05", "Semilla",            fase_05_semilla),
    ("06", "Manifest + anclaje", fase_06_manifest),
    ("07", "Analisis",           fase_07_analisis),
    ("08", "Cronolog export",    fase_08_cronolog),
    ("09", "Audit report",       fase_09_audit),
    ("10", "Resumen final",      fase_10_resumen),
]


def imprimir_plan():
    print()
    print(_line("="))
    print("PIR RUN_ALL - PLAN DE EJECUCION")
    print(_line("="))
    for num, titulo, _ in FASES:
        print(f"  [{num}] {titulo}")
    print(_line("="))


def main():
    global RUN_LOG, RUN_LOG_PATH

    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-tests", action="store_true")
    ap.add_argument("--seed", action="store_true")
    ap.add_argument("--dashboard", action="store_true")
    ap.add_argument("--stop-on-fail", action="store_true")
    args = ap.parse_args()

    if args.dry_run:
        imprimir_plan()
        return

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    RUN_LOG_PATH = OUTPUTS / f"run_log_{_ts_compact()}.txt"
    RUN_LOG = open(RUN_LOG_PATH, "w", encoding="utf-8", newline="\n")

    inicio = time.time()

    _log(_line("="))
    _log("PIR RUN_ALL - EJECUCION COMPLETA")
    _log(_line("="))
    _log(f"Timestamp:   {_ts()}")
    _log(f"Python:      {PY}")
    _log(f"CWD:         {Path.cwd()}")
    _log(f"Repo:        {BASE}")
    _log(f"Flags:       seed={args.seed} skip_tests={args.skip_tests} "
         f"dashboard={args.dashboard} stop_on_fail={args.stop_on_fail}")
    _log(_line("="))

    resultados = []
    for num, titulo, fn in FASES:
        t0 = time.time()
        try:
            status, detalle = fn(args, {})
        except Exception as e:
            status, detalle = "FAIL", {"error": str(e)}
        dur = time.time() - t0
        resultados.append({
            "fase": num, "titulo": titulo, "status": status,
            "duracion_s": round(dur, 2), "detalle": detalle,
        })
        marca = {"OK": "OK", "FAIL": "FAIL", "WARN": "WARN", "SKIP": "SKIP"}.get(status, status)
        _log(f"[PHASE {num}] {marca} ({dur:.2f}s)")
        if status == "FAIL" and args.stop_on_fail:
            _log("[stop-on-fail] abortando por fallo")
            break

    total = time.time() - inicio

    last = {
        "timestamp_utc": _ts(),
        "duracion_total_s": round(total, 2),
        "python": PY,
        "cwd": str(Path.cwd()),
        "repo": str(BASE),
        "flags": vars(args),
        "fases": resultados,
        "run_log": str(RUN_LOG_PATH.relative_to(BASE)),
    }
    LAST_RUN.write_text(json.dumps(last, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8", newline="\n")

    n_ok = sum(1 for r in resultados if r["status"] == "OK")
    n_fail = sum(1 for r in resultados if r["status"] == "FAIL")
    n_skip = sum(1 for r in resultados if r["status"] == "SKIP")
    n_warn = sum(1 for r in resultados if r["status"] == "WARN")

    _log("")
    _log(_line("="))
    _log("RESUMEN FINAL")
    _log(_line("="))
    _log(f"Fases:      {len(resultados)}")
    _log(f"OK:         {n_ok}")
    _log(f"FAIL:       {n_fail}")
    _log(f"WARN:       {n_warn}")
    _log(f"SKIP:       {n_skip}")
    _log(f"Duracion:   {total:.2f}s")
    _log(_line("="))
    _log(f"Ultimo audit report: {OUTPUTS / 'audit_report_latest.txt'}")
    _log(f"Log completo:        {RUN_LOG_PATH}")
    _log(_line("="))

    RUN_LOG.close()

    if args.dashboard:
        _log("")
        _log(_line("="))
        _log("DASHBOARD - streamlit run app.py")
        _log("  http://localhost:8501")
        _log("  (Ctrl+C para detener)")
        _log(_line("="))
        try:
            subprocess.run(
                [PY, "-m", "streamlit", "run", "app.py",
                 "--server.port", "8501", "--server.address", "0.0.0.0"],
                cwd=str(BASE),
            )
        except KeyboardInterrupt:
            _log("Dashboard detenido por el usuario.")

    sys.exit(0 if n_fail == 0 else 1)


if __name__ == "__main__":
    main()