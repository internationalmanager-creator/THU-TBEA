#!/usr/bin/env python3
"""Resumen estadistico del JSON final de extraccion."""
import io
import json
import os
import statistics
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(os.path.dirname(BASE), "registry", "prisma", "raw_exports")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    d = json.load(io.open(os.path.join(RAW, "prisma_extraccion_llm.json"), encoding="utf-8"))
    con, sin = d["con_beta"], d["sin_beta"]
    betas = [e["beta"] for e in con]
    with_s = [e["beta"] for e in con if e["sigma"] is not None]
    print("papers totales      :", len(con) + len(sin))
    print("con_beta            :", len(con))
    print("sin_beta            :", len(sin))
    print("con sigma numerico  :", len(with_s))
    print("sin sigma           :", len(con) - len(with_s))
    print("beta: min/mediana/max = %.3f / %.3f / %.3f" % (min(betas), statistics.median(betas), max(betas)))
    if with_s:
        print(
            "solo con sigma: min/mediana/max = %.3f / %.3f / %.3f"
            % (min(with_s), statistics.median(with_s), max(with_s))
        )
    print("en rango 0.2-0.4    :", sum(1 for b in betas if 0.2 <= b <= 0.4))
    print("betas ordenados     :", ", ".join("%g" % b for b in sorted(betas)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
