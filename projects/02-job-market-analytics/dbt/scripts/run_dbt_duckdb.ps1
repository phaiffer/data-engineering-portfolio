param(
    [ValidateSet("debug", "run", "test", "parse")]
    [string]$Command = "run",

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$DbtArgs
)

$ErrorActionPreference = "Stop"
$DbtRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

Push-Location $DbtRoot
try {
    $arguments = @(
        "run",
        "--python", "3.12",
        "--with-requirements", "requirements.txt",
        "dbt",
        $Command,
        "--profiles-dir", ".",
        "--target", "duckdb"
    ) + $DbtArgs

    & uv @arguments
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
finally {
    Pop-Location
}
