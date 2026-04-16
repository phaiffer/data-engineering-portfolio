param(
    [string[]]$BatchId,
    [switch]$Force
)

. (Join-Path $PSScriptRoot "_helpers.ps1")

$Arguments = @("projects/05-event-stream-analytics/src/jobs/run_silver.py")

foreach ($Id in $BatchId) {
    $Arguments += @("--batch-id", $Id)
}
if ($Force) {
    $Arguments += "--force"
}

Invoke-ProjectPython -Arguments $Arguments
