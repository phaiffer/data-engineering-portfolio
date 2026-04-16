param(
    [int]$MinYear,
    [switch]$SkipDocs
)

. (Join-Path $PSScriptRoot "_helpers.ps1")

Invoke-Dbt -Arguments @("debug")
Invoke-Dbt -Arguments @("deps")

$RunArguments = @("run")
if ($MinYear) {
    $RunArguments += @("--vars", "{`"stackoverflow_min_year`": $MinYear}")
}
Invoke-Dbt -Arguments $RunArguments

Invoke-Dbt -Arguments @("test")

if (-not $SkipDocs) {
    Invoke-Dbt -Arguments @("docs", "generate")
}
