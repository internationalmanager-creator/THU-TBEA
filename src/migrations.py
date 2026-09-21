"""Migraciones de schema (idempotentes).

Uso:
    python src/migrations.py            # aplica hasta la ultima version
    python src/migrations.py --status   # solo reporta

Reglas:
- Cada migracion lleva fecha, autor, motivo.
- Se aplica en orden. Nunca se saltan.
- Toda migracion debe ser idempotente.
"""
import argparse
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent
DB_PATH = BASE / "data" / "pir.sqlite"


def _ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _version(conn):
    return conn.execute("PRAGMA user_version").fetchone()[0]


def migrar_v1_a_v2(conn):
    """v1 -> v2: anade reproducibilidad, provenance_history, eventos, schema_version.

    Idempotente: usa IF NOT EXISTS y comprueba columnas antes de anadir.
    """
    # Detectar si la tabla provenance existia sin las columnas nuevas
    tablas = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}

    if "provenance" in tablas:
        cols_prov = {r[1] for r in conn.execute("PRAGMA table_info(provenance)")}
        if "reproducibilidad" not in cols_prov:
            conn.execute("ALTER TABLE provenance ADD COLUMN reproducibilidad TEXT")
        if "version" not in cols_prov:
            conn.execute("ALTER TABLE provenance ADD COLUMN version INTEGER DEFAULT 1")
        if "hash_registro" not in cols_prov:
            conn.execute("ALTER TABLE provenance ADD COLUMN hash_registro TEXT")
        if "prev_hash" not in cols_prov:
            conn.execute("ALTER TABLE provenance ADD COLUMN prev_hash TEXT")

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at_utc TEXT NOT NULL,
            notes TEXT
        );
        CREATE TABLE IF NOT EXISTS provenance_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_entidad TEXT NOT NULL,
            version INTEGER NOT NULL,
            timestamp_utc TEXT NOT NULL,
            cita_completa TEXT, doi TEXT, tipo_publicacion TEXT, ano INTEGER,
            instrumento TEXT, condiciones TEXT, reproducibilidad TEXT,
            extracto TEXT, hash_pdf TEXT, fecha_descarga_utc TEXT, notas TEXT,
            hash_registro TEXT NOT NULL, prev_hash TEXT,
            UNIQUE(id_entidad, version)
        );
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp_utc TEXT NOT NULL,
            tipo TEXT NOT NULL, entidad_id TEXT,
            descripcion TEXT NOT NULL, payload_json TEXT,
            prev_hash TEXT, hash TEXT NOT NULL
        );
        CREATE VIEW IF NOT EXISTS provenance_actual AS
            SELECT * FROM provenance_history p
            WHERE p.version = (
                SELECT MAX(version) FROM provenance_history
                WHERE id_entidad = p.id_entidad
            );
        CREATE INDEX IF NOT EXISTS idx_eventos_ts ON eventos(timestamp_utc);
        CREATE INDEX IF NOT EXISTS idx_eventos_tipo ON eventos(tipo);
        CREATE INDEX IF NOT EXISTS idx_eventos_entidad ON eventos(entidad_id);
        CREATE INDEX IF NOT EXISTS idx_provhist_entidad
            ON provenance_history(id_entidad, version);
    """)

    conn.execute("PRAGMA user_version = 2")
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at_utc, notes)
        VALUES (2, ?, 'Migracion v1->v2 automatica')
    """, (_ts(),))


MIGRACIONES = {
    2: ("v1 -> v2 (reproducibilidad + provenance_history + eventos)",
        migrar_v1_a_v2),
}


def status(db_path=None):
    path = str(db_path or DB_PATH)
    if not Path(path).exists():
        print(f"DB no existe: {path} (nada que migrar)")
        return
    conn = sqlite3.connect(path)
    try:
        v = _version(conn)
        print(f"DB: {path}")
        print(f"schema_version: {v}")
        tiene_sv = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
        ).fetchone()
        if tiene_sv:
            for r in conn.execute("SELECT * FROM schema_version ORDER BY version"):
                print(f"  v{r[0]}: {r[1]} - {r[2]}")
    finally:
        conn.close()


def aplicar(db_path=None):
    path = str(db_path or DB_PATH)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=FULL;")
    try:
        v = _version(conn)
        if v == 0:
            # DB vacia -> inicializar directo con v2
            print("DB vacia: inicializando schema v2 completo")
            conn.close()
            sys.path.insert(0, str(BASE / "src"))
            import db_manager
            db_manager.inicializar_db(path)
            return
        for destino in sorted(MIGRACIONES):
            if v < destino:
                desc, fn = MIGRACIONES[destino]
                print(f"Aplicando: {desc}")
                fn(conn)
                conn.commit()
                v = _version(conn)
                print(f"OK -> v{v}")
        print(f"Schema final: v{v}")
    finally:
        conn.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--db", default=None)
    args = ap.parse_args()
    if args.status:
        status(args.db)
    else:
        aplicar(args.db)


if __name__ == "__main__":
    main()