"""Clonador de laboratorio PIR + THU-TBEA.

Crea una copia local e independiente del template oficial con:
- Cadenas de auditoría reseteadas (independientes del padre)
- Metadata del clon con hash SHA-256 del template padre
- Sin .github/ (laboratorio local, sin CI/CD ni push)
- Hereda todo el código, datos de referencia, figuras y derivaciones

Uso:
    python src/clone_investigacion.py --nombre "LaboratorioSecreto" --slug "lab_secreto"
    python src/clone_investigacion.py --listar
    python src/clone_investigacion.py --verificar ../Investigacion_lab_secreto
"""
import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent


def _ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ts_compact():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _calcular_template_hash():
    """Calcula hash SHA-256 compuesto del template oficial."""
    h = hashlib.sha256()
    archivos_clave = [
        "src/thu/figures.py",
        "src/thu/derivaciones.py",
        "src/thu/loader.py",
        "src/thu/i18n_thu.py",
        "registry/GLOSARIO.md",
        "registry/DECISIONS.md",
        "registry/project_metadata.json",
        "registry/thu/problems.json",
        "registry/thu/predictions.json",
    ]
    for archivo in archivos_clave:
        path = BASE / archivo
        if path.exists():
            h.update(_sha256_file(path).encode())
    return h.hexdigest()


def _limpiar_cadenas(destino, template_hash):
    """Resetea las cadenas de auditoría para independencia total."""
    # epistemic_log.md
    log_path = destino / "registry" / "epistemic_log.md"
    if log_path.exists():
        contenido = f"""# Log Epistémico - Laboratorio Clonado

> Registro cronológico append-only del laboratorio clonado.
> Cadena independiente del template padre.

---

## {_ts()} - Entrada 000 - Clonación desde template oficial

**Acción:** Creación de laboratorio local independiente.
**Razón:** Espacio de experimentación para hipótesis y conjeturas.
**Consecuencia:** Cadena de auditoría local, sin exposición pública.
**Template padre hash (SHA-256 compuesto):** {template_hash[:32]}...
**Versión heredada:** PIR 0.7.0 / THU-TBEA 5.3

---
"""
        log_path.write_text(contenido, encoding="utf-8", newline="\n")
    
    # chronolog.md
    chronolog_path = destino / "registry" / "chronolog.md"
    if chronolog_path.exists():
        chronolog_path.write_text("# Cronolog\n\n> Cadena de eventos (vacía al inicio del clon)\n", encoding="utf-8")
    
    # reports.jsonl
    reports_path = destino / "registry" / "reports.jsonl"
    if reports_path.exists():
        reports_path.write_text("", encoding="utf-8")
    
    # HALLAZGOS_FALSADOS.md (mantener plantilla)
    hf_path = destino / "registry" / "HALLAZGOS_FALSADOS.md"
    if hf_path.exists():
        plantilla = """# Hallazgos Falsados

> Documento de honestidad científica. Registra hipótesis que NO sobrevivieron
> al escrutinio estadístico.

---

## Plantilla de entrada

### HN - Título de la hipótesis

**Formulación:** [enunciado preciso y falsable]

**Metodología de test:**
1. ...
2. ...

**Resultado:**
- ...
- ...

**Estatus:** FALSADA / NO TESTABLE

---
"""
        hf_path.write_text(plantilla, encoding="utf-8")


def _limpiar_artefactos(destino):
    """Elimina artefactos regenerables del clon."""
    # DB SQLite
    for pattern in ["data/*.sqlite", "data/*.sqlite-wal", "data/*.sqlite-shm"]:
        for f in destino.glob(pattern):
            f.unlink()
    
    # outputs (mantener reportes de derivaciones como referencia)
    outputs_dir = destino / "outputs"
    if outputs_dir.exists():
        for f in outputs_dir.glob("*"):
            if "derivaciones_report" not in f.name and f.name != ".gitkeep":
                f.unlink()
    
    # __pycache__
    for d in destino.rglob("__pycache__"):
        shutil.rmtree(d, ignore_errors=True)
    
    # data/inputs y provenance (limpiar)
    for d in ["data/inputs", "data/provenance"]:
        dir_path = destino / d
        if dir_path.exists():
            for f in dir_path.glob("*"):
                if f.name != ".gitkeep":
                    f.unlink()
    
    # seeds (limpiar, se regeneran)
    seeds_dir = destino / "seeds"
    if seeds_dir.exists():
        for f in seeds_dir.glob("seed_v*.json"):
            f.unlink()
        sums = seeds_dir / "SHA256SUMS.txt"
        if sums.exists():
            sums.unlink()


def _crear_metadata_clon(destino, nombre, slug, descripcion, template_hash):
    """Crea registry/investigacion.json con metadata del clon."""
    meta = {
        "id": f"CLONE-{slug.upper()}-{_ts_compact()}",
        "nombre": nombre,
        "slug": slug,
        "descripcion": descripcion or f"Laboratorio de experimentación local: {nombre}",
        "tipo": "laboratorio_local",
        "publicacion": False,
        "template_padre": {
            "path": str(BASE.resolve()),
            "manifest_sha256": template_hash,
            "version_pir": "0.7.0",
            "version_thu": "5.3",
        },
        "timestamp_creacion_utc": _ts(),
        "estado": "activo",
        "problemas_abiertos_heredados": ["A-6", "A-7", "A-15", "A-16", "A-17"],
        "predicciones_heredadas": [f"P{i}" for i in range(1, 12)],
        "reglas": {
            "idioma_defecto": "es",
            "i18n_disponible": ["es", "en", "de"],
            "sin_github": True,
            "sin_ci_cd": True,
            "cadena_independiente": True,
            "hash_todos_los_pasos": True,
        },
    }
    
    meta_path = destino / "registry" / "investigacion.json"
    meta_path.write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n"
    )
    return meta


def clonar(destino, nombre, slug, descripcion=None):
    """Genera un clon del template oficial."""
    print(f"\n{'='*70}")
    print(f"  CLONANDO TEMPLATE PIR + THU-TBEA")
    print(f"{'='*70}")
    print(f"  Destino: {destino}")
    print(f"  Nombre:  {nombre}")
    print(f"  Slug:    {slug}")
    print(f"{'='*70}\n")
    
    destino = Path(destino).resolve()
    if destino.exists():
        print(f"ERROR: {destino} ya existe", file=sys.stderr)
        sys.exit(1)
    
    # 1. Calcular hash del template padre
    print("[1/6] Calculando hash del template padre...")
    template_hash = _calcular_template_hash()
    
    # 2. Copiar todo el template (excepto .github y artefactos)
    print("[2/6] Copiando template (excluyendo .github y artefactos)...")
    shutil.copytree(BASE, destino, ignore=shutil.ignore_patterns(
        ".git", "__pycache__", "*.pyc", "data/*.sqlite*",
        "seeds/seed_v*.json", "replication/package_v*.zip",
        ".github", ".githooks", "outputs/run_log_*.txt",
        "outputs/last_run.json", "outputs/audit_report_*.txt",
    ))
    
    # 3. Limpiar cadenas de auditoría
    print("[3/6] Reseteando cadenas de auditoría (independencia total)...")
    _limpiar_cadenas(destino, template_hash)
    
    # 4. Limpiar artefactos regenerables
    print("[4/6] Limpiando artefactos regenerables...")
    _limpiar_artefactos(destino)
    
    # 5. Crear metadata del clon
    print("[5/6] Creando metadata del clon (registry/investigacion.json)...")
    meta = _crear_metadata_clon(destino, nombre, slug, descripcion, template_hash)
    
    # 6. Verificación final
    print("[6/6] Verificación final...")
    archivos_verificar = [
        "src/thu/figures.py",
        "src/thu/derivaciones.py",
        "src/thu/loader.py",
        "registry/investigacion.json",
        "registry/epistemic_log.md",
        "registry/thu/problems.json",
        "registry/thu/predictions.json",
    ]
    ok = True
    for archivo in archivos_verificar:
        path = destino / archivo
        if path.exists():
            print(f"  ✓ {archivo} ({path.stat().st_size} B)")
        else:
            print(f"  ✗ {archivo} FALTA")
            ok = False
    
    # Verificar que .github NO existe
    if not (destino / ".github").exists():
        print(f"  ✓ .github/ NO copiado (correcto)")
    else:
        print(f"   .github/ existe (ERROR)")
        ok = False
    
    print(f"\n{'='*70}")
    if ok:
        print(f"  ✓ CLON CREADO EXITOSAMENTE")
    else:
        print(f"  ✗ CLON CON PROBLEMAS")
    print(f"{'='*70}")
    print(f"\n  ID:          {meta['id']}")
    print(f"  Path:        {destino}")
    print(f"  Padre hash:  {template_hash[:32]}...")
    print(f"  Tipo:        {meta['tipo']}")
    print(f"  Publicación: {meta['publicacion']}")
    print(f"\n  Problemas abiertos heredados: {meta['problemas_abiertos_heredados']}")
    print(f"  Predicciones heredadas:       {meta['predicciones_heredadas']}")
    print(f"\n  Próximos pasos:")
    print(f"    cd {destino}")
    print(f"    python src/run_all.py --seed")
    print(f"    streamlit run app_thu.py")
    print(f"{'='*70}\n")
    
    return meta


def listar_clones():
    """Lista los clones existentes en el directorio padre."""
    padre = BASE.parent
    clones = []
    for d in padre.iterdir():
        if d.is_dir() and d.name.startswith("Investigacion_"):
            meta_path = d / "registry" / "investigacion.json"
            if meta_path.exists():
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                clones.append(meta)
    
    if not clones:
        print("No hay clones registrados.")
        return
    
    print(f"\n{'='*70}")
    print(f"  CLONES REGISTRADOS")
    print(f"{'='*70}\n")
    for c in clones:
        print(f"  ID:          {c['id']}")
        print(f"  Nombre:      {c['nombre']}")
        print(f"  Path:        {c['id'].replace('CLONE-', '').lower()}")
        print(f"  Creado:      {c['timestamp_creacion_utc']}")
        print(f"  Estado:      {c['estado']}")
        print(f"  Problemas:   {c.get('problemas_abiertos_heredados', [])}")
        print(f"  Predicciones: {c.get('predicciones_heredadas', [])}")
        print(f"  {'-'*60}")
    print()


def verificar_clon(path):
    """Verifica la integridad de un clon."""
    p = Path(path).resolve()
    meta_path = p / "registry" / "investigacion.json"
    if not meta_path.exists():
        print(f"ERROR: {p} no es un clon válido (falta registry/investigacion.json)")
        sys.exit(1)
    
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    print(f"\n{'='*70}")
    print(f"  VERIFICACIÓN DE CLON")
    print(f"{'='*70}\n")
    print(f"  ID:          {meta['id']}")
    print(f"  Nombre:      {meta['nombre']}")
    print(f"  Tipo:        {meta['tipo']}")
    print(f"  Padre hash:  {meta['template_padre']['manifest_sha256'][:32]}...")
    print(f"\n  Archivos críticos:")
    
    criticos = [
        "src/thu/figures.py",
        "src/thu/derivaciones.py",
        "src/thu/loader.py",
        "src/thu/i18n_thu.py",
        "registry/thu/problems.json",
        "registry/thu/predictions.json",
        "registry/epistemic_log.md",
    ]
    
    ok = True
    for archivo in criticos:
        path_archivo = p / archivo
        if path_archivo.exists():
            print(f"    ✓ {archivo}")
        else:
            print(f"    ✗ {archivo} FALTA")
            ok = False
    
    print(f"\n  {'✓ CLON ÍNTEGRO' if ok else '✗ CLON CON PROBLEMAS'}")
    print(f"{'='*70}\n")


def main():
    ap = argparse.ArgumentParser(description="Clonador de laboratorio PIR + THU-TBEA")
    ap.add_argument("--nombre", help="Nombre del laboratorio")
    ap.add_argument("--slug", help="Slug (sin espacios, minúsculas)")
    ap.add_argument("--descripcion", help="Descripción (opcional)")
    ap.add_argument("--destino", help="Path destino (default: ../Investigacion_{slug})")
    ap.add_argument("--listar", action="store_true", help="Listar clones existentes")
    ap.add_argument("--verificar", help="Verificar integridad de un clon")
    
    args = ap.parse_args()
    
    if args.listar:
        listar_clones()
        return
    
    if args.verificar:
        verificar_clon(args.verificar)
        return
    
    if not args.nombre or not args.slug:
        print("ERROR: --nombre y --slug son obligatorios para crear un clon")
        sys.exit(1)
    
    destino = args.destino or f"../Investigacion_{args.slug}"
    clonar(destino, args.nombre, args.slug, args.descripcion)


if __name__ == "__main__":
    main()
