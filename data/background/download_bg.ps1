$RAW = "C:\Users\kg4tr\Documents\Investigacion_LaboratorioSecreto\data\raw"
$LOG = "$RAW\_background_log.txt"

function Blog($msg) {
    $ts = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    Add-Content -Path $LOG -Value "[$ts] $msg" -Encoding utf8NoBOM
}

# Definir descargas: (dataset, archivo, urls[], minBytes)
$descargas = @(
    # --- Planck PR4 likelihoods de birefringencia ---
    @{ d="planck_pr4\hillipop"; f="hillipop_v4.2.tar.gz"; min=1000; urls=@(
        "https://github.com/CarronJ/hillipop/archive/refs/heads/master.tar.gz",
        "https://github.com/CarronJ/hillipop/archive/refs/heads/main.tar.gz")},
    @{ d="planck_pr4\lollipop"; f="lollipop_v3.3.tar.gz"; min=1000; urls=@(
        "https://github.com/CarronJ/lollipop/archive/refs/heads/master.tar.gz",
        "https://github.com/CarronJ/lollipop/archive/refs/heads/main.tar.gz")},

    # --- Planck PR4 SMICA CMB maps (component-separated) ---
    @{ d="planck_pr4\smica_maps"; f="COM_CMB_IQU-smica_2048_R3.00_full.fits"; min=1000000; urls=@(
        "https://pla.esac.esa.int/pla/aio/product-action?COSMOLOGY.FILE_ID=COM_CMB_IQU-smica_2048_R3.00_full.fits")},

    # --- Planck 2018 CB maps (Minami-Komatsu data) ---
    @{ d="planck_pr4\cb_2020"; f="planck_353_EE_BB_spectra.txt"; min=500; urls=@(
        "https://raw.githubusercontent.com/giorgiazagatti/CB_Planck_maps_spectra/main/data/planck_353_spectra.txt",
        "https://raw.githubusercontent.com/giorgiazagatti/CB_Planck_maps_spectra/master/data/planck_353_spectra.txt")},

    # --- BICEP/Keck BK18 (via LAMBDA) ---
    @{ d="bicep_keck\bk18"; f="bk18_bandpowers.txt"; min=500; urls=@(
        "https://bicepkeck.org/BK18_datarelease/bk18_bandpowers.txt",
        "https://raw.githubusercontent.com/bicepkeck/BK18/main/bk18_bandpowers.txt")},

    # --- WMAP 9yr polarization maps (small, historical) ---
    @{ d="wmap\wmap9"; f="wmap_9yr_pol.README"; min=100; urls=@(
        "https://lambda.gsfc.nasa.gov/data/map/dr5/dfp/README.txt")},

    # --- LiteBIRD forecast (futuro, para comparacion) ---
    @{ d="litebird\forecast"; f="litebird_forecast_beta.txt"; min=100; urls=@(
        "https://raw.githubusercontent.com/litebird/litebird_sim/master/README.md")},

    # --- Pantheon+ light curves (BIG: ~9 GB) ---
    @{ d="pantheon_plus\light_curves"; f="Pantheon+SH0ES_LSST.tar.gz"; min=1000000; urls=@(
        "https://github.com/PantheonPlusSH0ES/DataRelease/raw/main/Pantheon%2B_Data/3_LIGHTCURVES/Pantheon%2BSH0ES_LSST.tar.gz",
        "https://github.com/PantheonPlusSH0ES/DataRelease/raw/main/Pantheon%2B_Data/3_LIGHTCURVES/Pantheon%2BSH0ES.tar.gz")}
)

Blog "=== INICIO background ==="
Blog "Total descargas: $($descargas.Count)"

foreach ($d in $descargas) {
    $dir = Join-Path $RAW $d.d
    $dest = Join-Path $dir $d.f
    $part = "$dest.part"

    Blog "--- $($d.d) / $($d.f) ---"

    # Skip si ya existe valido
    if ((Test-Path $dest) -and ((Get-Item $dest).Length -ge $d.min)) {
        Blog "  ya existe OK ($((Get-Item $dest).Length) B)"
        continue
    }

    $ok = $false
    foreach ($url in $d.urls) {
        Blog "  intentando: $url"
        $curlArgs = @(
            "-L","--retry","5","--retry-delay","20","--retry-connrefused",
            "--continue-at","-",
            "--max-time","7200",
            "-s","-o",$part,
            "-w","%{http_code}",
            $url
        )
        $httpCode = (& curl.exe @curlArgs 2>$null)
        $rc = $LASTEXITCODE

        if ($rc -ne 0 -or $httpCode -ne "200") {
            Blog "    HTTP=$httpCode rc=$rc — siguiente"
            continue
        }
        if (-not (Test-Path $part)) {
            Blog "    .part no existe — siguiente"
            continue
        }
        $size = (Get-Item $part).Length
        if ($size -lt $d.min) {
            Blog "    tamano $size < $($d.min) — descartado"
            Remove-Item $part -Force
            continue
        }
        if (Test-Path $dest) { Remove-Item $dest -Force }
        Rename-Item -Path $part -NewName $d.f
        $sha = (Get-FileHash $dest -Algorithm SHA256).Hash.ToLower()
        $sizeFinal = (Get-Item $dest).Length
        Blog "  OK $sizeFinal B sha256=$($sha.Substring(0,16))..."
        $ok = $true
        break
    }

    if (-not $ok) {
        Blog "  FALLO todas las URLs"
    }
}

Blog "=== FIN background ==="
