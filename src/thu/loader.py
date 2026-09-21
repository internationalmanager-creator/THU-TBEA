"""Carga los JSON de registry/thu/ y expone estructura validada."""
import json
from functools import lru_cache
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
THU_DIR = BASE / "registry" / "thu"


def _load(name):
    p = THU_DIR / name
    if not p.exists():
        raise FileNotFoundError(f"Falta {p}")
    return json.loads(p.read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def project():          return _load("project.json")
@lru_cache(maxsize=None)
def problems():         return _load("problems.json")
@lru_cache(maxsize=None)
def predictions():      return _load("predictions.json")
@lru_cache(maxsize=None)
def patches():          return _load("patches.json")
@lru_cache(maxsize=None)
def versions():         return _load("versions.json")
@lru_cache(maxsize=None)
def epistemic_matrix(): return _load("epistemic_matrix.json")
@lru_cache(maxsize=None)
def glossary():         return _load("glossary.json")
@lru_cache(maxsize=None)
def references():       return _load("references.json")
@lru_cache(maxsize=None)
def prisma():           return _load("prisma.json")
@lru_cache(maxsize=None)
def datasets():         return _load("datasets.json")
@lru_cache(maxsize=None)
def sections():         return _load("sections.json")
@lru_cache(maxsize=None)
def annexes():          return _load("annexes.json")
@lru_cache(maxsize=None)
def changelog():        return _load("changelog.json")


@lru_cache(maxsize=None)
def figure_metadata():
    """Carga el catalogo de metadata de figuras (equation + theory + demo)."""
    p2 = THU_DIR / "figures_metadata.json"
    if not p2.exists():
        return {"figures": {}, "source": None, "note": None}
    return json.loads(p2.read_text(encoding="utf-8"))


def figure_meta(nombre):
    """Devuelve dict {equation, theory, demo} o None si no existe."""
    return figure_metadata().get("figures", {}).get(nombre)


def stats():
    """Resumen cuantitativo para el dashboard."""
    probs = problems()["problems"]
    preds = predictions()["predictions"]
    chg = changelog()
    return {
        "version": project()["version"],
        "problems_total": len(probs),
        "problems_closed": sum(1 for p in probs if p["status"] == "CERRADO"),
        "problems_open":   sum(1 for p in probs if p["status"] == "ABIERTO"),
        "predictions":     len(preds),
        "preds_prereg":    sum(1 for p in preds if p["status"] == "Preregistrada"),
        "patches":         len(patches()["patches"]),
        "versions":        len(versions()["versions"]),
        "refs":            len(references()["refs"]),
        "chapters":        len(sections()["chapters"]),
        "appendices":      len(sections()["appendices"]),
        "prisma_included": prisma()["flow"]["included"],
        "datasets":        len(datasets()["datasets"]),
        "annexes":         len(annexes().get("annexes", [])),
        "retiros":         len(chg["retiros"]),
        "trasplantes":     len(chg["trasplantes"]),
        "etapas":          len(chg["etapas"]),
    }


def clear_cache():
    for f in (project, problems, predictions, patches, versions,
              epistemic_matrix, glossary, references, prisma,
              datasets, sections, annexes, changelog, figure_metadata):
        f.cache_clear()


def label_color(label):
    """Color de cada etiqueta epistemica."""
    if not label:
        return "#636E72"
    return {
        "D": "#00B894",
        "P": "#6C5CE7",
        "F": "#E17055",
        "A": "#FDCB6E",
    }.get(label[0], "#636E72")


def label_name(label, lang="es"):
    first = (label or "P")[0]
    names = {
        "es": {"D": "Derivado", "P": "Postulado", "F": "Frontera", "A": "Analogia"},
        "en": {"D": "Derived", "P": "Postulated", "F": "Frontier", "A": "Analogy"},
        "de": {"D": "Abgeleitet", "P": "Postuliert", "F": "Grenze", "A": "Analogie"},
    }
    return names.get(lang, names["es"]).get(first, first)


def coherencia():
    """Verifica coherencia entre patches/problemas/predicciones/referencias.

    Devuelve (ok, lista_de_errores).
    """
    err = []
    probs = problems()["problems"]
    preds = predictions()["predictions"]
    pats = patches()["patches"]
    refs = references()["refs"]
    proj = project()

    # 17 patches
    if len(pats) != 17:
        err.append(f"patches != 17 (hay {len(pats)})")
    etapas = {}
    for p in pats:
        etapas[p["stage"]] = etapas.get(p["stage"], 0) + 1
    if etapas != {"VII": 7, "VIII": 3, "IX": 3, "X": 4}:
        err.append(f"etapas patches incorrectas: {etapas}")
    if sorted(p["n"] for p in pats) != list(range(1, 18)):
        err.append("numeracion patches con saltos")

    # 17 problemas, 12 cerrados + 5 abiertos
    if len(probs) != 17:
        err.append(f"problems != 17 (hay {len(probs)})")
    cerrados = [p for p in probs if p["status"] == "CERRADO"]
    abiertos = [p for p in probs if p["status"] == "ABIERTO"]
    if len(cerrados) != 12:
        err.append(f"problems cerrados != 12 (hay {len(cerrados)})")
    if len(abiertos) != 5:
        err.append(f"problems abiertos != 5 (hay {len(abiertos)})")

    abiertos_ok = {"A-6": "F", "A-7": "A", "A-15": "F", "A-16": "F", "A-17": "F"}
    for p in abiertos:
        if p["id"] not in abiertos_ok:
            err.append(f"problems: {p['id']} no deberia estar abierto")
        elif p["label"] != abiertos_ok[p["id"]]:
            err.append(f"problems: {p['id']} label {p['label']} incorrecto")

    # P1..P11
    if [p["id"] for p in preds] != [f"P{i}" for i in range(1, 12)]:
        err.append("predictions IDs incorrectos")

    # 68 referencias
    if len(refs) != 68:
        err.append(f"references != 68 (hay {len(refs)})")

    # counters project.json
    if proj.get("patches_total") != 17:
        err.append("project.patches_total != 17")
    if proj.get("problems_total") != 17:
        err.append("project.problems_total != 17")

    return (len(err) == 0, err)


if __name__ == "__main__":
    from tqdm import tqdm
    print("=== Test loader.py ===")
    s = stats()
    for k, v in tqdm(list(s.items()), desc="Stats", ncols=80):
        print(f"  {k:<20} {v}")
    print()
    ok, errs = coherencia()
    if ok:
        print("COHERENCIA OK")
    else:
        print(f"COHERENCIA FALLIDA ({len(errs)} errores):")
        for e in errs:
            print(f"  - {e}")
    assert ok, "coherencia fallida"
    assert s["problems_total"] == 17
    assert s["predictions"] == 11
    assert s["patches"] == 17
    assert s["refs"] == 68
    assert s["chapters"] == 21
    assert s["appendices"] == 10
    assert s["retiros"] == 3
    assert s["trasplantes"] == 15
    assert s["etapas"] == 10
    print("=== TEST OK ===")