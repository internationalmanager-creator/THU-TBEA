"""Muestra las 47 mediciones con beta extraidas por Harness."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
JSON_FILE = BASE / "registry" / "prisma" / "raw_exports" / "prisma_extraccion_llm.json"

with open(JSON_FILE, "r", encoding="utf-8") as fh:
    data = json.load(fh)

con_beta = data.get("con_beta", [])
sin_beta = data.get("sin_beta", [])

print(f"Con beta: {len(con_beta)}")
print(f"Sin beta: {len(sin_beta)}")
print()
print("=" * 100)
print("PRIMERAS 20 MEDICIONES CON BETA:")
print("=" * 100)

for i, m in enumerate(con_beta[:20], 1):
    doi = m.get("doi", "?")
    beta = m.get("beta", "?")
    sigma = m.get("sigma", "?")
    titulo = (m.get("titulo") or "?")[:70]
    print(f"{i:2d}. {doi}")
    print(f"    beta={beta} | sigma={sigma} | {titulo}")
    print()