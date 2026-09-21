"""Pre-registro de hipotesis (inmutable una vez bloqueado).

Ciclo de vida:
    borrador  -> editable
    bloqueado -> hash fijo, NO editable (base del test)
    testeado  -> se anade resultado, hash del test
    falsado | confirmado -> estado final

Regla Popperiana:
    Sin criterio de falsacion explicito -> la hipotesis NO se puede bloquear.
    Sin bloqueo -> el test no vale (HARKing).

Uso:
    python src/preregistro.py nuevo H-2026-001 --titulo "..." --categoria geofisica
    python src/preregistro.py editar H-2026-001 hipotesis "..."
    python src/preregistro.py bloquear H-2026-001
    python src/preregistro.py testear H-2026-001 --script src/investigaciones/H-2026-001.py
    python src/preregistro.py verificar H-2026-001
    python src/preregistro.py listar
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE / "src"))
import db_manager

PREREG_DIR = BASE / "registry" / "preregistro"

PLANTILLA = {
    "id": "",
    "titulo": "",
    "categoria": "",
    "estatus": "borrador",
    "hipotesis": "",
    "criterio_falsacion": "",
    "prediccion_cuantitativa": "",
    "test_estadistico": "",
    "parametros_test": {},
    "umbral_significancia": 0.05,
    "datos_requeridos": {
        "n_minimo": 0,
        "categoria_fuente": "",
        "criterios_inclusion": [],
        "criterios_exclusion": [],
    },
    "riesgos_conocidos": [],
    "analisis_secundarios": [],
    "timestamp_creacion_utc": "",
    "timestamp_bloqueo_utc": None,
    "hash_bloqueo": None,
    "resultado": None,
}


def _ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha(d):
    canonico = json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canonico.encode("utf-8")).hexdigest()


def _hash_sin_bloqueo(d):
    """Hash canonico del preregistro excluyendo los campos que cambian."""
    copia = {k: v for k, v in d.items()
             if k not in ("hash_bloqueo", "timestamp_bloqueo_utc", "resultado", "estatus")}
    return _sha(copia)


def _path(hid):
    return PREREG_DIR / f"{hid}.json"


def _cargar(hid):
    p = _path(hid)
    if not p.exists():
        raise FileNotFoundError(f"No existe pre-registro {hid}")
    return json.loads(p.read_text(encoding="utf-8"))


def _guardar(d):
    PREREG_DIR.mkdir(parents=True, exist_ok=True)
    p = _path(d["id"])
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n",
                 encoding="utf-8", newline="\n")


def _siguiente_id(categoria):
    PREREG_DIR.mkdir(parents=True, exist_ok=True)
    year = datetime.now(timezone.utc).year
    existentes = sorted(PREREG_DIR.glob(f"H-{year}-*.json"))
    n = 1
    if existentes:
        ult = existentes[-1].stem.split("-")[-1]
        try:
            n = int(ult) + 1
        except ValueError:
            n = 1
    return f"H-{year}-{n:03d}"

# === PARTE 2 se agrega a continuacion ===

# ============================================================
# Comandos
# ============================================================

def nuevo(hid, titulo=None, categoria=None):
    if hid is None:
        hid = _siguiente_id(categoria)
    if _path(hid).exists():
        raise FileExistsError(f"Ya existe {hid}")
    d = dict(PLANTILLA)
    d["id"] = hid
    d["titulo"] = titulo or "(titulo pendiente)"
    d["categoria"] = categoria or "otros"
    d["timestamp_creacion_utc"] = _ts()
    _guardar(d)
    db_manager.inicializar_db()
    db_manager.registrar_evento(
        "preregistro_creado",
        f"Pre-registro {hid} creado (categoria={categoria})",
        entidad_id=hid,
        payload={"titulo": d["titulo"], "categoria": d["categoria"]},
    )
    print(f"OK: {_path(hid).relative_to(BASE)}")
    print(f"Editar: python src/preregistro.py editar {hid} <campo> <valor>")
    return d


def editar(hid, campo=None, valor=None):
    """Edicion por campo. Si no se pasan, devuelve el JSON completo."""
    d = _cargar(hid)
    if d["estatus"] != "borrador":
        raise PermissionError(
            f"{hid} esta en estado '{d['estatus']}' — solo se editan borradores. "
            f"Para modificar uno bloqueado, crea uno nuevo que lo reemplace."
        )
    if campo and valor is not None:
        # Soporta notacion con punto (parametros_test.alpha)
        partes = campo.split(".")
        cur = d
        for p in partes[:-1]:
            if p not in cur or not isinstance(cur[p], dict):
                cur[p] = {}
            cur = cur[p]
        try:
            v = json.loads(valor)
        except json.JSONDecodeError:
            v = valor
        cur[partes[-1]] = v
        _guardar(d)
        print(f"OK: {campo} = {v!r}")
    else:
        print(json.dumps(d, indent=2, ensure_ascii=False))
    return d


def bloquear(hid):
    """Fija el hash de la hipotesis. Inmutable desde aqui."""
    d = _cargar(hid)
    if d["estatus"] != "borrador":
        raise PermissionError(f"{hid} ya esta en estado '{d['estatus']}'")

    # Validacion: campos obligatorios antes de bloquear
    faltantes = []
    for c in ("titulo", "categoria", "hipotesis", "criterio_falsacion",
              "prediccion_cuantitativa", "test_estadistico"):
        if not d.get(c):
            faltantes.append(c)
    if not d.get("parametros_test"):
        faltantes.append("parametros_test")
    if not d["datos_requeridos"].get("n_minimo"):
        faltantes.append("datos_requeridos.n_minimo")
    if faltantes:
        raise ValueError(
            "No se puede bloquear. Faltan:\n  - " + "\n  - ".join(faltantes)
        )

    d["estatus"] = "bloqueado"
    d["timestamp_bloqueo_utc"] = _ts()
    d["hash_bloqueo"] = _hash_sin_bloqueo(d)
    _guardar(d)

    db_manager.inicializar_db()
    db_manager.registrar_evento(
        "preregistro_bloqueado",
        f"Pre-registro {hid} BLOQUEADO (hash={d['hash_bloqueo'][:16]}...)",
        entidad_id=hid,
        payload={
            "hash_bloqueo": d["hash_bloqueo"],
            "test_estadistico": d["test_estadistico"],
            "umbral": d["umbral_significancia"],
        },
    )
    print(f"OK: {hid} BLOQUEADO")
    print(f"hash_bloqueo: {d['hash_bloqueo']}")
    print(f"Este hash es la base del test. Cualquier cambio posterior invalida la hipotesis.")
    return d

# === PARTE 3 se agrega a continuacion ===

def testear(hid, script=None, resultado_json=None):
    """Ejecuta el test pre-declarado y registra el resultado."""
    d = _cargar(hid)
    if d["estatus"] not in ("bloqueado",):
        raise PermissionError(f"{hid} debe estar 'bloqueado' antes de testear")

    # Verificar que el hash del preregistro no cambio
    actual = _hash_sin_bloqueo(d)
    if actual != d["hash_bloqueo"]:
        raise RuntimeError(
            f"Hash del pre-registro cambio. Esperado {d['hash_bloqueo'][:16]}, "
            f"actual {actual[:16]}. El preregistro fue alterado despues del bloqueo."
        )

    if resultado_json:
        res = json.loads(Path(resultado_json).read_text(encoding="utf-8"))
    elif script:
        import subprocess
        import re
        print(f"Ejecutando {script} ...")
        r = subprocess.run([sys.executable, script], capture_output=True, text=True)
        print(r.stdout)
        if r.returncode != 0:
            print(r.stderr, file=sys.stderr)
            raise RuntimeError(f"El test fallo con rc={r.returncode}")
        # El script debe imprimir un JSON entre marcadores
        m = re.search(r"===RESULT_JSON===\s*(\{.*?\})\s*===END===", r.stdout, re.DOTALL)
        if not m:
            raise RuntimeError("El script no emitio ===RESULT_JSON=== ... ===END===")
        res = json.loads(m.group(1))
    else:
        raise ValueError("Debe especificar --script o --resultado-json")

    d["estatus"] = "testeado"
    d["resultado"] = {
        "timestamp_utc": _ts(),
        "datos": res,
        "veredicto": res.get("veredicto", "indeterminado"),
    }
    _guardar(d)

    db_manager.registrar_evento(
        "preregistro_testeado",
        f"Pre-registro {hid} testeado -> {d['resultado']['veredicto']}",
        entidad_id=hid,
        payload={
            "veredicto": d["resultado"]["veredicto"],
            "hash_bloqueo": d["hash_bloqueo"],
            "resultado": res,
        },
    )
    print(f"OK: {hid} -> {d['resultado']['veredicto']}")
    return d


def verificar(hid):
    d = _cargar(hid)
    if d["estatus"] == "borrador":
        print(f"{hid}: borrador (no bloqueado, sin hash)")
        return True
    actual = _hash_sin_bloqueo(d)
    ok = actual == d["hash_bloqueo"]
    print(f"{hid}: {'OK' if ok else 'ALTERADO'}")
    print(f"  hash_bloqueo: {d['hash_bloqueo']}")
    print(f"  hash_actual:  {actual}")
    return ok


def listar():
    PREREG_DIR.mkdir(parents=True, exist_ok=True)
    archivos = sorted(PREREG_DIR.glob("H-*.json"))
    if not archivos:
        print("(sin pre-registros)")
        return
    print(f"{'ID':<14} {'CATEGORIA':<16} {'ESTATUS':<12} TITULO")
    print("-" * 90)
    for a in archivos:
        d = json.loads(a.read_text(encoding="utf-8"))
        print(f"{d['id']:<14} {d['categoria']:<16} {d['estatus']:<12} {d['titulo'][:45]}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("nuevo")
    n.add_argument("id", nargs="?", default=None)
    n.add_argument("--titulo", default=None)
    n.add_argument("--categoria", default=None)

    e = sub.add_parser("editar")
    e.add_argument("id")
    e.add_argument("campo", nargs="?", default=None)
    e.add_argument("valor", nargs="?", default=None)

    b = sub.add_parser("bloquear")
    b.add_argument("id")

    t = sub.add_parser("testear")
    t.add_argument("id")
    t.add_argument("--script", default=None)
    t.add_argument("--resultado-json", default=None)

    v = sub.add_parser("verificar")
    v.add_argument("id")

    sub.add_parser("listar")

    args = ap.parse_args()
    try:
        if args.cmd == "nuevo":
            nuevo(args.id, args.titulo, args.categoria)
        elif args.cmd == "editar":
            editar(args.id, args.campo, args.valor)
        elif args.cmd == "bloquear":
            bloquear(args.id)
        elif args.cmd == "testear":
            testear(args.id, args.script, args.resultado_json)
        elif args.cmd == "verificar":
            sys.exit(0 if verificar(args.id) else 1)
        elif args.cmd == "listar":
            listar()
    except (FileNotFoundError, FileExistsError, PermissionError, ValueError, RuntimeError) as ex:
        print(f"ERROR: {ex}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()