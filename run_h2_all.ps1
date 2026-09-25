# run_h2_all.ps1
# FASE H.2 - Certificacion + verificaciones
# Guardar en C:\Users\kg4tr\Documents\Investigacion_lab_secreto\run_h2_all.ps1
# Ejecutar: cd C:\Users\kg4tr\Documents\Investigacion_lab_secreto; .\run_h2_all.ps1

$ErrorActionPreference = "Stop"
$Repo = "C:\Users\kg4tr\Documents\Investigacion_lab_secreto"
$Raw  = Join-Path $Repo "data\raw"
$Inv  = Join-Path $Repo "data\inventory"
New-Item -ItemType Directory -Force -Path $Inv | Out-Null

Write-Host "=== FASE H.2 ===" -ForegroundColor Cyan

# ---------- 1. CERTIFICAR DATOS EN DISCO ----------
Write-Host "`n[1/3] Certificando datos..." -ForegroundColor Yellow
$Archivos = Get-ChildItem -Path $Raw -Recurse -File | Where-Object { $_.Length -gt 0 }
$Cert = @()
$i = 0
foreach ($f in $Archivos) {
    $i++
    Write-Host ("  [{0}/{1}] {2}" -f $i, $Archivos.Count, $f.Name)
    $h = Get-FileHash -Path $f.FullName -Algorithm SHA256
    $Cert += @{
        nombre    = $f.Name
        ruta      = $f.FullName.Substring($Repo.Length + 1)
        bytes     = $f.Length
        sha256    = $h.Hash.ToLower()
        fecha_mod = $f.LastWriteTimeUtc.ToString("o")
    }
}
$CertOut = Join-Path $Inv "certificacion_h2.json"
@{ fase="H.2"; fecha=(Get-Date).ToUniversalTime().ToString("o"); total=$Cert.Count; archivos=$Cert } |
    ConvertTo-Json -Depth 6 | Set-Content -Path $CertOut -Encoding UTF8
Write-Host "  -> $CertOut ($($Cert.Count))" -ForegroundColor Green

# ---------- 2. VERIFICAR C_top (A-19) ----------
Write-Host "`n[2/3] Verificando C_top (A-19)..." -ForegroundColor Yellow
$phi = [decimal]((1.0 + [Math]::Sqrt(5.0)) / 2.0)
$pi  = [decimal][Math]::PI
$phi2 = $phi * $phi
$phi_inv2 = 1.0 / $phi2
$Ctop0 = 4.0 * $pi / [decimal][Math]::Sqrt(8.0)
$objetivo = [decimal]4.466

$fA = ($phi / (2.0 * $pi)) * (($phi2 - 1.0) / ($phi2 + 1.0))
$CA = $Ctop0 * (1.0 + $fA)
$fB = ($phi / (2.0 * $pi)) * ($phi2 - $phi_inv2 + 1.0)
$CB = $Ctop0 * (1.0 + $fB)
$fReq = ($objetivo / $Ctop0) - 1.0

Write-Host ("  C_top(0)    = {0}" -f $Ctop0)
Write-Host ("  Formula A   = {0}  (diff {1})" -f $CA, [Math]::Abs($CA - $objetivo))
Write-Host ("  Formula B   = {0}  (diff {1})" -f $CB, [Math]::Abs($CB - $objetivo))
Write-Host ("  Factor req. = {0}" -f $fReq)

$veredictoCtop = if ([Math]::Abs($CA - $objetivo) -lt 0.005 -or [Math]::Abs($CB - $objetivo) -lt 0.005) { "resuelto" } else { "A-19_abierto" }

$CtopOut = Join-Path $Inv "verify_ctop.json"
@{
    fase="H.2"; fecha=(Get-Date).ToUniversalTime().ToString("o")
    objetivo=[double]$objetivo
    C_top_0=[double]$Ctop0
    formula_A=@{ C_top=[double]$CA; diff=[double]([Math]::Abs($CA - $objetivo)) }
    formula_B=@{ C_top=[double]$CB; diff=[double]([Math]::Abs($CB - $objetivo)) }
    factor_requerido=[double]$fReq
    veredicto=$veredictoCtop
} | ConvertTo-Json -Depth 6 | Set-Content -Path $CtopOut -Encoding UTF8
Write-Host "  -> $CtopOut ($veredictoCtop)" -ForegroundColor Green

# ---------- 3. VERIFICAR beta(z) (INC-11) ----------
Write-Host "`n[3/3] Verificando beta(z) (INC-11)..." -ForegroundColor Yellow
$H0 = 67.4
$Om = 0.315
$Ol = 1.0 - $Om
$ZMAX = 1000.0
$NSTEPS = 20000

function Get-H([double]$z) { return $H0 * [Math]::Sqrt($Om * [Math]::Pow(1.0 + $z, 3.0) + $Ol) }

function Get-t([double]$z) {
    $lzmin = [Math]::Log(1.0 + $z)
    $lzmax = [Math]::Log(1.0 + $ZMAX)
    $dlz = ($lzmax - $lzmin) / $NSTEPS
    $sum = 0.0
    for ($i = 0; $i -lt $NSTEPS; $i++) {
        $lz1 = $lzmin + $i * $dlz
        $lz2 = $lzmin + ($i + 1) * $dlz
        $z1 = [Math]::Exp($lz1) - 1.0
        $z2 = [Math]::Exp($lz2) - 1.0
        $sum += 0.5 * (1.0/(Get-H $z1) + 1.0/(Get-H $z2)) * $dlz
    }
    return $sum
}

$t0 = Get-t 0.0
$Tabla = [ordered]@{ 0.5=0.374; 1.0=0.573; 1.5=0.688; 2.0=0.760; 2.5=0.809; 3.0=0.843 }
$Filas = @()
foreach ($z in $Tabla.Keys) {
    $t = Get-t $z
    $bc = 1.0 - $t / $t0
    $bt = $Tabla[$z]
    $Filas += @{ z=$z; beta_calc=$bc; beta_v5=$bt; diff=($bc - $bt) }
    Write-Host ("  z={0:F1}  calc={1:F4}  v5={2:F4}  diff={3:F4}" -f $z, $bc, $bt, ($bc - $bt))
}
$maxdiff = ($Filas | ForEach-Object { [Math]::Abs($_.diff) } | Measure-Object -Maximum).Maximum
$veredictoBeta = if ($maxdiff -lt 0.02) { "reproduce_v5.0" } else { "revisar" }

$BetaOut = Join-Path $Inv "verify_beta_z.json"
@{ fase="H.2"; fecha=(Get-Date).ToUniversalTime().ToString("o"); t0=$t0; maxdiff=$maxdiff; veredicto=$veredictoBeta; tabla=$Filas } |
    ConvertTo-Json -Depth 6 | Set-Content -Path $BetaOut -Encoding UTF8
Write-Host "  -> $BetaOut ($veredictoBeta)" -ForegroundColor Green

Write-Host "`n=== COMPLETADO ===" -ForegroundColor Cyan