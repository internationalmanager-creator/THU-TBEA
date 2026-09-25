# run_h2_mcmc_final.ps1
# FASE H.2 — Cierre MCMC run_id=3
# Lee el HDF5 correctamente (grupo -> sub-datasets), calcula stats,
# actualiza fase_e_cierre.json.

$ErrorActionPreference = "Stop"
$Repo = "C:\Users\kg4tr\Documents\Investigacion_lab_secreto"
$Inv  = Join-Path $Repo "data\inventory"
$Scr  = Join-Path $Repo "scripts"
$Reg  = Join-Path $Repo "registry\thu"
New-Item -ItemType Directory -Force -Path $Inv, $Scr, $Reg | Out-Null

Write-Host ""
Write-Host ("=" * 72) -ForegroundColor Cyan
Write-Host "  FASE H.2 - Cierre MCMC run_id=3 (lector corregido)" -ForegroundColor Cyan
Write-Host ("=" * 72) -ForegroundColor Cyan
Write-Host ""

# ========== PASO 1: escribir lector corregido ==========
Write-Progress -Id 0 -Activity "FASE H.2" -Status "Paso 1/3: escribiendo lector v2" -PercentComplete 0
Write-Host "[1/3] Escribiendo scripts\read_mcmc_h5_v2.py..." -ForegroundColor Yellow

$pyCode = @'
#!/usr/bin/env python3
"""Lector HDF5 emcee v2: maneja estructura de Grupo + burn-in + stats."""
import json
from pathlib import Path
from datetime import datetime
import numpy as np
import h5py

BASE = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
BM = BASE / "data" / "raw" / "cosmic-birefringence-planck-act" / "beta_mcmc"
H5 = BM.parent / "data" / "computed" / "mcmc_chain.h5"
OUT = BASE / "data" / "inventory" / "mcmc_run_id_3_final.json"

MCMC_N_BURN = 5000  # segun config guardada

print(f"[HDF5] {H5}")
if not H5.exists():
    raise SystemExit(f"No existe {H5}")

report = {
    "fecha": datetime.utcnow().isoformat() + "Z",
    "h5_path": str(H5),
    "n_burn": MCMC_N_BURN,
    "beta_mean": None, "beta_std": None,
    "beta_median": None, "beta_p16": None, "beta_p84": None,
    "n_samples": None, "chain_shape": None, "h5_keys": None,
    "h5_subkeys": None,
}

with h5py.File(H5, "r") as f:
    keys = list(f.keys())
    print(f"  top-level keys: {keys}")
    report["h5_keys"] = keys

    if "mcmc" not in f:
        raise SystemExit(f"grupo 'mcmc' ausente. keys={keys}")

    grp = f["mcmc"]
    subkeys = list(grp.keys())
    print(f"  mcmc sub-keys : {subkeys}")
    report["h5_subkeys"] = subkeys

    if "chain" not in grp:
        raise SystemExit(f"'chain' ausente dentro de mcmc. subkeys={subkeys}")

    chain = np.array(grp["chain"])  # (nsteps, nwalkers, ndim)
    print(f"  chain shape   : {chain.shape}")
    report["chain_shape"] = list(chain.shape)

    nsteps, nwalkers, ndim = chain.shape
    burn = min(MCMC_N_BURN, nsteps // 2)
    print(f"  burn-in       : {burn} (pedido {MCMC_N_BURN})")

    chain_post = chain[burn:, :, :]  # (nsteps-burn, nwalkers, ndim)
    flat = chain_post.reshape(-1, ndim)
    beta = flat[:, 0]
    beta_ok = beta[np.isfinite(beta)]

    if len(beta_ok) == 0:
        raise SystemExit("sin samples finitos tras burn-in")

    m  = float(np.mean(beta_ok))
    s  = float(np.std(beta_ok))
    p16 = float(np.percentile(beta_ok, 16))
    p50 = float(np.percentile(beta_ok, 50))
    p84 = float(np.percentile(beta_ok, 84))

    print()
    print(f"  n_samples     : {len(beta_ok)}")
    print(f"  beta mean+/−std: {m:.4f} +/- {s:.4f}")
    print(f"  beta median    : {p50:.4f} [{p16:.4f}, {p84:.4f}]")

    report.update({
        "beta_mean": m, "beta_std": s,
        "beta_median": p50, "beta_p16": p16, "beta_p84": p84,
        "n_samples": int(len(beta_ok)),
    })

    # otros parametros (alpha_i) — solo estadisticos basicos
    others = {}
    for j in range(1, ndim):
        col = flat[:, j]
        col_ok = col[np.isfinite(col)]
        if len(col_ok):
            others[f"param_{j}"] = {
                "mean": float(np.mean(col_ok)),
                "std":  float(np.std(col_ok)),
            }
    report["otros_parametros"] = others

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fp:
    json.dump(report, fp, indent=2, ensure_ascii=False)
print()
print(f"  -> {OUT}")
'@

$PyPath = Join-Path $Scr "read_mcmc_h5_v2.py"
Set-Content -Path $PyPath -Value $pyCode -Encoding utf8NoBOM
Write-Host "  -> $PyPath" -ForegroundColor Green

# ========== PASO 2: ejecutar lector ==========
Write-Progress -Id 0 -Activity "FASE H.2" -Status "Paso 2/3: leyendo HDF5" -PercentComplete 33
Write-Host ""
Write-Host "[2/3] Leyendo HDF5 con lector v2..." -ForegroundColor Yellow
Write-Host ("-" * 72) -ForegroundColor DarkGray
& python $PyPath
$pyExit = $LASTEXITCODE
if ($pyExit -ne 0) {
    Write-Host "Lector fallo (exit $pyExit). Abortando." -ForegroundColor Red
    exit 1
}

# ========== PASO 3: actualizar fase_e_cierre.json ==========
Write-Progress -Id 0 -Activity "FASE H.2" -Status "Paso 3/3: actualizando registro" -PercentComplete 66
Write-Host ""
Write-Host "[3/3] Actualizando registry\thu\fase_e_cierre.json..." -ForegroundColor Yellow

$FinalJson = Join-Path $Inv "mcmc_run_id_3_final.json"
$Final = Get-Content $FinalJson -Raw | ConvertFrom-Json

$CierrePath = Join-Path $Reg "fase_e_cierre.json"
if (Test-Path $CierrePath) {
    $Cierre = Get-Content $CierrePath -Raw | ConvertFrom-Json
} else {
    $Cierre = [PSCustomObject]@{}
}

# anadir/actualizar campo mcmc_run_id_3
$entry = [PSCustomObject]@{
    run_id              = 3
    status              = "completed_90pct"
    steps_completados   = 27100
    steps_objetivo      = 30000
    n_walkers           = 12
    n_params            = 6
    n_burn              = $Final.n_burn
    beta_mean_deg       = $Final.beta_mean
    beta_std_deg        = $Final.beta_std
    beta_median_deg     = $Final.beta_median
    beta_p16_deg        = $Final.beta_p16
    beta_p84_deg        = $Final.beta_p84
    n_samples_post_burn = $Final.n_samples
    chain_shape         = $Final.chain_shape
    fecha_lectura       = $Final.fecha
    h5_path             = $Final.h5_path
    nota                = "MCMC fallo al 90% por PermissionError en save_step. Chain recuperado integro."
}

# Compatibilidad con PSCustomObject
$Cierre | Add-Member -NotePropertyName "mcmc_run_id_3" -NotePropertyValue $entry -Force

$Cierre | ConvertTo-Json -Depth 10 | Set-Content -Path $CierrePath -Encoding UTF8
Write-Host "  -> $CierrePath" -ForegroundColor Green

Write-Host ""
Write-Host ("-" * 72) -ForegroundColor DarkGray
Write-Host ""
Write-Host "  RESULTADO FINAL:" -ForegroundColor Cyan
Write-Host ("    beta_deg = {0:N4} +/- {1:N4}" -f $Final.beta_mean, $Final.beta_std) -ForegroundColor White
Write-Host ""
Write-Host "  Comparaciones:" -ForegroundColor Yellow
$ref_prev  = 0.207;  $s_prev  = 0.073
$ref_paper = 0.215;  $s_paper = 0.074
$s_comb_prev  = [Math]::Sqrt($Final.beta_std*$Final.beta_std + $s_prev*$s_prev)
$s_comb_paper = [Math]::Sqrt($Final.beta_std*$Final.beta_std + $s_paper*$s_paper)
$sig_prev  = [Math]::Abs($Final.beta_mean - $ref_prev)  / $s_comb_prev
$sig_paper = [Math]::Abs($Final.beta_mean - $ref_paper) / $s_comb_paper
Write-Host ("    E.3-C8f previo       {0:N4} +/- {1:N4}   -> {2:N2} sigma" -f $ref_prev, $s_prev, $sig_prev) -ForegroundColor Gray
Write-Host ("    Diego-Palazuelos 25  {0:N4} +/- {1:N4}   -> {2:N2} sigma" -f $ref_paper, $s_paper, $sig_paper) -ForegroundColor Gray

Write-Progress -Id 0 -Activity "FASE H.2" -Status "Completado" -PercentComplete 100
Start-Sleep -Milliseconds 300
Write-Progress -Id 0 -Activity "FASE H.2" -Completed

Write-Host ""
Write-Host "=== COMPLETADO ===" -ForegroundColor Cyan
Write-Host "  Reporte: $FinalJson" -ForegroundColor Green
Write-Host "  Registro: $CierrePath" -ForegroundColor Green
Write-Host ""