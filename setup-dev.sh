#!/bin/bash
# Development environment setup script for MsgCenterPy

set -e  # Exit on any error

echo "🚀 Setting up MsgCenterPy development environment..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    exit 1
fi

# Install the package in development mode
echo "📦 Installing package in development mode..."
pip install -e .[dev]

# Install pre-commit
echo "🔧 Installing pre-commit..."
pip install pre-commit

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install

# Install pre-commit hooks for commit-msg (optional)
echo "📝 Installing commit-msg hooks..."
pre-commit install --hook-type commit-msg || echo "⚠️  commit-msg hooks installation failed (optional)"

# Run pre-commit on all files to check setup
echo "🔍 Running pre-commit on all files to verify setup..."
if pre-commit run --all-files; then
    echo "✅ Pre-commit setup completed successfully!"
    echo ""
    echo "🎉 You're all set! Pre-commit will now run automatically on every commit."
    echo ""
    echo "📋 Quick commands:"
    echo "  • Run all hooks manually:     pre-commit run --all-files"
    echo "  • Update hook versions:       pre-commit autoupdate"
    echo "  • Skip hooks for one commit:  git commit --no-verify"
    echo "  • Run tests:                  pytest"
    echo "  • Type checking:              mypy msgcenterpy"
else
    echo "⚠️  Pre-commit found some issues. Please fix them and run 'pre-commit run --all-files' again."
    echo "💡 Or use 'pre-commit run --all-files --show-diff-on-failure' to see what needs to be fixed."
fi

echo ""
echo "🔗 Integration with CI:"
echo "  • CI will run the same pre-commit hooks"
echo "  • If you skip pre-commit locally, CI will catch the issues"
echo "  • Best practice: Always let pre-commit fix issues before committing"
