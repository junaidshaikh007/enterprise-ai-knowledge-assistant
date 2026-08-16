$ErrorActionPreference = "Stop"

$apiPath = Join-Path $PSScriptRoot "..\apps\api"

Push-Location $apiPath
try {
    python -m pytest tests
}
finally {
    Pop-Location
}
