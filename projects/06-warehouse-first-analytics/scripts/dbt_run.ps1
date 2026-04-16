param(
    [string]$Select,
    [int]$MinYear
)

. (Join-Path $PSScriptRoot "_helpers.ps1")

$Arguments = @("run")

if ($Select) {
    $Arguments += @("--select", $Select)
}
if ($MinYear) {
    $Arguments += @("--vars", "{`"stackoverflow_min_year`": $MinYear}")
}

Invoke-Dbt -Arguments $Arguments
