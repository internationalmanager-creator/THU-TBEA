# consolidar_y_borrar.ps1
# Version corregida 2026-09-21

$A = "C:\Users\kg4tr\Documents\Investigacion_lab_secreto"
$B = "C:\Users\kg4tr\Documents\Investigacion_LaboratorioSecreto"

Write-Host ""
Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host "  FASE H.2 - Consolidacion y borrado de B" -ForegroundColor Cyan
Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $B)) {
    Write-Host "  B no existe. Nada que hacer." -ForegroundColor Green
    exit 0
}

# ---------- PASO 1: Analizar los 7 unicos de B ----------
$unicos = @(
    "data\inputs\COSM-001.json",
    "data\inputs\COSM-002.json",
    "data\inputs\COSM-003.json",
    "data\inputs\COSM-004.json",
    "data\inputs\COSM-005.json",
    "data\inputs\COSM-006.json",
    "seeds\seed_v0.7.0_20260920.json"
)

Write-Host "[1/4] Contenido de los 7 archivos unicos de B" -ForegroundColor Yellow
Write-Host ("-" * 78)

foreach ($rel in $unicos) {
    $pB = Join-Path $B $rel
    $pA = Join-Path $A $rel
    Write-Host ""
    Write-Host ("  >> {0}" -f $rel) -ForegroundColor Cyan
    Write-Host ("     Existe en A? {0}" -f (Test-Path $pA)) -ForegroundColor Gray

    if (Test-Path $pB) {
        $item = Get-Item $pB
        Write-Host ("     Tamano B: {0} bytes, mod {1}" -f $item.Length, $item.LastWriteTime)
        if ($item.Length -lt 4096 -and $rel -match "\.json$") {
            $content = Get-Content $pB -Raw
            Write-Host "     --- contenido ---"
            $content -split "`n" | Select-Object -First 20 | ForEach-Object {
                Write-Host ("       {0}" -f $_)
            }
            Write-Host "     --- fin ---"
        }
    } else {
        Write-Host "     [NO EXISTE EN B]" -ForegroundColor Red
    }
}

# ---------- PASO 2: Ver si A tiene versiones previas ----------
Write-Host ""
Write-Host "[2/4] Buscando equivalentes en A" -ForegroundColor Yellow
Write-Host ("-" * 78)

$inputsA = Join-Path $A "data\inputs"
if (Test-Path $inputsA) {
    $cosmA = Get-ChildItem $inputsA -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -match "^COSM-" }
    Write-Host ("  En A\data\inputs\: {0} archivos COSM-*" -f $cosmA.Count)
    $cosmA | Sort-Object Name | ForEach-Object {
        Write-Host ("    {0,-30} {1,8} bytes" -f $_.Name, $_.Length)
    }
} else {
    Write-Host "  A\data\inputs no existe"
}

$seedsA = Join-Path $A "seeds"
if (Test-Path $seedsA) {
    $seedsFiles = Get-ChildItem $seedsA -File -ErrorAction SilentlyContinue
    Write-Host ""
    Write-Host ("  En A\seeds\: {0} archivos" -f $seedsFiles.Count)
    $seedsFiles | Sort-Object Name | ForEach-Object {
        Write-Host ("    {0,-40} {1,8} bytes" -f $_.Name, $_.Length)
    }
} else {
    Write-Host "  A\seeds no existe"
}

# ---------- PASO 3: Confirmacion ----------
Write-Host ""
Write-Host "[3/4] Plan de consolidacion" -ForegroundColor Yellow
Write-Host ("-" * 78)
Write-Host "  Se van a mover 7 archivos de B a A (preservando estructura):"
foreach ($rel in $unicos) {
    $existeA = Test-Path (Join-Path $A $rel)
    $mark = if ($existeA) { "(sobrescribe A)" } else { "(nuevo en A)" }
    Write-Host ("    {0}  {1}" -f $rel, $mark)
}
Write-Host ""
Write-Host "  Luego se respalda B completo (ZIP) y se elimina."
Write-Host ""
$r = Read-Host "  Continuar? (escribi CONSOLIDAR)"
if ($r -ne "CONSOLIDAR") {
    Write-Host "  Cancelado. No se toco nada." -ForegroundColor Yellow
    exit 0
}

# ---------- PASO 4: Mover unicos + backup + borrar ----------
Write-Host ""
Write-Host "[4/4] Ejecutando..." -ForegroundColor Yellow

# 4a. Mover unicos
Write-Host "  4a. Moviendo 7 archivos unicos a A..." -ForegroundColor Cyan
foreach ($rel in $unicos) {
    $pB = Join-Path $B $rel
    $pA = Join-Path $A $rel
    if (-not (Test-Path $pB)) { continue }
    $dirA = Split-Path $pA -Parent
    if (-not (Test-Path $dirA)) { New-Item -ItemType Directory -Force -Path $dirA | Out-Null }
    Copy-Item $pB $pA -Force
    Write-Host "    [OK] $rel" -ForegroundColor Green
}

# 4b. Backup ZIP de B entero
$BackupRoot = Join-Path $A "data\_backup_borrado"
New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
$Stamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
$ZipPath = Join-Path $BackupRoot ("B_backup_{0}.zip" -f $Stamp)

Write-Host ""
Write-Host "  4b. Comprimiendo B..." -ForegroundColor Cyan
Compress-Archive -Path (Join-Path $B "*") -DestinationPath $ZipPath -CompressionLevel Optimal
$zipMB = [Math]::Round((Get-Item $ZipPath).Length / 1MB, 2)
Write-Host "    [OK] ZIP: $zipMB MB" -ForegroundColor Green

# 4c. Borrar B
Write-Host ""
Write-Host "  4c. Eliminando B..." -ForegroundColor Cyan
Remove-Item $B -Recurse -Force
Write-Host "    [OK] B eliminado" -ForegroundColor Green

# 4d. Reporte
Write-Host ""
Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host "  COMPLETADO" -ForegroundColor Green
Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host ""
Write-Host "  Carpetas del proyecto:" -ForegroundColor Yellow
Get-ChildItem "C:\Users\kg4tr\Documents" -Directory |
    Where-Object { $_.Name -like "*nvestigacion*" } |
    Format-Table Name, LastWriteTime -AutoSize

Write-Host "  Backup: $ZipPath" -ForegroundColor Green
Write-Host ""