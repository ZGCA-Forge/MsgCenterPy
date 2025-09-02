# Development environment setup script for MsgCenterPy (Windows PowerShell)

Write-Host "🚀 Setting up MsgCenterPy development environment..." -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python 3 is required but not found in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.10+ and add it to your PATH." -ForegroundColor Yellow
    exit 1
}

# Install the package in development mode
Write-Host "📦 Installing package in development mode..." -ForegroundColor Blue
pip install -e .[dev]
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install package in development mode" -ForegroundColor Red
    exit 1
}

# Install pre-commit
Write-Host "🔧 Installing pre-commit..." -ForegroundColor Blue
pip install pre-commit
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install pre-commit" -ForegroundColor Red
    exit 1
}

# Install pre-commit hooks
Write-Host "🪝 Installing pre-commit hooks..." -ForegroundColor Blue
pre-commit install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install pre-commit hooks" -ForegroundColor Red
    exit 1
}

# Install pre-commit hooks for commit-msg (optional)
Write-Host "📝 Installing commit-msg hooks..." -ForegroundColor Blue
pre-commit install --hook-type commit-msg
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  commit-msg hooks installation failed (optional)" -ForegroundColor Yellow
}

# Run pre-commit on all files to check setup
Write-Host "🔍 Running pre-commit on all files to verify setup..." -ForegroundColor Blue
pre-commit run --all-files
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Pre-commit setup completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 You're all set! Pre-commit will now run automatically on every commit." -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Quick commands:" -ForegroundColor Cyan
    Write-Host "  • Run all hooks manually:     pre-commit run --all-files" -ForegroundColor White
    Write-Host "  • Update hook versions:       pre-commit autoupdate" -ForegroundColor White
    Write-Host "  • Skip hooks for one commit:  git commit --no-verify" -ForegroundColor White
    Write-Host "  • Run tests:                  pytest" -ForegroundColor White
    Write-Host "  • Type checking:              mypy msgcenterpy" -ForegroundColor White
} else {
    Write-Host "⚠️  Pre-commit found some issues. Please fix them and run 'pre-commit run --all-files' again." -ForegroundColor Yellow
    Write-Host "💡 Or use 'pre-commit run --all-files --show-diff-on-failure' to see what needs to be fixed." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🔗 Integration with CI:" -ForegroundColor Cyan
Write-Host "  • CI will run the same pre-commit hooks" -ForegroundColor White
Write-Host "  • If you skip pre-commit locally, CI will catch the issues" -ForegroundColor White
Write-Host "  • Best practice: Always let pre-commit fix issues before committing" -ForegroundColor White
