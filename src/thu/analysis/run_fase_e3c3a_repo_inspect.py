# -*- coding: utf-8 -*-
"""E.3-C3-A — Inspeccionar estructura del repo cosmic-birefringence."""
import sys
from pathlib import Path

REPO = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto\data\raw\cosmic-birefringence-planck-act")

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# --- 1: README ---
hdr("1. README principal")
for name in ["README.md", "README.rst", "README.txt", "readme.md"]:
    p = REPO / name
    if p.exists():
        print(f"  ({p.name}, {p.stat().st_size} bytes)")
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        for l in lines[:150]:
            print(f"    {l}")
        if len(lines) > 150:
            print(f"    ... ({len(lines)-150} lineas mas)")
        break
else:
    print("  No se encontro README")

# --- 2: requirements.txt ---
hdr("2. requirements.txt")
p = REPO / "requirements.txt"
if p.exists():
    for l in p.read_text(encoding="utf-8").splitlines():
        print(f"    {l}")

# --- 3: Estructura completa de .py ---
hdr("3. Scripts .py del repo")
pys = sorted(REPO.rglob("*.py"))
print(f"  Total: {len(pys)}")
for p in pys:
    rel = p.relative_to(REPO)
    print(f"    {str(rel):70s}  {p.stat().st_size:8d} B")

# --- 4: Contenido del directorio data/ ---
hdr("4. Directorio data/ (que archivos espera)")
data = REPO / "data"
if data.exists():
    for f in sorted(data.rglob("*")):
        if f.is_file():
            print(f"    {f.relative_to(REPO):70s}  {f.stat().st_size:8d} B")
        elif f.is_dir():
            print(f"    [DIR] {f.relative_to(REPO)}")

# --- 5: Configuracion / YAML ---
hdr("5. Archivos de configuracion (yaml, json, toml)")
for ext in [".yaml", ".yml", ".json", ".toml"]:
    for f in sorted(REPO.rglob(f"*{ext}")):
        print(f"    {f.relative_to(REPO):70s}  {f.stat().st_size:8d} B")

# --- 6: Buscar URLs de descarga en el codigo ---
hdr("6. URLs mencionadas en el codigo")
import re
urls = set()
for p in REPO.rglob("*"):
    if p.is_file() and p.suffix in [".py", ".md", ".rst", ".txt", ".yaml", ".toml"]:
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
            for m in re.findall(r'https?://[^\s"\'<>)]+', txt):
                urls.add(m)
        except Exception:
            pass
for u in sorted(urls):
    print(f"    {u}")

# --- 7: Palabras clave de datos ---
hdr("7. Busqueda de palabras clave (planck, act, npipe, masks, beams)")
for p in REPO.rglob("*.py"):
    txt = p.read_text(encoding="utf-8", errors="replace")
    for kw in ["npipe", "planck", "act_dr6", "actpol"]:
        n = txt.lower().count(kw)
        if n > 0:
            print(f"    {p.relative_to(REPO):60s}  '{kw}' x{n}")
