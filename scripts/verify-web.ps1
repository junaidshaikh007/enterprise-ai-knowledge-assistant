$ErrorActionPreference = "Stop"

$webPath = Join-Path $PSScriptRoot "..\apps\web"

Push-Location $webPath
try {
    npm run lint
    npm run build
}
finally {
    Pop-Location
}
