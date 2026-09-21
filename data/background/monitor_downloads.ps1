param(
    [string]$QueueFile = "C:\Users\kg4tr\Documents\Investigacion_lab_secreto\data\background\queue_d8.json",
    [string]$RAW = "C:\Users\kg4tr\Documents\Investigacion_lab_secreto\data\raw",
    [int]$RefreshSec = 2
)

if (-not (Test-Path $QueueFile)) { Write-Host "ERROR: no se encuentra $QueueFile" -ForegroundColor Red; return }
$queue = Get-Content $QueueFile -Raw | ConvertFrom-Json

function Format-Bar($pct, $width = 20) {
    $pct = [math]::Max(0, [math]::Min(100, $pct))
    $filled = [math]::Floor($pct * $width / 100)
    $empty = $width - $filled
    return ("=" * $filled) + ("-" * $empty)
}
function Format-MB($bytes) {
    if ($bytes -ge 1GB) { return "$([math]::Round($bytes/1GB, 2)) GB" }
    if ($bytes -ge 1MB) { return "$([math]::Round($bytes/1MB, 2)) MB" }
    if ($bytes -ge 1KB) { return "$([math]::Round($bytes/1KB, 2)) KB" }
    return "$bytes B"
}

$startTime = Get-Date
$lastSize = 0
$lastCheck = $startTime

while ($true) {
    $now = Get-Date
    $elapsed = $now - $startTime
    $dt = ($now - $lastCheck).TotalSeconds
    $totalExpected = 0; $totalDone = 0; $allComplete = $true; $rows = @()

    foreach ($d in $queue) {
        $dest = Join-Path (Join-Path $RAW $d.d) $d.f
        $part = "$dest.part"
        $expBytes = 0
        if ($d.PSObject.Properties.Name -contains 'esperado' -and $d.esperado) { $expBytes = [int64]$d.esperado }
        $totalExpected += $expBytes

        if (Test-Path $dest) {
            $size = (Get-Item $dest).Length
            $pct = if ($expBytes -gt 0) { [math]::Min(100, [math]::Round(100 * $size / $expBytes, 1)) } else { 100 }
            $status = "OK"; $color = "Green"; $totalDone += $size
        } elseif (Test-Path $part) {
            $size = (Get-Item $part).Length
            $pct = if ($expBytes -gt 0) { [math]::Round(100 * $size / $expBytes, 1) } else { 0 }
            $status = "bajando"; $color = "Yellow"; $totalDone += $size; $allComplete = $false
        } else {
            $size = 0; $pct = 0; $status = "pendiente"; $color = "DarkGray"; $allComplete = $false
        }

        $rows += [PSCustomObject]@{
            Archivo = if ($d.f.Length -gt 45) { $d.f.Substring(0,42)+"..." } else { $d.f }
            Bar = "[" + (Format-Bar $pct 20) + "]"
            Pct = "$pct%"
            Progreso = "$(Format-MB $size) / $(Format-MB $expBytes)"
            Estado = $status
            _Color = $color
        }
    }

    $speedBps = if ($dt -gt 0) { ($totalDone - $lastSize) / $dt } else { 0 }
    $lastSize = $totalDone; $lastCheck = $now
    $globalPct = if ($totalExpected -gt 0) { [math]::Min(100, [math]::Round(100 * $totalDone / $totalExpected, 1)) } else { 0 }
    $eta = if ($speedBps -gt 0 -and $totalExpected -gt $totalDone) {
        $etaSec = ($totalExpected - $totalDone) / $speedBps
        [timespan]::FromSeconds($etaSec).ToString("hh\:mm\:ss")
    } else { "--:--:--" }

    Clear-Host
    Write-Host "=================================================================" -ForegroundColor Cyan
    Write-Host " MONITOR DE DESCARGAS  —  $($now.ToString('HH:mm:ss'))" -ForegroundColor Cyan
    Write-Host "=================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host " GLOBAL: [$(Format-Bar $globalPct 50)] $globalPct%" -ForegroundColor Yellow
    Write-Host "         $(Format-MB $totalDone) / $(Format-MB $totalExpected)   |   $(Format-MB $speedBps)/s   |   ETA: $eta   |   Transcurrido: $($elapsed.ToString('hh\:mm\:ss'))" -ForegroundColor Gray
    Write-Host ""

    $i = 0
    foreach ($r in $rows) {
        $i++
        $line = "{0,2}. {1,-48} {2} {3,7}  {4,-28}  {5}" -f $i, $r.Archivo, $r.Bar, $r.Pct, $r.Progreso, $r.Estado
        Write-Host $line -ForegroundColor $r._Color
    }

    Write-Host ""
    if ($allComplete) {
        Write-Host " >>> TODAS LAS DESCARGAS COMPLETADAS <<<" -ForegroundColor Green
        Write-Host " Tiempo total: $($elapsed.ToString('hh\:mm\:ss'))" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds $RefreshSec
}
