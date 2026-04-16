param(
    [switch]$IncludeIngestion,
    [switch]$SkipBronze,
    [switch]$SkipGold,
    [switch]$SkipDbtBuild
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $ProjectRoot "..\..")
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

function Invoke-PythonJob {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ScriptPath
    )

    if (Test-Path $VenvPython) {
        & $VenvPython $ScriptPath
    }
    else {
        $RootRequirements = Join-Path $RepoRoot "requirements.txt"
        & uv run --python 3.12 --with-requirements $RootRequirements python $ScriptPath
    }

    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

Push-Location $ProjectRoot
try {
    if ($IncludeIngestion) {
        Invoke-PythonJob "src/jobs/run_ingestion.py"
    }

    if (-not $SkipBronze) {
        Invoke-PythonJob "src/jobs/run_bronze.py"
    }

    Invoke-PythonJob "src/jobs/run_silver.py"

    if (-not $SkipGold) {
        Invoke-PythonJob "src/jobs/run_gold.py"
    }

    if (-not $SkipDbtBuild) {
        & (Join-Path $PSScriptRoot "dbt_build.ps1") build
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    }
}
finally {
    Pop-Location
}
