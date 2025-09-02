#!/bin/bash
set -e  # Exit on any error

echo "[INFO] Setting up MsgCenterPy development environment..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is required but not installed."
    exit 1
fi

# Install the package in development mode
echo "[INFO] Installing package in development mode..."
pip install -e .[dev]

# Install pre-commit hooks
echo "[INFO] Installing pre-commit hooks..."
pre-commit install

# Install pre-commit hooks for commit-msg (optional)
echo "[INFO] Installing commit-msg hooks..."
pre-commit install --hook-type commit-msg || echo "[WARNING] commit-msg hooks installation failed (optional)"

# Run pre-commit on all files to check setup
echo "[INFO] Running pre-commit on all files to verify setup..."
if pre-commit run --all-files; then
    echo "[SUCCESS] Pre-commit setup completed successfully!"
    echo ""
    echo "[SUCCESS] You're all set! Pre-commit will now run automatically on every commit."
    echo ""
    echo "[INFO] Quick commands:"
    echo "  • Run all hooks manually:     pre-commit run --all-files"
    echo "  • Update hook versions:       pre-commit autoupdate"
    echo "  • Skip hooks for one commit:  git commit --no-verify"
    echo "  • Run tests:                  pytest"
    echo "  • Type checking:              mypy msgcenterpy"
else
    echo "[WARNING] Pre-commit found some issues. Please fix them and run 'pre-commit run --all-files' again."
    echo "[TIP] Or use 'pre-commit run --all-files --show-diff-on-failure' to see what needs to be fixed."
fi

echo ""
echo "[INFO] Integration with CI:"
echo "  • CI will run the same pre-commit hooks"
echo "  • If you skip pre-commit locally, CI will catch the issues"
echo "  • Best practice: Always let pre-commit fix issues before committing"
