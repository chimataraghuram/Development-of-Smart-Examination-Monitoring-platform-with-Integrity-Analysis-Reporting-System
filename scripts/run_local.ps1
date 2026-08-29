$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path "$PSScriptRoot\..").Path
$projectPattern = [regex]::Escape($projectRoot)

Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
    Where-Object { $_.CommandLine -match $projectPattern -and $_.CommandLine -match 'Backend\.app' } |
    ForEach-Object {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        Write-Host "Stopped stale project server PID $($_.ProcessId)"
    }

Start-Sleep -Seconds 1
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw "Virtual environment Python was not found at $python" }
Set-Location $projectRoot
Write-Host "Serving project: $projectRoot"
Write-Host "Local URL: http://127.0.0.1:5000/login"
& $python -m Backend.app
