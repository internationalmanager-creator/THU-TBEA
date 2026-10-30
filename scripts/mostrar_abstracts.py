#!/usr/bin/env python3
"""Imprime el abstract completo de los DOIs pasados por argumento."""
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


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    src = {norm(p["doi"]): p for p in json.load(io.open(os.path.join(RAW, "para_harness.json"), encoding="utf-8"))}
    out = {
        norm(e["doi"]): e
        for e in json.load(io.open(os.path.join(RAW, "prisma_extraccion_llm.json"), encoding="utf-8"))["con_beta"]
    }
    for arg in sys.argv[1:]:
        d = norm(arg)
        p = src.get(d)
        if not p:
            print("NO EXISTE:", arg)
            continue
        print("=" * 100)
        print(d, "| extraido: beta=%s sigma=%s" % (out.get(d, {}).get("beta"), out.get(d, {}).get("sigma")))
        print(re.sub(r"\s+", " ", p.get("abstract", "")))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
