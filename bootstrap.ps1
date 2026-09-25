# =====================================================================
# bootstrap.ps1 — Instalacion 1-click para THU-TBEA
# =====================================================================
# Uso: .\bootstrap.ps1
#      .\bootstrap.ps1 -SkipFetch   (no baja data)
#      .\bootstrap.ps1 -SkipLatex   (no verifica MiKTeX)
# =====================================================================
param(
    [switch]$SkipFetch,
    [switch]$SkipLatex
)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

function Line { Write-Host ("-" * 78) -ForegroundColor Cyan }
function Titulo($m) { Write-Host ""; Line; Write-Host "  $m" -ForegroundColor Cyan; Line }
function OK($m) { Write-Host "  [OK] $m" -ForegroundColor Green }
function WARN($m) { Write-Host "  [!] $m" -ForegroundColor Yellow }
function ERR($m) { Write-Host "  [X] $m" -ForegroundColor Red }

Titulo "THU-TBEA — Bootstrap"

# --- 1. Verificar Python ---
Write-Host ""
Write-Host "  [1/6] Verificando Python..."
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    ERR "Python no encontrado. Instalalo desde https://python.org/downloads"
    ERR "Verifica que 'python' este en PATH"
    exit 1
}
$pyv = & python --version 2>&1
OK "$pyv en $($py.Source)"

# --- 2. Venv ---
Write-Host ""
Write-Host "  [2/6] Creando entorno virtual..."
if (-not (Test-Path ".venv")) {
    & python -m venv .venv
    OK ".venv creado"
} else {
    OK ".venv ya existe"
}
& .\.venv\Scripts\Activate.ps1
$pyv = & python --version
OK "venv activado con $pyv"

# --- 3. Pip install ---
Write-Host ""
Write-Host "  [3/6] Instalando dependencias Python..."
& pip install --upgrade pip --quiet
& pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    ERR "Falla pip install"
    exit 1
}
OK "dependencias instaladas"

# --- 4. MiKTeX / pdflatex ---
if (-not $SkipLatex) {
    Write-Host ""
    Write-Host "  [4/6] Verificando pdflatex..."
    $pdflatex = Get-Command pdflatex -ErrorAction SilentlyContinue
    if (-not $pdflatex) {
        WARN "pdflatex no en PATH"
        $mik = "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"
        if (Test-Path $mik) {
            OK "MiKTeX presente pero no en PATH: $mik"
            $env:PATH = "$(Split-Path $mik);$env:PATH"
        } else {
            WARN "MiKTeX no instalado. Instalando con winget..."
            $wg = Get-Command winget -ErrorAction SilentlyContinue
            if ($wg) {
                & winget install --id MiKTeX.MiKTeX --accept-source-agreements --accept-package-agreements
                if ($LASTEXITCODE -eq 0) {
                    OK "MiKTeX instalado (puede requerir reiniciar terminal)"
                } else {
                    WARN "Falla winget. Instala manualmente desde https://miktex.org/download"
                }
            } else {
                WARN "winget no disponible. Instala MiKTeX manual desde https://miktex.org/download"
            }
        }
    } else {
        OK "pdflatex en PATH"
    }
} else {
    Write-Host ""
    Write-Host "  [4/6] pdflatex (skipped por -SkipLatex)"
}

# --- 5. Fetch data ---
if (-not $SkipFetch) {
    Write-Host ""
    Write-Host "  [5/6] Descargando datasets (inventory_v4.json)..."
    & python src\fetch_data.py --inventory --solo-faltantes
    if ($LASTEXITCODE -ne 0) {
        WARN "Algunas descargas fallaron (puede ser red). El pipeline continuara sin ellas."
    }
} else {
    Write-Host ""
    Write-Host "  [5/6] Fetch data (skipped por -SkipFetch)"
}

# --- 6. Ejecutar pipeline ---
Write-Host ""
Write-Host "  [6/6] Ejecutando pipeline completo..."
& python src\run_all.py

Titulo "LISTO"
Write-Host ""
Write-Host "  PDFs:       paper\thu\dist\tesis_es.pdf"
Write-Host "              paper\thu\dist\tesis_en.pdf"
Write-Host "              paper\thu\dist\tesis_de.pdf"
Write-Host ""
Write-Host "  Dashboard:  .\.venv\Scripts\activate; streamlit run app_thu.py"
Write-Host "              http://localhost:8501"
Write-Host ""
Line
