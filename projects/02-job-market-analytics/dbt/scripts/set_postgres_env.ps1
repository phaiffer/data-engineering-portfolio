param(
    [string]$EnvFile = (Join-Path $PSScriptRoot "..\..\.env")
)

$ErrorActionPreference = "Stop"
$ResolvedEnvFile = Resolve-Path $EnvFile -ErrorAction SilentlyContinue

if (-not $ResolvedEnvFile) {
    Write-Host "Project .env not found at $EnvFile. DBT will use profile defaults or existing environment variables."
    return
}

Get-Content $ResolvedEnvFile | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith("#") -or -not $line.Contains("=")) {
        return
    }

    $parts = $line.Split("=", 2)
    $name = $parts[0].Trim()
    $value = $parts[1].Trim().Trim('"').Trim("'")

    if ($name.StartsWith("JOB_MARKET_")) {
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

Write-Host "Loaded JOB_MARKET_* PostgreSQL environment variables from $($ResolvedEnvFile.Path)"
