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
$DbtVenvPython = Join-Path $RepoRoot ".venv-dbt\Scripts\python.exe"
$DbtVenvCli = Join-Path $RepoRoot ".venv-dbt\Scripts\dbt.exe"
$DbtRequirements = Join-Path $DbtRoot "requirements.txt"

function Test-CommandAvailable {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CommandName
    )

    return $null -ne (Get-Command $CommandName -ErrorAction SilentlyContinue)
}

function Test-UvExecutable {
    if (-not (Test-CommandAvailable "uv")) {
        return $false
    }

    try {
        & uv --version *> $null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

function Show-DbtSetupHelp {
    Write-Host "DBT needs a Python 3.12 environment for this project." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "From the repository root, run:"
    Write-Host "  py -3.12 -m venv .venv-dbt"
    Write-Host "  .\.venv-dbt\Scripts\python.exe -m pip install --upgrade pip"
    Write-Host "  .\.venv-dbt\Scripts\python.exe -m pip install -r .\projects\03-retail-revenue-analytics\dbt\requirements.txt"
    Write-Host ""
    Write-Host "Then retry:"
    Write-Host "  .\projects\03-retail-revenue-analytics\scripts\dbt_build.ps1 build"
}

Push-Location $DbtRoot
try {
    if (Test-Path $DbtVenvPython) {
        if (Test-Path $DbtVenvCli) {
            & $DbtVenvCli $Command --profiles-dir . --target duckdb @DbtArgs
        }
        else {
            & $DbtVenvPython -m dbt.cli.main $Command --profiles-dir . --target duckdb @DbtArgs
        }
    }
    elseif (Test-CommandAvailable "py") {
        & py -3.12 -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)"
        if ($LASTEXITCODE -ne 0) {
            Show-DbtSetupHelp
            exit 1
        }

        & py -3.12 -c "try:`n import dbt.cli.main`n raise SystemExit(0)`nexcept Exception:`n raise SystemExit(1)"
        if ($LASTEXITCODE -ne 0) {
            Show-DbtSetupHelp
            exit 1
        }

        & py -3.12 -m dbt.cli.main $Command --profiles-dir . --target duckdb @DbtArgs
    }
    elseif (Test-UvExecutable) {
        & uv run --python 3.12 --with-requirements $DbtRequirements python -m dbt.cli.main $Command --profiles-dir . --target duckdb @DbtArgs
    }
    else {
        Show-DbtSetupHelp
        exit 1
    }

    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
finally {
    Pop-Location
}
