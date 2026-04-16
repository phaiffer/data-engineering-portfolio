param(
    [int]$MaxEvents = 100,
    [int]$MaxSeconds = 60,
    [switch]$Force
)

. (Join-Path $PSScriptRoot "_helpers.ps1")

$Arguments = @(
    "projects/05-event-stream-analytics/src/jobs/run_publisher.py",
    "--max-events",
    "$MaxEvents",
    "--max-seconds",
    "$MaxSeconds"
)

if ($Force) {
    $Arguments += "--force"
}

Invoke-ProjectPython -Arguments $Arguments
