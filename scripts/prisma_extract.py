"""Extrae beta de los 253 candidatos PRISMA."""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CAND_FILE = BASE / "registry" / "prisma" / "raw_exports" / "openalex_screening_candidates.json"
OUT_CON_BETA = BASE / "registry" / "prisma" / "raw_exports" / "prisma_con_beta.json"
OUT_SIN_BETA = BASE / "registry" / "prisma" / "raw_exports" / "prisma_sin_beta.json"

def reconstruir_abstract(inverted_index):
    """OpenAlex devuelve abstracts como inverted index. Esto los reconstruye."""
    if not inverted_index:
        return ""
    palabras = []
    for palabra, posiciones in inverted_index.items():
        for pos in posiciones:
            palabras.append((pos, palabra))
    palabras.sort()
    return " ".join([p[1] for p in palabras])

def extraer_beta(texto):
    """Intenta extraer beta y sigma de un abstract en texto plano."""
    if not texto:
        return None, None
    patrones = [
        r"beta\s*=\s*([0-9.]+)\s*(?:\+/-|\+-|\u00b1)\s*([0-9.]+)",
        r"birefringence\s*angle\s*(?:of\s*)?([0-9.]+)\s*(?:\+/-|\+-|\u00b1)\s*([0-9.]+)",
        r"([0-9.]+)\s*(?:\+/-|\+-|\u00b1)\s*([0-9.]+)\s*(?:deg|degree)"
    ]
    for patron in patrones:
        match = re.search(patron, texto, re.IGNORECASE)
        if match:
            return float(match.group(1)), float(match.group(2))
    return None, None

def main():
    print("=" * 60)
    print("  EXTRACCION BETA DE 253 CANDIDATOS")
    print("=" * 60)
    
    with open(CAND_FILE, "r", encoding="utf-8") as fh:
        candidatos = json.load(fh)
    
    print(f"Candidatos cargados: {len(candidatos)}")
    
    con_beta = []
    sin_beta = []
    
    for p in candidatos:
        doi = p.get("doi", "?")
        titulo = p.get("title", "") or ""
        anio = p.get("publication_year", 0)
        autores = [a.get("author", {}).get("display_name", "") for a in p.get("authorships", [])]
        inverted = p.get("abstract_inverted_index", {})
        abstract = reconstruir_abstract(inverted)
        
        beta, sigma = extraer_beta(abstract)
        if beta is not None:
            con_beta.append({
                "doi": doi,
                "titulo": titulo,
                "anio": anio,
                "autores": autores,
                "beta": beta,
                "sigma": sigma,
                "abstract": abstract[:300]
            })
        else:
            sin_beta.append({
                "doi": doi,
                "titulo": titulo,
                "anio": anio,
                "razon": "Sin beta numerico en abstract"
            })
    
    print(f"\n=== CON BETA EXTRAIBLE: {len(con_beta)} ===")
    for m in con_beta:
        print(f"  {m['anio']} | {m['doi']} | beta={m['beta']} ± {m['sigma']} | {m['titulo'][:50]}")
    
    print(f"\n=== SIN BETA EXTRAIBLE: {len(sin_beta)} ===")
    
    with open(OUT_CON_BETA, "w", encoding="utf-8") as fh:
        json.dump(con_beta, fh, indent=2, ensure_ascii=False)
    print(f"\nGuardado: {OUT_CON_BETA}")
    
    with open(OUT_SIN_BETA, "w", encoding="utf-8") as fh:
        json.dump(sin_beta, fh, indent=2, ensure_ascii=False)
    print(f"Guardado: {OUT_SIN_BETA}")

if __name__ == "__main__":
    main()