#!/usr/bin/env python3
"""Muestra cada fila con_beta junto al fragmento del abstract donde aparece beta,
para verificacion visual. Solo lee."""
import io
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
RAW = os.path.join(ROOT, "registry", "prisma", "raw_exports")


def norm(d):
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
    src = {norm(p["doi"]): p for p in load(os.path.join(RAW, "para_harness.json"))}
    out = load(os.path.join(RAW, "prisma_extraccion_llm.json"))
    for i, e in enumerate(out["con_beta"], 1):
        a = src[norm(e["doi"])].get("abstract", "")
        m = re.search(r"(\\beta|\bbeta\b|\u03b2|\bdegrees?\b|\u00b0)", a, re.I)
        start = max(0, (m.start() if m else 0) - 120)
        ctx = re.sub(r"\s+", " ", a[start : start + 320])
        print("%02d. %s" % (i, e["doi"]))
        print("    beta=%s sigma=%s" % (e["beta"], e["sigma"]))
        print("    ABSTRACT: ...%s..." % ctx)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
