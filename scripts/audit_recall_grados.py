#!/usr/bin/env python3
"""Auditoria de recall #2: sin_beta cuyo abstract menciona birefringence /
rotation angle / parity y contiene numeros con grados o +- cerca.
Solo lee; imprime contexto para revision manual.
"""
import io
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
RAW = os.path.join(ROOT, "registry", "prisma", "raw_exports")

TRIGGER = re.compile(r"birefring|rotation angle|rotat\w+ (?:angle|plane)|parity-violat", re.I)
ANGLENUM = re.compile(
    r"[-+]?\d+(?:\.\d+)?\s*(?:\\ifmmode\^\\circ|\\textdegree|\u00b0|\\deg|deg\b|degree)"
    r"|[-+]?\d+(?:\.\d+)?\s*\u00b1",
    re.I,
)


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
    hits = []
    for e in out["sin_beta"]:
        d = norm_doi(e["doi"])
        a = src.get(d, {}).get("abstract") or ""
        if not TRIGGER.search(a):
            continue
        ms = list(ANGLENUM.finditer(a))
        if not ms:
            continue
        # exigir cercania (<120 chars) entre trigger y numero angular
        tg = [m.start() for m in TRIGGER.finditer(a)]
        close = []
        for m in ms:
            if any(abs(m.start() - t) < 140 for t in tg):
                close.append(m.group(0))
        if close:
            ctx = a[max(0, ms[0].start() - 130) : ms[0].end() + 130].replace("\n", " ")
            hits.append((d, close[:4], ctx))
    print("candidatos:", len(hits))
    print()
    for d, nums, ctx in hits:
        print("-", d, "| nums:", nums)
        print("   ", ctx)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
