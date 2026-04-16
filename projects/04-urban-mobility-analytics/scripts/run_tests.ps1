$ProjectRoot = Split-Path -Parent $PSScriptRoot
$RepoRoot = Resolve-Path (Join-Path $ProjectRoot "..\..")

Push-Location $RepoRoot
try {
    python -m pytest projects/04-urban-mobility-analytics/tests
}
finally {
    Pop-Location
}
