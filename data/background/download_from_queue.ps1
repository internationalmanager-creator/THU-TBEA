$RAW = "C:\Users\kg4tr\Documents\Investigacion_LaboratorioSecreto\data\raw"
$BG  = "C:\Users\kg4tr\Documents\Investigacion_LaboratorioSecreto\data\background"
$LOG = "$RAW\_background_v3_log.txt"
function Blog($m) { Add-Content -Path $LOG -Value "[$((Get-Date).ToUniversalTime().ToString('s'))Z] $m" -Encoding utf8NoBOM }

$descargas = Get-Content "$BG\download_queue.json" -Raw | ConvertFrom-Json
Blog "=== INICIO descarga completa ==="
Blog "Total: $($descargas.Count) archivos"

$i = 0
foreach ($d in $descargas) {
    $i++
    $dir = Join-Path $RAW $d.d
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    $dest = Join-Path $dir $d.f
    $part = "$dest.part"

    Blog "[$i/$($descargas.Count)] --- $($d.d)/$($d.f) ---"

    if ((Test-Path $dest) -and ((Get-Item $dest).Length -ge $d.min)) {
        Blog "  ya existe OK ($((Get-Item $dest).Length) B)"
        continue
    }

    $curlArgs = @("-L","--retry","5","--retry-delay","20","--retry-connrefused","--continue-at","-","--max-time","7200","-s","-o",$part,"-w","%{http_code}",$d.url)
    $httpCode = (& curl.exe @curlArgs 2>$null)

    if ($httpCode -ne "200" -or -not (Test-Path $part)) {
        Blog "  HTTP=$httpCode FALLO"
        continue
    }
    $size = (Get-Item $part).Length
    if ($size -lt $d.min) {
        Blog "  tamano $size < $($d.min) descartado"
        Remove-Item $part -Force
        continue
    }
    if (Test-Path $dest) { Remove-Item $dest -Force }
    Rename-Item -Path $part -NewName $d.f
    $sha = (Get-FileHash $dest -Algorithm SHA256).Hash.ToLower()
    $mb = [math]::Round($size/1MB, 2)
    Blog "  OK $mb MB sha256=$($sha.Substring(0,16))..."
}
Blog "=== FIN ==="
