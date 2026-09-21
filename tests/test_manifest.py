"""Test del manifest encadenado."""
from pathlib import Path

import pytest

import hash_manifest


@pytest.fixture
def fake_repo(tmp_path):
    (tmp_path / "a.py").write_text("print('a')\n")
    (tmp_path / "b.txt").write_text("hello\n")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.md").write_text("# c\n")
    return tmp_path


def test_manifest_deterministico(fake_repo):
    """Generar el manifest dos veces debe dar el mismo chain_root y manifest_sha256."""
    m1 = hash_manifest.generar_manifest(str(fake_repo), version="t")
    m2 = hash_manifest.generar_manifest(str(fake_repo), version="t")
    assert m1["chain_root"] == m2["chain_root"]
    assert m1["manifest_sha256"] == m2["manifest_sha256"]


def test_manifest_detecta_cambio(fake_repo):
    """Modificar un archivo debe cambiar el chain_root."""
    m1 = hash_manifest.generar_manifest(str(fake_repo), version="t")
    (fake_repo / "b.txt").write_text("hello changed\n")
    m2 = hash_manifest.generar_manifest(str(fake_repo), version="t")
    assert m1["chain_root"] != m2["chain_root"]


def test_manifest_detecta_borrado(fake_repo):
    """Borrar un archivo debe cambiar el chain_root y reducir file_count."""
    m1 = hash_manifest.generar_manifest(str(fake_repo), version="t")
    (fake_repo / "a.py").unlink()
    m2 = hash_manifest.generar_manifest(str(fake_repo), version="t")
    assert m1["chain_root"] != m2["chain_root"]
    assert m1["file_count"] != m2["file_count"]


def test_manifest_verificar_ok(fake_repo):
    """Verificar un manifest recien generado debe dar OK."""
    hash_manifest.generar_manifest(str(fake_repo), version="t")
    seeds = list((fake_repo / "seeds").glob("seed_vt_*.json"))
    assert seeds, "no se genero el manifest"
    ok, errs = hash_manifest.verificar_manifest(str(seeds[0]), root=str(fake_repo))
    assert ok, f"manifest deberia verificar, errores: {errs[:3]}"


def test_manifest_verificar_falla_si_cambia_archivo(fake_repo):
    """Verificar despues de modificar un archivo debe fallar."""
    hash_manifest.generar_manifest(str(fake_repo), version="t")
    seeds = list((fake_repo / "seeds").glob("seed_vt_*.json"))
    (fake_repo / "b.txt").write_text("cambiado\n")
    ok, errs = hash_manifest.verificar_manifest(str(seeds[0]), root=str(fake_repo))
    assert not ok, "deberia fallar la verificacion"
    assert any("HASH DISTINTO" in e for e in errs), f"errores: {errs[:3]}"