"""Calcula el promedio inverso-variance de las 5 mediciones A."""
import json
import csv
from pathlib import Path
import math

BASE = Path(__file__).resolve().parents[1]
CSV_FILE = BASE / "registry" / "prisma" / "prisma_2026.csv"
OUT_FILE = BASE / "registry" / "prisma" / "beta_analysis_honest.json"

# Leer CSV
with open(CSV_FILE, "r", encoding="utf-8") as fh:
    reader = csv.DictReader(fh)
    rows = list(reader)

# Filtrar las incluidas en sintesis
incluidas = [r for r in rows if r["incluido_sintesis"] == "si"]

print(f"Mediciones incluidas: {len(incluidas)}")
print()

# Calcular promedio inverso-variance
sum_w = 0.0
sum_wx = 0.0
for r in incluidas:
    beta = float(r["beta"])
    sigma = float(r["sigma"])
    w = 1.0 / (sigma ** 2)
    sum_w += w
    sum_wx += w * beta

beta_avg = sum_wx / sum_w
sigma_avg = math.sqrt(1.0 / sum_w)

print(f"beta promedio = {beta_avg:.4f} +- {sigma_avg:.4f}")
print()

# Calcular tension contra THU (0.3803 +- 0.038)
beta_thu = 0.3803
sigma_thu = 0.038

tension = abs(beta_thu - beta_avg) / math.sqrt(sigma_thu**2 + sigma_avg**2)
print(f"Tension vs THU-TBEA (0.3803 +- 0.038): {tension:.2f} sigma")
print()

# Calcular tambien el promedio de las 7 A (con o sin sigma)
todas_A = [r for r in rows if r["categoria"] == "A"]
print(f"Mediciones categoria A (7, incluyendo sin sigma y duplicados):")
for r in todas_A:
    sigma_str = r["sigma"] if r["sigma"] else "None"
    print(f"  {r['doi']} | beta={r['beta']} | sigma={sigma_str} | incluido={r['incluido_sintesis']}")

# Guardar resultado
resultado = {
    "fecha": "2026-10-27",
    "mediciones_incluidas": len(incluidas),
    "beta_promedio": round(beta_avg, 4),
    "sigma_promedio": round(sigma_avg, 4),
    "beta_thu": beta_thu,
    "sigma_thu": sigma_thu,
    "tension_sigma": round(tension, 2),
    "mediciones": [
        {"doi": r["doi"], "beta": float(r["beta"]), "sigma": float(r["sigma"]), "razon": r["razon_clasificacion"]}
        for r in incluidas
    ]
}

with open(OUT_FILE, "w", encoding="utf-8") as fh:
    json.dump(resultado, fh, indent=2, ensure_ascii=False)

print(f"\nGuardado: {OUT_FILE}")