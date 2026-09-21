"""Registra una entidad completa desde JSON (v2).

Emite eventos al log cronografico en cada paso relevante.

Pipeline (idempotente, anti-cortes):
    1. Lee data/inputs/{id}.json
    2. Valida campos obligatorios
    3. Escribe data/provenance/{id}_{fuente}.md
    4. UPSERT en SQLite (entidades + provenance + progreso)
    5. Emite evento cronografico
    6. Regenera data/entidades.csv desde DB

Uso:
    python src/registrar_entidad.py CAT-001
    python src/registrar_entidad.py CAT-001 --dry-run
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
import db_manager
from tqdm import tqdm

BASE = Path(__file__).parent.parent
INPUTS_DIR = BASE / "data" / "inputs"
PROVENANCE_DIR = BASE / "data" / "provenance"
CSV_PATH = BASE / "data" / "entidades.csv"

CAMPOS_OBLIGATORIOS = ["id", "categoria", "valor_principal", "incertidumbre",
                        "unidad", "fuente", "origen", "estatus"]
PROVENANCE_OBLIGATORIOS = ["cita_completa", "tipo_publicacion", "ano",
                            "instrumento", "condiciones", "extracto"]
CATEGORIAS_VALIDAS = {"cosmologia", "geofisica", "biologia",
                       "neurofisiologia", "cuantica", "antropologia",
                       "otros", "test"}
ESTATUS_VALIDOS = {"D", "P", "F", "A"}
ORIGENES_VALIDOS = {"observado", "generado", "inferido", "simulado"}


def _ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cargar_input(eid):
    path = INPUTS_DIR / f"{eid}.json"
    if not path.exists():
        raise FileNotFoundError(f"No existe {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validar(d):
    err = []
    for c in CAMPOS_OBLIGATORIOS:
        if c not in d or d[c] in (None, ""):
            err.append(f"Falta campo: {c}")
    if "provenance" not in d:
        err.append("Falta seccion 'provenance'")
    else:
        for c in PROVENANCE_OBLIGATORIOS:
            if c not in d["provenance"] or d["provenance"][c] in (None, ""):
                err.append(f"Falta provenance: {c}")
    if d.get("categoria") and d["categoria"] not in CATEGORIAS_VALIDAS:
        err.append(f"Categoria invalida: {d['categoria']}")
    if d.get("estatus") and d["estatus"] not in ESTATUS_VALIDOS:
        err.append(f"Estatus invalido: {d['estatus']}")
    if d.get("origen") and d["origen"] not in ORIGENES_VALIDOS:
        err.append(f"Origen invalido: {d['origen']}")
    try:
        if float(d["valor_principal"]) <= 0:
            err.append("valor_principal debe ser > 0")
    except (TypeError, ValueError):
        err.append("valor_principal no numerico")
    if err:
        raise ValueError("Errores:\n  - " + "\n  - ".join(err))


def escribir_ficha(d):
    p = d["provenance"]
    slug = d["fuente"].lower().replace(" ", "_")
    path = PROVENANCE_DIR / f"{d['id']}_{slug}.md"
    contenido = f"""# {d['id']} - {d.get('titulo', d['categoria'])}

## Identificacion
- ID: {d['id']}
- Categoria: {d['categoria']}
- Origen: {d['origen']}
- Estatus: [{d['estatus']}]

## Valor registrado
- Valor: {d['valor_principal']} {d['unidad']}
- Incertidumbre: {d['incertidumbre']} {d['unidad']}

## Fuente primaria
- Cita: {p['cita_completa']}
- DOI: {p.get('doi') or 'N/A'}
- Tipo: {p['tipo_publicacion']}
- Ano: {p['ano']}

## Metodo
- Instrumento: {p['instrumento']}
- Condiciones: {p['condiciones']}
- Reproducibilidad: {p.get('reproducibilidad') or 'N/A'}

## Extracto
> {p['extracto']}

## Hash del documento fuente
- SHA-256: {p.get('hash_pdf') or 'pendiente'}
- Fecha descarga: {p.get('fecha_descarga_utc') or 'pendiente'}

## Notas
{d.get('notas') or '(sin notas)'}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(contenido)
    return path


def regenerar_csv(db_path=None):
    filas = db_manager.listar_entidades(db_path)
    if not filas:
        return
    df = pd.DataFrame(filas)
    cols = ["id", "categoria", "valor_principal", "incertidumbre", "unidad",
            "fuente", "origen", "estatus", "notas"]
    df = df[[c for c in cols if c in df.columns]]
    df.to_csv(CSV_PATH, index=False, lineterminator="\n", encoding="utf-8")


def registrar(eid, dry_run=False, db_path=None):
    print(f"=== Registrando {eid} ===")
    with tqdm(total=7, desc="Pipeline", ncols=80) as pbar:
        datos = cargar_input(eid)
        pbar.update(1); pbar.set_postfix_str("leido")

        validar(datos)
        pbar.update(1); pbar.set_postfix_str("validado")

        if dry_run:
            print("  [dry-run] No se escribe nada")
            return

        ficha = escribir_ficha(datos)
        pbar.update(1); pbar.set_postfix_str("ficha escrita")

        db_manager.guardar_entidad({
            "id": datos["id"], "categoria": datos["categoria"],
            "valor_principal": float(datos["valor_principal"]),
            "incertidumbre": float(datos["incertidumbre"]),
            "unidad": datos["unidad"], "fuente": datos["fuente"],
            "origen": datos["origen"], "estatus": datos["estatus"],
            "notas": datos.get("notas", ""),
        }, db_path)
        pbar.update(1); pbar.set_postfix_str("entidad UPSERT")

        p = datos["provenance"]
        r = db_manager.guardar_provenance({
            "id_entidad": datos["id"], "cita_completa": p["cita_completa"],
            "doi": p.get("doi"), "tipo_publicacion": p["tipo_publicacion"],
            "ano": int(p["ano"]), "instrumento": p["instrumento"],
            "condiciones": p["condiciones"],
            "reproducibilidad": p.get("reproducibilidad"),
            "extracto": p["extracto"], "hash_pdf": p.get("hash_pdf"),
            "fecha_descarga_utc": p.get("fecha_descarga_utc"),
            "notas": p.get("notas"),
        }, db_path)
        pbar.update(1); pbar.set_postfix_str(f"prov v{r['version']}")

        db_manager.actualizar_progreso(datos["id"], "completado",
                                        f"Registrado {_ts()}", db_path)
        regenerar_csv(db_path)
        pbar.update(1); pbar.set_postfix_str("csv regenerado")

        db_manager.registrar_evento(
            tipo="entidad_registrada",
            descripcion=f"Entidad {datos['id']} registrada (categoria={datos['categoria']})",
            entidad_id=datos["id"],
            payload={
                "provenance_version": r["version"],
                "provenance_hash": r["hash_registro"],
                "valor_principal": datos["valor_principal"],
                "unidad": datos["unidad"],
                "origen": datos["origen"],
                "estatus": datos["estatus"],
            },
            db_path=db_path,
        )
        pbar.update(1); pbar.set_postfix_str("evento logueado")

    resumen = db_manager.obtener_resumen(db_path)
    print(f"\n=== OK: {eid} registrado ===")
    print(f"Total: {resumen['total']} | Eventos: {resumen['eventos']} | "
          f"Schema v{resumen['schema_version']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("eid")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--db", default=None)
    args = ap.parse_args()
    db_manager.inicializar_db(args.db)
    try:
        registrar(args.eid, dry_run=args.dry_run, db_path=args.db)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()