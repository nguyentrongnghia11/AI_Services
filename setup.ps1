# AI Services - Quick Setup with UV
# Run this script to set up the project quickly

Write-Host "================================" -ForegroundColor Cyan
Write-Host "AI Services - UV Quick Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if uv is installed
Write-Host "Checking for UV..." -ForegroundColor Yellow
$uvInstalled = Get-Command uv -ErrorAction SilentlyContinue

if (-not $uvInstalled) {
    Write-Host "UV not found. Installing UV..." -ForegroundColor Yellow
    pip install uv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install UV. Please install manually:" -ForegroundColor Red
        Write-Host "  pip install uv" -ForegroundColor White
        exit 1
    }
    Write-Host "UV installed successfully!" -ForegroundColor Green
} else {
    Write-Host "UV is already installed." -ForegroundColor Green
}

Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment with UV..." -ForegroundColor Yellow
uv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to create virtual environment." -ForegroundColor Red
    exit 1
}
Write-Host "Virtual environment created!" -ForegroundColor Green

Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$activateScript = ".\.venv\Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    # Set execution policy for this session
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
    
    # Activate
    & $activateScript
    
    if ($LASTEXITCODE -eq 0 -or $?) {
        Write-Host "Virtual environment activated!" -ForegroundColor Green
    } else {
        Write-Host "Warning: Activation may have issues. Continuing..." -ForegroundColor Yellow
    }
} else {
    Write-Host "Activation script not found at $activateScript" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Install dependencies
Write-Host "Installing dependencies with UV (this is fast!)..." -ForegroundColor Yellow
uv pip install -e .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install dependencies." -ForegroundColor Red
    exit 1
}
Write-Host "Dependencies installed successfully!" -ForegroundColor Green

Write-Host ""

# Check for .env file
Write-Host "Checking for .env file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host ".env file found!" -ForegroundColor Green
} else {
    Write-Host ".env file not found. Creating template..." -ForegroundColor Yellow
    @"
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/MUSIC_APP
DATABASE_NAME=MUSIC_APP

# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
"@ | Out-File -FilePath ".env" -Encoding utf8
    Write-Host ".env template created. Please update with your settings." -ForegroundColor Green
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Ensure RabbitMQ is running (rabbitmq-server)" -ForegroundColor White
Write-Host "  2. Ensure MongoDB is running (mongod)" -ForegroundColor White
Write-Host "  3. Update .env file with your configuration" -ForegroundColor White
Write-Host "  4. Test connections: python test_async_setup.py" -ForegroundColor White
Write-Host "  5. Start server: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor White
Write-Host ""
Write-Host "Or run in one command:" -ForegroundColor Yellow
Write-Host "  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor Cyan
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "  - QUICKSTART.md - Getting started guide" -ForegroundColor White
Write-Host "  - UV_SETUP.md - UV detailed guide" -ForegroundColor White
Write-Host "  - COMMANDS.md - Quick command reference" -ForegroundColor White
Write-Host ""
