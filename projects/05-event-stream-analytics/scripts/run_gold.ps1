param(
    [string[]]$EventDate,
    [switch]$Force
)

. (Join-Path $PSScriptRoot "_helpers.ps1")

$Arguments = @("projects/05-event-stream-analytics/src/jobs/run_gold.py")

foreach ($Date in $EventDate) {
    $Arguments += @("--event-date", $Date)
}
if ($Force) {
    $Arguments += "--force"
}

Invoke-ProjectPython -Arguments $Arguments
