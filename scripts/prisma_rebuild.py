"""Reconstruccion PRISMA usando la API publica de OpenAlex."""
import json
import urllib.request
import urllib.parse
import time
import re
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parents[1]
OUT_DIR = BASE / "registry" / "prisma" / "raw_exports"
OUT_DIR.mkdir(parents=True, exist_ok=True)

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

def consultar_openalex(query, per_page=200):
    """Consulta la API de OpenAlex con retry y pausa."""
    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per-page": str(per_page),
        "filter": "from_publication_date:2019-01-01,to_publication_date:2026-12-31"
    }
    full_url = url + "?" + urllib.parse.urlencode(params)
    print(f"  Consultando: {full_url}")
    
    req = urllib.request.Request(
        full_url,
        headers={
            "User-Agent": "THU-TBEA-PRISMA/1.0 (mailto:international_manager@comllcusa.com)"
        }
    )
    
    max_intentos = 3
    for intento in range(max_intentos):
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
            time.sleep(2)  # pausa entre requests
            return data
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"  [429] Rate limit. Esperando 5s (intento {intento+1}/{max_intentos})...")
                time.sleep(5)
            else:
                print(f"  ERROR HTTP {e.code}: {e.reason}")
                return {"results": []}
        except Exception as e:
            print(f"  ERROR: {e}")
            time.sleep(3)
    return {"results": []}

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
    print("  RECONSTRUCCION PRISMA - OPENALEX")
    print("=" * 60)
    
    queries = [
        "cosmic birefringence",
        "CMB polarization rotation",
        "parity violation CMB",
        "beta(z) tomography",
        "axion-like particles CMB"
    ]
    
    todos_los_papers = {}
    for q in queries:
        print(f"\n[QUERY] {q}")
        data = consultar_openalex(q)
        results = data.get("results", [])
        print(f"  Encontrados: {len(results)}")
        for r in results:
            doi = r.get("doi")
            if doi:
                todos_los_papers[doi] = r
    
    print(f"\n=== TOTAL UNICOS (por DOI): {len(todos_los_papers)} ===")
    
    fecha_str = datetime.now().strftime("%Y%m%d")
    
    # Guardar raw
    raw_file = OUT_DIR / f"openalex_raw_{fecha_str}.json"
    with open(raw_file, "w", encoding="utf-8") as fh:
        json.dump(list(todos_los_papers.values()), fh, indent=2, ensure_ascii=False)
    print(f"  Guardado: {raw_file}")
    
    # Procesar para extraer beta
    con_beta = []
    for doi, r in todos_los_papers.items():
        titulo = r.get("title", "") or ""
        inverted = r.get("abstract_inverted_index", {})
        abstract = reconstruir_abstract(inverted)
        anio = r.get("publication_year", 0)
        autores = [a.get("author", {}).get("display_name", "") for a in r.get("authorships", [])]
        beta, sigma = extraer_beta(abstract)
        if beta is not None:
            con_beta.append({
                "doi": doi,
                "titulo": titulo,
                "anio": anio,
                "autores": autores,
                "beta": beta,
                "sigma": sigma
            })
    
    print(f"\n=== CON BETA EXTRAIBLE: {len(con_beta)} ===")
    if con_beta:
        for m in con_beta:
            print(f"  {m['doi']} | {m['titulo'][:50]} | beta={m['beta']} +- {m['sigma']}")
    
    # Guardar extraction
    ext_file = OUT_DIR / f"openalex_extraction_{fecha_str}.json"
    with open(ext_file, "w", encoding="utf-8") as fh:
        json.dump(con_beta, fh, indent=2, ensure_ascii=False)
    print(f"  Guardado: {ext_file}")

if __name__ == "__main__":
    main()