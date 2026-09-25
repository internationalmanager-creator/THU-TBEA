# -*- coding: utf-8 -*-
"""FASE E.3-A3 — Buscar datos EB/TB en disco (raw + extracted)."""
import sys, re
from pathlib import Path

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# Directorios prioritarios según handoff
prioritarios = [
    LAB / "data" / "raw" / "pred_alpha_lm",
    LAB / "data" / "raw" / "pred_birefringence",
    LAB / "data" / "raw" / "birefringence",
    LAB / "data" / "extracted" / "birefringence",
    LAB / "data" / "raw" / "cmb_tools",
    LAB / "data" / "raw" / "litebird",
    LAB / "data" / "raw" / "planck_pr4",
]

hdr("A. Contenido de directorios prioritarios (recursivo, completo)")
for d in prioritarios:
    print(f"\n--- {d.relative_to(LAB)} ---")
    print(f"  Existe: {d.exists()}")
    if not d.exists():
        continue
    total_kb = 0
    n_files = 0
    for f in sorted(d.rglob("*")):
        if f.is_file():
            rel = f.relative_to(d)
            size_kb = f.stat().st_size / 1024
            total_kb += size_kb
            n_files += 1
            print(f"    {str(rel):70s}  {size_kb:10.2f} KB")
    print(f"  TOTAL: {n_files} archivos, {total_kb/1024:.2f} MB")

# B. Búsqueda global con regex CORREGIDO (word boundaries)
hdr("B. Busqueda global de archivos con 'EB' o 'TB' como tokens")
# Patrones: '_EB_', '_TB_', '-EB-', ' EB ', 'EB.', '.EB', '^EB', 'TB$' etc
patterns = [
    re.compile(r'(?:^|[_\-\s])EB(?:[_\-\s\.]|$)'),
    re.compile(r'(?:^|[_\-\s])TB(?:[_\-\s\.]|$)'),
    re.compile(r'(?:^|[_\-\s])EBTB'),
    re.compile(r'(?:^|[_\-\s])TBEB'),
    re.compile(r'biref', re.IGNORECASE),
    re.compile(r'alphalm|alpha_lm|alpha-lm', re.IGNORECASE),
]

hits = []
search_roots = [LAB / "data" / "raw", LAB / "data" / "extracted"]
for root in search_roots:
    if not root.exists():
        continue
    for f in root.rglob("*"):
        if not f.is_file():
            continue
        name = f.name
        relstr = str(f.relative_to(LAB))
        for pat in patterns:
            if pat.search(name) or pat.search(relstr):
                hits.append((relstr, f.stat().st_size / 1024))
                break

print(f"  Total archivos coincidentes: {len(hits)}")
for rel, kb in sorted(hits)[:100]:
    print(f"    {rel:75s}  {kb:10.2f} KB")
if len(hits) > 100:
    print(f"    ... ({len(hits)-100} mas)")

# C. Búsqueda dentro de archivos pequeños (.txt, .yaml, .json, .md)
hdr("C. Busqueda en CONTENIDO de archivos pequenos (< 500 KB)")
# Limitar a .txt .yaml .json .md .rst .py
ext_ok = {".txt", ".yaml", ".yml", ".json", ".md", ".rst", ".py", ".toml"}
content_hits = []
for root in search_roots:
    if not root.exists():
        continue
    for f in root.rglob("*"):
        if not f.is_file() or f.suffix.lower() not in ext_ok:
            continue
        if f.stat().st_size > 500_000:
            continue
        try:
            txt = f.read_text(encoding="utf-8", errors="replace").lower()
        except Exception:
            continue
        # Buscar palabras especificas como tokens
        if (" eb" in txt and " tb" in txt) or "birefringence" in txt or "alphalm" in txt.replace(" ", ""):
            content_hits.append(str(f.relative_to(LAB)))

print(f"  Archivos con 'birefringence' / 'alphalm' / (eb y tb) en contenido: {len(content_hits)}")
for h in sorted(content_hits)[:50]:
    print(f"    {h}")

# D. Resumen
hdr("D. Resumen")
print(f"  Directorios prioritarios explorados: {sum(1 for d in prioritarios if d.exists())}/{len(prioritarios)}")
print(f"  Archivos con 'EB'/'TB'/'biref'/'alphalm' en nombre: {len(hits)}")
print(f"  Archivos con 'birefringence'/'alphalm' en contenido: {len(content_hits)}")
print()
print("  Si hay archivos EB/TB -> siguiente: revisar formato y aplicar modelo beta")
print("  Si NO hay -> siguiente: obtener ACT DR6 alpha-lm del repo publico")
