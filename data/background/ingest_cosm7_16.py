import json, sys
from pathlib import Path

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
sys.path.insert(0, str(LAB / "src"))
import db_manager

db_manager.inicializar_db()
inp = LAB / "data" / "inputs"

nuevos = []
for cid in sorted(p.stem for p in inp.glob("COSM-*.json")):
    try:
        num = int(cid.split("-")[1])
        if num < 7:
            continue
    except:
        continue
    nuevos.append(cid)

print(f"  Entidades nuevas a ingresar: {len(nuevos)}")

for cid in nuevos:
    d = json.loads((inp / f"{cid}.json").read_text(encoding="utf-8"))
    try:
        db_manager.guardar_entidad({
            "id": d["id"],
            "categoria": d["categoria"],
            "valor_principal": 1.0,
            "incertidumbre": 0.0,
            "unidad": d["unidad"],
            "fuente": d["fuente"],
            "origen": d["origen"],
            "estatus": d["estatus"],
            "notas": d["notas"],
        })
        p = d["provenance"]
        r = db_manager.guardar_provenance({
            "id_entidad": d["id"],
            "cita_completa": p["cita_completa"],
            "doi": p.get("doi") or None,
            "tipo_publicacion": p["tipo_publicacion"],
            "ano": int(p["ano"]),
            "instrumento": p["instrumento"],
            "condiciones": p["condiciones"],
            "reproducibilidad": p["reproducibilidad"],
            "extracto": p["extracto"],
            "hash_pdf": p.get("hash_pdf") or None,
            "fecha_descarga_utc": p.get("fecha_descarga_utc") or None,
            "notas": p.get("notas") or "",
        })
        db_manager.registrar_evento(
            tipo="dataset_ingestado",
            descripcion=f"{d['id']} ({d['titulo']}) ingestado",
            entidad_id=d["id"],
            payload={
                "fuente": d["fuente"],
                "hash_raw": p.get("hash_pdf") or "",
                "dataset_path": d["dataset_ref"]["path"],
                "n_files": d["dataset_ref"]["files_count"],
                "bytes": d["dataset_ref"]["bytes_total"],
                "provenance_hash": r["hash_registro"],
            },
        )
        print(f"  OK {cid} -> {d['titulo'][:60]}")
    except Exception as e:
        print(f"  ERROR {cid}: {e}")

# Verificacion
ok, idx, eid = db_manager.verificar_cadena_eventos()
print()
print(f"Cadena eventos: {'OK' if ok else f'ROTA idx={idx}'}")
print(f"Total entidades: {len(db_manager.listar_entidades())}")
print(f"Total eventos: {len(db_manager.listar_eventos())}")
