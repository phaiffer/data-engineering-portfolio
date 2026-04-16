. (Join-Path $PSScriptRoot "_helpers.ps1")

Invoke-Dbt -Arguments @("deps")
