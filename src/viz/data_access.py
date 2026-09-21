"""Acceso a datos desde SQLite para el dashboard.

Devuelve pandas DataFrames listos para graficar. Cada funcion abre
y cierra la conexion (no hay estado global).
"""
import sys
import sqlite3
from pathlib import Path

import pandas as pd

# --- Import dual para funcionar como paquete o como script ---
try:
    _ = __file__
except NameError:
    pass

BASE = Path(__file__).parent.parent.parent
DB_PATH = BASE / "data" / "pir.sqlite"


def _conn():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"DB no existe: {DB_PATH}. Corre 'python src/migrations.py' primero."
        )
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def get_entidades():
    """Todas las entidades con su estado de progreso."""
    with _conn() as conn:
        return pd.read_sql_query("""
            SELECT e.*, p.estado
            FROM entidades e
            LEFT JOIN progreso p ON p.id_entidad = e.id
            ORDER BY e.id
        """, conn)


def get_entidad(eid):
    """Una entidad por id. Devuelve dict o None."""
    with _conn() as conn:
        r = conn.execute("SELECT * FROM entidades WHERE id=?", (eid,)).fetchone()
        return dict(r) if r else None


def get_provenance_by_id(eid):
    """Provenance materializada (ultima version) de una entidad."""
    with _conn() as conn:
        r = conn.execute(
            "SELECT * FROM provenance WHERE id_entidad=?", (eid,)
        ).fetchone()
        return dict(r) if r else None


def get_provenance_history(eid):
    """Todas las versiones del provenance de una entidad (append-only)."""
    with _conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM provenance_history WHERE id_entidad=? ORDER BY version",
            (eid,)).fetchall()]


def get_eventos(limit=None):
    """Eventos de la cadena cronografica. Si limit, ultimos N."""
    with _conn() as conn:
        q = "SELECT * FROM eventos ORDER BY id"
        if limit:
            q = f"SELECT * FROM ({q} DESC LIMIT {int(limit)}) ORDER BY id"
        return pd.read_sql_query(q, conn)


def get_resumen():
    """Resumen agregado para los KPIs del dashboard."""
    if not DB_PATH.exists():
        return {
            "total": 0, "categorias": 0, "completadas": 0,
            "eventos": 0, "rango_ordenes": 0.0, "schema_version": 0,
        }
    with _conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM entidades").fetchone()[0]
        doms = conn.execute(
            "SELECT COUNT(DISTINCT categoria) FROM entidades"
        ).fetchone()[0]
        comp = conn.execute(
            "SELECT COUNT(*) FROM progreso WHERE estado='completado'"
        ).fetchone()[0]
        eventos = conn.execute("SELECT COUNT(*) FROM eventos").fetchone()[0]
        try:
            fmin, fmax = conn.execute(
                "SELECT MIN(valor_principal), MAX(valor_principal) FROM entidades"
            ).fetchone()
        except sqlite3.OperationalError:
            fmin, fmax = 0, 0
        ver = conn.execute("PRAGMA user_version").fetchone()[0]
    import math
    rango = math.log10(fmax/fmin) if fmin and fmax and fmin > 0 else 0
    return {
        "total": total, "categorias": doms, "completadas": comp,
        "eventos": eventos, "rango_ordenes": rango, "schema_version": ver,
    }


def get_categorias_count():
    """DataFrame con conteo por categoria, ordenado descendente."""
    if not DB_PATH.exists():
        return pd.DataFrame(columns=["categoria", "n"])
    with _conn() as conn:
        return pd.read_sql_query("""
            SELECT categoria, COUNT(*) AS n
            FROM entidades
            GROUP BY categoria
            ORDER BY n DESC
        """, conn)


def verificar_cadena():
    """Verifica la cadena de eventos. Devuelve (ok, idx, id)."""
    sys.path.insert(0, str(BASE / "src"))
    import db_manager
    return db_manager.verificar_cadena_eventos(str(DB_PATH))


def get_file(rel_path):
    """Lee un archivo del repo como string. '' si no existe."""
    p = BASE / rel_path
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""


def db_exists():
    return DB_PATH.exists()


if __name__ == "__main__":
    from tqdm import tqdm
    print("=== Test data_access.py ===")
    if not db_exists():
        print(f"  DB no existe: {DB_PATH}")
        print("  Corre: python src/migrations.py")
        print("  (No se puede testear sin DB)")
        sys.exit(0)

    r = get_resumen()
    print(f"  Resumen: {r}")

    ent = get_entidades()
    print(f"  Entidades: {len(ent)} filas, columnas={list(ent.columns)[:5]}...")

    ev = get_eventos()
    print(f"  Eventos: {len(ev)} filas")

    cats = get_categorias_count()
    print(f"  Categorias: {len(cats)} filas")

    if len(ent) > 0:
        eid = ent.iloc[0]["id"]
        p = get_provenance_by_id(eid)
        h = get_provenance_history(eid)
        print(f"  Provenance de {eid}: materializada={p is not None}, "
              f"historial={len(h)} versiones")

    ok, idx, eid = verificar_cadena()
    print(f"  Cadena: {'OK' if ok else f'ROTA en idx={idx} id={eid}'}")

    log = get_file("registry/DECISIONS.md")
    print(f"  DECISIONS.md leido: {len(log)} bytes")

    print("=== TEST OK ===")