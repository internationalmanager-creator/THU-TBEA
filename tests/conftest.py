"""Configuracion comun de pytest: agrega src/ al sys.path."""
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE / "src"))