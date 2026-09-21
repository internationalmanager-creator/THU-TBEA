"""Gestor de base de datos SQLite para PIR (schema v2).

Diseno anti-cortes de energia:
- journal_mode=WAL: los cambios van primero a <db>-wal, se consolidan despues.
- synchronous=FULL: escritura fisica antes de confirmar (durabilidad total).
- UPSERT idempotente: re-ejecutar no duplica.

Schema version:
    1 -> entidades, provenance, progreso
    2 -> + reproducibilidad, provenance_history, eventos, schema_version

Formalizacion de la cadena criptografica de eventos:
    H_i = SHA256(ts_i | tipo_i | entidad_i | desc_i | payload_i | H_{i-1})
    H_0 = SHA256("GENESIS")
"""
import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = "data/pir.sqlite"
SCHEMA_VERSION_ACTUAL = 2
GENESIS = "GENESIS"

ESQUEMA_V2 = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at_utc TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS entidades (
    id TEXT PRIMARY KEY,
    categoria TEXT NOT NULL,
    valor_principal REAL NOT NULL,
    incertidumbre REAL,
    unidad TEXT,
    fuente TEXT,
    origen TEXT DEFAULT 'observado'
        CHECK(origen IN ('observado','generado','inferido','simulado')),
    estatus TEXT CHECK(estatus IN ('D','P','F','A')),
    notas TEXT
);

-- Materializada: siempre refleja la ultima version de provenance_history
CREATE TABLE IF NOT EXISTS provenance (
    id_entidad TEXT PRIMARY KEY,
    cita_completa TEXT,
    doi TEXT,
    tipo_publicacion TEXT,
    ano INTEGER,
    instrumento TEXT,
    condiciones TEXT,
    reproducibilidad TEXT,
    extracto TEXT,
    hash_pdf TEXT,
    fecha_descarga_utc TEXT,
    notas TEXT,
    version INTEGER DEFAULT 1,
    hash_registro TEXT,
    prev_hash TEXT,
    FOREIGN KEY (id_entidad) REFERENCES entidades(id)
);

-- Append-only: toda version de provenance queda registrada
CREATE TABLE IF NOT EXISTS provenance_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_entidad TEXT NOT NULL,
    version INTEGER NOT NULL,
    timestamp_utc TEXT NOT NULL,
    cita_completa TEXT,
    doi TEXT,
    tipo_publicacion TEXT,
    ano INTEGER,
    instrumento TEXT,
    condiciones TEXT,
    reproducibilidad TEXT,
    extracto TEXT,
    hash_pdf TEXT,
    fecha_descarga_utc TEXT,
    notas TEXT,
    hash_registro TEXT NOT NULL,
    prev_hash TEXT,
    UNIQUE(id_entidad, version),
    FOREIGN KEY (id_entidad) REFERENCES entidades(id)
);

CREATE VIEW IF NOT EXISTS provenance_actual AS
    SELECT * FROM provenance_history p
    WHERE p.version = (
        SELECT MAX(version) FROM provenance_history
        WHERE id_entidad = p.id_entidad
    );

-- Log cronografico encadenado
CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp_utc TEXT NOT NULL,
    tipo TEXT NOT NULL,
    entidad_id TEXT,
    descripcion TEXT NOT NULL,
    payload_json TEXT,
    prev_hash TEXT,
    hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS progreso (
    id_entidad TEXT PRIMARY KEY,
    estado TEXT CHECK(estado IN ('pendiente','en_progreso','completado'))
        DEFAULT 'pendiente',
    fecha_actualizacion_utc TEXT,
    notas TEXT,
    FOREIGN KEY (id_entidad) REFERENCES entidades(id)
);

CREATE INDEX IF NOT EXISTS idx_entidades_categoria ON entidades(categoria);
CREATE INDEX IF NOT EXISTS idx_entidades_origen ON entidades(origen);
CREATE INDEX IF NOT EXISTS idx_progreso_estado ON progreso(estado);
CREATE INDEX IF NOT EXISTS idx_eventos_ts ON eventos(timestamp_utc);
CREATE INDEX IF NOT EXISTS idx_eventos_tipo ON eventos(tipo);
CREATE INDEX IF NOT EXISTS idx_eventos_entidad ON eventos(entidad_id);
CREATE INDEX IF NOT EXISTS idx_provhist_entidad ON provenance_history(id_entidad, version);
"""

# === PARTE 2 se agrega a continuacion ===

def _ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _hash_prov(d):
    """Hash canonico de un registro de provenance (version + campos)."""
    orden = [
        "id_entidad", "version", "timestamp_utc", "cita_completa", "doi",
        "tipo_publicacion", "ano", "instrumento", "condiciones",
        "reproducibilidad", "extracto", "hash_pdf", "fecha_descarga_utc", "notas",
    ]
    partes = [str(d.get(k, "") if d.get(k) is not None else "") for k in orden]
    return hashlib.sha256("|".join(partes).encode("utf-8")).hexdigest()


def _hash_evento(ts, tipo, eid, desc, payload_json, prev_hash):
    partes = [ts, tipo, eid or "", desc or "", payload_json or "", prev_hash or GENESIS]
    return hashlib.sha256("|".join(partes).encode("utf-8")).hexdigest()


@contextmanager
def get_connection(db_path=None):
    path = db_path or DB_PATH
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=FULL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _version_actual(conn):
    r = conn.execute("PRAGMA user_version").fetchone()
    return r[0] if r else 0


def _set_version(conn, v):
    conn.execute(f"PRAGMA user_version = {int(v)}")


def inicializar_db(db_path=None):
    """Crea schema v2 completo. Idempotente."""
    with get_connection(db_path) as conn:
        conn.executescript(ESQUEMA_V2)
        v = _version_actual(conn)
        if v < SCHEMA_VERSION_ACTUAL:
            _set_version(conn, SCHEMA_VERSION_ACTUAL)
            conn.execute("""
                INSERT OR REPLACE INTO schema_version (version, applied_at_utc, notes)
                VALUES (?, ?, ?)
            """, (SCHEMA_VERSION_ACTUAL, _ts(),
                  "Schema v2: reproducibilidad + provenance_history + eventos"))


def guardar_entidad(datos, db_path=None):
    with get_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO entidades (id, categoria, valor_principal, incertidumbre,
                                   unidad, fuente, origen, estatus, notas)
            VALUES (:id, :categoria, :valor_principal, :incertidumbre,
                    :unidad, :fuente, :origen, :estatus, :notas)
            ON CONFLICT(id) DO UPDATE SET
                categoria=excluded.categoria,
                valor_principal=excluded.valor_principal,
                incertidumbre=excluded.incertidumbre,
                unidad=excluded.unidad,
                fuente=excluded.fuente,
                origen=excluded.origen,
                estatus=excluded.estatus,
                notas=excluded.notas
        """, datos)
        conn.execute("""
            INSERT INTO progreso (id_entidad, estado, fecha_actualizacion_utc)
            VALUES (:id, 'pendiente', :ts)
            ON CONFLICT(id_entidad) DO NOTHING
        """, {"id": datos["id"], "ts": _ts()})


def guardar_provenance(datos, db_path=None):
    """Append-only en provenance_history + materializa en provenance.

    Cada llamada CREA una nueva version. Nunca sobrescribe.
    Devuelve dict con version, hash_registro, prev_hash.
    """
    with get_connection(db_path) as conn:
        eid = datos["id_entidad"]
        # Siguiente version
        r = conn.execute(
            "SELECT COALESCE(MAX(version), 0) + 1 AS v FROM provenance_history WHERE id_entidad=?",
            (eid,),
        ).fetchone()
        version = r["v"]

        # prev_hash = hash de la version previa (o GENESIS si es la primera)
        rp = conn.execute(
            "SELECT hash_registro FROM provenance_history "
            "WHERE id_entidad=? ORDER BY version DESC LIMIT 1",
            (eid,),
        ).fetchone()
        prev = rp["hash_registro"] if rp else GENESIS

        ts = _ts()
        registro = {
            "id_entidad": eid, "version": version, "timestamp_utc": ts,
            "cita_completa": datos.get("cita_completa"),
            "doi": datos.get("doi"),
            "tipo_publicacion": datos.get("tipo_publicacion"),
            "ano": datos.get("ano"),
            "instrumento": datos.get("instrumento"),
            "condiciones": datos.get("condiciones"),
            "reproducibilidad": datos.get("reproducibilidad"),
            "extracto": datos.get("extracto"),
            "hash_pdf": datos.get("hash_pdf"),
            "fecha_descarga_utc": datos.get("fecha_descarga_utc"),
            "notas": datos.get("notas"),
        }
        h = _hash_prov(registro)

        conn.execute("""
            INSERT INTO provenance_history
                (id_entidad, version, timestamp_utc, cita_completa, doi,
                 tipo_publicacion, ano, instrumento, condiciones,
                 reproducibilidad, extracto, hash_pdf, fecha_descarga_utc,
                 notas, hash_registro, prev_hash)
            VALUES (:id_entidad, :version, :timestamp_utc, :cita_completa, :doi,
                    :tipo_publicacion, :ano, :instrumento, :condiciones,
                    :reproducibilidad, :extracto, :hash_pdf, :fecha_descarga_utc,
                    :notas, :hash_registro, :prev_hash)
        """, {**registro, "hash_registro": h, "prev_hash": prev})

        # Materializar (upsert) en la tabla actual
        conn.execute("""
            INSERT INTO provenance
                (id_entidad, cita_completa, doi, tipo_publicacion, ano,
                 instrumento, condiciones, reproducibilidad, extracto,
                 hash_pdf, fecha_descarga_utc, notas, version, hash_registro, prev_hash)
            VALUES (:id_entidad, :cita_completa, :doi, :tipo_publicacion, :ano,
                    :instrumento, :condiciones, :reproducibilidad, :extracto,
                    :hash_pdf, :fecha_descarga_utc, :notas, :version,
                    :hash_registro, :prev_hash)
            ON CONFLICT(id_entidad) DO UPDATE SET
                cita_completa=excluded.cita_completa,
                doi=excluded.doi,
                tipo_publicacion=excluded.tipo_publicacion,
                ano=excluded.ano,
                instrumento=excluded.instrumento,
                condiciones=excluded.condiciones,
                reproducibilidad=excluded.reproducibilidad,
                extracto=excluded.extracto,
                hash_pdf=excluded.hash_pdf,
                fecha_descarga_utc=excluded.fecha_descarga_utc,
                notas=excluded.notas,
                version=excluded.version,
                hash_registro=excluded.hash_registro,
                prev_hash=excluded.prev_hash
        """, {**registro, "hash_registro": h, "prev_hash": prev})

        return {"version": version, "hash_registro": h, "prev_hash": prev}


def actualizar_progreso(id_entidad, estado, notas=None, db_path=None):
    if estado not in ("pendiente", "en_progreso", "completado"):
        raise ValueError(f"Estado invalido: {estado}")
    with get_connection(db_path) as conn:
        conn.execute("""
            UPDATE progreso SET estado=?, fecha_actualizacion_utc=?, notas=?
            WHERE id_entidad=?
        """, (estado, _ts(), notas, id_entidad))

# === PARTE 3 se agrega a continuacion ===

def listar_entidades(db_path=None, categoria=None, origen=None):
    with get_connection(db_path) as conn:
        q = "SELECT * FROM entidades WHERE 1=1"
        params = []
        if categoria:
            q += " AND categoria=?"
            params.append(categoria)
        if origen:
            q += " AND origen=?"
            params.append(origen)
        q += " ORDER BY id"
        return [dict(r) for r in conn.execute(q, params).fetchall()]


def obtener_resumen(db_path=None):
    with get_connection(db_path) as conn:
        por_estado = {r["estado"]: r["n"] for r in conn.execute(
            "SELECT estado, COUNT(*) as n FROM progreso GROUP BY estado").fetchall()}
        por_origen = {r["origen"]: r["n"] for r in conn.execute(
            "SELECT origen, COUNT(*) as n FROM entidades GROUP BY origen").fetchall()}
        por_categoria = {r["categoria"]: r["n"] for r in conn.execute(
            "SELECT categoria, COUNT(*) as n FROM entidades GROUP BY categoria").fetchall()}
        n_eventos = conn.execute("SELECT COUNT(*) FROM eventos").fetchone()[0]
        return {
            "total": sum(por_estado.values()),
            "por_estado": por_estado,
            "por_origen": por_origen,
            "por_categoria": por_categoria,
            "eventos": n_eventos,
            "fecha_consulta_utc": _ts(),
            "schema_version": _version_actual(conn),
        }


# ============================================================
# Registro cronografico encadenado (eventos)
# ============================================================

def registrar_evento(tipo, descripcion, entidad_id=None, payload=None, db_path=None):
    """Anade evento a la cadena. Devuelve hash."""
    ts = _ts()
    payload_json = json.dumps(payload, ensure_ascii=False, sort_keys=True) if payload else None
    with get_connection(db_path) as conn:
        r = conn.execute("SELECT hash FROM eventos ORDER BY id DESC LIMIT 1").fetchone()
        prev = r["hash"] if r else GENESIS
        h = _hash_evento(ts, tipo, entidad_id, descripcion, payload_json, prev)
        conn.execute("""
            INSERT INTO eventos (timestamp_utc, tipo, entidad_id,
                                 descripcion, payload_json, prev_hash, hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (ts, tipo, entidad_id, descripcion, payload_json, prev, h))
        return h


def listar_eventos(db_path=None, limit=None, tipo=None, entidad_id=None):
    with get_connection(db_path) as conn:
        q = "SELECT * FROM eventos WHERE 1=1"
        params = []
        if tipo:
            q += " AND tipo=?"
            params.append(tipo)
        if entidad_id:
            q += " AND entidad_id=?"
            params.append(entidad_id)
        q += " ORDER BY id"
        if limit:
            q = f"SELECT * FROM ({q}) LIMIT {int(limit)}"
        return [dict(r) for r in conn.execute(q, params).fetchall()]


def verificar_cadena_eventos(db_path=None):
    """Recalcula todos los hashes. Devuelve (ok, idx, id)."""
    with get_connection(db_path) as conn:
        eventos = [dict(r) for r in conn.execute("SELECT * FROM eventos ORDER BY id").fetchall()]
    prev = GENESIS
    for i, ev in enumerate(eventos):
        h = _hash_evento(ev["timestamp_utc"], ev["tipo"], ev["entidad_id"],
                         ev["descripcion"], ev["payload_json"], prev)
        if h != ev["hash"] or ev["prev_hash"] != prev:
            return False, i, ev["id"]
        prev = ev["hash"]
    return True, None, None


# ============================================================
# Auto-test
# ============================================================

if __name__ == "__main__":
    from tqdm import tqdm
    print("=== Test db_manager v2 ===")
    test_db = "data/test_pir.sqlite"
    for ext in ("", "-wal", "-shm"):
        Path(test_db + ext).unlink(missing_ok=True)

    inicializar_db(test_db)

    with tqdm(total=6, desc="Test", ncols=80) as pbar:
        guardar_entidad({
            "id": "TEST-001", "categoria": "test", "valor_principal": 1.0,
            "incertidumbre": 0.1, "unidad": "Hz", "fuente": "test",
            "origen": "observado", "estatus": "D", "notas": "",
        }, test_db)
        pbar.update(1); pbar.set_postfix_str("entidad")

        r1 = guardar_provenance({
            "id_entidad": "TEST-001", "cita_completa": "v1",
            "doi": "10.0/test", "tipo_publicacion": "test", "ano": 2024,
            "instrumento": "t", "condiciones": "t", "reproducibilidad": "indep",
            "extracto": "e", "hash_pdf": None, "fecha_descarga_utc": None, "notas": "",
        }, test_db)
        assert r1["version"] == 1
        pbar.update(1); pbar.set_postfix_str("prov v1")

        r2 = guardar_provenance({
            "id_entidad": "TEST-001", "cita_completa": "v2 (corregida)",
            "doi": "10.0/test.v2", "tipo_publicacion": "test", "ano": 2024,
            "instrumento": "t", "condiciones": "t", "reproducibilidad": "indep",
            "extracto": "e", "hash_pdf": None, "fecha_descarga_utc": None, "notas": "",
        }, test_db)
        assert r2["version"] == 2
        assert r2["prev_hash"] == r1["hash_registro"], "cadena provenance rota"
        pbar.update(1); pbar.set_postfix_str("prov v2")

        with get_connection(test_db) as conn:
            r = conn.execute("SELECT reproducibilidad FROM provenance WHERE id_entidad='TEST-001'").fetchone()
            assert r["reproducibilidad"] == "indep", "reproducibilidad perdida!"
        pbar.update(1); pbar.set_postfix_str("reproducibilidad OK")

        registrar_evento("test", "evento 1", "TEST-001", {"k": 1}, test_db)
        registrar_evento("test", "evento 2", "TEST-001", {"k": 2}, test_db)
        ok, i, eid = verificar_cadena_eventos(test_db)
        assert ok, f"cadena rota en {i}"
        pbar.update(1); pbar.set_postfix_str("cadena OK")

        actualizar_progreso("TEST-001", "completado", None, test_db)
        pbar.update(1); pbar.set_postfix_str("progreso OK")

    for ext in ("", "-wal", "-shm"):
        Path(test_db + ext).unlink(missing_ok=True)
    print("=== TEST OK ===")