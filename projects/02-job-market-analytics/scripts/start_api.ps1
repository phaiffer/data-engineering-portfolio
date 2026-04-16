param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $ProjectRoot "..\..\..")
$RepoVenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (Test-Path $RepoVenvPython) {
    $PythonCommand = $RepoVenvPython
}
else {
    $PythonCommand = "python"
}

Push-Location $RepoRoot
try {
    & $PythonCommand "projects/02-job-market-analytics/api/app.py"
}
finally {
    Pop-Location
}
