#!/usr/bin/env python3
"""Auditoria de recall: busca patrones de beta numerico en los abstracts
marcados como sin_beta y muestra el contexto para revision manual.
Solo lee; no escribe nada.
"""
import io
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
RAW = os.path.join(ROOT, "registry", "prisma", "raw_exports")

PATTERNS = [
    r"\\beta",
    r"\bbeta\b",
    r"\u03b2",
]

NUM_NEAR = [
    r"[=~<>]\s*[-+]?\d",
    r"\d+(?:[.,]\d+)?\s*(?:\\ifmmode\^\\circ|\\textdegree|\u00b0|deg\b|degree)",
    r"\u00b1",
]


def norm_doi(d):
    d = (d or "").strip().lower()
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", d)


def load(p):
    with io.open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    src = {norm_doi(p["doi"]): p for p in load(os.path.join(RAW, "para_harness.json"))}
    out = load(os.path.join(RAW, "prisma_extraccion_llm.json"))
    con_dois = {norm_doi(e["doi"]) for e in out["con_beta"]}

    hits = []
    for e in out["sin_beta"]:
        d = norm_doi(e["doi"])
        a = src.get(d, {}).get("abstract") or ""
        if not a.strip():
            continue
        has_beta = any(re.search(p, a, re.I) for p in PATTERNS)
        if not has_beta:
            continue
        # recortes alrededor de cada mencion de beta
        for m in re.finditer(r"(\\beta|\bbeta\b|\u03b2)", a, re.I):
            ctx = a[max(0, m.start() - 90) : m.end() + 110].replace("\n", " ")
            if any(re.search(p, ctx, re.I) for p in NUM_NEAR):
                hits.append((d, ctx))
                break
    print("sin_beta con posible beta numerico:", len(hits))
    print("con_beta total:", len(con_dois), "| sin_beta total:", len(out["sin_beta"]))
    print()
    for d, ctx in hits:
        print("-", d)
        print("   ", ctx)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
