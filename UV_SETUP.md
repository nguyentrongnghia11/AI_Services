# UV Setup Guide

## What is UV?

`uv` is a blazingly fast Python package installer and resolver written in Rust. It's a drop-in replacement for pip that's 10-100x faster.

## Installation

### Install UV (Windows PowerShell)

```powershell
# Using PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or using pip
pip install uv
```

### Install UV (Linux/macOS)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Quick Start

### 1. Create Virtual Environment with UV

```powershell
# From project root
cd D:\ProjectPersonal\Social_Website\ai_services

# Create venv with uv (much faster than python -m venv)
uv venv
```

### 2. Activate Virtual Environment

```powershell
# PowerShell
.\.venv\Scripts\Activate.ps1

# CMD
.\.venv\Scripts\activate.bat
```

### 3. Install Dependencies with UV

```powershell
# Install all dependencies from pyproject.toml (10-100x faster than pip)
uv pip install -e .

# Or sync from lock file (recommended for reproducible builds)
uv pip sync

# Install with dev dependencies
uv pip install -e ".[dev]"
```

## Using UV Commands

### Add New Dependency

```powershell
# Add a new package
uv add <package-name>

# Example: Add numpy
uv add numpy

# Add dev dependency
uv add --dev pytest-cov
```

### Remove Dependency

```powershell
uv remove <package-name>

# Example: Remove numpy
uv remove numpy
```

### Update Dependencies

```powershell
# Update all dependencies
uv pip install --upgrade -e .

# Update specific package
uv pip install --upgrade <package-name>
```

### List Installed Packages

```powershell
uv pip list
```

### Sync Environment (Recommended)

```powershell
# Sync environment to match pyproject.toml exactly
uv pip sync
```

## Running the Application with UV

### Development Mode

```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Run with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Using UV Run (No activation needed)

```powershell
# UV can run commands in the venv automatically
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
uv run pytest

# Run test script
uv run python test_async_setup.py
```

## Migration from pip to uv

### Step 1: Install UV

```powershell
pip install uv
```

### Step 2: Create pyproject.toml (Already done ✅)

The project now has `pyproject.toml` with all dependencies.

### Step 3: Remove old venv (optional)

```powershell
# Deactivate current venv if active
deactivate

# Remove old venv
Remove-Item -Recurse -Force .venv
```

### Step 4: Create new venv with UV

```powershell
# Create venv with uv (super fast)
uv venv

# Activate
.\.venv\Scripts\Activate.ps1

# Install dependencies (much faster than pip)
uv pip install -e .
```

## Performance Comparison

| Operation | pip | uv | Speedup |
|-----------|-----|-----|---------|
| Fresh install | ~2 min | ~5 sec | **24x faster** |
| Reinstall (cached) | ~30 sec | ~1 sec | **30x faster** |
| Resolve deps | ~10 sec | ~0.5 sec | **20x faster** |

## Common Commands Cheat Sheet

```powershell
# Create venv
uv venv

# Activate venv (PowerShell)
.\.venv\Scripts\Activate.ps1

# Install all deps
uv pip install -e .

# Install with dev deps
uv pip install -e ".[dev]"

# Add new package
uv add <package>

# Remove package
uv remove <package>

# Update all packages
uv pip install --upgrade -e .

# Run command without activation
uv run <command>

# Sync to exact versions
uv pip sync

# List packages
uv pip list

# Freeze deps
uv pip freeze > requirements.txt
```

## Project Structure with UV

```
ai_services/
├── .venv/                  # Virtual environment (created by uv venv)
├── app/                    # Application code
│   ├── __init__.py
│   ├── main.py
│   ├── consumer.py
│   ├── database/
│   ├── services/
│   └── utils/
├── pyproject.toml          # Project config & dependencies (uv reads this)
├── requirements.txt        # Legacy support (optional, can keep for backup)
├── test_async_setup.py
├── QUICKSTART.md
└── ASYNC_MIGRATION.md
```

## Troubleshooting

### UV not found after install

**Solution:** Restart PowerShell or add to PATH:
```powershell
$env:PATH += ";$env:USERPROFILE\.cargo\bin"
```

### Slow first install

**Solution:** UV downloads packages on first run. Subsequent installs use cache and are much faster.

### Can't activate venv

**Solution:** 
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
```

### Want to go back to pip

**Solution:** Just use `pip` commands as normal. UV is a drop-in replacement, not exclusive.

## Why Use UV?

✅ **10-100x faster** than pip  
✅ **Better dependency resolution** - catches conflicts earlier  
✅ **Disk space efficient** - shared cache across projects  
✅ **Drop-in replacement** - works with existing pip/pyproject.toml  
✅ **Modern tooling** - written in Rust, actively maintained  
✅ **Compatible** - works with PyPI, private registries  

## Next Steps

1. ✅ Install UV: `pip install uv`
2. ✅ Create venv: `uv venv`
3. ✅ Activate: `.\.venv\Scripts\Activate.ps1`
4. ✅ Install deps: `uv pip install -e .`
5. 🚀 Run app: `uvicorn app.main:app --reload`

Or use the one-liner:
```powershell
uv venv && .\.venv\Scripts\Activate.ps1 && uv pip install -e . && uvicorn app.main:app --reload
```
