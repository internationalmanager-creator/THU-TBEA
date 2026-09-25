# -*- coding: utf-8 -*-
"""
FASE E.3-D1 — Verificar URLs ACT DR6 antes de descargar.
Regla: HEAD primero, descarga solo si 200 OK.
"""
import sys, urllib.request, urllib.error, json, time
from pathlib import Path

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
OUT = LAB / "data" / "raw" / "act_dr6"
OUT.mkdir(parents=True, exist_ok=True)

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

def head(url, timeout=20):
    """HEAD request. Retorna (status, size_bytes) o (None, None)."""
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

# --- URLs candidatas (a verificar, NO se asume que funcionan) ---
hdr("1. HEAD requests a URLs candidatas de ACT DR6")

candidatas = [
    # Dominio LAMBDA principal
    "https://lambda.gsfc.nasa.gov/product/act/act_dr6.02/",
    "https://lambda.gsfc.nasa.gov/product/act/",
    # Servidor de datos (nombre que usé de memoria)
    "https://gs66-vdclambda.ndc.nasa.gov/data/act/pspipe/spectra_and_cov/act_dr6.02_spectra_and_cov_xtra.tar.gz",
    "https://gs66-vdclambda.ndc.nasa.gov/data/act/pspipe/spectra_and_cov/act_dr6.02_spectra_and_cov_binning_50.tar.gz",
    # Variantes alternativas
    "https://lambda.gsfc.nasa.gov/data/act/pspipe/spectra_and_cov/act_dr6.02_spectra_and_cov_xtra.tar.gz",
    "https://lambda.gsfc.nasa.gov/data/act/pspipe/spectra_and_cov/act_dr6.02_spectra_and_cov_binning_50.tar.gz",
    # GitHub
    "https://github.com/ACTCollaboration/act_dr6_mflike",
    "https://github.com/ACTCollaboration/act_dr6_likelihood",
    "https://github.com/ACTCollaboration",
    # Zenodo (paper puede tener datos aquí)
    "https://zenodo.org/search?q=ACT+DR6+birefringence",
]

resultados = []
for url in candidatas:
    status, info = head(url)
    if isinstance(info, int):
        size_str = f"{info/1024/1024:.2f} MB" if info > 1024*1024 else f"{info/1024:.2f} KB"
    else:
        size_str = str(info) if info else "desconocido"
    ok = "OK" if status == 200 else "FALLA"
    print(f"  [{ok:5s}] {status}  {size_str:15s}  {url}")
    resultados.append({"url": url, "status": status, "size": size_str})

# --- 2: Buscar en el índice de LAMBDA ---
hdr("2. Explorar índice HTML de LAMBDA (si existe)")

def get_html(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as e:
        return f"ERROR: {e}"

for url in ["https://lambda.gsfc.nasa.gov/product/act/",
            "https://lambda.gsfc.nasa.gov/product/act/act_dr6.02/"]:
    print(f"\n  --- {url} ---")
    html = get_html(url)
    if html.startswith("ERROR"):
        print(f"    {html}")
        continue
    # Buscar links relevantes
    import re
    links = re.findall(r'href="([^"]+)"', html)
    relevantes = [l for l in links if any(k in l.lower() for k in
                  ["spectra", "cov", "eb", "tb", "biref", "dr6", "xtra"])]
    print(f"    Links relevantes encontrados: {len(relevantes)}")
    for l in relevantes[:30]:
        print(f"      {l}")
    if len(relevantes) > 30:
        print(f"      ... ({len(relevantes)-30} mas)")

# --- 3: Verificar si ACT collaboration tiene repositorio en GitHub ---
hdr("3. Verificar repos GitHub de ACT collaboration")

github_urls = [
    "https://api.github.com/repos/ACTCollaboration/act_dr6_mflike",
    "https://api.github.com/users/ACTCollaboration/repos",
    "https://api.github.com/orgs/ACTCollaboration/repos",
]

for url in github_urls:
    print(f"\n  --- {url} ---")
    html = get_html(url)
    if html.startswith("ERROR"):
        print(f"    {html}")
        continue
    try:
        data = json.loads(html)
        if isinstance(data, list):
            print(f"    Repos encontrados: {len(data)}")
            for repo in data[:20]:
                print(f"      {repo.get('name', '?')}: {repo.get('description', '')[:60]}")
        else:
            print(f"    name: {data.get('name', '?')}")
            print(f"    desc: {data.get('description', '')[:100]}")
            print(f"    size: {data.get('size', '?')} KB")
            print(f"    html: {data.get('html_url', '?')}")
    except json.JSONDecodeError:
        print(f"    no es JSON, longitud HTML: {len(html)}")

# --- 4: Guardar reporte ---
hdr("4. Guardar reporte de verificación")
report = {
    "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "urls_verificadas": resultados,
}
report_path = OUT / "reporte_verificacion_urls.json"
report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                       encoding="utf-8")
print(f"  Reporte guardado: {report_path}")

print()
print("="*72)
print("  CONCLUSION")
print("="*72)
print("  Con este reporte:")
print("  - Si alguna URL da status 200 -> descargamos ESA")
print("  - Si ninguna funciona -> buscamos via API LAMBDA/GitHub")
print("  - NO descargamos a ciegas URLs inventadas")
