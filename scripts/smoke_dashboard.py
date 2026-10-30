#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke test del dashboard THU: ejecuta app_thu.py headless y recorre las 15 secciones.

Usa streamlit.testing.v1.AppTest: corre el script de verdad, sin navegador.
Reporta excepciones, errores mostrados y cuantas widgets se renderizan por seccion.
"""
import sys
import time
from pathlib import Path

from streamlit.testing.v1 import AppTest

BASE = Path(__file__).resolve().parents[1]

SECCIONES = [
    "overview", "derivations", "problems", "predictions", "patches", "versions",
    "epistemic", "glossary", "refs", "prisma", "datasets", "sections",
    "annexes", "downloads", "figures",
]


def resumen(at):
    return {
        "excepciones": [str(e.value)[:300] for e in at.exception],
        "errores": [str(e.value)[:200] for e in at.error],
        "warnings": [str(w.value)[:200] for w in at.warning],
        "markdown": len(at.markdown),
        "dataframes": len(at.dataframe),
        "plotly": len(at.get("plotly_chart")) if hasattr(at, "get") else "n/a",
        "latex": len(at.latex),
        "imagenes": len(at.get("imgs")) if hasattr(at, "get") else "n/a",
    }


def main():
    t0 = time.time()
    at = AppTest.from_file(str(BASE / "app_thu.py"), default_timeout=600)
    at.run()
    r = resumen(at)
    print("INICIAL (overview): %.1f s" % (time.time() - t0))
    print("  excepciones:", r["excepciones"] or "ninguna")
    print("  errores    :", r["errores"] or "ninguno")
    print("  warnings   :", r["warnings"][:3] or "ninguno")
    print(f"  widgets    : markdown={r['markdown']} dataframe={r['dataframes']} latex={r['latex']}")

    fallas = []
    for sid in SECCIONES:
        botones = [b for b in at.sidebar.button if getattr(b, "key", None) == f"btn_{sid}"]
        if not botones:
            print(f"\n[{sid}] SIN BOTON en el sidebar")
            fallas.append((sid, "sin boton"))
            continue
        t1 = time.time()
        botones[0].click()
        at.run()
        r = resumen(at)
        estado = "OK" if not r["excepciones"] and not r["errores"] else "FALLA"
        print(f"\n[{sid}] {estado}  ({time.time()-t1:.1f} s)  markdown={r['markdown']} "
              f"df={r['dataframes']} latex={r['latex']}")
        if r["excepciones"]:
            print("  excepciones:", r["excepciones"])
            fallas.append((sid, r["excepciones"][0]))
        if r["errores"]:
            print("  errores:", r["errores"])
            fallas.append((sid, "error: " + r["errores"][0]))
        if r["warnings"]:
            print("  warnings:", r["warnings"][:2])
        if not r["excepciones"] and not r["errores"] and r["markdown"] < 3:
            print("  OJO: muy poco contenido renderizado")

    print("\n" + "=" * 70)
    print("TOTAL: %.1f s" % (time.time() - t0))
    if fallas:
        print("SECCIONES CON PROBLEMAS:")
        for sid, msg in fallas:
            print("  -", sid, ":", msg)
    else:
        print("Las 15 secciones corrieron sin excepciones ni errores.")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
