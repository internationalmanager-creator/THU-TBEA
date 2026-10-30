"""Base de datos de estado del proyecto (SQLite).

Uso:
    python scripts/state_db.py init       # crear tablas
    python scripts/state_db.py status     # ver estado actual
    python scripts/state_db.py log "msg"  # agregar log
"""
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DB_PATH = BASE / "registry" / "state.db"


def _ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=FULL;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS derivaciones (
            id INTEGER PRIMARY KEY,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            estado TEXT NOT NULL CHECK(estado IN ('pendiente','en_progreso','completado','fallido')),
            herramienta TEXT,
            notas TEXT,
            fecha_inicio_utc TEXT,
            fecha_fin_utc TEXT,
            evidencia TEXT
        );

        CREATE TABLE IF NOT EXISTS log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp_utc TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            nivel TEXT DEFAULT 'info'
        );

        CREATE TABLE IF NOT EXISTS sesiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inicio_utc TEXT NOT NULL,
            fin_utc TEXT,
            descripcion TEXT
        );
        """)
        
        # Insertar las 5 derivaciones pendientes si no existen
        derivaciones = [
            ("D.1-PUNTO-FIJO", "Punto fijo aureo (integrales de loop)", "pendiente", "FeynCalc/Package-X"),
            ("D.2-VACIO", "Cancelacion del vacio (N=88, CY3)", "pendiente", "SageMath/Macaulay2"),
            ("D.3-BETA0", "Prediccion beta_0 = 0.3803 (amplitude)", "pendiente", "FeynArts/FormCalc"),
            ("D.4-AJUSTE", "Ajuste cosmologico THU vs DESI/Pantheon", "pendiente", "Cobaya"),
            ("D.5-DIRAC-4D", "Dirac-Bergmann 4D completo (U4)", "pendiente", "SymPy + Cadabra2"),
        ]
        for codigo, nombre, estado, herramienta in derivaciones:
            conn.execute("""
                INSERT OR IGNORE INTO derivaciones (codigo, nombre, estado, herramienta, fecha_inicio_utc)
                VALUES (?, ?, ?, ?, ?)
            """, (codigo, nombre, estado, herramienta, _ts()))
        
        # Registrar inicio de sesion
        conn.execute("INSERT INTO sesiones (inicio_utc, descripcion) VALUES (?, ?)",
                     (_ts(), "Sesion iniciada"))
        
        print(f"[OK] DB inicializada en {DB_PATH}")


def status():
    with get_conn() as conn:
        print("=" * 80)
        print("  ESTADO DE DERIVACIONES")
        print("=" * 80)
        rows = conn.execute("SELECT * FROM derivaciones ORDER BY id").fetchall()
        for r in rows:
            icon = {"pendiente": "[ ]", "en_progreso": "[~]", "completado": "[X]", "fallido": "[!]"}[r["estado"]]
            print(f"  {icon} {r['codigo']:20s} | {r['nombre']:50s} | {r['estado']}")
        
        print()
        print("=" * 80)
        print("  ULTIMOS 10 LOGS")
        print("=" * 80)
        logs = conn.execute("SELECT * FROM log ORDER BY id DESC LIMIT 10").fetchall()
        for l in logs:
            print(f"  [{l['timestamp_utc']}] {l['nivel'].upper():6s} | {l['mensaje'][:80]}")


def log(msg, nivel="info"):
    with get_conn() as conn:
        conn.execute("INSERT INTO log (timestamp_utc, mensaje, nivel) VALUES (?, ?, ?)",
                     (_ts(), msg, nivel))
    print(f"[LOG] {msg}")


def update_derivacion(codigo, estado, evidencia=None):
    with get_conn() as conn:
        if estado == "completado":
            conn.execute("""
                UPDATE derivaciones SET estado=?, fecha_fin_utc=?, evidencia=?
                WHERE codigo=?
            """, (estado, _ts(), evidencia, codigo))
        else:
            conn.execute("""
                UPDATE derivaciones SET estado=?, evidencia=?
                WHERE codigo=?
            """, (estado, evidencia, codigo))
        log(f"Derivacion {codigo} -> {estado}", "update")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "init":
        init_db()
    elif cmd == "status":
        status()
    elif cmd == "log" and len(sys.argv) > 2:
        log(sys.argv[2])
    elif cmd == "update" and len(sys.argv) > 3:
        update_derivacion(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    else:
        print("Uso: python scripts/state_db.py [init|status|log <msg>|update <codigo> <estado> [evidencia]]")