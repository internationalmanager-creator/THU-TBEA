import ast, sys
from pathlib import Path

FIG = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto\src\thu\figures.py")
src = FIG.read_text(encoding="utf-8")

try:
    tree = ast.parse(src)
except SyntaxError as e:
    print(f"SYNTAX ERROR pre-fix: linea {e.lineno}: {e.text}")
    sys.exit(1)

removidos = 0
# Iterar desde el final para no invalidar offsets
for node in reversed(tree.body):
    if not isinstance(node, ast.Expr):
        continue
    v = node.value
    if not isinstance(v, ast.Call):
        continue
    f = v.func
    if not (isinstance(f, ast.Attribute) and f.attr == "update"):
        continue
    if not (isinstance(f.value, ast.Name) and f.value.id == "GENERADORES"):
        continue
    start = node.lineno - 1
    end = node.end_lineno
    lines = src.split("\n")
    print(f"  Orphan: lineas {node.lineno}..{node.end_lineno} ({end-start} lineas)")
    print(f"  Primera: {lines[start][:80]}")
    print(f"  Ultima:  {lines[end-1][:80]}")
    new_lines = lines[:start] + lines[end:]
    # limpiar lineas vacias consecutivas
    while start < len(new_lines) and new_lines[start].strip() == "":
        del new_lines[start]
    src = "\n".join(new_lines)
    removidos += 1

if removidos == 0:
    print("  No se encontro orphan update")
else:
    try:
        ast.parse(src)
        FIG.write_text(src, encoding="utf-8")
        print(f"  OK: {removidos} orphan removido, sintaxis valida post-fix")
    except SyntaxError as e:
        print(f"  ERROR post-fix linea {e.lineno}: {e.text}")
        sys.exit(1)
