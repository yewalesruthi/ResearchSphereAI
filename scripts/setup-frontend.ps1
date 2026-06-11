# ResearchSphere AI — Frontend Setup (Windows PowerShell)
$ErrorActionPreference = "Stop"
$FrontendDir = Join-Path $PSScriptRoot "..\frontend"
Set-Location $FrontendDir

Write-Host "Installing npm dependencies..." -ForegroundColor Cyan
npm install

if (-not (Test-Path ".env.local")) {
    Copy-Item ".env.local.example" ".env.local"
    Write-Host "Created .env.local from example." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Frontend setup complete." -ForegroundColor Green
Write-Host "Run: cd frontend; npm run dev" -ForegroundColor Cyan
