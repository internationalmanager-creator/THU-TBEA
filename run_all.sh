#!/usr/bin/env bash
# =====================================================================
# PIR — Wrapper bash para src/run_all.py
# =====================================================================
# Uso:
#   ./run_all.sh                       # secuencia completa
#   ./run_all.sh --seed                # crea TEST-001 si vacio
#   ./run_all.sh --seed --dashboard    # arranca streamlit al final
#   ./run_all.sh --skip-tests
#   ./run_all.sh --stop-on-fail
#   ./run_all.sh --dry-run             # solo muestra el plan
# =====================================================================
set -euo pipefail
cd "$(dirname "$0")"

# Activar venv si existe
if [ -f "venv/bin/activate" ]; then
    echo "[run_all] Activando venv..."
    # shellcheck disable=SC1091
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    echo "[run_all] Activando .venv..."
    # shellcheck disable=SC1091
    source .venv/bin/activate
else
    echo "[run_all] Sin venv; usando python global"
fi

# Elegir interprete
if command -v python >/dev/null 2>&1; then
    PY=python
elif command -v python3 >/dev/null 2>&1; then
    PY=python3
else
    echo "ERROR: no se encuentra python ni python3" >&2
    exit 1
fi

echo "[run_all] python: $PY"
exec "$PY" src/run_all.py "$@"