import sys, time, json, hashlib, shutil
from pathlib import Path
from datetime import datetime, timezone

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
sys.path.insert(0, str(LAB / "src"))
OUT = LAB / "outputs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

from thu import figures as F

resultados = []
t0 = time.time()
total = len(F.GENERADORES)
print(f"=== Regenerando {total} figuras (leyendo dicts) ===\n")

for i, (nombre, fn) in enumerate(F.GENERADORES.items(), 1):
    t_start = time.time()
    try:
        result = fn()
        t_dur = time.time() - t_start

        if not isinstance(result, dict):
            resultados.append({
                "figura": nombre, "funcion": fn.__name__,
                "status": "formato_inesperado", "tipo": type(result).__name__
            })
            print(f"  [{i:2d}/{total}] {nombre:45s}  NO-DICT  {type(result).__name__}")
            continue

        # Extraer campos
        rname = result.get("name", nombre)
        rpath = result.get("path")
        rsha = result.get("sha256")

        # Copiar a outputs/figures para consolidar
        dst = None
        sha_final = rsha
        bytes_final = 0
        if rpath and Path(rpath).exists():
            src = Path(rpath)
            dst = OUT / src.name
            if src.resolve() != dst.resolve():
                shutil.copy2(src, dst)
            bytes_final = dst.stat().st_size
            if not sha_final:
                sha_final = hashlib.sha256(dst.read_bytes()).hexdigest()

        resultados.append({
            "figura": nombre, "funcion": fn.__name__,
            "archivo": dst.name if dst else None,
            "path_origen": str(rpath) if rpath else None,
            "bytes": bytes_final,
            "sha256": sha_final,
            "duracion_s": round(t_dur, 3),
            "status": "ok" if (dst and dst.exists()) else "sin_archivo"
        })
        icon = "OK " if (dst and dst.exists()) else "SIN"
        sz = f"{bytes_final/1024:.1f}KB" if bytes_final else "0KB"
        print(f"  [{i:2d}/{total}] {nombre:45s}  {icon}  {sz:>8}  {t_dur:.2f}s")

    except Exception as e:
        t_dur = time.time() - t_start
        resultados.append({
            "figura": nombre, "funcion": fn.__name__,
            "status": "error", "error": f"{type(e).__name__}: {str(e)[:150]}",
            "duracion_s": round(t_dur, 3)
        })
        print(f"  [{i:2d}/{total}] {nombre:45s}  ERROR  {type(e).__name__}")

t_total = time.time() - t0
ok = sum(1 for r in resultados if r["status"] == "ok")
sin = sum(1 for r in resultados if r["status"] == "sin_archivo")
err = sum(1 for r in resultados if r["status"] == "error")

mf = {
    "version": "2.0.0",
    "fecha": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "total_funciones": total,
    "figuras_ok": ok,
    "sin_archivo": sin,
    "errores": err,
    "duracion_total_s": round(t_total, 2),
    "detalle": resultados
}
mf_path = LAB / "data" / "inventory" / "figuras_manifest.json"
mf_path.write_text(json.dumps(mf, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"\n=== RESUMEN ===")
print(f"  Total funciones: {total}")
print(f"  Figuras OK:      {ok}")
print(f"  Sin archivo:     {sin}")
print(f"  Errores:         {err}")
print(f"  Duracion total:  {t_total:.1f}s")
print(f"  Manifest:        {mf_path}")

if err > 0:
    print(f"\n=== ERRORES ===")
    for r in resultados:
        if r["status"] == "error":
            print(f"  {r['figura']}: {r.get('error', '')[:120]}")
