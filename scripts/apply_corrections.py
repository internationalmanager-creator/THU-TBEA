#!/usr/bin/env python3
"""Aplica correcciones puntuales sobre los _partN.json (idempotente).

Lee _correcciones.json:
  [{"doi": "...", "to": "sin_beta"}]                 -> mueve a sin_beta
  [{"doi": "...", "to": "con_beta", "beta": 0.1,
    "sigma": null, "abstract_snippet": "..."}]       -> mueve/actualiza en con_beta

Busca el DOI en cualquiera de las partes. Imprime qué hizo.
"""
import io
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
RAW = os.path.join(ROOT, "registry", "prisma", "raw_exports")
RAZON = "No se encontro valor numerico de beta"


def norm(d):
    d = (d or "").strip().lower()
    return __import__("re").sub(r"^https?://(dx\.)?doi\.org/", "", d)


def load(p):
    with io.open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def dump(p, data):
    with io.open(p, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    corr = load(os.path.join(RAW, "_correcciones.json"))
    parts = [os.path.join(RAW, "_part%d.json" % i) for i in range(1, 7)]
    loaded = {p: load(p) for p in parts if os.path.exists(p)}

    for c in corr:
        target = norm(c["doi"])
        # 1) localizar la parte dueña: preferir la que lo tiene en con_beta
        owner = None
        for p, data in loaded.items():
            if any(norm(e.get("doi")) == target for e in data["con_beta"]):
                owner = p
                break
        if owner is None:
            for p, data in loaded.items():
                if any(norm(e.get("doi")) == target for e in data["sin_beta"]):
                    owner = p
                    break
        if owner is None:
            print("!! no encontrado en ninguna parte:", c["doi"])
            continue
        # 2) borrarlo de TODAS las partes (dedupe)
        for p, data in loaded.items():
            data["con_beta"] = [e for e in data["con_beta"] if norm(e.get("doi")) != target]
            data["sin_beta"] = [e for e in data["sin_beta"] if norm(e.get("doi")) != target]
        # 3) insertarlo en la parte dueña
        data = loaded[owner]
        if c["to"] == "sin_beta":
            titulo = c.get("titulo")
            if not titulo:
                orig = load(os.path.join(RAW, "para_harness.json"))
                titulo = next((o["titulo"] for o in orig if norm(o.get("doi")) == target), "")
            data["sin_beta"].append({"doi": c["doi"], "titulo": titulo, "razon": RAZON})
            print("-> sin_beta:", c["doi"], "en", os.path.basename(owner))
        else:
            titulo = c.get("titulo")
            if not titulo:
                orig = load(os.path.join(RAW, "para_harness.json"))
                titulo = next((o["titulo"] for o in orig if norm(o.get("doi")) == target), "")
            data["con_beta"].append(
                {
                    "doi": c["doi"],
                    "titulo": titulo,
                    "beta": c["beta"],
                    "sigma": c.get("sigma"),
                    "abstract_snippet": c.get("abstract_snippet", ""),
                }
            )
            print("-> con_beta:", c["doi"], "en", os.path.basename(owner))

    for p, data in loaded.items():
        dump(p, data)
        print("escrito", os.path.basename(p), "con_beta=%d sin_beta=%d" % (len(data["con_beta"]), len(data["sin_beta"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
