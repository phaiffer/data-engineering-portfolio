. (Join-Path $PSScriptRoot "_helpers.ps1")

Push-Location $ProjectRoot
try {
    docker compose down
}
finally {
    Pop-Location
}
