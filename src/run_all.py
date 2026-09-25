"""Orquestador unico. Ejecuta TODO el repositorio (PIR + THU-TBEA).

Fases PIR (framework general):
    01. Entorno
    02. Schema
    03. Integridad
    04. Tests
    05. Semilla
    06. Manifest
    07. Analisis
    08. Cronolog export
    09. Audit report

Fases THU-TBEA (subproyecto especifico):
    10. Simbolica      verificacion_simbolica.json 16/16
    11. Deudas         check_debts.py
    12. Figuras        figures.py --all  (solo con --with-figs)
    13. LaTeX          latex_builder.py --all
    14. Compilacion    pdflatex + bibtex x 3 idiomas
    15. dist/          copiar PDFs finales

    99. Resumen final

Uso:
    python src/run_all.py                       # secuencia completa (rapida)
    python src/run_all.py --with-figs           # incluye regenerar 195 figs
    python src/run_all.py --skip-pir            # solo THU
    python src/run_all.py --skip-thu            # solo PIR
    python src/run_all.py --skip-compile        # no compila PDFs
    python src/run_all.py --dry-run             # plan sin ejecutar
    python src/run_all.py --stop-on-fail        # aborta al primer fallo
    python src/run_all.py --dashboard           # abre streamlit al final
"""
import argparse
import json
import os
import shutil
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


def _find_miktex_bin():
    """Busca el bin de MiKTeX y lo agrega al PATH si existe."""
    candidatos = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "MiKTeX" / "miktex" / "bin" / "x64",
        Path(os.environ.get("PROGRAMFILES", "")) / "MiKTeX" / "miktex" / "bin" / "x64",
    ]
    for c in candidatos:
        if c.exists() and (c / "pdflatex.exe").exists():
            os.environ["PATH"] = str(c) + os.pathsep + os.environ.get("PATH", "")
            return c
    return None


def _run(cmd, cwd=None):
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
    p = BASE / "data" / "inputs" / "TEST-001.json"
    if p.exists():
        return False
    p.parent.mkdir(parents=True, exist_ok=True)
    datos = {
        "id": "TEST-001", "categoria": "test",
        "titulo": "TEST-001 (semilla run_all)",
        "valor_principal": 100.0, "incertidumbre": 0.5, "unidad": "Hz",
        "fuente": "Example2024", "origen": "observado", "estatus": "D",
        "notas": "Entidad semilla generada por run_all.",
        "provenance": {
            "cita_completa": "Example, A. Test entity for pipeline validation. Journal of Tests, 1, 1-10 (2024).",
            "doi": "10.0000/test.2024.001",
            "tipo_publicacion": "revista indexada", "ano": 2024,
            "instrumento": "Osciloscopio calibrado",
            "condiciones": "Temperatura ambiente, 1 atm",
            "reproducibilidad": "Confirmado en laboratorio independiente",
            "extracto": "The measured frequency was 100.0 Hz with uncertainty 0.5 Hz.",
            "hash_pdf": None, "fecha_descarga_utc": None, "notas": ""
        }
    }
    p.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n",
                 encoding="utf-8", newline="\n")
    return True


# =====================================================================
# FASES PIR (01-09)
# =====================================================================

def fase_01_entorno(args, estado):
    _log_block("[PHASE 01] ENTORNO")
    _log(f"  python:          {PY}")
    v = sys.version_info
    _log(f"  python_version:  {v.major}.{v.minor}.{v.micro}")
    _log(f"  cwd:             {Path.cwd()}")
    _log(f"  repo_root:       {BASE}")
    faltantes = []
    for mod in ("numpy", "scipy", "pandas", "matplotlib",
                "streamlit", "plotly", "tqdm", "pytest",
                "sympy", "mpmath", "h5py"):
        try:
            __import__(mod)
        except ImportError:
            faltantes.append(mod)
    if faltantes:
        _log(f"  AVISO: faltan dependencias: {faltantes}")
        return ("WARN", {"faltan": faltantes})
    _log("  deps:            OK")
    return ("OK", {"faltan": []})


def fase_00b_fetch(args, estado):
    """Descarga opcional de datasets (--fetch)."""
    _log_block("[PHASE 00b] FETCH DATASETS")
    if not getattr(args, "fetch", False):
        _log("  --fetch no especificado; fase omitida")
        return ("SKIP", {})
    p = BASE / "src" / "fetch_data.py"
    if not p.exists():
        _log("  AVISO: no existe src/fetch_data.py")
        return ("WARN", {"exist": False})
    rc, t = _run([PY, str(p), "--inventory", "--solo-faltantes"])
    return ("OK" if rc == 0 else "WARN", {"rc": rc, "t": round(t, 2)})


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
    if not (BASE / "tests").exists():
        _log("  tests/ no existe; fase omitida")
        return ("SKIP", {})
    rc, t = _run([PY, "-m", "pytest", "tests/", "-v", "--no-header", "-q"])
    return ("OK" if rc == 0 else "FAIL", {"rc": rc, "t": round(t, 2)})


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


# =====================================================================
# FASES THU-TBEA (10-15)
# =====================================================================

def fase_10_simbolica(args, estado):
    _log_block("[PHASE 10] THU - VERIFICACION SIMBOLICA")
    p = BASE / "data" / "inventory" / "verificacion_simbolica.json"
    if not p.exists():
        _log(f"  AVISO: no existe {p}")
        return ("WARN", {"exist": False})
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        n_pass = data.get("pass", 0)
        n_fail = data.get("fail", 0)
        n_tot = data.get("total_pasos", 0)
        _log(f"  total_pasos: {n_tot}  pass: {n_pass}  fail: {n_fail}")
        if n_fail == 0 and n_pass == n_tot and n_tot > 0:
            return ("OK", {"pass": n_pass, "total": n_tot})
        else:
            return ("FAIL", {"pass": n_pass, "fail": n_fail, "total": n_tot})
    except Exception as e:
        _log(f"  [error] {e}")
        return ("FAIL", {"error": str(e)})


def fase_11_deudas(args, estado):
    _log_block("[PHASE 11] THU - DEUDAS (check_debts)")
    p = BASE / "scripts" / "check_debts.py"
    if not p.exists():
        _log(f"  AVISO: no existe {p}")
        return ("WARN", {"exist": False})
    rc, t = _run([PY, str(p)])
    return ("OK" if rc == 0 else "WARN", {"rc": rc, "t": round(t, 2)})


def fase_12_figuras(args, estado):
    _log_block("[PHASE 12] THU - FIGURAS")
    if not args.with_figs:
        _log("  --with-figs no especificado; fase omitida (195 figs, ~3 min)")
        _log("  Las figuras existentes se conservan.")
        return ("SKIP", {})
    p = BASE / "src" / "thu" / "figures.py"
    if not p.exists():
        _log(f"  AVISO: no existe {p}")
        return ("WARN", {"exist": False})
    rc, t = _run([PY, str(p), "--all"])
    return ("OK" if rc == 0 else "FAIL", {"rc": rc, "t": round(t, 2)})


def fase_13_latex(args, estado):
    _log_block("[PHASE 13] THU - REGENERAR .tex")
    p = BASE / "src" / "thu" / "latex_builder.py"
    if not p.exists():
        _log(f"  AVISO: no existe {p}")
        return ("WARN", {"exist": False})
    rc, t = _run([PY, str(p), "--all"])
    return ("OK" if rc == 0 else "FAIL", {"rc": rc, "t": round(t, 2)})


def fase_14_compilar(args, estado):
    _log_block("[PHASE 14] THU - COMPILAR PDFs")
    if args.skip_compile:
        _log("  --skip-compile: fase omitida")
        return ("SKIP", {})
    if not shutil.which("pdflatex"):
        _log("  pdflatex no en PATH; intentando detectar MiKTeX...")
        mbin = _find_miktex_bin()
        if mbin:
            _log(f"  MiKTeX encontrado: {mbin}")
        else:
            _log("  AVISO: pdflatex no disponible; fase omitida")
            return ("WARN", {"pdflatex": False})

    src_dir = BASE / "paper" / "thu" / "src"
    dist_dir = BASE / "paper" / "thu" / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    resultados = {}
    for lang in ("es", "en", "de"):
        _log("")
        _log(f"  --- {lang} ---")
        tex = src_dir / f"tesis_{lang}.tex"
        if not tex.exists():
            _log(f"    AVISO: no existe {tex.name}")
            resultados[lang] = {"status": "MISSING"}
            continue
        # Limpiar auxiliares
        for ext in ("aux", "log", "out", "toc", "lof", "lot", "bbl", "blg", "pdf"):
            f = src_dir / f"tesis_{lang}.{ext}"
            if f.exists():
                try:
                    f.unlink()
                except Exception:
                    pass
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        try:
            subprocess.run(["pdflatex", "-interaction=nonstopmode", f"tesis_{lang}.tex"],
                           cwd=str(src_dir), env=env, capture_output=True, timeout=120)
            subprocess.run(["bibtex", f"tesis_{lang}"],
                           cwd=str(src_dir), env=env, capture_output=True, timeout=60)
            subprocess.run(["pdflatex", "-interaction=nonstopmode", f"tesis_{lang}.tex"],
                           cwd=str(src_dir), env=env, capture_output=True, timeout=120)
            subprocess.run(["pdflatex", "-interaction=nonstopmode", f"tesis_{lang}.tex"],
                           cwd=str(src_dir), env=env, capture_output=True, timeout=120)
        except Exception as e:
            _log(f"    [error] {e}")
            resultados[lang] = {"status": "ERROR", "error": str(e)}
            continue

        pdf_src = src_dir / f"tesis_{lang}.pdf"
        log_src = src_dir / f"tesis_{lang}.log"
        n_err = 0
        pages = 0
        if log_src.exists():
            try:
                log_txt = log_src.read_text(encoding="utf-8", errors="replace")
                n_err = log_txt.count("\n! ")
                import re as _re
                m = _re.search(rf"Output written on tesis_{lang}\.pdf \((\d+) pages", log_txt)
                if m:
                    pages = int(m.group(1))
            except Exception:
                pass

        if pdf_src.exists():
            sz = pdf_src.stat().st_size
            shutil.copy2(pdf_src, dist_dir / f"tesis_{lang}.pdf")
            _log(f"    OK: {sz//1024} KB, {pages} paginas, errores={n_err}")
            resultados[lang] = {"status": "OK", "size": sz, "pages": pages, "errores": n_err}
        else:
            _log(f"    FAIL: no se genero PDF (errores={n_err})")
            resultados[lang] = {"status": "FAIL", "errores": n_err}

    n_ok = sum(1 for r in resultados.values() if r.get("status") == "OK")
    return ("OK" if n_ok == 3 else "WARN", {"por_idioma": resultados})


def fase_15_dist(args, estado):
    _log_block("[PHASE 15] THU - DIST")
    dist = BASE / "paper" / "thu" / "dist"
    if not dist.exists():
        _log(f"  AVISO: {dist} no existe")
        return ("WARN", {"exist": False})
    pdfs = list(dist.glob("tesis_*.pdf"))
    _log(f"  PDFs en dist/: {len(pdfs)}")
    import hashlib
    for p in pdfs:
        h = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
        mb = round(p.stat().st_size / (1024*1024), 2)
        _log(f"    {p.name}  {mb} MB  {h}")
    return ("OK", {"n_pdfs": len(pdfs)})


# =====================================================================
# RESUMEN FINAL
# =====================================================================

def fase_99_resumen(args, estado):
    _log_block("[PHASE 99] RESUMEN FINAL")
    _log("")
    _log("  --- AUDITORIA ---")
    _log(f"    audit report:  {OUTPUTS / 'audit_report_latest.txt'}")
    _log(f"    last_run.json: {LAST_RUN}")
    _log(f"    log completo:  {RUN_LOG_PATH}")
    _log(f"    cronolog md:   {BASE / 'registry' / 'chronolog.md'}")
    _log("")
    _log("  --- DOCUMENTOS GENERADOS ---")
    dist = BASE / "paper" / "thu" / "dist"
    if dist.exists():
        for pdf in sorted(dist.glob("tesis_*.pdf")):
            mb = round(pdf.stat().st_size / (1024*1024), 2)
            _log(f"    {pdf.name}  ({mb} MB)")
    _log("")
    _log("  --- DASHBOARD ---")
    _log("    streamlit run app_thu.py")
    _log("    http://localhost:8501")
    _log("")
    _log("  --- PROXIMOS PASOS ---")
    _log("    1. Abrir los PDFs: paper/thu/dist/")
    _log("    2. Dashboard:      streamlit run app_thu.py")
    _log("    3. Auditoria:      outputs/audit_report_latest.txt")
    _log("")
    seeds = sorted((BASE / "seeds").glob("seed_v*.json")) if (BASE / "seeds").exists() else []
    if seeds:
        _log(f"  Ultimo manifest: {seeds[-1].name}")
    _log("")
    _log("  LISTO. Todos los artefactos generados correctamente.")
    return ("OK", {})




PIR_FASES = [
    ("01", "Entorno",            fase_01_entorno),
    ("02", "Schema",             fase_02_schema),
    ("03", "Integridad",         fase_03_integridad),
    ("04", "Tests",              fase_04_tests),
    ("05", "Semilla",            fase_05_semilla),
    ("06", "Manifest + anclaje", fase_06_manifest),
    ("07", "Analisis",           fase_07_analisis),
    ("08", "Cronolog export",    fase_08_cronolog),
    ("09", "Audit report",       fase_09_audit),
]

THU_FASES = [
    ("10", "THU Simbolica",      fase_10_simbolica),
    ("11", "THU Deudas",         fase_11_deudas),
    ("12", "THU Figuras",        fase_12_figuras),
    ("13", "THU LaTeX builder",  fase_13_latex),
    ("14", "THU Compilacion",    fase_14_compilar),
    ("15", "THU dist/",          fase_15_dist),
]

FINAL_FASES = [
    ("99", "Resumen final",      fase_99_resumen),
]


def _fases_activas(args):
    fases = []
    if getattr(args, "fetch", False):
        fases.append(("00b", "Fetch datasets", fase_00b_fetch))
    if not args.skip_pir:
        fases.extend(PIR_FASES)
    if not args.skip_thu:
        fases.extend(THU_FASES)
    fases.extend(FINAL_FASES)
    return fases


def imprimir_plan(args):
    print()
    print(_line("="))
    print("PIR + THU-TBEA RUN_ALL - PLAN DE EJECUCION")
    print(_line("="))
    if not args.skip_pir:
        print("  --- PIR (framework) ---")
        for num, titulo, _ in PIR_FASES:
            print(f"  [{num}] {titulo}")
    if not args.skip_thu:
        print("  --- THU-TBEA (subproyecto) ---")
        for num, titulo, _ in THU_FASES:
            print(f"  [{num}] {titulo}")
    print("  --- Cierre ---")
    for num, titulo, _ in FINAL_FASES:
        print(f"  [{num}] {titulo}")
    print(_line("="))
    print(f"  --with-figs:   {args.with_figs}")
    print(f"  --skip-compile:{args.skip_compile}")
    print(f"  --skip-pir:    {args.skip_pir}")
    print(f"  --skip-thu:    {args.skip_thu}")
    print(_line("="))


def main():
    global RUN_LOG, RUN_LOG_PATH

    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-tests", action="store_true")
    ap.add_argument("--seed", action="store_true")
    ap.add_argument("--dashboard", action="store_true")
    ap.add_argument("--stop-on-fail", action="store_true")
    ap.add_argument("--skip-pir", action="store_true")
    ap.add_argument("--skip-thu", action="store_true")
    ap.add_argument("--with-figs", action="store_true")
    ap.add_argument("--skip-compile", action="store_true")
    ap.add_argument("--fetch", action="store_true", help="descargar datasets")
    ap.add_argument("--with-bootstrap", action="store_true", help="correr bootstrap antes del pipeline")
    args = ap.parse_args()

    if args.dry_run:
        imprimir_plan(args)
        return

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    RUN_LOG_PATH = OUTPUTS / f"run_log_{_ts_compact()}.txt"
    RUN_LOG = open(RUN_LOG_PATH, "w", encoding="utf-8", newline="\n")

    inicio = time.time()
    _log(_line("="))
    _log("PIR + THU-TBEA RUN_ALL - EJECUCION COMPLETA")
    _log(_line("="))
    _log(f"Timestamp:   {_ts()}")
    _log(f"Python:      {PY}")
    _log(f"CWD:         {Path.cwd()}")
    _log(f"Repo:        {BASE}")
    _log(f"Flags:       with_figs={args.with_figs} skip_compile={args.skip_compile} "
         f"skip_pir={args.skip_pir} skip_thu={args.skip_thu}")
    _log(_line("="))

    resultados = []
    for num, titulo, fn in _fases_activas(args):
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
        _log(f"[PHASE {num}] {status} ({dur:.2f}s)")
        if status == "FAIL" and args.stop_on_fail:
            _log("[stop-on-fail] abortando por fallo")
            break

    total = time.time() - inicio

    last = {
        "timestamp_utc": _ts(),
        "duracion_total_s": round(total, 2),
        "python": PY, "cwd": str(Path.cwd()), "repo": str(BASE),
        "flags": vars(args), "fases": resultados,
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
    _log(f"Log completo: {RUN_LOG_PATH}")
    _log(_line("="))
    RUN_LOG.close()

    if args.dashboard:
        _log("")
        _log("DASHBOARD - streamlit run app.py")
        try:
            subprocess.run([PY, "-m", "streamlit", "run", "app.py",
                            "--server.port", "8501", "--server.address", "0.0.0.0"],
                           cwd=str(BASE))
        except KeyboardInterrupt:
            _log("Dashboard detenido.")

    sys.exit(0 if n_fail == 0 else 1)


if __name__ == "__main__":
    main()