# -*- coding: utf-8 -*-
"""
FASE E.3-B — Certificacion y comparacion beta_obs vs beta_THU.
"""
import sys, json, hashlib, time
from pathlib import Path
import numpy as np

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
PP4 = LAB / "data" / "raw" / "planck_pr4"

TOTAL = 6
t0 = time.time()

def barra(i):
    pct = int(100 * i / TOTAL)
    filled = pct * 40 // 100
    return "=" * filled + "." * (40 - filled), pct

def paso(i, titulo, desc):
    bar, pct = barra(i)
    print()
    print("=" * 72)
    print(f"  PASO {i}/{TOTAL}  [{bar}]  {pct:3d}%")
    print(f"  {titulo}")
    print(f"  -> {desc}")
    print("=" * 72)
    sys.stdout.flush()

def sha256_file(path, chunk=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

# -- 1: Certificacion de archivos --
paso(1, "Certificacion SHA-256 de datasets",
     "Integridad de cada archivo")

archivos = [
    ("beta_planck_pr4.csv", PP4 / "beta_planck_pr4.csv"),
    ("NPIPE_CB_spectra.csv", PP4 / "cb_spectra" / "NPIPE_CB_spectra.csv"),
    ("PR3_CB_spectra.csv", PP4 / "cb_spectra" / "PR3_CB_spectra.csv"),
    ("NPIPE_alpha_CMB_cc.csv", PP4 / "cb_spectra" / "NPIPE_alpha_CMB_cc.csv"),
]

cert = []
for nombre, path in archivos:
    if path.exists():
        sha = sha256_file(path)
        size_kb = path.stat().st_size / 1024
        print(f"  {nombre}")
        print(f"    SHA-256: {sha}")
        print(f"    Tamano:  {size_kb:.2f} KB")
        cert.append({"nombre": nombre, "sha256": sha, "size_kb": size_kb})
    else:
        print(f"  {nombre}: NO EXISTE")

# -- 2: Leer beta observado --
paso(2, "Leer beta observado de Planck PR4",
     "beta_planck_pr4.csv")

import csv
with open(PP4 / "beta_planck_pr4.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    row = next(reader)
    beta_obs = float(row["valor"])
    sigma_obs = float(row["sigma"])
    unidad = row["unidad"]
    fuente = row["fuente"]
print(f"  beta_obs   = {beta_obs} {unidad}")
print(f"  sigma_obs  = {sigma_obs} {unidad}")
print(f"  Fuente CSV = {fuente}")

# -- 3: Leer beta teorico --
paso(3, "Leer beta teorico de THU-TBEA 5.0",
     "Programa completo, §10.5")

beta_thu = 0.3803
sigma_thu = 0.040
print(f"  beta_THU   = {beta_thu} grados")
print(f"  sigma_THU  = {sigma_thu} grados")
print(f"  Estatus: [P] condicional a completitud VL")

# -- 4: Comparacion estadistica --
paso(4, "Comparacion estadistica beta_obs vs beta_THU",
     "Tension en sigmas")

delta = beta_thu - beta_obs
sigma_comb = np.sqrt(sigma_thu**2 + sigma_obs**2)
tension_sigma = abs(delta) / sigma_comb

print(f"  beta_THU - beta_obs = {delta:.4f} grados")
print(f"  sigma_combinada     = {sigma_comb:.4f} grados")
print(f"  Tension             = {tension_sigma:.3f} sigma")
print()
if tension_sigma < 1:
    print(f"  VEREDICTO: COMPATIBLE a < 1 sigma")
elif tension_sigma < 2:
    print(f"  VEREDICTO: COMPATIBLE a < 2 sigma")
elif tension_sigma < 3:
    print(f"  VEREDICTO: TENSION MARGINAL (2-3 sigma)")
else:
    print(f"  VEREDICTO: TENSION SIGNIFICATIVA (> 3 sigma)")

# -- 5: Verificar espectros CB --
paso(5, "Verificar estructura de espectros CB",
     "NPIPE_CB_spectra.csv y PR3_CB_spectra.csv")

for nombre, path in [("NPIPE", PP4 / "cb_spectra" / "NPIPE_CB_spectra.csv"),
                     ("PR3", PP4 / "cb_spectra" / "PR3_CB_spectra.csv")]:
    data = np.genfromtxt(path, delimiter=",", comments="#", skip_header=0)
    print(f"\n  {nombre}_CB_spectra.csv")
    print(f"    Shape: {data.shape}")
    print(f"    L range: {data[1,0]:.0f}..{data[-1,0]:.0f}")
    print(f"    Columnas: L, Full, A x A, B x B, A x B")
    print(f"    CB(L=0) Full: {data[1,1]:.6e}")
    print(f"    CB(L=100) Full: {data[101,1]:.6e}")

# -- 6: Guardar certificacion --
paso(6, "Guardar certificacion y resumen",
     "JSON + reporte legible")

out_dir = LAB / "data" / "inventory"
out_dir.mkdir(parents=True, exist_ok=True)

cert_data = {
    "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "beta_thu": {"valor": beta_thu, "sigma": sigma_thu, "estatus": "[P]"},
    "beta_obs_planck_pr4": {
        "valor": beta_obs,
        "sigma": sigma_obs,
        "fuente": "Diego-Palazuelos et al. (2022), PRL 128, 091302",
        "doi": "10.1103/PhysRevLett.128.091302",
    },
    "tension_sigma": round(tension_sigma, 4),
    "archivos_certificados": cert,
}
cert_path = out_dir / "certificacion_birefringencia.json"
cert_path.write_text(json.dumps(cert_data, indent=2), encoding="utf-8")
print(f"  Certificacion guardada: {cert_path}")

t_total = time.time() - t0
print()
print("=" * 72)
print(f"  FIN E.3-B   (duracion: {t_total:.2f}s)")
print("=" * 72)
