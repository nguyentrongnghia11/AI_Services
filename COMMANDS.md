# Quick Command Reference

## Setup Commands

### With UV (Recommended ⚡)
```powershell
# One-time setup
pip install uv
uv venv
.\.venv\Scripts\Activate.ps1
uv pip install -e .

# Quick run (no activation needed)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### With pip (Traditional)
```powershell
# One-time setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Daily Development Commands

### Start Server
```powershell
# Development with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or with UV (no activation needed)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Production mode (no reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Test Connections
```powershell
python test_async_setup.py

# Or with UV
uv run python test_async_setup.py
```

### Add Dependencies
```powershell
# With UV (recommended)
uv add <package-name>

# With pip
pip install <package-name>
pip freeze > requirements.txt
```

### Update Dependencies
```powershell
# With UV
uv pip install --upgrade -e .

# With pip
pip install --upgrade -r requirements.txt
```

## Useful URLs

- **API Status**: http://localhost:8000/
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs (FastAPI auto-docs)
- **ReDoc**: http://localhost:8000/redoc

## Service Commands

### RabbitMQ
```powershell
# Start RabbitMQ (if installed as service)
rabbitmq-server

# Check status
rabbitmq-diagnostics status

# Management UI
# http://localhost:15672 (guest/guest)
```

### MongoDB
```powershell
# Start MongoDB (if installed as service)
mongod

# Check connection
mongosh
```

## Debugging Commands

### Check Active Processes
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace <PID> with actual PID)
taskkill /PID <PID> /F
```

### Check Python Environment
```powershell
# Which Python
python --version
where python

# List installed packages
pip list
# or
uv pip list
```

### Check Logs
```powershell
# Follow logs in real-time (when running)
# Just watch the terminal output

# Or redirect to file
uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs.txt 2>&1
```

## Git Commands (if using version control)

```powershell
# Check status
git status

# Stage changes
git add .

# Commit
git commit -m "Your message"

# Push
git push origin main
```

## Complete Restart Flow

```powershell
# 1. Stop current server (Ctrl+C)

# 2. Update code (if using git)
git pull

# 3. Update dependencies
uv pip install -e .
# or
pip install -r requirements.txt

# 4. Restart server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Troubleshooting Commands

### Reset Virtual Environment
```powershell
# Deactivate
deactivate

# Remove old venv
Remove-Item -Recurse -Force .venv

# Create new venv
uv venv
# or
python -m venv .venv

# Activate and reinstall
.\.venv\Scripts\Activate.ps1
uv pip install -e .
# or
pip install -r requirements.txt
```

### Clear Python Cache
```powershell
# Remove __pycache__ directories
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Recurse -Force

# Or use Python
python -c "import pathlib; import shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]"
```

### Check Port Availability
```powershell
# Check if port 8000 is in use
Test-NetConnection -ComputerName localhost -Port 8000
```

## Environment Variables

```powershell
# View current environment
Get-ChildItem Env:

# Set environment variable (temporary)
$env:RABBITMQ_HOST = "localhost"
$env:MONGO_URI = "mongodb://localhost:27017/MUSIC_APP"

# Or edit .env file
notepad .env
```

## Performance Testing

```powershell
# Basic load test with curl (Windows)
for ($i=1; $i -le 100; $i++) {
    Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
}

# Or use ab (Apache Bench) if installed
ab -n 1000 -c 10 http://localhost:8000/health
```

## Backup Commands

```powershell
# Backup current environment
pip freeze > requirements.backup.txt

# Create project snapshot
Compress-Archive -Path . -DestinationPath "../ai_services_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
```
