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
    8. Predicciones P1-P12
    9. Bitacora de parches (Etapas VII-X)
    10. Bitacora Lakatosiana 1.0 -> 5.3
    11. Referencias (68)
    12. Anexos V5.0 (dinamicos)

Uso:
    python src/thu/latex_builder.py --lang es
    python src/thu/latex_builder.py --all
"""
import argparse
import re
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
THU = BASE / "registry" / "thu"
OUT = BASE / "paper" / "thu" / "src"

LANGS = ["es", "en", "de"]
PREAMBLE_LANG = {"es": "spanish", "en": "english", "de": "ngerman"}


# --- v5.4: figuras ---
FIG_WIDTH = r"0.85\textwidth"
FIG_LABELS = {"es": "Figura", "en": "Figure", "de": "Abbildung"}
FIGURES_MANIFEST = BASE / "paper" / "thu" / "figures" / "figures_manifest.json"


def _norm_sec(s):
    """Normaliza '03.01' -> '3.1', 'B.01' -> 'B.1'. Idempotente."""
    if not s:
        return ""
    out = []
    for p in str(s).split("."):
        if not p:
            continue
        out.append(str(int(p)) if p.isdigit() else p)
    return ".".join(out)


def _load(name):
    return json.loads((THU / name).read_text(encoding="utf-8"))



def _load_chapter_bodies():
    """Carga chapter_bodies.json si existe. Devuelve dict vacio si no."""
    p = THU / "chapter_bodies.json"
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data.get("chapters", {})
    except Exception as e:
        print(f"AVISO: no se pudo cargar chapter_bodies.json: {e}")
        return {}

def _load_figures_by_section():
    """Devuelve {sec_norm: [figuras]} desde manifest + metadata."""
    if not FIGURES_MANIFEST.exists():
        return {}
    meta_path = THU / "figures_metadata.json"
    if not meta_path.exists():
        return {}
    try:
        manifest = json.loads(FIGURES_MANIFEST.read_text(encoding="utf-8"))
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception as e:
        print("AVISO: fallo al cargar figuras: " + str(e))
        return {}
    meta_figs = meta.get("figures", {})
    index = {}
    for entry in manifest.get("figures", []):
        name = entry.get("name")
        if not name or name not in meta_figs:
            continue
        sec_raw = meta_figs[name].get("sec", "")
        if not sec_raw:
            continue
        key = _norm_sec(sec_raw)
        index.setdefault(key, []).append({
            "name": name,
            "source": entry.get("source", name),
        })
    for k in index:
        index[k].sort(key=lambda x: x["name"])
    return index


def _ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _esc_caption(s):
    r"""Escapa caracteres peligrosos FUERA de math mode ($...$).
    Preserva LaTeX inline como $\chi^2$. Idempotente: si ya esta
    escapado (\_), no duplica."""
    if not isinstance(s, str):
        s = str(s)
    out = []
    in_math = False
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "$":
            in_math = not in_math
            out.append(ch)
        elif not in_math and ch in "_^&#%":
            # Evitar duplicar si ya esta escapado
            if i > 0 and s[i-1] == "\\":
                out.append(ch)
            else:
                out.append("\\" + ch)
        elif not in_math and ch == "~":
            out.append("\\textasciitilde{}")
        else:
            out.append(ch)
        i += 1
    return "".join(out)


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
        r"\documentclass[11pt,letterpaper]{article}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage{newunicodechar}",
        r"\newunicodechar{α}{\ensuremath{\alpha}}",
        r"\newunicodechar{β}{\ensuremath{\beta}}",
        r"\newunicodechar{γ}{\ensuremath{\gamma}}",
        r"\newunicodechar{δ}{\ensuremath{\delta}}",
        r"\newunicodechar{ε}{\ensuremath{\epsilon}}",
        r"\newunicodechar{ζ}{\ensuremath{\zeta}}",
        r"\newunicodechar{η}{\ensuremath{\eta}}",
        r"\newunicodechar{θ}{\ensuremath{\theta}}",
        r"\newunicodechar{ι}{\ensuremath{\iota}}",
        r"\newunicodechar{κ}{\ensuremath{\kappa}}",
        r"\newunicodechar{λ}{\ensuremath{\lambda}}",
        r"\newunicodechar{μ}{\ensuremath{\mu}}",
        r"\newunicodechar{ν}{\ensuremath{\nu}}",
        r"\newunicodechar{ξ}{\ensuremath{\xi}}",
        r"\newunicodechar{ο}{o}",
        r"\newunicodechar{π}{\ensuremath{\pi}}",
        r"\newunicodechar{ρ}{\ensuremath{\rho}}",
        r"\newunicodechar{ς}{\ensuremath{\varsigma}}",
        r"\newunicodechar{σ}{\ensuremath{\sigma}}",
        r"\newunicodechar{τ}{\ensuremath{\tau}}",
        r"\newunicodechar{υ}{\ensuremath{\upsilon}}",
        r"\newunicodechar{φ}{\ensuremath{\phi}}",
        r"\newunicodechar{χ}{\ensuremath{\chi}}",
        r"\newunicodechar{ψ}{\ensuremath{\psi}}",
        r"\newunicodechar{ω}{\ensuremath{\omega}}",
        r"\newunicodechar{Γ}{\ensuremath{\Gamma}}",
        r"\newunicodechar{Δ}{\ensuremath{\Delta}}",
        r"\newunicodechar{Θ}{\ensuremath{\Theta}}",
        r"\newunicodechar{Λ}{\ensuremath{\Lambda}}",
        r"\newunicodechar{Ξ}{\ensuremath{\Xi}}",
        r"\newunicodechar{Π}{\ensuremath{\Pi}}",
        r"\newunicodechar{Σ}{\ensuremath{\Sigma}}",
        r"\newunicodechar{Υ}{\ensuremath{\Upsilon}}",
        r"\newunicodechar{Φ}{\ensuremath{\Phi}}",
        r"\newunicodechar{Ψ}{\ensuremath{\Psi}}",
        r"\newunicodechar{Ω}{\ensuremath{\Omega}}",
        r"\newunicodechar{²}{\textsuperscript{2}}",
        r"\newunicodechar{³}{\textsuperscript{3}}",
        r"\newunicodechar{¹}{\textsuperscript{1}}",
        r"\newunicodechar{⁰}{\textsuperscript{0}}",
        r"\newunicodechar{⁴}{\textsuperscript{4}}",
        r"\newunicodechar{⁵}{\textsuperscript{5}}",
        r"\newunicodechar{⁶}{\textsuperscript{6}}",
        r"\newunicodechar{⁷}{\textsuperscript{7}}",
        r"\newunicodechar{⁸}{\textsuperscript{8}}",
        r"\newunicodechar{⁹}{\textsuperscript{9}}",
        r"\newunicodechar{⁻}{\textsuperscript{-}}",
        r"\newunicodechar{⁺}{\textsuperscript{+}}",
        r"\newunicodechar{ⁿ}{\textsuperscript{n}}",
        r"\newunicodechar{ⁱ}{\textsuperscript{i}}",
        r"\newunicodechar{§}{\S}",
        r"\newunicodechar{·}{\textperiodcentered}",
        r"\newunicodechar{–}{\textendash}",
        r"\newunicodechar{—}{\textemdash}",
        r"\newunicodechar{‘}{`}",
        r"\newunicodechar{’}{'}",
        r"\newunicodechar{“}{``}",
        r"\newunicodechar{”}{''}",
        r"\newunicodechar{…}{\ldots}",
        r"\newunicodechar{×}{\ensuremath{\times}}",
        r"\newunicodechar{÷}{\ensuremath{\div}}",
        r"\newunicodechar{±}{\ensuremath{\pm}}",
        r"\newunicodechar{−}{\ensuremath{-}}",
        r"\newunicodechar{→}{\ensuremath{\to}}",
        r"\newunicodechar{←}{\ensuremath{\leftarrow}}",
        r"\newunicodechar{↔}{\ensuremath{\leftrightarrow}}",
        r"\newunicodechar{⇒}{\ensuremath{\Rightarrow}}",
        r"\newunicodechar{⇐}{\ensuremath{\Leftarrow}}",
        r"\newunicodechar{⇔}{\ensuremath{\Leftrightarrow}}",
        r"\newunicodechar{≤}{\ensuremath{\le}}",
        r"\newunicodechar{≥}{\ensuremath{\ge}}",
        r"\newunicodechar{≠}{\ensuremath{\neq}}",
        r"\newunicodechar{≈}{\ensuremath{\approx}}",
        r"\newunicodechar{∞}{\ensuremath{\infty}}",
        r"\newunicodechar{∂}{\ensuremath{\partial}}",
        r"\newunicodechar{∇}{\ensuremath{\nabla}}",
        r"\newunicodechar{∫}{\ensuremath{\int}}",
        r"\newunicodechar{∑}{\ensuremath{\sum}}",
        r"\newunicodechar{√}{\ensuremath{\sqrt{}}}",
        r"\newunicodechar{∈}{\ensuremath{\in}}",
        r"\newunicodechar{∉}{\ensuremath{\notin}}",
        r"\newunicodechar{⊂}{\ensuremath{\subset}}",
        r"\newunicodechar{⊃}{\ensuremath{\supset}}",
        r"\newunicodechar{⊆}{\ensuremath{\subseteq}}",
        r"\newunicodechar{⊇}{\ensuremath{\supseteq}}",
        r"\newunicodechar{∪}{\ensuremath{\cup}}",
        r"\newunicodechar{∩}{\ensuremath{\cap}}",
        r"\newunicodechar{∅}{\ensuremath{\emptyset}}",
        r"\newunicodechar{∀}{\ensuremath{\forall}}",
        r"\newunicodechar{∃}{\ensuremath{\exists}}",
        r"\newunicodechar{¬}{\ensuremath{\neg}}",
        r"\newunicodechar{∧}{\ensuremath{\wedge}}",
        r"\newunicodechar{∨}{\ensuremath{\vee}}",
        r"\newunicodechar{⊕}{\ensuremath{\oplus}}",
        r"\newunicodechar{⊗}{\ensuremath{\otimes}}",
        r"\newunicodechar{⋅}{\ensuremath{\cdot}}",
        r"\newunicodechar{⁄}{\ensuremath{/}}",
        r"\newunicodechar{Δ}{\ensuremath{\Delta}}",
        r"\newunicodechar{ }{~}",
        r"\usepackage{geometry}",
        r"\usepackage{amsmath,amssymb,amsfonts}",
        r"\usepackage{graphicx}",
        r"\usepackage{adjustbox}",
        r"\usepackage{setspace}",
        r"\usepackage{newtxtext,newtxmath}",
        r"\usepackage{microtype}",
        r"\graphicspath{{figures/}}",
        r"\usepackage{booktabs}",
        r"\usepackage{longtable}",
        r"\usepackage{array}",
        r"\usepackage{enumitem}",
        r"\usepackage{xcolor}",
        r"\usepackage{hyperref}",
        r"\usepackage{fancyhdr}",
        r"\geometry{letterpaper,top=2.5cm,bottom=2.5cm,left=2.5cm,right=2.5cm}",
        r"\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=blue,citecolor=blue}",
        r"\definecolor{Dgreen}{HTML}{00B894}",
        r"\definecolor{Ppurple}{HTML}{6C5CE7}",
        r"\definecolor{Forange}{HTML}{E17055}",
        r"\definecolor{Ayellow}{HTML}{D4A017}",
        r"\setcounter{tocdepth}{2}",
        r"\setcounter{secnumdepth}{2}",
        r"\onehalfspacing",
        r"\setlength{\emergencystretch}{3em}",
        r"\sloppy",
        "",
        r"\title{\textbf{" + titulo + r"} \\[0.5em] \large " + _esc(t["subtitle"][lang]) + "}",
        r"\author{" + autor + r" \\ \texttt{" + orcid + r"}" + r" \\ \textit{" + _esc(meta["author"].get("affiliation_" + lang, meta["author"].get("affiliation_es", "Investigador Independiente"))) + r"}" + r" \\ \texttt{" + _esc(meta["author"].get("email", "international_manager@comllcusa.com")) + r"}" + r" \\ \textit{" + _esc(t["theory_name"][lang]) + "}}",
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



def _sanitize_body(text):
    r"""Escapa _ ^ ~ fuera de math mode. Preserva \cmd y $...$ / $$...$$ / \[..\]."""
    if not isinstance(text, str):
        return text
    out = []
    in_math = False
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        # Backslash commands: no tocar
        if ch == "\\" and i + 1 < n:
            nxt = text[i+1]
            # \[ y \( abren math; \] y \) cierran
            if nxt == "[" or nxt == "(":
                in_math = True
                out.append(text[i:i+2])
                i += 2
                continue
            if nxt == "]" or nxt == ")":
                in_math = False
                out.append(text[i:i+2])
                i += 2
                continue
            # Otras secuencias: \cmd o \char, saltar 2
            out.append(text[i:i+2])
            i += 2
            continue
        # $$ como delimitador unico
        if text[i:i+2] == "$$":
            in_math = not in_math
            out.append("$$")
            i += 2
            continue
        # $ simple toggle
        if ch == "$":
            in_math = not in_math
            out.append(ch)
            i += 1
            continue
        # Fuera de math: escapar _ ^ ~
        if not in_math:
            if ch == "_":
                out.append("\\_")
            elif ch == "^":
                out.append("\\textasciicircum{}")
            elif ch == "~":
                out.append("\\textasciitilde{}")
            else:
                out.append(ch)
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def _clean_eq(eq):
    """Reduce dobles backslashes de JSON a single backslash."""
    if not isinstance(eq, str):
        return eq
    return eq.replace("\\\\", "\\")


def _strip_num_prefix(title):
    """Quita el prefijo numerico ('1. ', '3.2. ') del titulo."""
    return re.sub(r'^\d+(?:\.\d+)*\.?\s+', '', title)


def _wrap_display_math(text):
    """Reemplaza $$...$$ por equation* con resizebox condicional."""
    if not isinstance(text, str):
        return text
    def repl(m):
        eq = m.group(1).strip()
        return (
            "\\begin{equation*}\n"
            "  \\resizebox{\\ifdim\\width>\\linewidth \\linewidth\\else\\width\\fi}{!}{$\\displaystyle "
            + eq + "$}\n"
            "\\end{equation*}"
        )
    return re.sub(r'\$\$(.+?)\$\$', repl, text, flags=re.DOTALL)




def _wrap_wide_tables(text):
    """Envuelve cada tabular en resizebox condicional para evitar overflow."""
    if not isinstance(text, str):
        return text
    pattern = r'(\\begin\{tabular\}\{[^}]*\}.*?\\end\{tabular\})'
    def repl(m):
        tab = m.group(1)
        return (
            "\\resizebox{\\ifdim\\width>\\linewidth \\linewidth\\else\\width\\fi}{!}{%\n"
            + tab + "\n}"
        )
    return re.sub(pattern, repl, text, flags=re.DOTALL)

def _chapters(lang, t):
    caps = t["chapter_titles"]
    eqs = t.get("chapter_equations", {})
    bodies = _load_chapter_bodies()
    figs_by_sec = _load_figures_by_section()
    lbl = t["labels"][lang]

    parts = []
    for n in sorted(caps.keys(), key=lambda x: int(x)):
        titulo = _esc(_strip_num_prefix(caps[n][lang]))
        parts.append(r"\section{" + titulo + "}")

        ch_key = "ch" + str(int(n)).zfill(2)
        if ch_key in bodies:
            ch = bodies[ch_key]
            for sec in ch.get("sections", []):
                sec_title = sec.get("title", {}).get(lang, sec.get("title", {}).get("es", ""))
                sec_body = sec.get("body", {}).get(lang, sec.get("body", {}).get("es", ""))
                if sec_title:
                    parts.append(r"\subsection{" + _esc(_strip_num_prefix(sec_title)) + "}")
                if sec_body:
                    body_clean = _wrap_wide_tables(_sanitize_body(sec_body))
                    body_clean = _wrap_display_math(body_clean)
                    parts.append(body_clean)
                sec_n_norm = _norm_sec(sec.get("n", ""))
                for fig in figs_by_sec.get(sec_n_norm, []):
                    parts.append(r"\begin{figure}[htbp]")
                    parts.append(r"  \centering")
                    parts.append(r"  \includegraphics[width=" + FIG_WIDTH + r"]{" + fig["name"] + r".pdf}")
                    parts.append(r"  \caption{" + _esc_caption(fig["source"]) + r"}")
                    parts.append(r"  \label{fig:" + fig["name"] + r"}")
                    parts.append(r"\end{figure}")
            parts.append("")

        if n in eqs:
            parts.append(r"\textbf{" + _esc(lbl["equations"]) + ":}")
            parts.append(r"\begin{align*}")
            for i, eq in enumerate(eqs[n]):
                sep = r" \\" if i < len(eqs[n]) - 1 else ""
                parts.append("    " + _clean_eq(eq) + sep)
            parts.append(r"\end{align*}")
    parts.append(r"\newpage")
    return "\n".join(parts)



def _appendices(lang, t):
    titles = t.get("appendix_titles", {})
    bodies = t.get("appendix_bodies", {})
    figs_by_sec = _load_figures_by_section()

    all_letters = sorted(set(list(titles.keys()) + list(bodies.keys())))
    out = [r"\appendix", ""]
    for letter in all_letters:
        if letter in titles and lang in titles[letter]:
            title = titles[letter][lang]
        elif letter in titles and "es" in titles[letter]:
            title = titles[letter]["es"]
        elif letter in bodies and lang in bodies[letter]:
            title = bodies[letter][lang].get("title", "Appendix " + letter)
        else:
            title = "Appendix " + letter
        out.append(r"\section{" + _esc(title) + "}")

        if letter in bodies and lang in bodies[letter]:
            b = bodies[letter][lang]
            for sec in b.get("sections", []):
                sec_n = sec.get("n", "")
                sec_body = sec.get("body", "")
                out.append(r"\subsection{" + _esc(sec_n) + " " + _esc(sec.get("title","")) + "}")
                if sec_body:
                    out.append(_wrap_wide_tables(_wrap_display_math(_sanitize_body(sec_body))))
                sec_n_norm = _norm_sec(sec_n)
                for fig in figs_by_sec.get(sec_n_norm, []):
                    out.append(r"\begin{figure}[htbp]")
                    out.append(r"  \centering")
                    out.append(r"  \includegraphics[width=" + FIG_WIDTH + r"]{" + fig["name"] + r".pdf}")
                    out.append(r"  \caption{" + _esc_caption(fig["source"]) + r"}")
                    out.append(r"  \label{fig:" + fig["name"] + r"}")
                    out.append(r"\end{figure}")
        else:
            out.append(r"\textit{(en preparacion)}")

    out.append(r"\newpage")
    return "\n".join(out)



def _problems_table(lang, t, probs):
    lbl = t["labels"][lang]
    out = [r"\section*{" + _esc(lbl["problems_registry"]) + "}", ""]
    out.append(r"\begin{longtable}{@{}p{1.2cm}p{6.5cm}p{1.8cm}p{2cm}@{}}")
    out.append(r"\toprule")
    out.append(r"\textbf{ID} & \textbf{Title} & \textbf{Label} & \textbf{Status} \\")
    out.append(r"\midrule")
    out.append(r"\endhead")
    for p in probs:
        color = {"D": "Dgreen", "P": "Ppurple", "F": "Forange", "A": "Ayellow"}.get(p["label"][0], "black")
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



def _escape_tt(s):
    """Escapa chars peligrosos para uso dentro de \\texttt{}."""
    if not isinstance(s, str):
        s = str(s)
    out = []
    for ch in s:
        if ch == "_":
            out.append("\\_")
        elif ch == "^":
            out.append("\\textasciicircum{}")
        elif ch == "&":
            out.append("\\&")
        elif ch == "#":
            out.append("\\#")
        elif ch == "%":
            out.append("\\%")
        elif ch == "$":
            out.append("\\$")
        elif ch == "~":
            out.append("\\textasciitilde{}")
        elif ch == "{":
            out.append("\\{")
        elif ch == "}":
            out.append("\\}")
        else:
            out.append(ch)
    return "".join(out)


def _patches_table(lang, t, patches):
    lbl = t["labels"][lang]
    sec_title = _esc(lbl["patches"])
    out = [r"\section{" + sec_title + "}",
           r"\addcontentsline{toc}{section}{" + sec_title + "}",
           ""]
    out.append(r"\begin{itemize}[leftmargin=*]")
    for p in patches:
        color = {"D": "Dgreen", "P": "Ppurple", "F": "Forange", "A": "Ayellow"}.get(p["label"][0], "black")
        before_txt = p["before"][:55]
        after_txt = p["after"][:55]
        for bad, good in [("_", "-"), ("^", "*"), ("{", "("), ("}", ")"), ("&", "+"), ("~", " "), ("\\", "/"), ("$", "S"), ("#", "N"), ("%", "pct")]:
            before_txt = before_txt.replace(bad, good)
            after_txt = after_txt.replace(bad, good)
        out.append(
            r"\item \textbf{" + str(p["n"]) + "} (" + _esc(p["stage"]) + "): "
            + _esc(before_txt)
            + r" $\rightarrow$ "
            + _esc(after_txt)
            + r" \textcolor{" + color + r"}{\textbf{[" + p["label"] + "]}}"
        )
    out.append(r"\end{itemize}")
    out.append("")
    out.append(r"\newpage")
    return "\n".join(out)



def _versions_timeline(lang, t, versions):
    lbl = t["labels"][lang]
    out = [r"\section*{" + _esc(lbl["bitacora"]) + "}", ""]
    out.append(r"\begin{itemize}[leftmargin=*]")
    for v in versions["versions"]:
        color = {"D": "Dgreen", "P": "Ppurple", "F": "Forange", "A": "Ayellow"}.get(v["label"][0], "black")
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
        out.append(r"\textbf{Timestamp:} " + _esc(a["timestamp_utc"]) + r" \\")
        out.append(r"\textbf{Chapter of origin:} " + _esc(a["capitulo_origen"]) + r" \\")
        out.append(r"\textbf{Label:} \textcolor{" + color + r"}{\textbf{[" + a["label"] + "]}} \\")
        out.append(r"\textbf{SHA-256:} \texttt{" + a["sha256"][:32] + r"...} \\[0.5em]")
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


def _appendix_bodies(lang, t):
    """Apendices B y K con figuras (v5.4 1e-part-2)."""
    bodies = t.get("appendix_bodies", {})
    if not bodies:
        return ""
    figs_by_sec = _load_figures_by_section()
    fig_label = FIG_LABELS.get(lang, "Figure")
    parts = [r"\newpage", ""]
    for letter in sorted(bodies.keys()):
        b = bodies[letter]
        if lang not in b:
            continue
        parts.append(r"\section*{" + _esc(b[lang].get("title", letter)) + "}")
        parts.append("")
        for sec in b[lang].get("sections", []):
            sec_n = sec.get("n", "")
            parts.append(r"\paragraph{" + _esc(sec_n) + " " + _esc(sec.get("title", "")) + "}")
            parts.append("")
            parts.append(sec.get("body", ""))
            parts.append("")
            sec_n_norm = _norm_sec(sec_n)
            for fig in figs_by_sec.get(sec_n_norm, []):
                parts.append("")
                parts.append(r"\begin{figure}[htbp]")
                parts.append(r"  \centering")
                parts.append(
                    r"  \includegraphics[width=" + FIG_WIDTH + r"]{"
                    + fig["name"] + r".pdf}"
                )
                parts.append(
                    r"  \caption{\textbf{" + fig_label + r":} "
                    + _esc_caption(fig["source"]) + r"}"
                )
                parts.append(r"  \label{fig:" + fig["name"] + r"}")
                parts.append(r"\end{figure}")
                parts.append("")
    return "\n".join(parts)


def _bibliography(lang, t):
    """Inserta bibliografia al final del documento."""
    return "\n".join([
        r"\newpage",
        r"\nocite{*}",
        r"\bibliographystyle{plain}",
        r"\bibliography{thu_references}",
        "",
    ])

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
            entry = (_esc(r["authors"]) + r", \textit{" + _esc(r["title"])
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
    # [v5.4] Eliminada: la bibliografia se genera con \bibliography (con DOIs).
    partes.append(r"\vspace{2em}")
    partes.append(r"\begin{center}")
    partes.append(r"\small")
    partes.append(r"\textit{End of document}")
    partes.append(r"\end{center}")
    partes.append(_bibliography(lang, i18n))
    partes.append(r'\end{document}')

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
        # [v5.4] assert eliminado: bibliografia se genera con \bibliography
        assert "P1" in content, "faltan predicciones"
        assert "A-1" in content, "faltan problemas"
        assert "V5.0" in content or "Anexos" in content or "Annexes" in content, "faltan anexos"
    print("=== TEST OK ===")
    for p in paths:
        print(f"  {p.name}: {p.stat().st_size} B")