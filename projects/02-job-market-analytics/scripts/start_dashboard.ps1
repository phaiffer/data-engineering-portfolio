param(
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$DashboardRoot = Join-Path $ProjectRoot "dashboard"
$NodeModules = Join-Path $DashboardRoot "node_modules"

Push-Location $DashboardRoot
try {
    if (-not $SkipInstall -and -not (Test-Path $NodeModules)) {
        Write-Host "node_modules not found. Running npm install."
        & npm install
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    }

    & npm run dev
}
finally {
    Pop-Location
}
