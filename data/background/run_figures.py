import sys, time, traceback, json, hashlib
from pathlib import Path
from datetime import datetime, timezone

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
sys.path.insert(0, str(LAB / "src"))

OUT = LAB / "outputs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

from thu import figures as F

# Capturar figuras previas
prev = set(p.name for p in OUT.glob("*.png"))

resultados = []
t0 = time.time()

total = len(F.GENERADORES)
print(f"=== Regenerando {total} figuras ===\n")

for i, (nombre, fn) in enumerate(F.GENERADORES.items(), 1):
    t_start = time.time()
    try:
        result = fn()
        t_dur = time.time() - t_start

        # Buscar PNGs generados por esta funcion
        # Heuristica: archivos modificados en los ultimos t_dur + 2 segundos
        nuevos = []
        for p in OUT.glob("*.png"):
            if p.stat().st_mtime >= t_start - 1:
                nuevos.append(p)

        if nuevos:
            for p in nuevos:
                sha = hashlib.sha256(p.read_bytes()).hexdigest()
                resultados.append({
                    "figura": nombre,
                    "funcion": fn.__name__,
                    "archivo": p.name,
                    "bytes": p.stat().st_size,
                    "sha256": sha,
                    "duracion_s": round(t_dur, 3),
                    "status": "ok"
                })
            print(f"  [{i:2d}/{total}] {nombre:45s}  OK  {len(nuevos)} PNG  {t_dur:.2f}s")
        else:
            resultados.append({
                "figura": nombre,
                "funcion": fn.__name__,
                "archivo": None,
                "bytes": 0,
                "sha256": None,
                "duracion_s": round(t_dur, 3),
                "status": "sin_png",
                "result_type": type(result).__name__
            })
            print(f"  [{i:2d}/{total}] {nombre:45s}  SIN-PNG  (dict con keys: {list(result.keys())[:3]})")

    except Exception as e:
        t_dur = time.time() - t_start
        err = f"{type(e).__name__}: {str(e)[:200]}"
        resultados.append({
            "figura": nombre,
            "funcion": fn.__name__,
            "archivo": None,
            "bytes": 0,
            "sha256": None,
            "duracion_s": round(t_dur, 3),
            "status": "error",
            "error": err
        })
        print(f"  [{i:2d}/{total}] {nombre:45s}  ERROR  {err[:80]}")

t_total = time.time() - t0
ok = sum(1 for r in resultados if r["status"] == "ok")
sin = sum(1 for r in resultados if r["status"] == "sin_png")
err = sum(1 for r in resultados if r["status"] == "error")

# Manifest
mf = {
    "version": "1.0.0",
    "fecha": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "total_funciones": total,
    "figuras_ok": ok,
    "sin_png": sin,
    "errores": err,
    "duracion_total_s": round(t_total, 2),
    "detalle": resultados
}
mf_path = LAB / "data" / "inventory" / "figuras_manifest.json"
mf_path.write_text(json.dumps(mf, indent=2), encoding="utf-8")

print(f"\n=== RESUMEN ===")
print(f"  Total funciones: {total}")
print(f"  Figuras OK:      {ok}")
print(f"  Sin PNG:         {sin}")
print(f"  Errores:         {err}")
print(f"  Duracion total:  {t_total:.1f}s")
print(f"  Manifest:        {mf_path}")

if err > 0:
    print(f"\n=== PRIMEROS ERRORES ===")
    for r in resultados:
        if r["status"] == "error":
            print(f"  {r['figura']}: {r.get('error', '')[:100]}")

if sin > 0:
    print(f"\n=== SIN PNG (funciones que no escriben en outputs/figures) ===")
    for r in resultados:
        if r["status"] == "sin_png":
            print(f"  {r['figura']}  ->  funcion {r['funcion']}")
