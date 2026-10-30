#!/usr/bin/env python3
"""Merge de las partes _partN.json en prisma_extraccion_llm.json + auditoria.

- Valida estructura de cada parte.
- Verifica cobertura exacta de DOIs contra para_harness.json (251).
- Audita anti-alucinacion: cada numero del snippet y el valor de beta deben
  aparecer en el abstract original.
- Escribe el JSON final con el esquema pedido por el usuario.
"""
import io
import json
import os
import re
import sys
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
RAW = os.path.join(ROOT, "registry", "prisma", "raw_exports")

RAZON = "No se encontro valor numerico de beta"
PARTS = [os.path.join(RAW, "_part%d.json" % i) for i in range(1, 7)]


def load(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def norm_doi(doi):
    d = (doi or "").strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return d


def norm_text(s):
    s = s or ""
    s = s.replace("\u00a0", " ")
    s = unicodedata.normalize("NFKC", s)
    return s


def numbers_in(text):
    return re.findall(r"\d+(?:[.,]\d+)?", text or "")


def fmt_variants(x):
    """Formas textuales plausibles de un float en el abstract."""
    out = set()
    for v in (x, abs(x)):
        out.add(("%g" % v))
        out.add(("%.1f" % v))
        out.add(("%.2f" % v))
        out.add(("%.3f" % v))
        out.add(("%.4f" % v))
        s = ("%g" % v).replace(".", ",")
        out.add(s)
    return {s for s in out if s}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    src = load(os.path.join(RAW, "para_harness.json"))
    src_by_doi = {}
    order = {}
    for i, p in enumerate(src):
        d = norm_doi(p.get("doi"))
        src_by_doi[d] = p
        order[d] = i

    problems = []
    con, sin = [], []
    seen = {}

    for path in PARTS:
        name = os.path.basename(path)
        if not os.path.exists(path):
            problems.append("FALTA %s" % name)
            continue
        try:
            part = load(path)
        except Exception as exc:  # noqa: BLE001
            problems.append("JSON INVALIDO en %s: %s" % (name, exc))
            continue
        for key in ("con_beta", "sin_beta"):
            if key not in part or not isinstance(part[key], list):
                problems.append("%s: falta lista %s" % (name, key))

        for e in part.get("con_beta", []):
            d = norm_doi(e.get("doi"))
            if d in seen:
                problems.append("DOI DUPLICADO %s (%s y %s)" % (d, seen[d], name))
                continue
            seen[d] = name
            beta = e.get("beta")
            sigma = e.get("sigma")
            if not isinstance(beta, (int, float)) or isinstance(beta, bool):
                problems.append("%s: beta no numerico en %s (%r)" % (name, d, beta))
                continue
            if sigma is not None and not isinstance(sigma, (int, float)):
                problems.append("%s: sigma no numerico en %s (%r)" % (name, d, sigma))
                sigma = None
            con.append(
                {
                    "_doi": d,
                    "doi": e.get("doi"),
                    "titulo": e.get("titulo"),
                    "beta": float(beta),
                    "sigma": None if sigma is None else float(sigma),
                    "abstract_snippet": e.get("abstract_snippet") or "",
                    "_part": name,
                }
            )

        for e in part.get("sin_beta", []):
            d = norm_doi(e.get("doi"))
            if d in seen:
                problems.append("DOI DUPLICADO %s (%s y %s)" % (d, seen[d], name))
                continue
            seen[d] = name
            sin.append(
                {"doi": e.get("doi"), "titulo": e.get("titulo"), "razon": RAZON, "_doi": d, "_part": name}
            )

    # cobertura
    src_dois = set(src_by_doi)
    out_dois = set(seen)
    missing = sorted(src_dois - out_dois)
    extra = sorted(out_dois - src_dois)
    if missing:
        problems.append("FALTAN %d DOIs del input: %s" % (len(missing), missing[:10]))
    if extra:
        problems.append("%d DOIs que no estan en el input: %s" % (len(extra), extra[:10]))

    # titulos verbatim
    for e in con + sin:
        d = e["_doi"]
        if d in src_by_doi:
            st = src_by_doi[d].get("titulo")
            if (e.get("titulo") or "").strip() != (st or "").strip():
                problems.append("TITULO distinto en %s: %r != %r" % (d, e.get("titulo"), st))

    # auditoria de snippets y de beta contra el abstract
    bad_snippet, beta_not_found, no_sigma = [], [], []
    for e in con:
        d = e["_doi"]
        abs_ = norm_text(src_by_doi.get(d, {}).get("abstract", ""))
        snip = norm_text(e["abstract_snippet"])
        if not snip.strip():
            bad_snippet.append((d, ["SNIPPET-VACIO"], ""))
            continue
        if True:
            nums = numbers_in(snip)
            abs_nums = set(numbers_in(abs_))
            flat_abs = abs_.replace(",", ".")
            flat_snip = snip.replace(",", ".")
            miss = [n for n in nums if n.replace(",", ".") not in abs_nums and n.replace(",", ".") not in flat_abs]
            # solapamiento de palabras (el abstract puede tener LaTeX, no exigimos substring)
            toks = [t for t in re.findall(r"[a-z]{4,}", flat_snip)]
            abs_toks = set(re.findall(r"[a-z]{3,}", flat_abs))
            hit = sum(1 for t in toks if t in abs_toks)
            frac = (hit / len(toks)) if toks else 0.0
            if miss or frac < 0.6:
                bad_snippet.append((d, miss or ["BAJO-SOLAPAMIENTO:%.2f" % frac], snip[:110]))
        variants = fmt_variants(e["beta"])
        hay = any(v in abs_ or v in abs_.replace(",", ".") for v in variants)
        if not hay:
            beta_not_found.append((d, e["beta"], snip[:110]))
        if e["sigma"] is None:
            no_sigma.append(d)

    # salida final en orden de aparicion del input
    con_sorted = sorted(con, key=lambda e: order.get(e["_doi"], 10**6))
    sin_sorted = sorted(sin, key=lambda e: order.get(e["_doi"], 10**6))
    out = {
        "con_beta": [
            {
                "doi": e["doi"],
                "titulo": e["titulo"],
                "beta": e["beta"],
                "sigma": e["sigma"],
                "abstract_snippet": e["abstract_snippet"],
            }
            for e in con_sorted
        ],
        "sin_beta": [{"doi": e["doi"], "titulo": e["titulo"], "razon": e["razon"]} for e in sin_sorted],
    }
    dest = os.path.join(RAW, "prisma_extraccion_llm.json")
    with io.open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print("=== RESULTADO ===")
    print("input papers      :", len(src))
    print("con_beta          :", len(out["con_beta"]))
    print("sin_beta          :", len(out["sin_beta"]))
    print("total escrito     :", len(out["con_beta"]) + len(out["sin_beta"]))
    print("sigma presente    :", sum(1 for e in out["con_beta"] if e["sigma"] is not None))
    print("sigma null        :", len(no_sigma))
    print("escrito           :", dest)
    print()
    print("=== PROBLEMAS DE ESTRUCTURA/COBERTURA (%d) ===" % len(problems))
    for p in problems:
        print(" -", p)
    print()
    print("=== SNIPPETS SOSPECHOSOS (%d) ===" % len(bad_snippet))
    for d, miss, s in bad_snippet:
        print(" -", d, "| faltan:", miss, "|", s)
    print()
    print("=== BETA NO ENCONTRADO LITERAL EN EL ABSTRACT (%d) ===" % len(beta_not_found))
    for d, b, s in beta_not_found:
        print(" -", d, "| beta=", b, "|", s)
    print()
    print("=== SIGMA NULL (%d) ===" % len(no_sigma))
    print(", ".join(no_sigma))
    return 0 if not (missing or extra or problems) else 1


if __name__ == "__main__":
    sys.exit(main())
