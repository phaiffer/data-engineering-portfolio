param(
    [switch]$SkipSilverRefresh
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $ProjectRoot "..\..\..")
$SilverDataset = Join-Path $ProjectRoot "data\silver\ai_job_market_insights_silver.csv"

function Get-PythonCommand {
    $RepoVenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
    if (Test-Path $RepoVenvPython) {
        return $RepoVenvPython
    }

    return "python"
}

if (-not $SkipSilverRefresh -and -not (Test-Path $SilverDataset)) {
    Write-Host "Silver dataset not found. Building Silver artifact first."
    Push-Location $RepoRoot
    try {
        & (Get-PythonCommand) "projects/02-job-market-analytics/src/jobs/run_silver.py"
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    }
    finally {
        Pop-Location
    }
}

$DbtScript = Join-Path $ProjectRoot "dbt\scripts\run_dbt_duckdb.ps1"

& $DbtScript debug
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

& $DbtScript run
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

& $DbtScript test
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "DuckDB dbt validation completed successfully."
