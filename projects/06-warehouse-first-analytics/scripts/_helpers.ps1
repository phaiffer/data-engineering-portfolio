$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$DbtRoot = Resolve-Path (Join-Path $ProjectRoot "dbt")
$ProjectVenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$VenvDbt = Join-Path $ProjectRoot ".venv\Scripts\dbt.exe"

function Invoke-Dbt {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    Push-Location $DbtRoot
    try {
        if (Test-Path $VenvDbt) {
            & $VenvDbt @Arguments
        }
        else {
            & dbt @Arguments
        }

        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    }
    finally {
        Pop-Location
    }
}

function Invoke-ProjectPython {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    Push-Location $ProjectRoot
    try {
        if (Test-Path $ProjectVenvPython) {
            & $ProjectVenvPython @Arguments
        }
        else {
            & python @Arguments
        }

        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    }
    finally {
        Pop-Location
    }
}
