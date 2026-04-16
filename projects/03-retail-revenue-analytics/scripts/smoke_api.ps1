param(
    [string]$BaseUrl = "http://127.0.0.1:5002"
)

$ErrorActionPreference = "Stop"

$CleanBaseUrl = $BaseUrl.TrimEnd("/")
$Checks = @(
    @{ Name = "health"; Path = "/health" },
    @{ Name = "api index"; Path = "/api/v1" },
    @{ Name = "kpis"; Path = "/api/v1/kpis" }
)

foreach ($Check in $Checks) {
    $Url = "$CleanBaseUrl$($Check.Path)"
    Write-Host "Checking $($Check.Name): $Url"

    try {
        $Response = Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 10
        if ($null -eq $Response) {
            throw "Empty response from $Url"
        }
    }
    catch {
        Write-Error "Smoke check failed for $($Check.Name) at $Url. Start the Flask API first, then retry. Details: $($_.Exception.Message)"
        exit 1
    }
}

Write-Host "API smoke checks passed for $CleanBaseUrl"
