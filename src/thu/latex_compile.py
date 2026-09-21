"""Compila LaTeX a PDF con pdflatex / xelatex / lualatex.

Gestiona:
    - Deteccion del motor LaTeX disponible
    - Multiples pasadas para TOC y referencias
    - Cache basado en hash del .tex
    - Captura de log y errores
    - Salida a paper/thu/dist/tesis_<lang>.pdf

Uso CLI:
    python src/thu/latex_compile.py --lang es
    python src/thu/latex_compile.py --all
    python src/thu/latex_compile.py --all --force
    python src/thu/latex_compile.py --doctor      # diagnostico

API (para Streamlit):
    from thu.latex_compile import compilar, doctor
    resultado = compilar("es")                     # dict con status
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
SRC_DIR = BASE / "paper" / "thu" / "src"
DIST_DIR = BASE / "paper" / "thu" / "dist"
BUILD_DIR = BASE / "paper" / "thu" / "build"
CACHE_FILE = BUILD_DIR / ".compile_cache.json"

LANGS = ["es", "en", "de"]
MOTORES = ["pdflatex", "xelatex", "lualatex"]


def _ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(8192), b""):
            h.update(c)
    return h.hexdigest()


def _load_cache():
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_cache(c):
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8", newline="\n")


def detectar_motor():
    """Devuelve el primer motor LaTeX disponible."""
    for m in MOTORES:
        if shutil.which(m):
            return m
    return None


def doctor():
    """Diagnostico del entorno LaTeX."""
    info = {
        "motor": detectar_motor(),
        "motores_disponibles": [m for m in MOTORES if shutil.which(m)],
        "src_dir": str(SRC_DIR),
        "src_existe": SRC_DIR.exists(),
        "dist_dir": str(DIST_DIR),
        "dist_existe": DIST_DIR.exists(),
        "tex_files": [p.name for p in SRC_DIR.glob("*.tex")] if SRC_DIR.exists() else [],
        "pdfs_generados": [p.name for p in DIST_DIR.glob("*.pdf")] if DIST_DIR.exists() else [],
    }
    if not info["motor"]:
        info["instalar"] = {
            "windows": "winget install MiKTeX.MiKTeX (o descargar de miktex.org)",
            "ubuntu": "sudo apt install texlive-latex-base texlive-latex-extra texlive-lang-spanish texlive-lang-german",
            "macos": "brew install --cask mactex-no-gui",
        }
    return info


def compilar(lang, force=False, timeout=180):
    """Compila tesis_<lang>.tex a PDF.

    Devuelve dict:
        {
            "lang": str,
            "status": "OK" | "SKIP" | "FAIL",
            "pdf": str | None,
            "sha256": str | None,
            "log": str,
            "duracion_s": float,
            "timestamp_utc": str,
            "razon": str | None,
        }
    """
    t0 = time.time()
    resultado = {
        "lang": lang,
        "status": "FAIL",
        "pdf": None,
        "sha256": None,
        "log": "",
        "duracion_s": 0.0,
        "timestamp_utc": _ts(),
        "razon": None,
    }

    if lang not in LANGS:
        resultado["razon"] = "Idioma invalido: " + lang
        return resultado

    motor = detectar_motor()
    if not motor:
        resultado["razon"] = ("No hay motor LaTeX instalado (pdflatex, xelatex "
                              "o lualatex). Ejecuta --doctor para instrucciones.")
        return resultado

    tex = SRC_DIR / ("tesis_" + lang + ".tex")
    if not tex.exists():
        resultado["razon"] = ("No existe " + str(tex.relative_to(BASE))
                              + ". Ejecuta primero latex_builder.py --lang " + lang)
        return resultado

    # Cache: si el .tex no cambio y el PDF existe y no es forzar -> skip
    tex_hash = _sha_file(tex)
    cache = _load_cache()
    clave = lang + ":" + motor + ":" + tex_hash
    if not force and cache.get(lang, {}).get("cache_key") == clave:
        pdf_prev = DIST_DIR / ("tesis_" + lang + ".pdf")
        if pdf_prev.exists():
            resultado.update({
                "status": "SKIP",
                "pdf": str(pdf_prev.relative_to(BASE)),
                "sha256": _sha_file(pdf_prev),
                "razon": "Cache: el .tex no cambio",
                "duracion_s": round(time.time() - t0, 2),
            })
            return resultado

    # Compilar en directorio de build
    work = BUILD_DIR / lang
    work.mkdir(parents=True, exist_ok=True)

    tex_work = work / tex.name
    shutil.copy2(tex, tex_work)

    log_partes = []

    # 2 pasadas para TOC
    for i in range(1, 3):
        cmd = [motor, "-interaction=nonstopmode", "-halt-on-error",
               "-file-line-error", tex_work.name]
        try:
            r = subprocess.run(cmd, cwd=str(work), capture_output=True,
                               text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            resultado["razon"] = "Timeout (" + str(timeout) + "s) en pasada " + str(i)
            resultado["log"] = "\n".join(log_partes)
            resultado["duracion_s"] = round(time.time() - t0, 2)
            return resultado

        log_partes.append("=== Pasada " + str(i) + " (rc=" + str(r.returncode) + ") ===")
        out = r.stdout or ""
        log_partes.append(out[-6000:] if len(out) > 6000 else out)
        if r.stderr:
            log_partes.append("--- stderr ---")
            log_partes.append(r.stderr[-2000:])

        if r.returncode != 0 and i == 1:
            resultado["razon"] = "pdflatex fallo en pasada 1 (rc=" + str(r.returncode) + ")"
            resultado["log"] = "\n".join(log_partes)
            resultado["duracion_s"] = round(time.time() - t0, 2)
            return resultado

    # Verificar PDF generado
    pdf_work = work / (tex_work.stem + ".pdf")
    if not pdf_work.exists():
        resultado["razon"] = "El PDF no se genero (revisa el log)"
        resultado["log"] = "\n".join(log_partes)
        resultado["duracion_s"] = round(time.time() - t0, 2)
        return resultado

    # Copiar a dist/
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    pdf_out = DIST_DIR / ("tesis_" + lang + ".pdf")
    shutil.copy2(pdf_work, pdf_out)

    pdf_hash = _sha_file(pdf_out)

    cache[lang] = {
        "cache_key": clave,
        "pdf_sha256": pdf_hash,
        "timestamp_utc": _ts(),
    }
    _save_cache(cache)

    resultado.update({
        "status": "OK",
        "pdf": str(pdf_out.relative_to(BASE)),
        "sha256": pdf_hash,
        "log": "\n".join(log_partes),
        "duracion_s": round(time.time() - t0, 2),
    })
    return resultado


def compilar_all(force=False):
    return [compilar(lang, force=force) for lang in LANGS]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=LANGS, default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--doctor", action="store_true")
    ap.add_argument("--json", action="store_true",
                    help="Salida JSON para integracion")
    args = ap.parse_args()

    if args.doctor:
        info = doctor()
        if args.json:
            print(json.dumps(info, indent=2, ensure_ascii=False))
        else:
            print("Motor:              " + (info["motor"] or "NO DISPONIBLE"))
            print("Motores instalados: " + (str(info["motores_disponibles"]) or "ninguno"))
            print("src/:               " + str(info["src_existe"])
                  + " (" + str(len(info["tex_files"])) + " .tex)")
            print("dist/:              " + str(info["dist_existe"])
                  + " (" + str(len(info["pdfs_generados"])) + " .pdf)")
            if info.get("instalar"):
                print()
                print("Para instalar:")
                for k, v in info["instalar"].items():
                    print("  " + k + ": " + v)
        return

    if args.all:
        for r in compilar_all(force=args.force):
            if args.json:
                print(json.dumps(r, ensure_ascii=False))
            else:
                msg = "[" + r["lang"] + "] " + r["status"] + " — " + str(r["duracion_s"]) + "s"
                if r["pdf"]:
                    msg += " — " + r["pdf"]
                if r["razon"]:
                    msg += " — " + r["razon"]
                print(msg)
    elif args.lang:
        r = compilar(args.lang, force=args.force)
        if args.json:
            print(json.dumps(r, ensure_ascii=False))
        else:
            print("[" + r["lang"] + "] " + r["status"] + " — " + str(r["duracion_s"]) + "s")
            if r["pdf"]:
                print("  PDF: " + r["pdf"])
                print("  sha256: " + r["sha256"])
            if r["razon"]:
                print("  Razon: " + r["razon"])
            if r["status"] == "FAIL":
                print()
                print("Ultimas lineas del log:")
                print("\n".join(r["log"].splitlines()[-30:]))
                sys.exit(1)
    else:
        ap.error("Especifica --lang, --all o --doctor")


if __name__ == "__main__":
    main()