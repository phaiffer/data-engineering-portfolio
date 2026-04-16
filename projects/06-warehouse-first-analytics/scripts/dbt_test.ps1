param(
    [string]$Select
)

. (Join-Path $PSScriptRoot "_helpers.ps1")

$Arguments = @("test")

if ($Select) {
    $Arguments += @("--select", $Select)
}

Invoke-Dbt -Arguments $Arguments
