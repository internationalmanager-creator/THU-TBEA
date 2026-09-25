# -*- coding: utf-8 -*-
"""E.3-C3-C — Verificar disponibilidad del SACC oficial de ACT DR6."""
import sys, json, urllib.request, urllib.error
from pathlib import Path

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

def head(url, timeout=20):
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

# --- 1: Dependencias ---
hdr("1. Verificar dependencias Python")
for mod in ["sacc", "emcee", "corner", "camb", "numpy", "scipy", "astropy"]:
    try:
        m = __import__(mod)
        v = getattr(m, "__version__", "?")
        print(f"  {mod:12s} OK  version {v}")
    except ImportError as e:
        print(f"  {mod:12s} FALTA: {e}")

# --- 2: URLs candidatas del SACC ---
hdr("2. HEAD requests a URLs candidatas del SACC")
candidatas = [
    # Variantes del nombre
    "https://lambda.gsfc.nasa.gov/data/act/pspipe/sacc/dr6_data.fits",
    "https://lambda.gsfc.nasa.gov/data/act/pspipe/sacc/act_dr6_data.fits",
    "https://lambda.gsfc.nasa.gov/data/act/pspipe/act_dr6.02_dr6_data.fits",
    "https://lambda.gsfc.nasa.gov/data/act/pspipe/sacc/act_dr6.02_sacc.fits",
    "https://lambda.gsfc.nasa.gov/data/act/sacc/dr6_data.fits",
    # Página índice oficial
    "https://lambda.gsfc.nasa.gov/product/act/act_dr6.02/act_dr6.02_pspipe_prod_table.html",
    # Variante Princeton (visto antes)
    "https://phy-act1.princeton.edu/public/snaess/actpol/dr6/",
]

for url in candidatas:
    status, info = head(url)
    if isinstance(info, int):
        s = f"{info/1024/1024:.2f} MB" if info > 1024*1024 else f"{info/1024:.2f} KB"
    else:
        s = str(info)[:40] if info else "?"
    print(f"  [{status}]  {s:15s}  {url}")

# --- 3: Verificar repo act_dr6_mflike ---
hdr("3. Explorar repo act_dr6_mflike (¿viene con SACC?)")
api_url = "https://api.github.com/repos/ACTCollaboration/act_dr6_mflike/contents"
req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        contents = json.loads(r.read().decode())
    print(f"  Total items: {len(contents)}")
    for item in contents:
        name = item.get("name", "?")
        type_ = item.get("type", "?")
        size = item.get("size", 0)
        print(f"    [{type_:4s}] {name:50s} {size:10d} B")
except Exception as e:
    print(f"  ERROR: {e}")

# --- 4: Descargar HTML de la tabla de productos pspipe ---
hdr("4. HTML de la tabla de productos (buscar 'sacc')")
url = "https://lambda.gsfc.nasa.gov/product/act/act_dr6.02/act_dr6.02_pspipe_prod_table.html"
try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read().decode("utf-8", errors="replace")
    print(f"  HTML len: {len(html)}")
    import re
    # Buscar links que contengan 'sacc' o 'fits'
    links = re.findall(r'href="([^"]+)"', html)
    relevantes = [l for l in links if any(k in l.lower() for k in ["sacc", ".fits", "cov"])]
    print(f"  Links con 'sacc' o '.fits' o 'cov': {len(relevantes)}")
    for l in relevantes[:30]:
        print(f"    {l}")
    # Buscar texto 'sacc'
    if "sacc" in html.lower():
        print(f"  'sacc' aparece en el HTML")
    else:
        print(f"  'sacc' NO aparece en el HTML")
except Exception as e:
    print(f"  ERROR: {e}")

# --- 5: Resumen ---
hdr("5. Resumen y decision")
print("  Si sacc esta instalado y el SACC se descarga:")
print("    -> E.3-C3-D: correr MASK='act_dr6' con el pipeline oficial")
print("    -> Tiempo estimado MCMC: horas (70000 pasos, ~50 walkers)")
print()
print("  Si el SACC no esta disponible publicamente:")
print("    -> contactar a J.R. Eskilt (j.r.eskilt@astro.uio.no) por email")
print("    -> o usar E.3-C2 como resultado final")
