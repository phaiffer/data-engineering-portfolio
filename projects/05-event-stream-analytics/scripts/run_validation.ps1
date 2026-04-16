param(
    [ValidateSet("normal", "broker_replay", "offline_replay")]
    [string]$Mode = "normal"
)

. (Join-Path $PSScriptRoot "_helpers.ps1")

$Arguments = @(
    "projects/05-event-stream-analytics/src/jobs/run_validation.py",
    "--mode",
    $Mode
)

Invoke-ProjectPython -Arguments $Arguments
