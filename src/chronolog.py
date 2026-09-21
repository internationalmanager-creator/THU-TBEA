"""Registro cronografico con cadena de hashes SHA-256 (append-only).

Modelo:
    Evento_i = (ts_i, tipo_i, entidad_i, desc_i, payload_i, prev_hash_i, hash_i)
    hash_i   = SHA256(ts_i | tipo_i | entidad_i | desc_i | payload_i | hash_{i-1})
    hash_0   = SHA256("GENESIS")

Propiedades:
    - Cualquier alteracion en Evento_k invalida hash_k y todos los posteriores.
    - El hash del ultimo evento es la "raiz" firmable.
    - Exportacion a Markdown preserva la cadena.

Uso:
    python src/chronolog.py registrar <tipo> "<descripcion>" [--entidad ID]
    python src/chronolog.py verificar
    python src/chronolog.py exportar
    python src/chronolog.py listar [--limit N]
"""
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE / "src"))
import db_manager

CHRONO_MD = BASE / "registry" / "chronolog.md"


def _ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def registrar(tipo, descripcion, entidad_id=None, payload=None, db_path=None):
    h = db_manager.registrar_evento(tipo, descripcion, entidad_id, payload, db_path)
    print(f"Evento registrado. hash={h[:16]}...")
    return h


def verificar(db_path=None):
    ok, idx, eid = db_manager.verificar_cadena_eventos(db_path)
    if ok:
        n = len(db_manager.listar_eventos(db_path))
        print(f"CADENA OK ({n} eventos, integridad verificada)")
        return True
    print(f"CADENA ROTA en indice {idx} (evento id={eid})", file=sys.stderr)
    return False

# === PARTE 2 se agrega a continuacion ===

def exportar(path=None, db_path=None):
    eventos = db_manager.listar_eventos(db_path)
    path = Path(path or CHRONO_MD)
    path.parent.mkdir(parents=True, exist_ok=True)

    lineas = [
        "# Chronolog — Registro Cronografico Encadenado",
        "",
        "> Generado automaticamente por `src/chronolog.py`. **NO editar a mano.**",
        "> Cada entrada incluye el hash del evento y el hash del evento previo.",
        "> Alterar cualquier linea invalida toda la cadena posterior.",
        "",
        f"- **Eventos:** {len(eventos)}",
        f"- **Generado:** {_ts()}",
        f"- **Algoritmo:** SHA-256 sobre `(ts|tipo|entidad|desc|payload|prev_hash)`",
        "",
        "---",
        "",
    ]
    for ev in tqdm(eventos, desc="Exportando", ncols=80):
        ts = ev["timestamp_utc"]
        tipo = ev["tipo"]
        eid = ev["entidad_id"] or "—"
        lineas.append(f"## `{ts}` · **{tipo}** · `{eid}`")
        lineas.append("")
        lineas.append(ev["descripcion"])
        lineas.append("")
        if ev["payload_json"]:
            lineas.append("```json")
            lineas.append(ev["payload_json"])
            lineas.append("```")
            lineas.append("")
        lineas.append(f"- `prev_hash` = `{ev['prev_hash']}`")
        lineas.append(f"- `hash`      = `{ev['hash']}`")
        lineas.append("")
        lineas.append("---")
        lineas.append("")
    path.write_text("\n".join(lineas), encoding="utf-8", newline="\n")
    print(f"Exportado: {path}")
    return path


def listar(limit=None, db_path=None):
    for ev in db_manager.listar_eventos(db_path, limit=limit):
        eid = (ev["entidad_id"] or "-")[:12]
        print(f"{ev['id']:>5} {ev['timestamp_utc']} {ev['tipo']:<18} "
              f"{eid:<12} {ev['descripcion'][:60]}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("registrar")
    r.add_argument("tipo")
    r.add_argument("descripcion")
    r.add_argument("--entidad", default=None)

    sub.add_parser("verificar")
    sub.add_parser("exportar")
    lp = sub.add_parser("listar")
    lp.add_argument("--limit", type=int, default=None)

    args = ap.parse_args()
    if args.cmd == "registrar":
        registrar(args.tipo, args.descripcion, args.entidad)
    elif args.cmd == "verificar":
        if not verificar():
            sys.exit(1)
    elif args.cmd == "exportar":
        exportar()
    elif args.cmd == "listar":
        listar(args.limit)


if __name__ == "__main__":
    main()