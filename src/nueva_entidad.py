"""Scaffold para crear JSON de entidad con provenance.

Uso:
    python src/nueva_entidad.py --id COSM-002 --categoria cosmologia `
        --valor 67.4 --unidad "km/s/Mpc" --fuente "Planck2020" `
        --origen observado --estatus D `
        --cita "Planck Collaboration. A&A 641, A6 (2020)." `
        --doi "10.1051/0004-6361/201833910" `
        --instrumento "Planck HFI" `
        --condiciones "Fondo cosmico de microondas" `
        --extracto "H0 = 67.4 +/- 0.5 km/s/Mpc"

Sin --cita, --instrumento, --condiciones o --extracto, se crea un borrador
marcado con estatus F (frontera, incompleto).
"""
import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
INPUTS = BASE / "data" / "inputs"

CATS = ["cosmologia", "geofisica", "biologia", "neurofisiologia",
        "cuantica", "antropologia", "otros", "test"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--categoria", required=True, choices=CATS)
    ap.add_argument("--valor", type=float, required=True)
    ap.add_argument("--incertidumbre", type=float, default=0.0)
    ap.add_argument("--unidad", required=True)
    ap.add_argument("--fuente", required=True)
    ap.add_argument("--origen", default="observado",
                    choices=["observado", "generado", "inferido", "simulado"])
    ap.add_argument("--estatus", default="F", choices=["D", "P", "F", "A"])
    ap.add_argument("--notas", default="")
    ap.add_argument("--titulo", default="")
    # provenance
    ap.add_argument("--cita", default="")
    ap.add_argument("--doi", default=None)
    ap.add_argument("--tipo-pub", default="")
    ap.add_argument("--ano", type=int, default=None)
    ap.add_argument("--instrumento", default="")
    ap.add_argument("--condiciones", default="")
    ap.add_argument("--reproducibilidad", default="")
    ap.add_argument("--extracto", default="")
    ap.add_argument("--forzar", action="store_true",
                    help="sobrescribir si ya existe")
    args = ap.parse_args()

    out = INPUTS / f"{args.id}.json"
    if out.exists() and not args.forzar:
        print(f"ERROR: {out} ya existe (usa --forzar)", file=sys.stderr)
        sys.exit(1)

    completo = all([args.cita, args.instrumento, args.condiciones,
                    args.extracto, args.ano, args.tipo_pub])
    estatus = args.estatus if completo else "F"
    if not completo and args.estatus != "F":
        print("AVISO: provenance incompleta, forzando estatus=F")

    datos = {
        "id": args.id,
        "categoria": args.categoria,
        "titulo": args.titulo or f"{args.id} ({args.categoria})",
        "valor_principal": args.valor,
        "incertidumbre": args.incertidumbre,
        "unidad": args.unidad,
        "fuente": args.fuente,
        "origen": args.origen,
        "estatus": estatus,
        "notas": args.notas,
        "provenance": {
            "cita_completa": args.cita,
            "doi": args.doi,
            "tipo_publicacion": args.tipo_pub,
            "ano": args.ano,
            "instrumento": args.instrumento,
            "condiciones": args.condiciones,
            "reproducibilidad": args.reproducibilidad,
            "extracto": args.extracto,
            "hash_pdf": None,
            "fecha_descarga_utc": None,
            "notas": "",
        },
    }
    INPUTS.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8", newline="\n")
    print(f"OK: {out.relative_to(BASE)}")
    print(f"Provenance: {'COMPLETA' if completo else 'INCOMPLETA (estatus=F)'}")
    print(f"Siguiente: python src/registrar_entidad.py {args.id}")


if __name__ == "__main__":
    main()