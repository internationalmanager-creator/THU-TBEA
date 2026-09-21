import json
from pathlib import Path
from collections import Counter

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
mf = json.loads((LAB / "data/inventory/figuras_manifest.json").read_text(encoding="utf-8"))

# Contar nombres de archivo duplicados
nombres = [r["archivo"] for r in mf["detalle"] if r.get("archivo")]
counts = Counter(nombres)

print(f"  Funciones ejecutadas: {mf['total_funciones']}")
print(f"  Figuras OK:           {mf['figuras_ok']}")
print(f"  Nombres unicos:       {len(set(nombres))}")
print()
print("  --- Nombres duplicados (mismo archivo, >1 funcion) ---")
dup_encontrados = False
for n, c in counts.items():
    if c > 1:
        dup_encontrados = True
        funcs = [r["figura"] for r in mf["detalle"] if r.get("archivo") == n]
        print(f"  {n}  ({c} funciones)")
        for f in funcs:
            print(f"      - {f}")
if not dup_encontrados:
    print("  (ninguno)")

print()
print("  --- Funciones sin archivo ---")
sin_archivo = [r for r in mf["detalle"] if not r.get("archivo")]
if sin_archivo:
    for r in sin_archivo:
        print(f"  {r['figura']}  status={r['status']}  path_origen={r.get('path_origen')}")
else:
    print("  (ninguna)")

print()
print("  --- Muestra de paths origen (5 primeras) ---")
for r in mf["detalle"][:5]:
    print(f"  {r['figura']:45s}  path_origen={r.get('path_origen')}")
