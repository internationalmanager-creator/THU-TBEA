# -*- coding: utf-8 -*-
r"""Genera docs\SESSION_BUNDLE.md a partir de los archivos criticos.

Uso:
    python docs\_bundle.py

Salida:
    docs\SESSION_BUNDLE.md  (archivo unico para adjuntar en chat nuevo)

Excluye los .tex (regenerables con latex_builder.py --all).
"""
import hashlib
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parent.parent
while REPO.parent != REPO and not (REPO / "registry" / "thu" / "chapter_bodies.json").exists():
    REPO = REPO.parent

BUNDLE = REPO / "docs" / "SESSION_BUNDLE.md"

FILES = [
    "docs/HANDOFF_V5.4_SESION_7.md",
    "scripts/check_debts.py",
    "docs/debts_history.json",
    "registry/thu/chapter_bodies.json",
    "registry/thu/i18n_content.json",
    "registry/thu/problems.json",
    "registry/thu/patches.json",
    "registry/thu/doi_registry.json",
    "registry/thu/figures_metadata.json",
    "data/inventory/verificacion_simbolica.json",
    "paper/thu/figures/figures_manifest.json",
    "paper/thu/src/thu_references.bib",
    "src/thu/latex_builder.py",
    "src/thu/figures.py",
    "src/thu/loader.py",
    "app_thu.py",
]


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def main():
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    parts = []
    parts.append("# SESSION BUNDLE v5.4")
    parts.append("")
    parts.append("**Generado:** " + ts)
    parts.append("**Repo:** " + str(REPO))
    parts.append("**Archivos:** " + str(len(FILES)))
    parts.append("")
    parts.append("Este archivo contiene todos los archivos criticos del repo,")
    parts.append("delimitados por marcadores `<<<FILE:...>>>` y `<<<END>>>`.")
    parts.append("Al adjuntarlo en un chat nuevo, el asistente puede parsear cada")
    parts.append("archivo por los marcadores.")
    parts.append("")
    parts.append("**NO incluye** `tesis_es.tex` / `tesis_en.tex` / `tesis_de.tex`")
    parts.append("(son regenerables con `python src\\thu\\latex_builder.py --all`).")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("## Indice")
    parts.append("")
    for rel in FILES:
        p = REPO / rel
        if p.exists():
            sz = p.stat().st_size
            h = _sha16(p)
            parts.append("- `" + rel + "` (" + str(sz) + " B, `" + h + "`)")
        else:
            parts.append("- `" + rel + "` **FALTA**")
    parts.append("")
    parts.append("---")
    parts.append("")

    missing = []
    total = 0
    for rel in FILES:
        p = REPO / rel
        parts.append("<<<FILE:" + rel + ">>>")
        if not p.exists():
            parts.append("**ERROR: archivo no encontrado**")
            missing.append(rel)
        else:
            try:
                content = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = p.read_text(encoding="latin-1")
            total += len(content)
            # Evita colision con el sentinel
            if "<<<END>>>" in content:
                content = content.replace("<<<END>>>", "<<<END_ESCAPED>>>")
            if "<<<FILE:" in content:
                content = content.replace("<<<FILE:", "<<<FILE_ESCAPED:")
            parts.append(content)
        parts.append("<<<END>>>")
        parts.append("")

    out = "\n".join(parts)
    BUNDLE.write_text(out, encoding="utf-8", newline="\n")

    print("  Escrito:     " + str(BUNDLE.relative_to(REPO)))
    print("  Bytes:       " + str(BUNDLE.stat().st_size))
    print("  Lineas:      " + str(out.count(chr(10))))
    print("  Archivos OK: " + str(len(FILES) - len(missing)) + "/" + str(len(FILES)))
    if missing:
        print("  FALTAN:")
        for m in missing:
            print("    - " + m)
    print()
    print("BUNDLE_OK" if not missing else "BUNDLE_FALTA")


if __name__ == "__main__":
    main()
