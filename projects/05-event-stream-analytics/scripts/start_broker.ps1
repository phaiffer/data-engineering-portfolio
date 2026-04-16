. (Join-Path $PSScriptRoot "_helpers.ps1")

Push-Location $ProjectRoot
try {
    docker compose up -d
    docker compose ps
}
finally {
    Pop-Location
}
