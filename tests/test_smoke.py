"""Smoke test: pipeline completo en DB temporal."""
import sqlite3
from pathlib import Path

import pytest

import db_manager


@pytest.fixture
def temp_db(tmp_path):
    p = tmp_path / "test.sqlite"
    db_manager.inicializar_db(str(p))
    yield str(p)
    for ext in ("", "-wal", "-shm"):
        Path(str(p) + ext).unlink(missing_ok=True)


def test_schema_version(temp_db):
    with db_manager.get_connection(temp_db) as conn:
        v = conn.execute("PRAGMA user_version").fetchone()[0]
        assert v == db_manager.SCHEMA_VERSION_ACTUAL


def test_entidad_insert_idempotente(temp_db):
    datos = {
        "id": "T-001", "categoria": "test", "valor_principal": 10.0,
        "incertidumbre": 0.1, "unidad": "Hz", "fuente": "t",
        "origen": "observado", "estatus": "D", "notas": "",
    }
    db_manager.guardar_entidad(datos, temp_db)
    db_manager.guardar_entidad(datos, temp_db)
    assert len(db_manager.listar_entidades(temp_db)) == 1


def test_reproducibilidad_persiste(temp_db):
    db_manager.guardar_entidad({
        "id": "T-002", "categoria": "test", "valor_principal": 1.0,
        "incertidumbre": 0.1, "unidad": "x", "fuente": "t",
        "origen": "observado", "estatus": "D", "notas": "",
    }, temp_db)
    db_manager.guardar_provenance({
        "id_entidad": "T-002", "cita_completa": "c", "doi": "d",
        "tipo_publicacion": "t", "ano": 2024, "instrumento": "i",
        "condiciones": "co", "reproducibilidad": "REPRO_X",
        "extracto": "e", "hash_pdf": None, "fecha_descarga_utc": None,
        "notas": "",
    }, temp_db)
    with db_manager.get_connection(temp_db) as conn:
        r = conn.execute(
            "SELECT reproducibilidad FROM provenance WHERE id_entidad='T-002'"
        ).fetchone()
        assert r["reproducibilidad"] == "REPRO_X"
        r2 = conn.execute(
            "SELECT reproducibilidad FROM provenance_history WHERE id_entidad='T-002'"
        ).fetchone()
        assert r2["reproducibilidad"] == "REPRO_X"


def test_provenance_history_append_only(temp_db):
    db_manager.guardar_entidad({
        "id": "T-003", "categoria": "test", "valor_principal": 1.0,
        "incertidumbre": 0.1, "unidad": "x", "fuente": "t",
        "origen": "observado", "estatus": "D", "notas": "",
    }, temp_db)
    base = {"id_entidad": "T-003", "cita_completa": "", "doi": "",
            "tipo_publicacion": "", "ano": 2024, "instrumento": "",
            "condiciones": "", "reproducibilidad": "", "extracto": "",
            "hash_pdf": None, "fecha_descarga_utc": None, "notas": ""}
    r1 = db_manager.guardar_provenance({**base, "cita_completa": "v1"}, temp_db)
    r2 = db_manager.guardar_provenance({**base, "cita_completa": "v2"}, temp_db)
    r3 = db_manager.guardar_provenance({**base, "cita_completa": "v3"}, temp_db)
    assert (r1["version"], r2["version"], r3["version"]) == (1, 2, 3)
    assert r2["prev_hash"] == r1["hash_registro"]
    assert r3["prev_hash"] == r2["hash_registro"]
    with db_manager.get_connection(temp_db) as conn:
        n = conn.execute(
            "SELECT COUNT(*) FROM provenance_history WHERE id_entidad='T-003'"
        ).fetchone()[0]
        assert n == 3


def test_evento_chain_detecta_alteracion(temp_db):
    for i in range(5):
        db_manager.registrar_evento("test", f"evento {i}", "T-004", {"i": i}, temp_db)
    ok, idx, eid = db_manager.verificar_cadena_eventos(temp_db)
    assert ok, f"cadena deberia estar OK, fallo en idx={idx}"

    with db_manager.get_connection(temp_db) as conn:
        conn.execute("UPDATE eventos SET descripcion='ALTERADO' WHERE id=3")
    ok, idx, eid = db_manager.verificar_cadena_eventos(temp_db)
    assert not ok, "alteracion no detectada"
    assert idx == 2, f"esperaba detectar en idx=2, detecto idx={idx}"