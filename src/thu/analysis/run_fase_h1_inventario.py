# -*- coding: utf-8 -*-
"""H.1 — Inventario de documentos y datos duros."""
import sys, json, hashlib, time
from pathlib import Path

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
REG = LAB / "registry" / "thu"
OUT = LAB / "data" / "inventory"
REG.mkdir(parents=True, exist_ok=True)

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

def sha256_file(path, chunk=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()

# --- 1: Inventario de documentos ---
hdr("1. Inventario de documentos THU-TBEA")

documentos = [
    {
        "id": "doc_01_unificacion",
        "titulo": "Unificación por la Geometría",
        "fecha": "2025-11-29",
        "version_teorica": "pre-v3.0",
        "contenido": "Verificación computacional (torsión, espectro, g-2)",
        "formato": "PDF (subido)",
    },
    {
        "id": "doc_02_tbea",
        "titulo": "Teoría de Bucles Espirales Áureos (TBEA)",
        "fecha": "2026-05-21",
        "version_teorica": "TBEA",
        "contenido": "Marco unificado: espiralones, áureones, modos Higgs",
        "formato": "PDF (subido)",
    },
    {
        "id": "doc_03_thu_integrada",
        "titulo": "THU-TBEA Teoría (integrada)",
        "fecha": "2026-05-29",
        "version_teorica": "post-v3.0",
        "contenido": "THU-TBEA integrada + sistema acoplado Ψ-Φ",
        "formato": "PDF (subido)",
    },
    {
        "id": "doc_04_mvsp",
        "titulo": "MVSP — Validación Matemática",
        "fecha": "2026-07-28",
        "version_teorica": "v3.0 (paralelo)",
        "contenido": "Validación matemática, física, epistemológica",
        "formato": "PDF (subido)",
    },
    {
        "id": "doc_05_thuv3sp",
        "titulo": "THUV3SP — Documento Maestro 3.0",
        "fecha": "2026 (sin fecha)",
        "version_teorica": "v3.0",
        "contenido": "Documento maestro THU-TBEA 3.0",
        "formato": "PDF (subido)",
    },
    {
        "id": "doc_06_tesis_v4",
        "titulo": "Tesis_THU_SP_8 — Tesis 4.0",
        "fecha": "2026 (sin fecha)",
        "version_teorica": "v4.0",
        "contenido": "Tesis completa THU-TBEA 4.0",
        "formato": "PDF (subido)",
    },
    {
        "id": "doc_07_programa_v5",
        "titulo": "PROGRAMA_COMPLETO_v5.0",
        "fecha": "2026-09-21",
        "version_teorica": "v5.0",
        "contenido": "Programa completo THU-TBEA 5.0 (última versión)",
        "formato": "PDF (subido)",
    },
]

print(f"  Total documentos: {len(documentos)}")
print()
print(f"  {'ID':30s}  {'Fecha':12s}  {'Versión':12s}")
for d in documentos:
    print(f"  {d['id']:30s}  {d['fecha']:12s}  {d['version_teorica']:12s}")

# --- 2: Inventario de datos duros en disco ---
hdr("2. Inventario de datos duros en disco")

datos = [
    ("data/raw/act_dr6/act_dr6.02_spectra_and_cov_xtra.tar.gz", "ACT DR6 EB/TB xtra"),
    ("data/raw/act_dr6/act_dr6.02_spectra_and_cov_binning_50.tar.gz", "ACT DR6 binning"),
    ("data/raw/planck_pr4/beta_planck_pr4.csv", "Planck PR4 beta"),
    ("data/raw/planck_pr4/cb_spectra/NPIPE_CB_spectra.csv", "Planck PR4 CB spectra"),
    ("data/raw/planck_pr4/cb_spectra/PR3_CB_spectra.csv", "Planck PR3 CB spectra"),
    ("data/raw/desi_dr2/desi_gaussian_bao_ALL_GCcomb_mean.txt", "DESI DR2 BAO mean"),
    ("data/raw/desi_dr2/desi_gaussian_bao_ALL_GCcomb_cov.txt", "DESI DR2 BAO cov"),
    ("data/raw/pantheon_plus/Pantheon+SH0ES.dat", "Pantheon+ SNe"),
    ("data/raw/pantheon_plus/Pantheon+SH0ES_STAT+SYS.cov", "Pantheon+ cov"),
    ("data/raw/act_dr6_packages/data/ACTDR6MFLike/v1.0/dr6_data.fits", "ACT DR6 SACC oficial"),
]

print(f"  {'Archivo':60s}  {'Estado':10s}  {'MB':10s}")
for rel, desc in datos:
    p = LAB / rel
    if p.exists():
        size_mb = p.stat().st_size / 1024 / 1024
        print(f"  {rel:60s}  OK  {size_mb:10.2f}")
    else:
        print(f"  {rel:60s}  FALTA")

# --- 3: Inventario de resultados intermedios ---
hdr("3. Resultados intermedios en data/inventory/")

for f in sorted((LAB / "data" / "inventory").glob("*.json")):
    size_kb = f.stat().st_size / 1024
    print(f"  {f.name:50s}  {size_kb:8.2f} KB")

# --- 4: Registro en registry/thu/ ---
hdr("4. Registro en registry/thu/")

for f in sorted(REG.glob("*.json")):
    size_kb = f.stat().st_size / 1024
    print(f"  {f.name:50s}  {size_kb:8.2f} KB")

# --- 5: Guardar inventario consolidado ---
hdr("5. Guardar inventario")

inventario = {
    "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "documentos": documentos,
    "datos_duros": [
        {"path": rel, "descripcion": desc, "existe": (LAB / rel).exists(),
         "size_mb": (LAB / rel).stat().st_size / 1024/1024 if (LAB / rel).exists() else None}
        for rel, desc in datos
    ],
    "preguntas_abiertas": [
        "¿Familia THU-TBEA cosmológica y familia TBEA/THU-TBEA unificada son la misma teoría o dos?",
        "¿Cuál es la versión canónica: v5.0 (cosmológica) o THU_TBEA_Teoria (unificada)?",
        "¿Los modos Higgs 77/48/29/18 GeV de TBEA son predicción de THU-TBEA o de TBEA?",
        "¿El sistema acoplado Ψ-Φ de THU_TBEA_Teoria está en v5.0?",
    ],
}

out = OUT / "inventario_documentos.json"
out.write_text(json.dumps(inventario, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"  Guardado: {out}")

print()
print("="*72)
print("  INVENTARIO COMPLETO")
print("="*72)
