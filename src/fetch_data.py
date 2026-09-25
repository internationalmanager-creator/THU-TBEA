"""Descarga de datasets desde inventory_v4.json + queues."""
import argparse
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

BASE = Path(__file__).parent.parent
INVENTORY = BASE / "data" / "inventory" / "inventory_v4.json"
QUEUES_DIR = BASE / "data" / "background"
RAW = BASE / "data" / "raw"
TIMEOUT = 60


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _descargar(url, destino, esperado_bytes=None):
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(destino.suffix + ".part")
    headers = {"User-Agent": "THU-TBEA-fetch/1.0"}
    req = urllib.request.Request(url, headers=headers)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r, open(tmp, "wb") as out:
            tam = 0
            while True:
                chunk = r.read(65536)
                if not chunk:
                    break
                out.write(chunk)
                tam += len(chunk)
    except Exception as e:
        if tmp.exists():
            tmp.unlink()
        return False, "error: " + str(e)[:100], 0
    dt = time.time() - t0
    tmp.replace(destino)
    return True, str(round(dt, 1)) + "s", tam


def _verificar(path, sha256_esperado):
    if not sha256_esperado:
        return path.exists()
    if not path.exists():
        return False
    return _sha256_file(path).lower() == sha256_esperado.lower()


def _cargar_inventario():
    if not INVENTORY.exists():
        print("[FALLA] no existe " + str(INVENTORY))
        sys.exit(1)
    data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    entradas = data.get("entradas", [])
    # Normalizar a schema comun
    out = []
    for e in entradas:
        out.append({
            "id": e.get("id", ""),
            "archivo": e.get("archivo", ""),
            "grupo": e.get("grupo", ""),
            "url": e.get("url", ""),
            "bytes": e.get("bytes", 0),
            "sha256": e.get("sha256", ""),
            "origen": "inventory",
        })
    return out


def _normalizar_queue_item(x, queue_name):
    """Extrae campos de cualquier schema de queue."""
    return {
        "id": "Q-" + queue_name.replace(".json", "") + "-" + str(x.get("f", x.get("filename", "")))[:20],
        "archivo": x.get("f", x.get("filename", "")),
        "grupo": x.get("d", x.get("grupo", "queues")),
        "url": x.get("url", ""),
        "bytes": x.get("esperado", x.get("bytes", x.get("min", 0))),
        "sha256": x.get("sha256", ""),
        "origen": "queue:" + queue_name,
    }


def _cargar_queues():
    if not QUEUES_DIR.exists():
        return []
    out = []
    for f in sorted(QUEUES_DIR.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        items = d if isinstance(d, list) else d.get("items", [])
        for x in items:
            if not x.get("url"):
                continue
            out.append(_normalizar_queue_item(x, f.name))
    return out


def _cargar_todo():
    return _cargar_inventario() + _cargar_queues()


def _destino(entrada):
    grupo = str(entrada.get("grupo", "sin_grupo")).replace("\\", "/")
    archivo = entrada.get("archivo", "sin_nombre")
    if not archivo:
        archivo = "sin_nombre"
    return RAW / grupo / archivo


def listar(entradas):
    inv = [e for e in entradas if e["origen"] == "inventory"]
    qs = [e for e in entradas if e["origen"].startswith("queue")]
    print("=== " + str(len(entradas)) + " entradas ===")
    print("  inventory_v4.json: " + str(len(inv)))
    print("  queues:            " + str(len(qs)))
    print()
    print("--- INVENTORY ---")
    for e in inv:
        dest = _destino(e)
        sha = e.get("sha256", "")
        if dest.exists():
            estado = "OK" if _verificar(dest, sha) else "SHA-FALLA"
        else:
            estado = "FALTA"
        print("  " + str(e.get("id")) + "  [" + estado + "]  " + str(e.get("bytes")) + " B  " + dest.name)
    print()
    print("--- QUEUES (primeros 10) ---")
    for e in qs[:10]:
        dest = _destino(e)
        estado = "OK" if dest.exists() else "FALTA"
        print("  [" + estado + "]  " + str(e.get("bytes")) + " B  " + dest.name)
    if len(qs) > 10:
        print("  ... (" + str(len(qs) - 10) + " mas)")


def bajar(entradas, filtro_origen=None, solo_faltantes=False, dry_run=False):
    if filtro_origen == "inventory":
        entradas = [e for e in entradas if e["origen"] == "inventory"]
    elif filtro_origen == "queues":
        entradas = [e for e in entradas if e["origen"].startswith("queue")]

    n_ok = n_skip = n_fail = 0
    for e in entradas:
        dest = _destino(e)
        sha = e.get("sha256", "")
        if dest.exists() and _verificar(dest, sha):
            n_skip += 1
            continue
        if solo_faltantes and dest.exists():
            n_skip += 1
            continue
        url = e.get("url", "")
        if not url:
            n_fail += 1
            continue
        if dry_run:
            print("  [DRY] " + e["origen"] + "  " + str(dest.name))
            n_ok += 1
            continue
        print("  [BAJAR] " + e["origen"] + "  " + str(dest.name))
        ok, info, tam = _descargar(url, dest, e.get("bytes", 0))
        if not ok:
            print("  [FAIL] " + info)
            n_fail += 1
            continue
        if sha and not _verificar(dest, sha):
            print("  [FAIL] SHA no coincide")
            n_fail += 1
            continue
        print("  [OK] " + str(tam//1024) + " KB  (" + info + ")")
        n_ok += 1
    print()
    print("=== RESUMEN: " + str(n_ok) + " OK, " + str(n_skip) + " skip, " + str(n_fail) + " fallas ===")
    return 0 if n_fail == 0 else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--solo-faltantes", action="store_true")
    ap.add_argument("--inventory", action="store_true", help="solo inventory_v4.json")
    ap.add_argument("--queues", action="store_true", help="solo queues")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    entradas = _cargar_todo()
    if args.listar:
        listar(entradas)
        return
    filtro = None
    if args.inventory: filtro = "inventory"
    if args.queues: filtro = "queues"
    if args.all and not args.queues and not args.inventory:
        filtro = "inventory"
    if args.all or args.solo_faltantes or args.inventory or args.queues:
        sys.exit(bajar(entradas, filtro_origen=filtro,
                       solo_faltantes=args.solo_faltantes,
                       dry_run=args.dry_run))
    ap.print_help()


if __name__ == "__main__":
    main()
