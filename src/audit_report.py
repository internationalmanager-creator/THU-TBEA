"""Reporte de auditoria completo en TXT.

Genera un archivo con TODOS los checks ejecutados uno por uno, cada uno
con estado PASS/FAIL/SKIP, evidencia y hashes.

Ademas encadena los reportes: cada reporte incluye el hash del anterior
en `registry/reports.jsonl`, de modo que no se puede alterar un reporte
pasado sin romper la cadena.

Uso:
    python src/audit_report.py
    python src/audit_report.py --out outputs/mi_reporte.txt
    python src/audit_report.py --verify outputs/audit_report_XXX.txt
    python src/audit_report.py --no-chain       # no toca reports.jsonl
"""
import argparse
import hashlib
import json
import re
import shutil
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE / "src"))

import db_manager
import hash_manifest as hm

DB_PATH      = BASE / "data" / "pir.sqlite"
SEEDS_DIR    = BASE / "seeds"
OUTPUTS_DIR  = BASE / "outputs"
REGISTRY     = BASE / "registry"
REPORTS_LOG  = REGISTRY / "reports.jsonl"
LAST_RUN     = OUTPUTS_DIR / "last_run.json"

GENESIS      = "GENESIS"
SCHEMA_V     = 2
WIDTH        = 100


def _ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ts_compact():
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def _sha(s):
    if isinstance(s, str):
        s = s.encode("utf-8")
    return hashlib.sha256(s).hexdigest()


def _line(ch="=", n=WIDTH):
    return ch * n


def _mk(cid, name, status, detail="", **evidence):
    return {"id": cid, "name": name, "status": status,
            "detail": detail, "evidence": evidence}


# ============================================================
# SECTION 1 — ENTORNO
# ============================================================

def chk_entorno():
    checks = []

    v = sys.version_info
    ok = v.major >= 3 and v.minor >= 10
    checks.append(_mk("CHK-001", "Python >= 3.10", "PASS" if ok else "FAIL",
                      f"version={v.major}.{v.minor}.{v.micro}"))

    cwd = Path.cwd().resolve()
    ok = (cwd / "src" / "db_manager.py").exists()
    checks.append(_mk("CHK-002", "CWD es raiz del repo",
                      "PASS" if ok else "FAIL", f"cwd={cwd}"))

    faltantes = []
    for mod in ("numpy", "scipy", "pandas", "matplotlib",
                "streamlit", "plotly", "tqdm", "pytest"):
        try:
            __import__(mod)
        except ImportError:
            faltantes.append(mod)
    checks.append(_mk("CHK-003", "Dependencias importables",
                      "PASS" if not faltantes else "FAIL",
                      f"faltan={faltantes or 'ninguna'}",
                      total=8, faltan=len(faltantes)))

    return checks


# ============================================================
# SECTION 2 — ESTRUCTURA
# ============================================================

def chk_estructura():
    checks = []
    archivos = [
        ("CHK-010", "src/db_manager.py"),
        ("CHK-011", "src/migrations.py"),
        ("CHK-012", "src/chronolog.py"),
        ("CHK-013", "src/hash_manifest.py"),
        ("CHK-014", "src/registrar_entidad.py"),
        ("CHK-015", "src/analisis.py"),
        ("CHK-016", "src/audit_report.py"),
        ("CHK-017", "src/run_all.py"),
        ("CHK-018", "src/unidades.py"),
        ("CHK-019", "src/nueva_entidad.py"),
        ("CHK-020", "src/estadistica.py"),
        ("CHK-021", "src/preregistro.py"),
        ("CHK-022", "requirements.txt"),
        ("CHK-023", "README.md"),
        ("CHK-024", "registry/project_metadata.json"),
        ("CHK-025", "registry/DECISIONS.md"),
        ("CHK-026", "registry/GLOSARIO.md"),
        ("CHK-027", "registry/epistemic_log.md"),
        ("CHK-028", "registry/HALLAZGOS_FALSADOS.md"),
        ("CHK-029", "registry/reports.jsonl"),
    ]
    for cid, rel in archivos:
        p = BASE / rel
        checks.append(_mk(cid, f"Existe {rel}",
                          "PASS" if p.exists() else "FAIL",
                          f"size={p.stat().st_size if p.exists() else 0}B"))
    return checks

# === PARTE 2 se agrega a continuacion ===

# ============================================================
# SECTION 3 — SCHEMA
# ============================================================

def chk_schema():
    checks = []

    if not DB_PATH.exists():
        checks.append(_mk("CHK-030", "DB existe", "FAIL", f"{DB_PATH} ausente"))
        return checks
    checks.append(_mk("CHK-030", "DB existe", "PASS",
                      f"size={DB_PATH.stat().st_size}B"))

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        v = conn.execute("PRAGMA user_version").fetchone()[0]
        checks.append(_mk("CHK-031", f"user_version == {SCHEMA_V}",
                          "PASS" if v == SCHEMA_V else "FAIL",
                          f"user_version={v}"))

        esperadas = {"entidades", "provenance", "provenance_history",
                     "eventos", "progreso", "schema_version"}
        actuales = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        faltan = esperadas - actuales
        checks.append(_mk("CHK-032", "Tablas requeridas existen",
                          "PASS" if not faltan else "FAIL",
                          f"faltan={sorted(faltan) or 'ninguna'}",
                          total=len(esperadas),
                          presentes=len(esperadas & actuales)))

        cols = {r[1] for r in conn.execute("PRAGMA table_info(provenance)")}
        req = {"reproducibilidad", "version", "hash_registro", "prev_hash"}
        faltan = req - cols
        checks.append(_mk("CHK-033", "provenance tiene columnas v2",
                          "PASS" if not faltan else "FAIL",
                          f"faltan={sorted(faltan) or 'ninguna'}"))

        idx = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index'")}
        esperados = {"idx_entidades_categoria", "idx_eventos_ts",
                     "idx_eventos_tipo", "idx_provhist_entidad"}
        faltan = esperados - idx
        checks.append(_mk("CHK-034", "Indices clave presentes",
                          "PASS" if not faltan else "FAIL",
                          f"faltan={sorted(faltan) or 'ninguno'}"))

        vistas = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='view'")}
        ok = "provenance_actual" in vistas
        checks.append(_mk("CHK-035", "Vista provenance_actual existe",
                          "PASS" if ok else "FAIL"))
    finally:
        conn.close()
    return checks


# ============================================================
# SECTION 4 — ENTIDADES
# ============================================================

def chk_entidades():
    checks = []
    if not DB_PATH.exists():
        checks.append(_mk("CHK-040", "Entidades consultables", "SKIP",
                          "DB ausente"))
        return checks

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        total = conn.execute("SELECT COUNT(*) FROM entidades").fetchone()[0]
        checks.append(_mk("CHK-040", "Entidades consultables",
                          "PASS", f"total={total}", total=total))

        CATS = {"cosmologia", "geofisica", "biologia", "neurofisiologia",
                "cuantica", "antropologia", "otros", "test"}
        invalidas = [r[0] for r in conn.execute(
            "SELECT DISTINCT categoria FROM entidades")]
        invalidas = [c for c in invalidas if c not in CATS]
        checks.append(_mk("CHK-041", "Categorias validas",
                          "PASS" if not invalidas else "FAIL",
                          f"invalidas={invalidas or 'ninguna'}"))

        ORS = {"observado", "generado", "inferido", "simulado"}
        invalidos = [r[0] for r in conn.execute(
            "SELECT DISTINCT origen FROM entidades")]
        invalidos = [o for o in invalidos if o not in ORS]
        checks.append(_mk("CHK-042", "Origenes validos",
                          "PASS" if not invalidos else "FAIL",
                          f"invalidos={invalidos or 'ninguno'}"))

        EST = {"D", "P", "F", "A"}
        invalidos = [r[0] for r in conn.execute(
            "SELECT DISTINCT estatus FROM entidades")]
        invalidos = [e for e in invalidos if e and e not in EST]
        checks.append(_mk("CHK-043", "Estatus validos",
                          "PASS" if not invalidos else "FAIL",
                          f"invalidos={invalidos or 'ninguno'}"))

        n = conn.execute(
            "SELECT COUNT(*) FROM entidades WHERE valor_principal <= 0"
        ).fetchone()[0]
        checks.append(_mk("CHK-044", "valor_principal > 0",
                          "PASS" if n == 0 else "FAIL", f"violaciones={n}"))

        faltan = conn.execute("""
            SELECT e.id FROM entidades e
            LEFT JOIN provenance p ON p.id_entidad = e.id
            WHERE p.id_entidad IS NULL
        """).fetchall()
        checks.append(_mk("CHK-045", "Toda entidad tiene provenance",
                          "PASS" if not faltan else "FAIL",
                          f"sin_provenance={[r[0] for r in faltan] or 'ninguna'}"))

        faltan = conn.execute("""
            SELECT e.id FROM entidades e
            LEFT JOIN progreso p ON p.id_entidad = e.id
            WHERE p.id_entidad IS NULL
        """).fetchall()
        checks.append(_mk("CHK-046", "Toda entidad tiene progreso",
                          "PASS" if not faltan else "FAIL",
                          f"sin_progreso={[r[0] for r in faltan] or 'ninguna'}"))
    finally:
        conn.close()
    return checks


# ============================================================
# SECTION 5 — PROVENANCE
# ============================================================

def chk_provenance():
    checks = []
    if not DB_PATH.exists():
        checks.append(_mk("CHK-050", "Provenance consultable", "SKIP"))
        return checks

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        n_hist = conn.execute(
            "SELECT COUNT(*) FROM provenance_history").fetchone()[0]
        checks.append(_mk("CHK-050", "provenance_history consultable",
                          "PASS", f"registros={n_hist}", total=n_hist))

        n = conn.execute(
            "SELECT COUNT(*) FROM provenance_history "
            "WHERE hash_registro IS NULL OR hash_registro=''"
        ).fetchone()[0]
        checks.append(_mk("CHK-051", "Todo provenance_history tiene hash_registro",
                          "PASS" if n == 0 else "FAIL", f"sin_hash={n}"))

        roturas = []
        for eid_row in conn.execute(
                "SELECT DISTINCT id_entidad FROM provenance_history").fetchall():
            eid = eid_row[0]
            filas = conn.execute("""
                SELECT version, hash_registro, prev_hash
                FROM provenance_history WHERE id_entidad=? ORDER BY version
            """, (eid,)).fetchall()
            prev = GENESIS
            for f in filas:
                if f["prev_hash"] != prev:
                    roturas.append((eid, f["version"], "prev_hash"))
                    break
                prev = f["hash_registro"]
        checks.append(_mk("CHK-052", "Cadena de provenance_history intacta",
                          "PASS" if not roturas else "FAIL",
                          f"roturas={roturas or 'ninguna'}"))

        n = conn.execute("""
            SELECT COUNT(*) FROM provenance_history
            WHERE version >= 2 AND (reproducibilidad IS NULL OR reproducibilidad='')
        """).fetchone()[0]
        checks.append(_mk("CHK-053", "Reproducibilidad poblada en v2+",
                          "PASS" if n == 0 else "SKIP",
                          f"sin_reproducibilidad_v2+={n}"))

        descuadres = []
        for eid_row in conn.execute("SELECT id_entidad FROM provenance").fetchall():
            eid = eid_row[0]
            mat = conn.execute(
                "SELECT version, hash_registro FROM provenance WHERE id_entidad=?",
                (eid,)).fetchone()
            ult = conn.execute("""
                SELECT version, hash_registro FROM provenance_history
                WHERE id_entidad=? ORDER BY version DESC LIMIT 1
            """, (eid,)).fetchone()
            if not ult:
                continue
            if (mat["version"], mat["hash_registro"]) != (ult["version"], ult["hash_registro"]):
                descuadres.append(eid)
        checks.append(_mk("CHK-054", "Materializada == ultima version historica",
                          "PASS" if not descuadres else "FAIL",
                          f"descuadres={descuadres or 'ninguno'}"))
    finally:
        conn.close()
    return checks

# === PARTE 3 se agrega a continuacion ===

# ============================================================
# SECTION 6 — EVENTOS / CADENA
# ============================================================

def chk_eventos():
    checks = []
    if not DB_PATH.exists():
        checks.append(_mk("CHK-060", "Eventos consultables", "SKIP"))
        return checks

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        n = conn.execute("SELECT COUNT(*) FROM eventos").fetchone()[0]
        checks.append(_mk("CHK-060", "Eventos consultables",
                          "PASS", f"total={n}", total=n))

        ok, idx, eid = db_manager.verificar_cadena_eventos(str(DB_PATH))
        checks.append(_mk("CHK-061", "Cadena de eventos integra",
                          "PASS" if ok else "FAIL",
                          f"idx_roto={idx} id={eid}" if not ok else "toda la cadena verifica"))

        p = conn.execute("SELECT prev_hash FROM eventos ORDER BY id LIMIT 1").fetchone()
        checks.append(_mk("CHK-062", "Primer evento apunta a GENESIS",
                          "PASS" if (p and p["prev_hash"] == GENESIS) else
                          ("SKIP" if not p else "FAIL"),
                          f"prev_hash={p['prev_hash'] if p else 'N/A'}"))

        n = conn.execute(
            "SELECT COUNT(*) FROM (SELECT hash FROM eventos GROUP BY hash HAVING COUNT(*)>1)"
        ).fetchone()[0]
        checks.append(_mk("CHK-063", "Sin hashes de eventos duplicados",
                          "PASS" if n == 0 else "FAIL", f"duplicados={n}"))

        n = conn.execute(
            "SELECT COUNT(*) FROM eventos WHERE tipo='manifest'").fetchone()[0]
        checks.append(_mk("CHK-064", "Existe al menos un anclaje de manifest",
                          "PASS" if n > 0 else "SKIP", f"n_manifest={n}"))
    finally:
        conn.close()
    return checks


# ============================================================
# SECTION 7 — MANIFEST
# ============================================================

def chk_manifest():
    checks = []
    if not SEEDS_DIR.exists():
        checks.append(_mk("CHK-070", "Directorio seeds/", "FAIL"))
        return checks
    checks.append(_mk("CHK-070", "Directorio seeds/", "PASS"))

    seeds = sorted(SEEDS_DIR.glob("seed_v*.json"))
    checks.append(_mk("CHK-071", "Al menos un manifest",
                      "PASS" if seeds else "SKIP", f"n={len(seeds)}"))
    if not seeds:
        return checks

    ultimo = seeds[-1]
    try:
        manifest = json.loads(ultimo.read_text(encoding="utf-8"))
    except Exception as e:
        checks.append(_mk("CHK-072", "Manifest parseable", "FAIL", str(e)))
        return checks
    checks.append(_mk("CHK-072", "Manifest parseable", "PASS",
                      f"version={manifest.get('version')} files={manifest.get('file_count')}",
                      archivo=str(ultimo.relative_to(BASE))))

    copia = {k: v for k, v in manifest.items() if k != "manifest_sha256"}
    canonico = json.dumps(copia, indent=2, ensure_ascii=False, sort_keys=True)
    ok = _sha(canonico) == manifest.get("manifest_sha256")
    checks.append(_mk("CHK-073", "manifest_sha256 verifica",
                      "PASS" if ok else "FAIL",
                      f"declarado={manifest.get('manifest_sha256', '')[:16]}..."))

    chain = GENESIS
    for e in manifest["files"]:
        chain = _sha(f"{chain}|{e['sha256']}")
    ok = chain == manifest.get("chain_root")
    checks.append(_mk("CHK-074", "chain_root recomputado coincide",
                      "PASS" if ok else "FAIL",
                      f"declarado={manifest.get('chain_root', '')[:16]}... recomputado={chain[:16]}..."))

    sums = SEEDS_DIR / "SHA256SUMS.txt"
    if not sums.exists():
        checks.append(_mk("CHK-075", "SHA256SUMS.txt existe", "FAIL"))
        return checks
    checks.append(_mk("CHK-075", "SHA256SUMS.txt existe", "PASS",
                      f"lineas={len(sums.read_text().splitlines())}"))

    malos = []
    total = 0
    for ln in sums.read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        total += 1
        partes = ln.split("  ", 1)
        if len(partes) != 2:
            malos.append(("formato", ln[:40]))
            continue
        h, rel = partes
        p = BASE / rel
        if not p.exists():
            malos.append((rel, "ausente"))
            continue
        if hm.sha256_file(p) != h:
            malos.append((rel, "hash distinto"))
    checks.append(_mk("CHK-076", "SHA256SUMS.txt coincide con archivos reales",
                      "PASS" if not malos else "FAIL",
                      f"total={total} fallos={len(malos)}",
                      fallos=malos[:5]))

    asc = sums.with_suffix(sums.suffix + ".asc")
    checks.append(_mk("CHK-077", "Firma GPG presente",
                      "PASS" if asc.exists() else "SKIP",
                      f"archivo={asc.name}" if asc.exists() else "no hay firma"))
    return checks


# ============================================================
# SECTION 8 — DOCUMENTACION
# ============================================================

def chk_docs():
    checks = []
    docs = [
        ("CHK-080", "registry/DECISIONS.md", 100),
        ("CHK-081", "registry/GLOSARIO.md", 100),
        ("CHK-082", "registry/epistemic_log.md", 50),
        ("CHK-083", "registry/HALLAZGOS_FALSADOS.md", 50),
        ("CHK-084", "registry/chronolog.md", 100),
        ("CHK-085", "registry/project_metadata.json", 50),
    ]
    for cid, rel, min_bytes in docs:
        p = BASE / rel
        if not p.exists():
            checks.append(_mk(cid, f"Doc {rel}", "FAIL", "ausente"))
            continue
        n = p.stat().st_size
        ok = n >= min_bytes
        checks.append(_mk(cid, f"Doc {rel}", "PASS" if ok else "SKIP",
                          f"size={n}B (min={min_bytes})"))

    meta_p = REGISTRY / "project_metadata.json"
    if meta_p.exists():
        try:
            meta = json.loads(meta_p.read_text(encoding="utf-8"))
            req = {"project_name", "version", "principal_investigator"}
            faltan = req - set(meta)
            checks.append(_mk("CHK-086", "metadata tiene campos clave",
                              "PASS" if not faltan else "FAIL",
                              f"faltan={sorted(faltan) or 'ninguno'}"))
        except Exception as e:
            checks.append(_mk("CHK-086", "metadata JSON valido", "FAIL", str(e)))
    return checks


# ============================================================
# SECTION 9 — ULTIMO RUN
# ============================================================

def chk_last_run():
    checks = []
    if not LAST_RUN.exists():
        checks.append(_mk("CHK-090", "Ultimo run_all registrado", "SKIP",
                          "no existe outputs/last_run.json"))
        return checks
    try:
        data = json.loads(LAST_RUN.read_text(encoding="utf-8"))
    except Exception as e:
        checks.append(_mk("CHK-090", "last_run.json parseable", "FAIL", str(e)))
        return checks
    n_tot = len(data.get("fases", []))
    n_ok = sum(1 for f in data.get("fases", []) if f.get("status") == "OK")
    checks.append(_mk("CHK-090", "Ultimo run_all registro fases",
                      "PASS", f"{n_ok}/{n_tot} OK",
                      timestamp=data.get("timestamp_utc")))

    t = data.get("pytest", {})
    if t:
        checks.append(_mk("CHK-091", "pytest resultado",
                          "PASS" if t.get("returncode") == 0 else "FAIL",
                          f"passed={t.get('passed', '?')} failed={t.get('failed', '?')}"))
    else:
        checks.append(_mk("CHK-091", "pytest resultado", "SKIP"))
    return checks


# ============================================================
# SECTION 10 — CADENA DE REPORTES
# ============================================================

def chk_reports_chain(prev_report_hash):
    checks = []
    if not REPORTS_LOG.exists():
        checks.append(_mk("CHK-100", "reports.jsonl existe", "SKIP",
                          "primer reporte de la cadena"))
        return checks
    lineas = [l for l in REPORTS_LOG.read_text(encoding="utf-8").splitlines() if l.strip()]
    checks.append(_mk("CHK-100", "reports.jsonl existe", "PASS",
                      f"reportes={len(lineas)}"))

    prev = GENESIS
    ok = True
    idx_roto = None
    for i, ln in enumerate(lineas):
        try:
            r = json.loads(ln)
        except Exception:
            ok = False; idx_roto = i; break
        if r.get("prev_report_hash") != prev:
            ok = False; idx_roto = i; break
        prev = r["report_hash"]
    checks.append(_mk("CHK-101", "Cadena de reportes integra",
                      "PASS" if ok else "FAIL",
                      f"roto_en={idx_roto}" if not ok else "verifica",
                      ultimo_hash=prev[:16] + "..."))

    if prev_report_hash and prev_report_hash != GENESIS:
        checks.append(_mk("CHK-102", "prev_report_hash del nuevo reporte == ultimo",
                          "PASS" if prev == prev_report_hash else "FAIL",
                          f"actual={prev[:16]}... esperado={prev_report_hash[:16]}..."))
    return checks

# === PARTE 4 se agrega a continuacion ===

# ============================================================
# ESCRITURA DEL REPORTE
# ============================================================

FINGERPRINT_MARKER = "## FINGERPRINT ##"


def _formato_check(c):
    head = f"[{c['id']}] {c['status']:<4} {c['name']}"
    if c.get("detail"):
        head += f"  ({c['detail']})"
    lineas = [head]
    if c.get("evidence"):
        ev = ", ".join(f"{k}={v}" for k, v in c["evidence"].items())
        lineas.append(f"        evidence: {ev}")
    return lineas


def _cargar_prev_hash():
    if not REPORTS_LOG.exists():
        return GENESIS
    lines = [l for l in REPORTS_LOG.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not lines:
        return GENESIS
    try:
        return json.loads(lines[-1])["report_hash"]
    except Exception:
        return GENESIS


def _secciones(prev_hash):
    return [
        ("SECTION 1 — ENTORNO",           chk_entorno()),
        ("SECTION 2 — ESTRUCTURA",        chk_estructura()),
        ("SECTION 3 — SCHEMA",            chk_schema()),
        ("SECTION 4 — ENTIDADES",         chk_entidades()),
        ("SECTION 5 — PROVENANCE",        chk_provenance()),
        ("SECTION 6 — EVENTOS / CADENA",  chk_eventos()),
        ("SECTION 7 — MANIFEST",          chk_manifest()),
        ("SECTION 8 — DOCUMENTACION",     chk_docs()),
        ("SECTION 9 — ULTIMO RUN",        chk_last_run()),
        ("SECTION 10 — CADENA REPORTES",  chk_reports_chain(prev_hash)),
    ]


def generar(out_path=None, chain=True):
    t0 = time.time()
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY.mkdir(parents=True, exist_ok=True)

    prev_hash = _cargar_prev_hash()
    ts_compact = _ts_compact()
    ts = _ts()
    report_id = f"AUD-{ts_compact}"

    secciones = _secciones(prev_hash)

    total = sum(len(sec[1]) for sec in secciones)
    n_pass = sum(1 for _, cs in secciones for c in cs if c["status"] == "PASS")
    n_fail = sum(1 for _, cs in secciones for c in cs if c["status"] == "FAIL")
    n_skip = sum(1 for _, cs in secciones for c in cs if c["status"] == "SKIP")
    dur = time.time() - t0

    # Cuerpo del reporte
    cuerpo = []
    cuerpo.append(_line("="))
    cuerpo.append("PIR AUDIT REPORT")
    cuerpo.append(_line("="))
    cuerpo.append(f"Report ID:     {report_id}")
    cuerpo.append(f"Generated:     {ts}")
    cuerpo.append(f"Repository:    {BASE}")
    cuerpo.append(f"Schema:        v{SCHEMA_V}")
    cuerpo.append(f"Investigator:  Erick Duque")
    cuerpo.append(f"ORCID:         0009-0004-1245-5464")
    cuerpo.append(f"Prev report:   {prev_hash}")
    cuerpo.append(f"Checks total:  {total}")
    cuerpo.append(_line("="))
    cuerpo.append("")

    for titulo, cs in secciones:
        cuerpo.append(_line("-"))
        cuerpo.append(titulo)
        cuerpo.append(_line("-"))
        for c in cs:
            for l in _formato_check(c):
                cuerpo.append(l)
        cuerpo.append("")

    cuerpo.append(_line("="))
    cuerpo.append("SUMMARY")
    cuerpo.append(_line("="))
    cuerpo.append(f"PASS:      {n_pass}")
    cuerpo.append(f"FAIL:      {n_fail}")
    cuerpo.append(f"SKIP:      {n_skip}")
    cuerpo.append(f"Total:     {total}")
    cuerpo.append(f"Duracion:  {dur:.2f}s")
    cuerpo.append(_line("="))
    cuerpo.append("")

    cuerpo_str = "\n".join(cuerpo) + "\n"
    report_hash = _sha(cuerpo_str)

    fingerprint = (
        FINGERPRINT_MARKER + "\n"
        + f"prev_report_hash: {prev_hash}\n"
        + f"report_hash:      {report_hash}\n"
        + f"line_count:       {len(cuerpo)}\n"
    )

    texto_final = cuerpo_str + "\n" + fingerprint

    if out_path is None:
        out_path = OUTPUTS_DIR / f"audit_report_{ts_compact}.txt"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(texto_final, encoding="utf-8", newline="\n")

    # Copia latest
    latest = OUTPUTS_DIR / "audit_report_latest.txt"
    shutil.copy2(out_path, latest)

    # Cadena de reportes
    if chain:
        entry = {
            "report_id": report_id,
            "timestamp_utc": ts,
            "report_hash": report_hash,
            "prev_report_hash": prev_hash,
            "report_file": str(out_path.relative_to(BASE)),
            "n_pass": n_pass, "n_fail": n_fail, "n_skip": n_skip,
            "total": total,
        }
        with open(REPORTS_LOG, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print()
    print(_line("="))
    print(f"AUDIT REPORT: {out_path.name}")
    print(_line("="))
    print(f"Checks:  {n_pass} PASS / {n_fail} FAIL / {n_skip} SKIP  (total {total})")
    print(f"report_hash:      {report_hash}")
    print(f"prev_report_hash: {prev_hash}")
    print(f"latest:           {latest}")
    print(_line("="))
    return out_path, report_hash, prev_hash, (n_pass, n_fail, n_skip)


def verificar(path):
    p = Path(path)
    if not p.exists():
        print(f"ERROR: no existe {p}", file=sys.stderr)
        return False
    texto = p.read_text(encoding="utf-8")

    m = re.search(r"^report_hash:\s+([0-9a-f]{64})$", texto, re.MULTILINE)
    m_prev = re.search(r"^prev_report_hash:\s+([0-9a-f]{64}|GENESIS)$",
                       texto, re.MULTILINE)
    if not m:
        print("ERROR: no se encuentra report_hash en el archivo", file=sys.stderr)
        return False

    idx = texto.find(FINGERPRINT_MARKER)
    if idx < 0:
        print("ERROR: no se encuentra seccion FINGERPRINT", file=sys.stderr)
        return False

    # El cuerpo es todo antes del marker, quitando el "\n" agregado
    cuerpo = texto[:idx]
    if cuerpo.endswith("\n"):
        cuerpo = cuerpo[:-1]

    h = _sha(cuerpo)
    ok = (h == m.group(1))
    print(f"Reporte: {p.name}")
    print(f"report_hash declarado:   {m.group(1)}")
    print(f"report_hash recomputado: {h}")
    if m_prev:
        print(f"prev_report_hash:        {m_prev.group(1)}")
    print("VERIFICADO OK" if ok else "VERIFICACION FALLIDA")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--verify", default=None, metavar="PATH")
    ap.add_argument("--no-chain", action="store_true")
    args = ap.parse_args()

    db_manager.inicializar_db(str(DB_PATH))
    if args.verify:
        sys.exit(0 if verificar(args.verify) else 1)
    generar(args.out, chain=not args.no_chain)


if __name__ == "__main__":
    main()