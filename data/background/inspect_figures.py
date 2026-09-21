import sys, inspect
from pathlib import Path

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
sys.path.insert(0, str(LAB / "src"))

from thu import figures as F

print("=== 1. Estructura de GENERADORES ===")
print(f"  Total entradas: {len(F.GENERADORES)}")
first_key = list(F.GENERADORES.keys())[0]
first_val = F.GENERADORES[first_key]
print(f"  Primera key: {first_key!r}")
print(f"  Tipo de valor: {type(first_val).__name__}")
if isinstance(first_val, tuple):
    print(f"  Contenido de la tupla: {[type(x).__name__ for x in first_val]}")
elif callable(first_val):
    print(f"  Callable: {first_val.__name__}")
else:
    print(f"  Valor: {first_val!r}")

print("\n=== 2. Prímeras 5 entradas ===")
for i, (k, v) in enumerate(list(F.GENERADORES.items())[:5]):
    print(f"  {i+1}. {k!r} -> {v!r}")

print("\n=== 3. Firmas de las primeras 5 funciones fig_* ===")
nombres = sorted([n for n in dir(F) if n.startswith("fig_")])
print(f"  Total fig_* encontradas: {len(nombres)}")
for n in nombres[:5]:
    fn = getattr(F, n)
    try:
        sig = inspect.signature(fn)
        print(f"  {n}{sig}")
    except Exception as e:
        print(f"  {n} — ERROR: {e}")

print("\n=== 4. Directorio de salida (buscando figuras existentes) ===")
candidatos = [
    LAB / "outputs",
    LAB / "figures",
    LAB / "outputs" / "figures",
    LAB / "docs" / "figures",
]
for c in candidatos:
    if c.exists():
        n = len(list(c.rglob("*.png")))
        mb = sum(f.stat().st_size for f in c.rglob("*.png")) / 1024 / 1024
        print(f"  {c.relative_to(LAB)}: {n} PNG, {mb:.1f} MB")

print("\n=== 5. Test-run de la primera funcion ===")
try:
    fn_name = nombres[0]
    fn = getattr(F, fn_name)
    sig = inspect.signature(fn)
    params = list(sig.parameters.keys())
    print(f"  {fn_name}{sig}")
    print(f"  Parámetros: {params}")
    if len(params) == 0:
        print("  Llamando sin args...")
        result = fn()
        print(f"  Resultado tipo: {type(result).__name__}")
    else:
        print(f"  NO test-run: requiere {len(params)} argumentos")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
