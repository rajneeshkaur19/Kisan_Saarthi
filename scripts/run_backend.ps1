$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Get-VenvPython {
    if (Test-Path "$Root\.venv\Scripts\python.exe") { return "$Root\.venv\Scripts\python.exe" }
    if (Test-Path "$Root\.venv\bin\python.exe") { return "$Root\.venv\bin\python.exe" }
    return $null
}

function Get-HostPython {
    # Prefer official Windows Python via the py launcher (avoids MSYS2/MinGW python).
    try {
        $p = & py -3.11 -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $p) { return $p.Trim() }
    } catch {}
    try {
        $p = & py -3 -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $p) { return $p.Trim() }
    } catch {}
    return "python"
}

$Python = Get-VenvPython
if (-not $Python) {
    Write-Host "Creating virtual environment with Windows Python..." -ForegroundColor Cyan
    $HostPython = Get-HostPython
    & $HostPython -m venv .venv
    $Python = Get-VenvPython
    if (-not $Python) { throw "Could not create or locate .venv Python executable." }
}

& $Python -m pip install --upgrade pip
& $Python -m pip install -r backend\requirements.txt

Write-Host "Starting FastAPI on http://localhost:8000 ..." -ForegroundColor Green
& $Python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
