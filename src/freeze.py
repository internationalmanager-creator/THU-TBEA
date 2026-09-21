"""Genera requirements.lock a partir del entorno actual.

Uso:
    python src/freeze.py

Escribe requirements.lock con versiones exactas del entorno.
El lock es la fuente de verdad para reproducibilidad estricta.
"""
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
LOCK = BASE / "requirements.lock"


def main():
    print("Generando requirements.lock desde el entorno actual...")
    r = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        capture_output=True, text=True, check=True,
    )
    paquetes = sorted(
        l for l in r.stdout.splitlines()
        if l and not l.startswith("#") and "==" in l
    )
    LOCK.write_text("\n".join(paquetes) + "\n", encoding="utf-8", newline="\n")
    print(f"OK: {LOCK} ({len(paquetes)} paquetes)")


if __name__ == "__main__":
    main()