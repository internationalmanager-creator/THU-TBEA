# -*- coding: utf-8 -*-
"""E.3-C3-D — Busqueda focalizada del SACC de ACT DR6."""
import sys, json, urllib.request, urllib.error, re
from pathlib import Path

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as e:
        return f"ERROR: {e}"

def head(url, timeout=15):
    req = urllib.request.Request(url, method="HEAD",
                                  headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            size = r.headers.get("Content-Length")
            return r.status, int(size) if size else None
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:
        return None, str(e)

# --- 1: HTML completo de la tabla pspipe, extraer contexto de 'sacc' ---
hdr("1. Contexto de 'sacc' en el HTML pspipe")

html = get("https://lambda.gsfc.nasa.gov/product/act/act_dr6.02/act_dr6.02_pspipe_prod_table.html")
if not html.startswith("ERROR"):
    # Buscar lineas que contengan 'sacc'
    for i, line in enumerate(html.splitlines()):
        if "sacc" in line.lower():
            # Limpiar HTML tags para legibilidad
            clean = re.sub(r'<[^>]+>', ' ', line)
            clean = re.sub(r'\s+', ' ', clean).strip()
            print(f"  L{i}: {clean[:200]}")
    # Extraer TODOS los hrefs absolutos y relativos
    hrefs = re.findall(r'href="([^"]+)"', html)
    print(f"\n  Total hrefs: {len(hrefs)}")
    # Filtrar por ficheros relevantes
    candidatos = [h for h in hrefs if any(k in h.lower()
                  for k in [".fits", ".txt", ".tar", "sacc", "cov", "pspipe"])]
    print(f"  Hrefs candidatos: {len(candidatos)}")
    for h in candidatos[:50]:
        print(f"    {h}")
else:
    print(f"  {html}")

# --- 2: Explorar act_dr6_mflike subdirs ---
hdr("2. Explorar subdirs de act_dr6_mflike")

for sub in ["act_dr6_mflike", "examples"]:
    api = f"https://api.github.com/repos/ACTCollaboration/act_dr6_mflike/contents/{sub}"
    print(f"\n  --- {sub} ---")
    data = get(api)
    if data.startswith("ERROR"):
        print(f"    {data}")
        continue
    try:
        items = json.loads(data)
        for item in items:
            print(f"    [{item.get('type','?'):4s}] {item.get('name','?'):50s} {item.get('size',0):10d} B")
    except Exception as e:
        print(f"    no JSON: {e}")

# --- 3: Leer README.rst de act_dr6_mflike (completo) ---
hdr("3. README.rst de act_dr6_mflike")
readme_url = "https://raw.githubusercontent.com/ACTCollaboration/act_dr6_mflike/main/README.rst"
txt = get(readme_url)
if not txt.startswith("ERROR"):
    lines = txt.splitlines()
    print(f"  ({len(lines)} lineas)")
    for l in lines[:120]:
        print(f"    {l}")
else:
    print(f"  {txt}")

# --- 4: Zenodo API — buscar SACC ---
hdr("4. Zenodo API — busqueda 'ACT DR6'")
zen = get("https://zenodo.org/api/records?q=ACT%20DR6%20SACC&size=5")
if not zen.startswith("ERROR"):
    try:
        data = json.loads(zen)
        hits = data.get("hits", {}).get("hits", [])
        print(f"  Resultados: {len(hits)}")
        for hit in hits:
            meta = hit.get("metadata", {})
            print(f"    title: {meta.get('title', '?')[:80]}")
            print(f"    doi:   {hit.get('doi', '?')}")
            print(f"    files: {len(hit.get('files', []))}")
            for f in hit.get("files", [])[:5]:
                print(f"      - {f.get('key', '?')} ({f.get('size', 0)} B)")
            print()
    except Exception as e:
        print(f"  Parse error: {e}")
else:
    print(f"  {zen}")

# --- 5: Verificar sacc tras instalacion ---
hdr("5. Verificar sacc instalado")
try:
    import sacc
    print(f"  sacc version: {sacc.__version__ if hasattr(sacc, '__version__') else '?'}")
except ImportError as e:
    print(f"  sacc aun falta: {e}")

# --- 6: Buscar 'dr6_data.fits' en GitHub global ---
hdr("6. Buscar 'dr6_data.fits' via GitHub code search API")
search_url = "https://api.github.com/search/code?q=dr6_data.fits+repo:ACTCollaboration"
# Nota: GitHub code search requiere auth token; puede fallar 401
data = get(search_url)
print(f"  Respuesta: {data[:300] if not data.startswith('ERROR') else data}")

# --- 7: Intentar paths alternativos del SACC ---
hdr("7. HEAD a paths alternativos")
alt = [
    "https://lambda.gsfc.nasa.gov/data/act/pspipe/act_dr6.02_sacc.fits",
    "https://lambda.gsfc.nasa.gov/data/act/pspipe/sacc/dr6_data_v1.0.fits",
    "https://lambda.gsfc.nasa.gov/data/act/pspipe/sacc/dr6_data_v1.fits",
    "https://lambda.gsfc.nasa.gov/data/act/pspipe/sacc/dr6_data.fits.gz",
    "https://lambda.gsfc.nasa.gov/data/act/pspipe/sacc/dr6_likelihood_data.fits",
    "https://lambda.gsfc.nasa.gov/data/act/pspipe/sacc/dr6_power_spectra.fits",
    "https://lambda.gsfc.nasa.gov/data/act/pspipe/sacc/dr6_cmb_only.fits",
    "https://lambda.gsfc.nasa.gov/data/act/pspipe/sacc/sacc_dr6.fits",
]
for url in alt:
    status, info = head(url)
    s = f"{info/1024/1024:.2f} MB" if isinstance(info, int) and info > 1024*1024 else \
        (f"{info/1024:.2f} KB" if isinstance(info, int) else "?")
    print(f"  [{status}]  {s:15s}  {url}")
