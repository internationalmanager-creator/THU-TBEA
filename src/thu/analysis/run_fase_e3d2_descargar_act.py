# -*- coding: utf-8 -*-
"""
FASE E.3-D2 — Listar repos ACT (fix) + descargar tar.gz + inspeccionar EB/TB.
"""
import sys, urllib.request, urllib.error, json, time, tarfile, hashlib, re
from pathlib import Path

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
OUT = LAB / "data" / "raw" / "act_dr6"
OUT.mkdir(parents=True, exist_ok=True)

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

def download(url, dest, timeout=120):
    """Descarga con progreso simple."""
    print(f"  Descargando: {url}")
    print(f"  Destino:     {dest}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
        dest.write_bytes(data)
        print(f"  OK: {len(data)/1024:.2f} KB")
        return True
    except Exception as e:
        print(f"  FALLA: {e}")
        return False

def sha256_file(path, chunk=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()

# --- 1: Listar TODOS los repos de ACT (fix None) ---
hdr("1. Listar TODOS los repos de la org ACTCollaboration")

url = "https://api.github.com/orgs/ACTCollaboration/repos?per_page=100"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=30) as r:
    repos = json.loads(r.read().decode())

print(f"  Total repos: {len(repos)}")
print()
for repo in repos:
    name = repo.get("name") or "?"
    desc = repo.get("description") or "(sin descripcion)"
    size_kb = repo.get("size", 0)
    print(f"  {name:40s}  {size_kb:7d} KB  {desc[:60]}")

# Buscar repos con keywords birefringence/beta/eb/tb/alpha
print()
print("  --- Repos candidatos a birefringence ---")
keywords = ["biref", "beta", "ebtb", "eb_tb", "alpha", "polar", "spectra"]
candidatos = []
for repo in repos:
    name_lower = (repo.get("name") or "").lower()
    desc_lower = (repo.get("description") or "").lower()
    if any(k in name_lower or k in desc_lower for k in keywords):
        print(f"    {repo.get('name')}: {repo.get('html_url')}")
        candidatos.append(repo)

# --- 2: Descargar los dos tar.gz ---
hdr("2. Descarga de tar.gz de ACT DR6 spectra_and_cov")

descargas = [
    ("act_dr6.02_spectra_and_cov_xtra.tar.gz",
     "https://lambda.gsfc.nasa.gov/data/act/pspipe/spectra_and_cov/act_dr6.02_spectra_and_cov_xtra.tar.gz"),
    ("act_dr6.02_spectra_and_cov_binning_50.tar.gz",
     "https://lambda.gsfc.nasa.gov/data/act/pspipe/spectra_and_cov/act_dr6.02_spectra_and_cov_binning_50.tar.gz"),
]

cert = []
for fname, url in descargas:
    dest = OUT / fname
    if dest.exists():
        print(f"\n  {fname} ya existe, saltando descarga")
    else:
        print()
        ok = download(url, dest)
        if not ok:
            continue
    sha = sha256_file(dest)
    size_kb = dest.stat().st_size / 1024
    print(f"  SHA-256: {sha}")
    cert.append({"archivo": fname, "sha256": sha, "size_kb": round(size_kb,2), "url": url})

# --- 3: Extraer y listar contenidos ---
hdr("3. Extraer tar.gz e inspeccionar")

for fname, _ in descargas:
    tgz = OUT / fname
    if not tgz.exists():
        continue
    extract_dir = OUT / fname.replace(".tar.gz", "")
    extract_dir.mkdir(exist_ok=True)
    print(f"\n  --- {fname} ---")
    try:
        with tarfile.open(tgz, "r:gz") as tar:
            members = tar.getmembers()
            print(f"  Miembros: {len(members)}")
            for m in members:
                size_kb = m.size / 1024
                print(f"    {m.name:70s}  {size_kb:10.2f} KB")
            # Extraer
            tar.extractall(extract_dir)
            print(f"  Extraido a: {extract_dir}")
    except Exception as e:
        print(f"  FALLA: {e}")

# --- 4: Buscar EB/TB en los archivos extraidos ---
hdr("4. Busqueda de EB/TB en los archivos extraidos")

hits = []
for f in OUT.rglob("*"):
    if not f.is_file():
        continue
    name_upper = f.name.upper()
    # Token EB o TB entre separadores
    if re.search(r'(?:^|[_\-\s\.])(EB|TB)(?:[_\-\s\.]|$)', name_upper):
        hits.append(f)

print(f"  Archivos con 'EB'/'TB' en nombre: {len(hits)}")
for h in hits[:30]:
    print(f"    {h.relative_to(OUT)}")

# Tambien buscar en contenido de .yaml, .txt, .md
print()
print("  Busqueda en contenido (.yaml, .txt, .md):")
content_hits = []
for f in OUT.rglob("*"):
    if not f.is_file() or f.suffix.lower() not in [".yaml", ".txt", ".md", ".rst", ".json"]:
        continue
    if f.stat().st_size > 1_000_000:
        continue
    try:
        txt = f.read_text(encoding="utf-8", errors="replace")
        # Buscar palabras como tokens (evitar "deber", "obtener", etc.)
        if re.search(r'\b(eb|tb)\b', txt, re.IGNORECASE):
            content_hits.append(f)
    except Exception:
        pass

print(f"  Archivos con token 'eb'/'tb' en contenido: {len(content_hits)}")
for h in content_hits[:20]:
    print(f"    {h.relative_to(OUT)}")

# --- 5: Guardar certificacion ---
hdr("5. Guardar certificacion de descargas")
cert_data = {
    "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "archivos_descargados": cert,
    "repos_act_total": len(repos),
    "repos_candidatos_biref": [r.get("name") for r in candidatos],
    "archivos_con_EB_TB_en_nombre": [str(h.relative_to(OUT)) for h in hits],
}
cert_path = OUT / "certificacion_act_dr6.json"
cert_path.write_text(json.dumps(cert_data, indent=2, ensure_ascii=False),
                     encoding="utf-8")
print(f"  Certificacion: {cert_path}")

print()
print("="*72)
print("  FIN E.3-D2")
print("="*72)
