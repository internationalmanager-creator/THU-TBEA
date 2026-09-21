import lzma, tarfile, io, sys
from pathlib import Path

RAW = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto\data\raw")
EXT = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto\data\extracted")

def diagnose(f):
    """Retorna (tipo, detalle)"""
    with open(f, 'rb') as fh:
        head = fh.read(6)
    if head == b'\xfd7zXZ\x00':
        return 'xz', 'XZ magic'
    if head[:2] == b'\x1f\x8b':
        return 'gzip', 'GZIP magic'
    if head[:4] == b'PK\x03\x04':
        return 'zip', 'ZIP magic'
    return 'unknown', head.hex()

def extract_xz_file(src, target_dir, name):
    """Extrae XZ puro (no tar.xz)."""
    target_dir.mkdir(parents=True, exist_ok=True)
    out = target_dir / name
    with lzma.open(src, 'rb') as xz:
        # Leer primeros bytes para ver si es tar
        preview = xz.read(512)
    # Reabrir para escritura completa
    with lzma.open(src, 'rb') as xz:
        # Detectar si es tar: "ustar" en offset 257
        if len(preview) >= 262 and preview[257:262] == b'ustar':
            # Es tar.xz, extraer como tar
            with lzma.open(src, 'rb') as xz2:
                with tarfile.open(fileobj=xz2, mode='r:') as tf:
                    tf.extractall(target_dir)
            return 'tar_extracted'
        else:
            # Archivo binario unico — guardar como .bin
            with open(out.with_suffix(out.suffix + '.bin'), 'wb') as out_fh:
                out_fh.write(preview)
                while True:
                    chunk = xz.read(65536)
                    if not chunk:
                        break
                    out_fh.write(chunk)
            return 'single_file'

# Buscar todos los .tar.xz en zen_runtime
targets = list((RAW / "zen_runtime").rglob("*.tar.xz"))
print(f"=== .tar.xz a reparar: {len(targets)} ===")

for f in targets:
    rel = f.relative_to(RAW)
    tipo, det = diagnose(f)
    size_mb = f.stat().st_size / 1024 / 1024
    print(f"\n--- {rel} ({size_mb:.2f} MB) ---")
    print(f"    Tipo: {tipo} ({det})")

    # Target: extraer a data/extracted/{rel_path_sin_ext}
    rel_no_ext = str(rel).replace('.tar.xz', '').replace('.xz', '').replace('.tar', '')
    target = EXT / rel_no_ext

    # Si ya esta extraido, saltar
    if target.exists() and len(list(target.rglob('*'))) > 1:
        n = len([p for p in target.rglob('*') if p.is_file()])
        print(f"    Ya extraido: {n} archivos")
        continue

    target.mkdir(parents=True, exist_ok=True)

    try:
        # Intentar tarfile primero (soporta tar.xz nativamente)
        try:
            with tarfile.open(f, 'r:xz') as tf:
                tf.extractall(target)
            n = len([p for p in target.rglob('*') if p.is_file()])
            sz = sum(p.stat().st_size for p in target.rglob('*') if p.is_file())
            print(f"    OK via tarfile: {n} archivos, {sz/1024/1024:.2f} MB")
        except tarfile.ReadError:
            # No es tar — extraer como xz puro
            result = extract_xz_file(f, target, f.stem)
            n = len([p for p in target.rglob('*') if p.is_file()])
            sz = sum(p.stat().st_size for p in target.rglob('*') if p.is_file())
            print(f"    OK via lzma ({result}): {n} archivos, {sz/1024/1024:.2f} MB")
    except Exception as e:
        print(f"    FALLO: {e}")

print("\n=== Reparacion completa ===")
