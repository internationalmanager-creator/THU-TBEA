"""Manifest SHA-256 con CADENA de hashes + firma GPG opcional.

Cada archivo tiene ademas un `chain_hash`:
    chain_i = SHA256(chain_{i-1} || sha256_i)
    chain_0 = SHA256("GENESIS")

Reordenar/eliminar archivos rompe la cadena.

El `manifest_sha256` se calcula sobre JSON canonico (sort_keys=True).

Uso:
    python src/hash_manifest.py 0.7.0 [--sign] [--anchor] [--out PATH]
    python src/hash_manifest.py --verify seeds/seed_v0.7.0_YYYYMMDD.json
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE / "src"))

GENESIS = "GENESIS"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_string(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _chain(prev, cur):
    return hashlib.sha256(f"{prev}|{cur}".encode("utf-8")).hexdigest()


def walk_files(root,
               include_ext=(".py", ".csv", ".json", ".md", ".txt", ".toml", ".lock"),
               include_names={".gitignore"},
               exclude_dirs={"venv", "__pycache__", ".git",
                             "outputs", "seeds", ".ipynb_checkpoints",
                             ".pytest_cache", ".streamlit"}):
    root = Path(root)
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        if any(part in exclude_dirs for part in path.parts):
            continue
        if path.name in include_names or path.suffix in include_ext:
            yield path


def _json_canonico(d):
    return json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True)


def _firmar_gpg(sums_path):
    """Intenta firmar SHA256SUMS.txt con GPG. Devuelve True si exito."""
    if shutil.which("gpg") is None:
        print("AVISO: gpg no encontrado; se omite firma")
        return False
    try:
        subprocess.run(
            ["gpg", "--armor", "--detach-sign", "--yes", str(sums_path)],
            check=True, capture_output=True,
        )
        print(f"Firma: {sums_path}.asc")
        return True
    except subprocess.CalledProcessError as e:
        print(f"AVISO: fallo la firma GPG: {e.stderr.decode(errors='replace')}")
        return False


def _anclar_evento(manifest, version, db_path=None):
    """Ancla el manifest en la tabla eventos."""
    try:
        import db_manager
        db_manager.inicializar_db(db_path)
        db_manager.registrar_evento(
            "manifest",
            f"Manifest v{version} generado (chain_root={manifest['chain_root'][:16]}...)",
            entidad_id=None,
            payload={
                "manifest_sha256": manifest["manifest_sha256"],
                "chain_root": manifest["chain_root"],
                "file_count": manifest["file_count"],
                "version": version,
            },
            db_path=db_path,
        )
        print("Anclado en tabla eventos")
        return True
    except Exception as e:
        print(f"AVISO: no se pudo anclar: {e}")
        return False


def generar_manifest(root=".", version="0.7.0", output=None,
                     firmar=False, anclar=False, db_path=None):
    root = Path(root).resolve()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    files = list(walk_files(root))

    entries = []
    chain = GENESIS
    with tqdm(total=len(files), desc="Hashing", ncols=80) as pbar:
        for path in files:
            rel = path.relative_to(root).as_posix()
            h = sha256_file(path)
            chain = _chain(chain, h)
            entries.append({
                "path": rel,
                "sha256": h,
                "size_bytes": path.stat().st_size,
                "chain_hash": chain,
            })
            pbar.update(1)
            pbar.set_postfix_str(rel[-30:])

    manifest = {
        "version": version,
        "generated_at_utc": ts,
        "root": str(root),
        "algorithm": "SHA-256",
        "chain_algorithm": "SHA256(prev_chain || file_sha256), genesis=SHA256('GENESIS')",
        "file_count": len(entries),
        "chain_root": chain,
        "files": entries,
    }
    canonico = _json_canonico(manifest)
    manifest["manifest_sha256"] = sha256_string(canonico)

    if output is None:
        date = ts[:10].replace("-", "")
        output = root / "seeds" / f"seed_v{version}_{date}.json"
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(_json_canonico(manifest), encoding="utf-8", newline="\n")

    # SHA256SUMS.txt
    sums_path = output.parent / "SHA256SUMS.txt"
    with open(sums_path, "w", encoding="utf-8", newline="\n") as f:
        for e in entries:
            f.write(f"{e['sha256']}  {e['path']}\n")

    # Firma GPG opcional
    if firmar:
        _firmar_gpg(sums_path)

    # Anclaje en la cadena cronografica
    if anclar:
        _anclar_evento(manifest, version, db_path)

    print(f"Manifest: {output}")
    print(f"Manifest SHA-256: {manifest['manifest_sha256']}")
    print(f"Chain root:       {chain}")
    print(f"Files:            {manifest['file_count']}")
    return manifest


def verificar_manifest(path, root="."):
    """Recalcula hashes y cadena desde el manifest. Devuelve (ok, errores)."""
    root = Path(root).resolve()
    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    errores = []

    copia = {k: v for k, v in manifest.items() if k != "manifest_sha256"}
    canonico = _json_canonico(copia)
    if sha256_string(canonico) != manifest["manifest_sha256"]:
        errores.append("manifest_sha256 no coincide con el contenido")

    chain = GENESIS
    for e in tqdm(manifest["files"], desc="Verificando", ncols=80):
        p = root / e["path"]
        if not p.exists():
            errores.append(f"FALTA: {e['path']}")
            continue
        h = sha256_file(p)
        if h != e["sha256"]:
            errores.append(f"HASH DISTINTO: {e['path']}")
        chain = _chain(chain, h)
        if chain != e["chain_hash"]:
            errores.append(f"CADENA ROTA en {e['path']}")
    if chain != manifest["chain_root"]:
        errores.append("chain_root final no coincide")
    return (len(errores) == 0, errores)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("version", nargs="?", default="0.7.0")
    ap.add_argument("--sign", action="store_true")
    ap.add_argument("--anchor", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--verify", default=None, metavar="MANIFEST_JSON")
    ap.add_argument("--db", default=None)
    args = ap.parse_args()

    if args.verify:
        ok, errs = verificar_manifest(args.verify)
        if ok:
            print("MANIFEST OK")
        else:
            print(f"MANIFEST CON {len(errs)} ERRORES:")
            for e in errs[:20]:
                print(f"  - {e}")
            sys.exit(1)
        return

    generar_manifest(".", version=args.version, output=args.out,
                     firmar=args.sign, anclar=args.anchor, db_path=args.db)


if __name__ == "__main__":
    main()