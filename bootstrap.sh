#!/usr/bin/env bash
# =====================================================================
# bootstrap.sh — Instalacion 1-click para THU-TBEA (Linux/Mac)
# =====================================================================
# Uso: ./bootstrap.sh
#      ./bootstrap.sh --skip-fetch
#      ./bootstrap.sh --skip-latex
# =====================================================================
set -euo pipefail
cd "$(dirname "$0")"

SKIP_FETCH=0
SKIP_LATEX=0
for arg in "$@"; do
    case "$arg" in
        --skip-fetch) SKIP_FETCH=1 ;;
        --skip-latex) SKIP_LATEX=1 ;;
    esac
done

titulo() { echo; echo "==="; echo "  $1"; echo "==="; }
ok()     { echo "  [OK] $1"; }
warn()   { echo "  [!] $1"; }
err()    { echo "  [X] $1"; }

titulo "THU-TBEA — Bootstrap"

# 1. Python
echo ""
echo "  [1/6] Verificando Python..."
if ! command -v python3 >/dev/null 2>&1; then
    err "python3 no encontrado"
    exit 1
fi
ok "$(python3 --version)"

# 2. Venv
echo ""
echo "  [2/6] Creando entorno virtual..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    ok ".venv creado"
else
    ok ".venv ya existe"
fi
# shellcheck disable=SC1091
source .venv/bin/activate

# 3. Pip install
echo ""
echo "  [3/6] Instalando dependencias Python..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
ok "dependencias instaladas"

# 4. LaTeX
if [ "$SKIP_LATEX" = "0" ]; then
    echo ""
    echo "  [4/6] Verificando pdflatex..."
    if command -v pdflatex >/dev/null 2>&1; then
        ok "pdflatex en PATH"
    else
        warn "pdflatex no instalado"
        warn "  Ubuntu/Debian: sudo apt install texlive-full"
        warn "  macOS:         brew install --cask mactex-no-gui"
        warn "  Continua sin LaTeX..."
    fi
else
    echo ""
    echo "  [4/6] pdflatex (skip)"
fi

# 5. Fetch
if [ "$SKIP_FETCH" = "0" ]; then
    echo ""
    echo "  [5/6] Descargando datasets..."
    python3 src/fetch_data.py --inventory --solo-faltantes || warn "fetch parcial"
else
    echo ""
    echo "  [5/6] Fetch (skip)"
fi

# 6. Pipeline
echo ""
echo "  [6/6] Ejecutando pipeline completo..."
python3 src/run_all.py

titulo "LISTO"
echo ""
echo "  PDFs:       paper/thu/dist/tesis_es.pdf"
echo "              paper/thu/dist/tesis_en.pdf"
echo "              paper/thu/dist/tesis_de.pdf"
echo ""
echo "  Dashboard:  source .venv/bin/activate; streamlit run app_thu.py"
echo "              http://localhost:8501"
echo ""
