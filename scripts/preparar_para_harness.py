"""Prepara los 251 papers para que Harness extraiga beta."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAW_FILE = BASE / "registry" / "prisma" / "raw_exports" / "openalex_raw_20261027.json"
SIN_BETA_FILE = BASE / "registry" / "prisma" / "raw_exports" / "prisma_sin_beta.json"
OUT_FILE = BASE / "registry" / "prisma" / "raw_exports" / "para_harness.json"

def reconstruir_abstract(inverted_index):
    if not inverted_index:
        return ""
    palabras = []
    for palabra, posiciones in inverted_index.items():
        for pos in posiciones:
            palabras.append((pos, palabra))
    palabras.sort()
    return " ".join([p[1] for p in palabras])

# Cargar raw (tiene los abstracts completos)
with open(RAW_FILE, "r", encoding="utf-8") as fh:
    raw_papers = json.load(fh)

# Cargar los que no tienen beta
with open(SIN_BETA_FILE, "r", encoding="utf-8") as fh:
    sin_beta = json.load(fh)

# Mapear por DOI
raw_por_doi = {p.get("doi"): p for p in raw_papers}

# Construir lista simplificada
papers_para_harness = []
for item in sin_beta:
    doi = item.get("doi")
    raw = raw_por_doi.get(doi)
    if not raw:
        continue
    inverted = raw.get("abstract_inverted_index", {})
    abstract = reconstruir_abstract(inverted)
    papers_para_harness.append({
        "doi": doi,
        "titulo": item.get("titulo", ""),
        "anio": item.get("anio", 0),
        "abstract": abstract[:1500]  # truncar para no exceder contexto
    })

with open(OUT_FILE, "w", encoding="utf-8") as fh:
    json.dump(papers_para_harness, fh, indent=2, ensure_ascii=False)

print(f"Preparados {len(papers_para_harness)} papers para Harness")
print(f"Guardado en: {OUT_FILE}")