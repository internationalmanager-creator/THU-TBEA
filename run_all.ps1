# =====================================================================
# PIR — Wrapper PowerShell para src/run_all.py
# =====================================================================
# Uso:
#   .\run_all.ps1
#   .\run_all.ps1 --seed --dashboard
#   .\run_all.ps1 --skip-tests --stop-on-fail
#   .\run_all.ps1 --dry-run
# =====================================================================
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    $Args
)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

# Activar venv si existe
$venvActivate = Join-Path $PSScriptRoot "venv\Scripts\Activate.ps1"
$venvActivate2 = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"

if (Test-Path $venvActivate) {
    Write-Host "[run_all] Activando venv..." -ForegroundColor Cyan
    & $venvActivate
} elseif (Test-Path $venvActivate2) {
    Write-Host "[run_all] Activando .venv..." -ForegroundColor Cyan
    & $venvActivate2
} else {
    Write-Host "[run_all] Sin venv; usando python global" -ForegroundColor Yellow
}

# Elegir interprete
$py = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $py = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $py = "python3"
} else {
    throw "No se encuentra python ni python3 en PATH"
}

Write-Host "[run_all] python: $py" -ForegroundColor Cyan
& $py "src\run_all.py" @Args
exit $LASTEXITCODE