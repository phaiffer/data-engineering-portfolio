param(
    [int]$MaxEvents = 100,
    [int]$MaxSeconds = 60,
    [switch]$Replay
)

. (Join-Path $PSScriptRoot "_helpers.ps1")

$Arguments = @(
    "projects/05-event-stream-analytics/src/jobs/run_bronze_consumer.py",
    "--max-events",
    "$MaxEvents",
    "--max-seconds",
    "$MaxSeconds"
)

if ($Replay) {
    $Arguments += "--replay"
}

Invoke-ProjectPython -Arguments $Arguments
