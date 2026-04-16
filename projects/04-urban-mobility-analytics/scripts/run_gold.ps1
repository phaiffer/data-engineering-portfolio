param(
    [string]$StartMonth,
    [string]$EndMonth,
    [switch]$Force
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$RepoRoot = Resolve-Path (Join-Path $ProjectRoot "..\..")
$JobPath = "projects/04-urban-mobility-analytics/src/jobs/run_gold.py"
$Arguments = @($JobPath)

if ($StartMonth) {
    $Arguments += @("--start-month", $StartMonth)
}
if ($EndMonth) {
    $Arguments += @("--end-month", $EndMonth)
}
if ($Force) {
    $Arguments += "--force"
}

Push-Location $RepoRoot
try {
    python @Arguments
}
finally {
    Pop-Location
}
