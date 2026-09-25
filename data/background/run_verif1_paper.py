# -*- coding: utf-8 -*-
"""Verificacion 1 — Leer paper ACT DR6 birefringence (arXiv:2509.13654)."""
import sys, urllib.request, json, re
from pathlib import Path

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# 1: Consultar arXiv API
hdr("1. Consultar arXiv API para 2509.13654")

url = "http://export.arxiv.org/api/query?id_list=2509.13654"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=30) as r:
    xml = r.read().decode("utf-8", errors="replace")

print(f"  Respuesta: {len(xml)} bytes")

# Extraer titulo
title_match = re.search(r"<title>(.*?)</title>", xml, re.DOTALL)
if title_match:
    print(f"  Titulo: {title_match.group(1).strip()}")

# Extraer abstract
abstract_match = re.search(r"<summary>(.*?)</summary>", xml, re.DOTALL)
if abstract_match:
    abstract = abstract_match.group(1).strip()
    print(f"\n  Abstract:")
    print(f"  {abstract}")

# Extraer autores
authors = re.findall(r"<name>(.*?)</name>", xml)
if authors:
    print(f"\n  Autores ({len(authors)}):")
    for a in authors[:5]:
        print(f"    {a}")
    if len(authors) > 5:
        print(f"    ... ({len(authors)-5} mas)")

# 2: Buscar valor beta en abstract
hdr("2. Extraer valor beta del abstract")

if abstract_match:
    abstract = abstract_match.group(1)
    # Buscar patrones beta
    patterns = [
        r"[βb]eta\s*=\s*([0-9.]+)\s*[°d]",
        r"([0-9.]+)\s*[°d]\s*±\s*([0-9.]+)\s*[°d]",
        r"birefringence.*?([0-9.]+)\s*±\s*([0-9.]+)",
        r"angle.*?([0-9.]+)\s*±\s*([0-9.]+)",
        r"([0-9.]+)\s*deg.*?([0-9.]+)\s*deg",
    ]
    for pat in patterns:
        matches = re.findall(pat, abstract, re.IGNORECASE)
        if matches:
            print(f"  Patron: {pat}")
            for m in matches[:5]:
                print(f"    {m}")
    
    # Buscar numeros
    nums = re.findall(r"0\.[0-9]{2,3}", abstract)
    print(f"\n  Numeros 0.XX en abstract: {set(nums)}")

# 3: Buscar paper en disco (por si existe)
hdr("3. Buscar paper en disco")
LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
for f in LAB.rglob("*2509*"):
    print(f"  {f.relative_to(LAB)}")
for f in LAB.rglob("*diego*palazuelos*"):
    print(f"  {f.relative_to(LAB)}")
for f in LAB.rglob("*act_dr6*biref*"):
    print(f"  {f.relative_to(LAB)}")
