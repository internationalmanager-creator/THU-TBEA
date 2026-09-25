# -*- coding: utf-8 -*-
"""Verificacion 1b — Comprobar si arXiv:2509.13654 existe (multi-metodo)."""
import sys, urllib.request, urllib.parse, json, re
from pathlib import Path

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; research-verification)",
        "Accept": "application/atom+xml, application/json, text/html, */*"
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace"), r.status
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}: {e.reason}", e.code
    except Exception as e:
        return f"ERROR: {e}", None

# Metodo 1: arXiv API (HTTPS + headers correctos)
hdr("1. arXiv API — HTTPS con headers")
xml, status = fetch("https://export.arxiv.org/api/query?id_list=2509.13654")
print(f"  Status: {status}")
if status == 200:
    title = re.search(r"<title>(.*?)</title>", xml, re.DOTALL)
    abstract = re.search(r"<summary>(.*?)</summary>", xml, re.DOTALL)
    authors = re.findall(r"<name>(.*?)</name>", xml)
    published = re.search(r"<published>(.*?)</published>", xml)
    updated = re.search(r"<updated>(.*?)</updated>", xml)
    
    if title:
        print(f"  Titulo: {title.group(1).strip()}")
    if authors:
        print(f"  Autores ({len(authors)}): {', '.join(authors[:5])}")
        if len(authors) > 5:
            print(f"    ... ({len(authors)-5} mas)")
    if published:
        print(f"  Publicado: {published.group(1)}")
    if updated:
        print(f"  Actualizado: {updated.group(1)}")
    if abstract:
        ab = abstract.group(1).strip()
        print(f"\n  ABSTRACT:")
        print(f"  {ab}")
        
        # Buscar numeros relevantes
        nums = re.findall(r"\d+\.\d+", ab)
        print(f"\n  Numeros encontrados: {nums}")
else:
    print(f"  Respuesta: {xml[:500] if xml else 'vacio'}")

# Metodo 2: Pagina HTML directa
hdr("2. Pagina HTML arXiv abs/2509.13654")
html, status = fetch("https://arxiv.org/abs/2509.13654")
print(f"  Status: {status}")
if status == 200:
    # Verificar si es pagina de "not found" o de paper real
    if "no encontrado" in html.lower() or "not found" in html.lower() or "does not exist" in html.lower():
        print(f"  *** PAPER NO EXISTE ***")
    else:
        # Buscar titulo
        m = re.search(r'<meta name="citation_title" content="([^"]+)"', html)
        if m:
            print(f"  Titulo (meta): {m.group(1)}")
        # Buscar abstract
        m = re.search(r'<blockquote class="abstract[^"]*">(.*?)</blockquote>', html, re.DOTALL)
        if m:
            ab = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            print(f"  Abstract (primeros 500 chars):")
            print(f"  {ab[:500]}")
else:
    print(f"  Respuesta: {html[:500] if html else 'vacio'}")

# Metodo 3: ArXiv listing (a veces hay redirect)
hdr("3. Semantic Scholar API")
url_ss = "https://api.semanticscholar.org/graph/v1/paper/arXiv:2509.13654?fields=title,authors,abstract,year,externalIds"
html_ss, status_ss = fetch(url_ss)
print(f"  Status: {status_ss}")
if status_ss == 200:
    try:
        data = json.loads(html_ss)
        print(f"  Titulo: {data.get('title')}")
        print(f"  Year: {data.get('year')}")
        print(f"  Authors: {[a.get('name') for a in data.get('authors', [])]}")
        ab = data.get('abstract', '')
        if ab:
            print(f"  Abstract (primeros 300): {ab[:300]}")
    except json.JSONDecodeError:
        print(f"  No JSON: {html_ss[:300]}")
elif status_ss == 404:
    print(f"  *** Semantic Scholar: paper no encontrado ***")
else:
    print(f"  Respuesta: {html_ss[:300] if html_ss else 'vacio'}")

# Metodo 4: INSPIRE-HEP
hdr("4. INSPIRE-HEP API")
url_inspire = "https://inspirehep.net/api/arxiv/2509.13654"
html_insp, status_insp = fetch(url_inspire)
print(f"  Status: {status_insp}")
if status_insp == 200:
    try:
        data = json.loads(html_insp)
        md = data.get("metadata", {})
        print(f"  Titulo: {md.get('titles', [{}])[0].get('title', '?')}")
        print(f"  Autores: {[a.get('full_name') for a in md.get('authors', [])][:5]}")
        print(f"  Abstract (primeros 300): {md.get('abstracts', [{}])[0].get('value', '')[:300]}")
    except Exception as e:
        print(f"  Error parseando: {e}")
elif status_insp == 404:
    print(f"  *** INSPIRE-HEP: paper no encontrado ***")
else:
    print(f"  Respuesta: {html_insp[:300] if html_insp else 'vacio'}")

# Metodo 5: Buscar en disco local
hdr("5. Busqueda en disco local")
LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
patrones = ["2509.13654", "diego*palazuelos*2025", "act*dr6*biref*"]
for pat in patrones:
    found = list(LAB.rglob(pat))
    print(f"  '{pat}': {len(found)} archivos")
    for f in found[:5]:
        print(f"    {f.relative_to(LAB)}")

# Metodo 6: Verificar el PDF original que subiste
hdr("6. Verificar que el PDF subido tiene esos valores")
pdfs = list(LAB.rglob("*PROGRAMA*"))
print(f"  PDFs encontrados: {len(pdfs)}")
for p in pdfs:
    print(f"    {p}")

print()
print("=" * 72)
print("  INTERPRETACION")
print("=" * 72)
print("  Si 3+ metodos dicen 'no encontrado': el paper NO existe.")
print("  En ese caso, todos los numeros 'verificados' del PDF son")
print("  valores escritos por el autor (Erick) sin respaldo externo.")
print("=" * 72)
