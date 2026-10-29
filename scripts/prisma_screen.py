"""Filtra los papers de OpenAlex para el screening manual."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAW_FILE = BASE / "registry" / "prisma" / "raw_exports" / "openalex_raw_20261027.json"
OUT_FILE = BASE / "registry" / "prisma" / "raw_exports" / "openalex_screening_candidates.json"

# Cargar raw
with open(RAW_FILE, "r", encoding="utf-8") as fh:
    papers = json.load(fh)

# Filtrar por titulo relevante
candidatos = []
for p in papers:
    titulo = (p.get("title") or "").lower()
    # Excluir papers que claramente no son de birefringencia/CMB
    if any(kw in titulo for kw in ["birefringence", "polarization rotation", "parity violation", "parity-odd", "beta(z)"]):
        candidatos.append(p)

print(f"Total papers: {len(papers)}")
print(f"Candidatos por titulo: {len(candidatos)}")

# Guardar candidatos
with open(OUT_FILE, "w", encoding="utf-8") as fh:
    json.dump(candidatos, fh, indent=2, ensure_ascii=False)
print(f"Guardado: {OUT_FILE}")

# Mostrar primeros 20
for c in candidatos[:20]:
    doi = c.get("doi", "?")
    titulo = (c.get("title") or "?")[:80]
    anio = c.get("publication_year", "?")
    print(f"  {anio} | {doi} | {titulo}")