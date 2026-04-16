param(
    [ValidateSet("debug", "run", "test", "build")]
    [string]$Command = "build",

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$DbtArgs
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $ProjectRoot "..\..")
$DbtRoot = Join-Path $ProjectRoot "dbt"
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

Push-Location $DbtRoot
try {
    $UseVenv = $false
    if (Test-Path $VenvPython) {
        & $VenvPython -c "try:`n import dbt.cli.main`n raise SystemExit(0)`nexcept Exception:`n raise SystemExit(1)"
        $UseVenv = $LASTEXITCODE -eq 0
    }

    if ($UseVenv) {
        & $VenvPython -m dbt.cli.main $Command --profiles-dir . --target duckdb @DbtArgs
    }
    else {
        $DbtRequirements = Join-Path $DbtRoot "requirements.txt"
        & uv run --python 3.12 --with-requirements $DbtRequirements python -m dbt.cli.main $Command --profiles-dir . --target duckdb @DbtArgs
    }

    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
finally {
    Pop-Location
}
