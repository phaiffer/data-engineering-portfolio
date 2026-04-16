param(
    [switch]$SkipPostgresLoad
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $ProjectRoot "..\..\..")

function Get-PythonCommand {
    $RepoVenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
    if (Test-Path $RepoVenvPython) {
        return $RepoVenvPython
    }

    return "python"
}

if (-not $SkipPostgresLoad) {
    Write-Host "Loading Silver data into PostgreSQL."
    Push-Location $RepoRoot
    try {
        & (Get-PythonCommand) "projects/02-job-market-analytics/src/jobs/run_postgres_load.py"
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    }
    finally {
        Pop-Location
    }
}

$DbtScript = Join-Path $ProjectRoot "dbt\scripts\run_dbt_postgres.ps1"

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

Write-Host "PostgreSQL dbt validation completed successfully."
