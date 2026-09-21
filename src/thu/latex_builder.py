"""Constructor de LaTeX multi-idioma (ES / EN / DE).

Genera paper/thu/src/tesis_<lang>.tex desde los JSON de registry/thu/.

Secciones del documento:
    1. Portada (title, author, ORCID, DOI o PENDIENTE)
    2. Resumen / Abstract / Zusammenfassung
    3. Keywords
    4. Indice general
    5. Capitulos 1-21 (titulo + ecuaciones clave)
    6. Apendices A-J
    7. Registro de problemas A-1..A-17
    8. Predicciones P1-P11
    9. Bitacora de parches (Etapas VII-X)
    10. Bitacora Lakatosiana 1.0 -> 5.3
    11. Referencias (68)
    12. Anexos V5.0 (dinamicos)

Uso:
    python src/thu/latex_builder.py --lang es
    python src/thu/latex_builder.py --all
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
THU = BASE / "registry" / "thu"
OUT = BASE / "paper" / "thu" / "src"

LANGS = ["es", "en", "de"]
PREAMBLE_LANG = {"es": "spanish", "en": "english", "de": "ngerman"}


def _load(name):
    return json.loads((THU / name).read_text(encoding="utf-8"))


def _ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _esc(s):
    """Escapa caracteres especiales de LaTeX."""
    if not isinstance(s, str):
        s = str(s)
    rep = {
        "\\": r"\textbackslash{}",
        "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
        "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    return "".join(rep.get(ch, ch) for ch in s)


def _preambulo(lang, t, meta):
    """Preambulo LaTeX con metadatos."""
    lang_babel = PREAMBLE_LANG[lang]
    titulo = _esc(t["title"][lang])
    autor = _esc(meta["author"]["name"])
    orcid = _esc(meta["author"]["orcid"])
    fecha = _ts()
    version = _esc(meta["version"])

    doi_field = meta.get("doi_versions", {}).get("current")
    if doi_field:
        doi_line = "DOI: \\href{https://doi.org/" + doi_field + "}{" + doi_field + "}"
    else:
        doi_line = _esc(t["labels"][lang]["no_doi"])

    lines = [
        r"\documentclass[11pt,a4paper]{article}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage[" + lang_babel + r"]{babel}",
        r"\usepackage{geometry}",
        r"\usepackage{amsmath,amssymb,amsfonts}",
        r"\usepackage{graphicx}",
        r"\usepackage{booktabs}",
        r"\usepackage{longtable}",
        r"\usepackage{array}",
        r"\usepackage{enumitem}",
        r"\usepackage{xcolor}",
        r"\usepackage{hyperref}",
        r"\usepackage{fancyhdr}",
        r"\geometry{margin=2.5cm}",
        r"\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=blue,citecolor=blue}",
        r"\definecolor{Dgreen}{HTML}{00B894}",
        r"\definecolor{Ppurple}{HTML}{6C5CE7}",
        r"\definecolor{Forange}{HTML}{E17055}",
        r"\definecolor{Ayellow}{HTML}{D4A017}",
        "",
        r"\title{\textbf{" + titulo + r"} \\[0.5em] \large " + _esc(t["subtitle"][lang]) + "}",
        r"\author{" + autor + r" \\ \texttt{" + orcid + r"} \\ \textit{" + _esc(t["theory_name"][lang]) + "}}",
        r"\date{Version " + version + " · " + fecha + r" \\ \small " + doi_line + r" \\ \small " + _esc(meta["license"]) + "}",
        "",
        r"\pagestyle{fancy}",
        r"\fancyhf{}",
        r"\fancyhead[L]{\small " + _esc(t["theory_name"][lang]) + "}",
        r"\fancyhead[R]{\small v" + version + "}",
        r"\fancyfoot[C]{\thepage}",
        "",
        r"\begin{document}",
        r"\maketitle",
        r"\thispagestyle{empty}",
        "",
    ]
    return "\n".join(lines)


def _abstract(lang, t):
    lines = [
        r"\section*{" + _esc(t["labels"][lang]["abstract"]) + "}",
        r"\addcontentsline{toc}{section}{" + _esc(t["labels"][lang]["abstract"]) + "}",
        "",
        _esc(t["abstract"][lang]),
        "",
        r"\vspace{1em}",
        r"\textbf{" + _esc(t["labels"][lang]["keywords"]) + ":} " + _esc(", ".join(t["keywords"][lang])),
        "",
        r"\newpage",
        r"\tableofcontents",
        r"\newpage",
        "",
    ]
    return "\n".join(lines)


def _epistemic_legend(lang, t):
    return "\n".join([
        r"\section*{Status legend}",
        r"\addcontentsline{toc}{section}{Status legend}",
        _esc(t["labels"][lang]["epistemic_legend"]),
        "",
        r"\vspace{0.5em}",
        r"\begin{itemize}[leftmargin=*]",
        r"\item \textcolor{Dgreen}{\textbf{[D]}} — " + _esc({"es": "Derivado", "en": "Derived", "de": "Abgeleitet"}[lang]),
        r"\item \textcolor{Ppurple}{\textbf{[P]}} — " + _esc({"es": "Postulado", "en": "Postulated", "de": "Postuliert"}[lang]),
        r"\item \textcolor{Forange}{\textbf{[F]}} — " + _esc({"es": "Frontera", "en": "Frontier", "de": "Grenze"}[lang]),
        r"\item \textcolor{Ayellow}{\textbf{[A]}} — " + _esc({"es": "Analogia", "en": "Analogy", "de": "Analogie"}[lang]),
        r"\end{itemize}",
        "",
        r"\newpage",
        "",
    ])


def _chapters(lang, t):
    caps = t["chapter_titles"]
    eqs = t.get("chapter_equations", {})
    lbl = t["labels"][lang]

    parts = [r"\section*{Chapters}", ""]
    for n in sorted(caps.keys(), key=lambda x: int(x)):
        titulo = _esc(caps[n][lang])
        parts.append(r"\subsection*{" + lbl["chapter"] + " " + n + ". " + titulo + "}")
        if n in eqs:
            parts.append("")
            parts.append(r"\textbf{" + _esc(lbl["equations"]) + ":}")
            parts.append(r"\begin{align*}")
            for i, eq in enumerate(eqs[n]):
                sep = r" \\" if i < len(eqs[n]) - 1 else ""
                parts.append("    " + eq + sep)
            parts.append(r"\end{align*}")
            parts.append("")
    parts.append(r"\newpage")
    parts.append("")
    return "\n".join(parts)


def _appendices(lang, t):
    lbl = t["labels"][lang]
    parts = [r"\section*{Appendices}", ""]
    for letter in sorted(t["appendix_titles"].keys()):
        titulo = _esc(t["appendix_titles"][letter][lang])
        parts.append(r"\subsection*{" + lbl["appendix"] + " " + letter + ". " + titulo + "}")
    parts.append(r"\newpage")
    parts.append("")
    return "\n".join(parts)

# === PARTE 2 se agrega a continuacion ===

def _problems_table(lang, t, probs):
    lbl = t["labels"][lang]
    out = [r"\section*{" + _esc(lbl["problems_registry"]) + "}", ""]
    out.append(r"\begin{longtable}{@{}p{1.2cm}p{6.5cm}p{1.8cm}p{2cm}@{}}")
    out.append(r"\toprule")
    out.append(r"\textbf{ID} & \textbf{Title} & \textbf{Label} & \textbf{Status} \\")
    out.append(r"\midrule")
    out.append(r"\endhead")
    for p in probs:
        color = {"D": "Dgreen", "P": "Ppurple", "F": "Forange", "A": "Ayellow"}[p["label"][0]]
        out.append(
            _esc(p["id"]) + " & " + _esc(p["title"]) + " & "
            + r"\textcolor{" + color + r"}{\textbf{[" + p["label"] + "]}} & "
            + _esc(p["status"]) + r" \\"
        )
    out.append(r"\bottomrule")
    out.append(r"\end{longtable}")
    out.append("")
    out.append(r"\newpage")
    return "\n".join(out)


def _predictions_table(lang, t, preds):
    lbl = t["labels"][lang]
    out = [r"\section*{" + _esc(lbl["predictions"]) + "}", ""]
    out.append(r"\begin{longtable}{@{}p{0.8cm}p{5.5cm}p{3.5cm}p{2.5cm}@{}}")
    out.append(r"\toprule")
    out.append(r"\textbf{ID} & \textbf{Observable} & \textbf{Arbiter} & \textbf{Status} \\")
    out.append(r"\midrule")
    out.append(r"\endhead")
    for p in preds:
        out.append(
            _esc(p["id"]) + " & " + _esc(p["observable"]) + " & "
            + _esc(p["arbiter"]) + " & " + _esc(p["status"]) + r" \\"
        )
    out.append(r"\bottomrule")
    out.append(r"\end{longtable}")
    out.append("")
    out.append(r"\newpage")
    return "\n".join(out)


def _patches_table(lang, t, patches):
    lbl = t["labels"][lang]
    out = [r"\section*{" + _esc(lbl["patches"]) + "}", ""]
    out.append(r"\begin{longtable}{@{}p{0.7cm}p{1.5cm}p{4.5cm}p{4.5cm}p{1.2cm}@{}}")
    out.append(r"\toprule")
    out.append(r"\textbf{N} & \textbf{Stage} & \textbf{Before} & \textbf{After} & \textbf{Label} \\")
    out.append(r"\midrule")
    out.append(r"\endhead")
    for p in patches:
        color = {"D": "Dgreen", "P": "Ppurple", "F": "Forange", "A": "Ayellow"}[p["label"][0]]
        before = p["before"][:55]
        after = p["after"][:55]
        out.append(
            str(p["n"]) + " & " + _esc(p["stage"]) + " & "
            + r"\texttt{" + _esc(before) + "} & "
            + r"\texttt{" + _esc(after) + "} & "
            + r"\textcolor{" + color + r"}{\textbf{[" + p["label"] + "]}} \\"
        )
    out.append(r"\bottomrule")
    out.append(r"\end{longtable}")
    out.append("")
    out.append(r"\newpage")
    return "\n".join(out)


def _versions_timeline(lang, t, versions):
    lbl = t["labels"][lang]
    out = [r"\section*{" + _esc(lbl["bitacora"]) + "}", ""]
    out.append(r"\begin{itemize}[leftmargin=*]")
    for v in versions["versions"]:
        color = {"D": "Dgreen", "P": "Ppurple", "F": "Forange", "A": "Ayellow"}[v["label"][0]]
        out.append(
            r"\item \textbf{v" + v["v"] + "} (" + _esc(v["epoch"]) + ") --- "
            + _esc(v["title"]) + " "
            + r"\textcolor{" + color + r"}{\textbf{[" + v["label"] + "]}}"
        )
    out.append(r"\end{itemize}")
    out.append("")
    out.append(r"\newpage")
    return "\n".join(out)


def _annexes(lang, t, annexes):
    lbl = t["labels"][lang]
    out = [r"\section*{" + _esc(lbl["annexes"]) + "}", ""]
    if not annexes.get("annexes"):
        out.append(r"\textit{(no annexes yet)}")
        out.append(r"\newpage")
        return "\n".join(out)
    for a in annexes["annexes"]:
        color = {"D": "Dgreen", "P": "Ppurple", "F": "Forange", "A": "Ayellow"}[a["label"][0]]
        out.append(r"\subsection*{" + _esc(a["id"]) + ": " + _esc(a["titulo"]) + "}")
        out.append(r"\textbf{Version:} V5.0 \\")
        out.append(r"\textbf{Timestamp:} " + _esc(a["timestamp_utc"]) + " \\")
        out.append(r"\textbf{Chapter of origin:} " + _esc(a["capitulo_origen"]) + " \\")
        out.append(r"\textbf{Label:} \textcolor{" + color + r"}{\textbf{[" + a["label"] + "]}} \\")
        out.append(r"\textbf{SHA-256:} \texttt{" + a["sha256"][:32] + "...} \\[0.5em]")
        out.append(r"\textbf{Finding:}")
        out.append("")
        out.append(_esc(a["hallazgo"]))
        out.append("")
        out.append(r"\textbf{Epistemic impact:}")
        out.append("")
        out.append(_esc(a["impacto_epistemico"]))
        out.append("")
        if a.get("ecuaciones"):
            out.append(r"\textbf{Equations:}")
            out.append(r"\begin{align*}")
            for i, eq in enumerate(a["ecuaciones"]):
                sep = r" \\" if i < len(a["ecuaciones"]) - 1 else ""
                out.append("    " + eq + sep)
            out.append(r"\end{align*}")
            out.append("")
        out.append(r"\vspace{1em}\hrule\vspace{1em}")
    out.append(r"\newpage")
    return "\n".join(out)


def _references(lang, t, refs):
    lbl = t["labels"][lang]
    out = [r"\section*{" + _esc(lbl["references"]) + "}", ""]
    out.append(r"\begin{thebibliography}{99}")
    for r in refs["refs"]:
        key = "ref" + str(r["n"])
        year = r.get("year", "n.d.")
        if "journal" in r:
            entry = _esc(r["authors"]) + ", " + _esc(r["journal"])
            if "vol" in r:
                entry += r", \textbf{" + _esc(r["vol"]) + "}"
            if "pages" in r:
                entry += ", " + _esc(r["pages"])
            entry += " (" + str(year) + ")."
        elif "title" in r:
            entry = (_esc(r["authors"]) + ", \textit{" + _esc(r["title"])
                     + "}, " + _esc(r.get("publisher", "")) + " (" + str(year) + ").")
        else:
            entry = _esc(r["authors"]) + " (" + str(year) + ")."
        out.append(r"\bibitem{" + key + "} " + entry)
    out.append(r"\end{thebibliography}")
    out.append("")
    return "\n".join(out)


def build(lang, out_dir=None):
    if lang not in LANGS:
        raise ValueError("Idioma invalido: " + lang)

    meta = _load("project.json")
    problems = _load("problems.json")["problems"]
    predictions = _load("predictions.json")["predictions"]
    patches = _load("patches.json")["patches"]
    versions = _load("versions.json")
    refs = _load("references.json")
    annexes = _load("annexes.json")
    i18n = _load("i18n_content.json")

    partes = []
    partes.append(_preambulo(lang, i18n, meta))
    partes.append(_abstract(lang, i18n))
    partes.append(_epistemic_legend(lang, i18n))
    partes.append(_chapters(lang, i18n))
    partes.append(_appendices(lang, i18n))
    partes.append(_problems_table(lang, i18n, problems))
    partes.append(_predictions_table(lang, i18n, predictions))
    partes.append(_patches_table(lang, i18n, patches))
    partes.append(_versions_timeline(lang, i18n, versions))
    partes.append(_annexes(lang, i18n, annexes))
    partes.append(_references(lang, i18n, refs))
    partes.append(r"\vspace{2em}")
    partes.append(r"\begin{center}")
    partes.append(r"\small")
    partes.append(r"\textit{End of document}")
    partes.append(r"\end{center}")
    partes.append(r"\end{document}")

    texto = "\n".join(partes)

    out_dir = Path(out_dir) if out_dir else OUT
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / ("tesis_" + lang + ".tex")
    out_path.write_text(texto, encoding="utf-8", newline="\n")

    print("OK: " + str(out_path.relative_to(BASE)) + "  (" + str(len(texto))
          + " bytes, " + str(texto.count(chr(10))) + " lineas)")
    return out_path


def build_all(out_dir=None):
    return [build(lang, out_dir) for lang in LANGS]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=LANGS, default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.all:
        build_all(args.out)
    elif args.lang:
        build(args.lang, args.out)
    else:
        ap.error("Especifica --lang o --all")


if __name__ == "__main__":
    from tqdm import tqdm
    print("=== Test latex_builder.py ===")
    paths = []
    for lang in tqdm(LANGS, desc="Generando", ncols=80):
        p = build(lang)
        paths.append(p)
    # Validaciones basicas
    for p in paths:
        content = p.read_text(encoding="utf-8")
        assert r"\documentclass" in content, "falta documentclass"
        assert r"\begin{document}" in content, "falta begin document"
        assert r"\end{document}" in content, "falta end document"
        assert "ref68" in content, "faltan referencias"
        assert "P1" in content, "faltan predicciones"
        assert "A-1" in content, "faltan problemas"
        assert "V5.0" in content or "Anexos" in content or "Annexes" in content, "faltan anexos"
    print("=== TEST OK ===")
    for p in paths:
        print(f"  {p.name}: {p.stat().st_size} B")