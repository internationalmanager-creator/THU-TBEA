"""Registro de anexos V5.0.

Cualquier hallazgo durante el desarrollo que NO este en el trabajo original
se anade aqui. Cada anexo recibe:
    - ID permanente: V5.0-A<NNN>
    - Etiqueta epistemica [D]/[P]/[F]/[A]
    - Hash SHA-256 del contenido
    - Evento en el cronolog
    - Inclusion automatica en la LaTeX multi-idioma

Uso:
    python src/thu/annex.py nuevo --titulo "..." --capitulo "12" ^
        --label D --hallazgo "..." --impacto "..." [--evidencia evid.json]
    python src/thu/annex.py listar
    python src/thu/annex.py verificar
    python src/thu/annex.py exportar-md
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE / "src"))
import db_manager

ANNEXES = BASE / "registry" / "thu" / "annexes.json"
WIDTH = 100


def _ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load():
    return json.loads(ANNEXES.read_text(encoding="utf-8"))


def _save(d):
    ANNEXES.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8", newline="\n")


def _hash_anexo(a):
    """Hash canonico del anexo (excluye su propio hash)."""
    copia = {k: v for k, v in a.items() if k != "sha256"}
    canonico = json.dumps(copia, indent=2, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canonico.encode("utf-8")).hexdigest()


def nuevo(titulo, capitulo, label, hallazgo, impacto,
          evidencia=None, ecuaciones=None, referencias=None):
    if label not in ("D", "P", "F", "A"):
        raise ValueError(f"Etiqueta invalida: {label} (usa D/P/F/A)")

    d = _load()
    n = d["next_id"]
    aid = f"V5.0-A{n:03d}"

    ev = {}
    if evidencia:
        p = Path(evidencia)
        if not p.exists():
            raise FileNotFoundError(f"Evidencia no existe: {evidencia}")
        ev = json.loads(p.read_text(encoding="utf-8"))

    anexo = {
        "id": aid,
        "version": "V5.0",
        "timestamp_utc": _ts(),
        "titulo": titulo,
        "capitulo_origen": str(capitulo),
        "label": label,
        "hallazgo": hallazgo,
        "impacto_epistemico": impacto,
        "evidencia": ev,
        "ecuaciones": ecuaciones or [],
        "referencias": referencias or [],
    }
    anexo["sha256"] = _hash_anexo(anexo)

    d["annexes"].append(anexo)
    d["next_id"] = n + 1
    _save(d)

    # Cadena al cronolog
    try:
        db_manager.inicializar_db()
        db_manager.registrar_evento(
            "thu_anexo_nuevo",
            f"Anexo {aid} creado: {titulo[:60]}",
            entidad_id=aid,
            payload={"label": label, "capitulo": str(capitulo),
                     "sha256": anexo["sha256"]},
        )
    except Exception as e:
        print(f"AVISO: no se pudo registrar evento: {e}")

    print(f"OK: {aid}")
    print(f"  titulo:   {titulo}")
    print(f"  label:    [{label}]")
    print(f"  sha256:   {anexo['sha256']}")
    print(f"  archivo:  {ANNEXES.relative_to(BASE)}")
    return anexo


def listar():
    d = _load()
    if not d["annexes"]:
        print("(sin anexos)")
        return
    print(f"{'ID':<12} {'LABEL':<6} {'CAP':<5} TITULO")
    print("-" * 90)
    for a in d["annexes"]:
        print(f"{a['id']:<12} [{a['label']:<3}]  {a['capitulo_origen']:<5} "
              f"{a['titulo'][:60]}")


def verificar():
    d = _load()
    malos = []
    for a in d["annexes"]:
        h = _hash_anexo(a)
        if h != a["sha256"]:
            malos.append((a["id"], h[:16], a["sha256"][:16]))
    if malos:
        print(f"ANEXOS ALTERADOS: {len(malos)}")
        for mid, h_actual, h_declarado in malos:
            print(f"  {mid}: actual={h_actual} declarado={h_declarado}")
        return False
    print(f"OK: {len(d['annexes'])} anexos verifican")
    return True


def exportar_md():
    d = _load()
    out = BASE / "registry" / "thu" / "ANEXOS_V5.0.md"
    lineas = [
        "# Anexos V5.0 — Extension del programa THU-TBEA",
        "",
        f"> Generado: {_ts()}",
        f"> Total: {len(d['annexes'])} anexos",
        "",
        "Los anexos V5.0 son hallazgos surgidos durante el desarrollo del",
        "programa. NO modifican los capitulos 1-21; se anexan como extension",
        "bajo la figura V5.0. Cada uno lleva hash SHA-256 y cadena al cronolog.",
        "",
        "---",
        "",
    ]
    for a in d["annexes"]:
        lineas.append(f"## {a['id']} — {a['titulo']}")
        lineas.append("")
        lineas.append(f"- **Version:** {a['version']}")
        lineas.append(f"- **Timestamp:** {a['timestamp_utc']}")
        lineas.append(f"- **Capitulo de origen:** {a['capitulo_origen']}")
        lineas.append(f"- **Etiqueta:** [{a['label']}]")
        lineas.append(f"- **SHA-256:** `{a['sha256']}`")
        lineas.append("")
        lineas.append("**Hallazgo:**")
        lineas.append("")
        lineas.append(a["hallazgo"])
        lineas.append("")
        lineas.append("**Impacto epistemico:**")
        lineas.append("")
        lineas.append(a["impacto_epistemico"])
        lineas.append("")
        if a.get("ecuaciones"):
            lineas.append("**Ecuaciones:**")
            lineas.append("")
            for eq in a["ecuaciones"]:
                lineas.append(f"$$ {eq} $$")
                lineas.append("")
        if a.get("evidencia"):
            lineas.append("**Evidencia:**")
            lineas.append("")
            lineas.append("```json")
            lineas.append(json.dumps(a["evidencia"], indent=2, ensure_ascii=False))
            lineas.append("```")
            lineas.append("")
        if a.get("referencias"):
            lineas.append("**Referencias:** " + ", ".join(str(r) for r in a["referencias"]))
            lineas.append("")
        lineas.append("---")
        lineas.append("")
    out.write_text("\n".join(lineas), encoding="utf-8", newline="\n")
    print(f"OK: {out.relative_to(BASE)}")
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("nuevo")
    n.add_argument("--titulo", required=True)
    n.add_argument("--capitulo", required=True)
    n.add_argument("--label", required=True, choices=["D", "P", "F", "A"])
    n.add_argument("--hallazgo", required=True)
    n.add_argument("--impacto", required=True)
    n.add_argument("--evidencia", default=None)
    n.add_argument("--ecuacion", action="append", default=[],
                   help="Ecuacion LaTeX (repetible)")
    n.add_argument("--ref", action="append", default=[],
                   help="Numero de referencia (repetible)")

    sub.add_parser("listar")
    sub.add_parser("verificar")
    sub.add_parser("exportar-md")

    args = ap.parse_args()
    try:
        if args.cmd == "nuevo":
            nuevo(args.titulo, args.capitulo, args.label,
                  args.hallazgo, args.impacto,
                  evidencia=args.evidencia,
                  ecuaciones=args.ecuacion or None,
                  referencias=[int(r) for r in args.ref] or None)
        elif args.cmd == "listar":
            listar()
        elif args.cmd == "verificar":
            sys.exit(0 if verificar() else 1)
        elif args.cmd == "exportar-md":
            exportar_md()
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()