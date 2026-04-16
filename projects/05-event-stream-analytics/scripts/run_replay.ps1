param(
    [ValidateSet("all", "silver", "gold")]
    [string]$Target = "all"
)

. (Join-Path $PSScriptRoot "_helpers.ps1")

$Arguments = @(
    "projects/05-event-stream-analytics/src/jobs/run_replay.py",
    "--target",
    $Target
)

Invoke-ProjectPython -Arguments $Arguments
