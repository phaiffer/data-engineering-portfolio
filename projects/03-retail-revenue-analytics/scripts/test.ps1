param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PytestArgs
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $ProjectRoot "..\..")
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

Push-Location $ProjectRoot
try {
    $UseVenv = $false
    if (Test-Path $VenvPython) {
        & $VenvPython -c "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('pytest') else 1)"
        $UseVenv = $LASTEXITCODE -eq 0
    }

    if ($UseVenv) {
        & $VenvPython -m pytest tests @PytestArgs
    }
    else {
        $RootRequirements = Join-Path $RepoRoot "requirements.txt"
        & uv run --python 3.12 --with-requirements $RootRequirements --with pytest python -m pytest tests @PytestArgs
    }

    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
finally {
    Pop-Location
}
