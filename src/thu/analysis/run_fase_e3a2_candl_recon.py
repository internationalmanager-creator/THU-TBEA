# -*- coding: utf-8 -*-
"""FASE E.3-A2 — Reconocimiento SPT3G_D1_BB_lite_v0 + candl_data README."""
import sys, os, json
from pathlib import Path

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
PKG = LAB / "data" / "raw" / "candl_data" / "candl_data"
ROOT = LAB / "data" / "raw" / "candl_data"

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# -- 1: README de candl_data (raiz del repo) --
hdr("1. Buscar README.md del repo candl_data")
for p in ROOT.rglob("README*"):
    print(f"  {p.relative_to(ROOT)}")
    if p.stat().st_size < 200000:
        try:
            txt = p.read_text(encoding="utf-8")
            lines = txt.splitlines()
            print(f"  ({len(lines)} lineas, primeras 100)")
            for l in lines[:100]:
                print(f"    {l}")
            if len(lines) > 100:
                print(f"    ... ({len(lines)-100} mas)")
        except Exception as e:
            print(f"  no se pudo leer: {e}")

# -- 2: Listar SPT3G_D1_BB_lite_v0 completo --
hdr("2. SPT3G_D1_BB_lite_v0 — listado completo")
BB_DIR = PKG / "SPT3G_D1_BB_lite_v0"
if not BB_DIR.exists():
    print(f"  ERROR: {BB_DIR} no existe")
    sys.exit(1)
for f in sorted(BB_DIR.rglob("*")):
    if f.is_file():
        rel = f.relative_to(BB_DIR)
        print(f"  {str(rel):60s}  {f.stat().st_size/1024:10.2f} KB")

# -- 3: YAML descriptor --
hdr("3. Contenido de los .yaml (descriptor del likelihood)")
for y in sorted(BB_DIR.rglob("*.yaml")):
    print(f"\n  --- {y.relative_to(BB_DIR)} ---")
    try:
        txt = y.read_text(encoding="utf-8")
        for l in txt.splitlines()[:80]:
            print(f"    {l}")
        if len(txt.splitlines()) > 80:
            print(f"    ... ({len(txt.splitlines())-80} mas)")
    except Exception as e:
        print(f"    error: {e}")

# -- 4: .py de ejemplo --
hdr("4. Scripts .py de ejemplo en candl_data")
for py in sorted(ROOT.rglob("*.py")):
    print(f"\n  --- {py.relative_to(ROOT)} ---")
    try:
        txt = py.read_text(encoding="utf-8")
        for l in txt.splitlines()[:60]:
            print(f"    {l}")
        if len(txt.splitlines()) > 60:
            print(f"    ... ({len(txt.splitlines())-60} mas)")
    except Exception as e:
        print(f"    error: {e}")

# -- 5: Primeras lineas de los .txt de SPT3G_D1_BB_lite_v0 --
hdr("5. Primeras lineas de .txt en SPT3G_D1_BB_lite_v0")
for t in sorted(BB_DIR.rglob("*.txt"))[:8]:
    print(f"\n  --- {t.relative_to(BB_DIR)} ---")
    try:
        with open(t, encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh):
                if i >= 5: 
                    print(f"    ...")
                    break
                print(f"    {line.rstrip()}")
    except Exception as e:
        print(f"    error: {e}")

# -- 6: Buscar EB / TB en nombre de archivos o contenido --
hdr("6. Busqueda de EB/TB en nombres y contenido")
hits_name = []
hits_content = []
for f in BB_DIR.rglob("*"):
    if f.is_file() and f.name.upper().find("EB") >= 0 or (f.is_file() and f.name.upper().find("TB") >= 0):
        hits_name.append(f)
    if f.is_file() and f.suffix in [".txt", ".yaml"]:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            if "EB" in content or "TB" in content or "eb" in content or "tb" in content:
                hits_content.append(f)
        except Exception:
            pass

print(f"  Archivos con 'EB'/'TB' en nombre: {len(hits_name)}")
for h in hits_name:
    print(f"    {h.relative_to(BB_DIR)}")
print(f"  Archivos con 'EB'/'TB' en contenido: {len(hits_content)}")
for h in hits_content[:10]:
    print(f"    {h.relative_to(BB_DIR)}")

# -- 7: Resumen --
hdr("7. Resumen y siguiente paso")
print(f"  SPT3G_D1_BB_lite_v0 existe: {(PKG / 'SPT3G_D1_BB_lite_v0').exists()}")
print(f"  Contiene EB/TB: {'SI' if hits_name or hits_content else 'NO detectado en este escaneo'}")
print(f"  Paquete candl instalado: ", end="")
try:
    import candl
    print(f"SI (version {getattr(candl, '__version__', '?')})")
except ImportError as e:
    print(f"NO ({e})")
