. (Join-Path $PSScriptRoot "_helpers.ps1")

$Arguments = @(
    "-m",
    "pytest",
    "projects/05-event-stream-analytics/tests"
)

Invoke-ProjectPython -Arguments $Arguments
