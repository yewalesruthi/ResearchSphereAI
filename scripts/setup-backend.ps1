# ResearchSphere AI — Backend Setup (Windows PowerShell)
$ErrorActionPreference = "Stop"
$BackendDir = Join-Path $PSScriptRoot "..\backend"
Set-Location $BackendDir

Write-Host "Creating virtual environment..." -ForegroundColor Cyan
python -m venv venv

Write-Host "Activating venv and installing dependencies..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"
pip install --upgrade pip
pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example — add your GROQ_API_KEY!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Backend setup complete." -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Edit backend\.env and set GROQ_API_KEY"
Write-Host "  2. Run: cd backend; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload"
