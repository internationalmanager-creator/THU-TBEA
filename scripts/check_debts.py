# -*- coding: utf-8 -*-
"""Verificador de deudas THU-TBEA v5.4 (persistente).

Reemplaza al checker volatil de $env:TEMP. Soporta:
  - historico:     marca "aceptado", no re-verifica
  - binario:       ejecuta un comando, exige returncode 0
  - exist:         verifica existencia + tamano minimo de archivos
  - json_field:    valida campos en JSON (all_entries_verified, has_chapter)
  - grep:          busca patrones en archivos (patterns_all, no_huerfana)
  - manual:        requiere input humano
  - doi_verify:    D-22 refinado con protocolo L1+L2+L3

Uso:
  python scripts/check_debts.py               # offline (L1+L2)
  python scripts/check_debts.py --online      # incluye L3 (Crossref)
  python scripts/check_debts.py --only D-22   # solo una deuda
"""
import json
import hashlib
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

REPO = Path.cwd()
DEBTS = REPO / "docs" / "debts_history.json"
ONLINE = "--online" in sys.argv
ONLY = None
if "--only" in sys.argv:
    i = sys.argv.index("--only")
    if i + 1 < len(sys.argv):
        ONLY = sys.argv[i + 1].strip()

# --- Regex validos ---
RE_DOI = re.compile(r"^10\.\d{4,9}/[^\s]+$")


# ============================================================
# Checkers basicos
# ============================================================

def check_binario(spec):
    cmd = spec.get("cmd", "")
    if not cmd:
        return False, "sin cmd"
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, timeout=15)
        return (r.returncode == 0), ("returncode=%d" % r.returncode)
    except Exception as e:
        return False, "exception: %s" % e


def check_hash(spec):
    p = REPO / spec["file"]
    if not p.exists():
        return False, "no existe"
    h = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    return (h == spec["expected"]), ("got %s" % h)


def check_exist(spec):
    files = spec.get("files") or [spec.get("file")]
    min_b = spec.get("min_bytes", 0)
    for f in files:
        p = REPO / f
        if not p.exists():
            return False, "falta %s" % f
        if p.stat().st_size < min_b:
            return False, "%s too small (%d B)" % (f, p.stat().st_size)
    return True, "%d archivos OK" % len(files)


def check_json_field(spec):
    p = REPO / spec["file"]
    if not p.exists():
        return False, "no existe"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return False, "JSON invalido: %s" % e
    kind = spec.get("assert", "")
    if kind == "all_entries_verified":
        entries = data.get("entries", [])
        bad = [e for e in entries if e.get("verified") is not True]
        return (len(bad) == 0), "%d sin verified:true (de %d)" % (len(bad), len(entries))
    if kind == "has_chapter":
        chs = data.get("chapters", {})
        ch = spec["chapter"]
        if ch not in chs:
            return False, "%s ausente" % ch
        n = len(chs[ch].get("sections", []))
        return (n >= spec.get("min_sections", 1)), "%d secciones" % n
    if kind == "braces_balanced":
        text = p.read_text(encoding="utf-8")
        n_open, n_close = text.count("{"), text.count("}")
        return (n_open == n_close), "braces %d/%d" % (n_open, n_close)
    if kind == "has_appendix_bodies":
        bodies = data.get("appendix_bodies", {})
        min_count = spec.get("min_count", 1)
        n = len(bodies)
        return (n >= min_count), "%d appendix_bodies (min %d)" % (n, min_count)
    return False, "assert desconocido: %s" % kind


def check_grep(spec):
    files = [REPO / f for f in spec["files"]]
    for f in files:
        if not f.exists():
            return False, "falta %s" % f.name
    kind = spec.get("assert", "patterns_all")
    if kind == "patterns_all":
        pats = spec.get("patterns_all", [])
        text = "".join(f.read_text(encoding="utf-8", errors="replace") for f in files)
        missing = [p for p in pats if p not in text]
        if missing:
            return False, "%d/%d ausentes" % (len(missing), len(pats))
        return True, "%d/%d presentes" % (len(pats), len(pats))
    if kind == "no_huerfana":
        fn = spec.get("function", "")
        for f in files:
            text = f.read_text(encoding="utf-8", errors="replace")
            n_def = text.count("def %s(" % fn)
            if n_def == 0:
                # Funcion eliminada = objetivo cumplido
                return True, "%s eliminada" % fn
            n_use = text.count("%s(" % fn) - n_def
            if n_use == 0:
                return False, "%s definida pero nunca usada" % fn
        return True, "%s usada" % fn
    return False, "assert desconocido: %s" % kind


def check_manual(spec):
    return None, "requiere input humano"


def check_historico(spec):
    return True, "historico"


# ============================================================
# D-22: doi_verify (L1 + L2 + L3 opcional)
# ============================================================

def _strip_bib_comments(text):
    out = []
    for ln in text.splitlines():
        # Saltar comentarios y lineas vacias
        s = ln.strip()
        if s.startswith("%") or not s:
            continue
        out.append(ln)
    return "\n".join(out)


def _bib_keys(text):
    """Extrae los keys de un .bib (tolerante a comentarios)."""
    clean = _strip_bib_comments(text)
    keys = set()
    for m in re.finditer(r"@\w+\{\s*([^,\s]+)\s*,", clean):
        keys.add(m.group(1).strip())
    return keys


def _bib_braces_balanced(text):
    clean = _strip_bib_comments(text)
    return clean.count("{") == clean.count("}")


def _doi_resolves_online(doi, timeout=8):
    """HEAD a doi.org; tolera 403 (Forbidden) como 'existe'.
    Fallback a GET si HEAD falla con errores no-403."""
    url = "https://doi.org/%s" % doi
    headers = {"User-Agent": "THU-TBEA-checker/1.0 (mailto:comipca@gmail.com)"}
    # Intento 1: HEAD
    try:
        req = urllib.request.Request(url, method="HEAD", headers=headers)
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=timeout) as r:
            dt = time.time() - t0
            if 200 <= r.status < 400:
                return True, "HTTP %d HEAD (%.2fs)" % (r.status, dt)
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return True, "HTTP 403 HEAD (existe, acceso restringido)"
        if e.code == 404:
            return False, "HTTP 404 (no existe)"
        # Otros HTTPError: probar GET
    except Exception:
        pass
    # Intento 2: GET
    try:
        req = urllib.request.Request(url, method="GET", headers=headers)
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=timeout) as r:
            dt = time.time() - t0
            return (200 <= r.status < 400), "HTTP %d GET (%.2fs)" % (r.status, dt)
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return True, "HTTP 403 GET (existe, acceso restringido)"
        return False, "HTTP %d GET" % e.code
    except Exception as e:
        return False, "err: %s" % str(e)[:80]


def check_braces(spec):
    """Verifica que un archivo de texto tenga llaves balanceadas."""
    p = REPO / spec["file"]
    if not p.exists():
        return False, "no existe"
    content = p.read_text(encoding="utf-8", errors="replace")
    n_open, n_close = content.count("{"), content.count("}")
    return (n_open == n_close), "braces %d/%d" % (n_open, n_close)


def check_doi_verify(spec):
    """D-22 refinado con L1+L2+L3."""
    reg_path = REPO / spec["registry"]
    bib_path = REPO / spec["bib"]
    if not reg_path.exists():
        return False, "falta %s" % spec["registry"]
    if not bib_path.exists():
        return False, "falta %s" % spec["bib"]

    registry = json.loads(reg_path.read_text(encoding="utf-8"))
    entries = registry.get("entries", [])
    bib_text = bib_path.read_text(encoding="utf-8")
    bib_keys = _bib_keys(bib_text)

    # --- L1: sintaxis DOI ---
    l1_bad = []
    for e in entries:
        doi = e.get("doi")
        if doi is None:
            # Aceptable si tiene arxiv o es historico sin DOI
            continue
        if not RE_DOI.match(doi):
            l1_bad.append((e["key"], doi))

    # --- L2: entrada presente en .bib ---
    l2_bad = []
    for e in entries:
        if e["key"] not in bib_keys:
            l2_bad.append(e["key"])
    l2_braces_ok = _bib_braces_balanced(bib_text)

    # --- L3: resolucion externa (solo si --online) ---
    l3_bad = []
    l3_tested = 0
    if ONLINE:
        suspect_keys = spec.get("suspect_keys", [])
        for key in suspect_keys:
            entry = next((e for e in entries if e["key"] == key), None)
            if entry is None:
                l3_bad.append((key, "no esta en registry"))
                continue
            doi = entry.get("doi")
            arxiv = entry.get("arxiv")
            if doi is None:
                # Sin DOI pero con arXiv = valido (preprint)
                if arxiv:
                    l3_tested += 1
                    continue
                l3_bad.append((key, "sin DOI ni arXiv"))
                continue
            ok, msg = _doi_resolves_online(doi, timeout=spec.get("timeout_per_doi", 8))
            l3_tested += 1
            if not ok:
                l3_bad.append((key, msg))
            # rate limit defensivo
            time.sleep(spec.get("rate_limit_ms", 300) / 1000.0)

    # --- Veredicto ---
    n_l1 = len(entries)
    n_doi = sum(1 for e in entries if e.get("doi"))
    lines = [
        "L1: %d/%d DOIs con formato valido" % (n_doi - len(l1_bad), n_doi),
        "L2: %d/%d keys presentes en .bib%s" % (
            len(entries) - len(l2_bad), len(entries),
            "" if l2_braces_ok else " (BRACES DESBALANCEADAS)"),
    ]

    fail = bool(l1_bad) or bool(l2_bad) or not l2_braces_ok

    if ONLINE:
        n_susp = len(spec.get("suspect_keys", []))
        lines.append("L3: %d/%d sospechosos resuelven en Crossref" % (
            n_susp - len(l3_bad), n_susp))
        if l3_bad:
            fail = True
        summary = " | ".join(lines)
        if fail:
            detail = ""
            if l1_bad:
                detail += " L1_fails=%s" % l1_bad[:3]
            if l2_bad:
                detail += " L2_missing=%s" % l2_bad[:3]
            if l3_bad:
                detail += " L3_fails=%s" % l3_bad[:3]
            return False, summary + detail
        return True, summary
    else:
        summary = " | ".join(lines) + " | L3: pendiente (correr --online)"
        if fail:
            return False, summary
        # L1+L2 OK pero L3 sin correr -> MANUAL (auditor decide cierre)
        return None, summary


# ============================================================
# Mapa de checkers
# ============================================================

CHECKS = {
    "binario": check_binario,
    "hash": check_hash,
    "exist": check_exist,
    "json_field": check_json_field,
    "grep": check_grep,
    "manual": check_manual,
    "historico": check_historico,
    "braces": check_braces,
    "doi_verify": check_doi_verify,
}


def main():
    if not DEBTS.exists():
        print("[FALLA] no existe %s" % DEBTS)
        return 1
    data = json.loads(DEBTS.read_text(encoding="utf-8"))
    debts = data.get("debts", [])

    print("=" * 78)
    print("REPORTE DE DEUDAS - THU-TBEA v5.4  (online=%s)" % ONLINE)
    print("=" * 78)
    print()

    counts = {"CERRADA": 0, "FALLA": 0, "MANUAL": 0, "ERROR": 0, "SKIP": 0}
    for d in debts:
        if ONLY and d["id"] != ONLY:
            counts["SKIP"] += 1
            continue
        ct = d.get("check_type", "")
        fn = CHECKS.get(ct)
        if fn is None:
            estado, msg = "ERROR", "check_type desconocido: %s" % ct
        else:
            try:
                ok, msg = fn(d.get("check_spec", {}))
            except Exception as e:
                ok, msg = False, "exception: %s" % str(e)[:80]
            if ok is None:
                estado = "MANUAL"
            elif ok:
                estado = "CERRADA"
            else:
                estado = "FALLA"
        counts[estado] += 1
        sym = {
            "CERRADA": "[OK]    ",
            "FALLA":   "[FALLA] ",
            "MANUAL":  "[MANUAL]",
            "ERROR":   "[ERROR] ",
        }.get(estado, "[?]     ")
        desc = d["descripcion"][:50]
        print("%s %s  %-5s  %-50s  %s" % (sym, d["id"], d["prioridad"], desc, msg))
        if estado == "CERRADA":
            d["estado_actual"] = "CERRADA"
        elif estado == "FALLA":
            d["estado_actual"] = "ABIERTA"
        elif estado == "MANUAL":
            d["estado_actual"] = "MANUAL"
        else:
            d["estado_actual"] = "ERROR"

    print()
    print("=" * 78)
    print("RESUMEN: %d cerradas / %d fallas / %d manuales / %d errores" % (
        counts["CERRADA"], counts["FALLA"], counts["MANUAL"], counts["ERROR"]))
    print("=" * 78)

    data["updated_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    DEBTS.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0 if (counts["FALLA"] == 0 and counts["ERROR"] == 0) else 1


if __name__ == "__main__":
    sys.exit(main())