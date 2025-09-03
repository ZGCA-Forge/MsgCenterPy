Contributing to MsgCenterPy
===========================

Thank you for your interest in contributing to MsgCenterPy! This document provides guidelines for contributing to the project.

Quick Links
-----------

- `GitHub Repository <https://github.com/ZGCA-Forge/MsgCenterPy>`_
- `Issue Tracker <https://github.com/ZGCA-Forge/MsgCenterPy/issues>`_
- `Pull Requests <https://github.com/ZGCA-Forge/MsgCenterPy/pulls>`_

Development Setup
-----------------

1. Fork the repository on GitHub
2. Clone your fork locally:

.. code-block:: bash

   git clone https://github.com/YOUR_USERNAME/MsgCenterPy.git
   cd MsgCenterPy

3. (Optional) If you need ROS2 support, set up ROS environment first:

.. code-block:: bash

   # Create and activate conda environment with ROS2
   conda create -n msgcenterpy-dev python=3.11
   conda activate msgcenterpy-dev
   conda install ros-humble-ros-core ros-humble-std-msgs ros-humble-geometry-msgs -c robostack-staging

4. Run the development setup script:

**Linux/macOS:**

.. code-block:: bash

   ./scripts/setup-dev.sh

**Windows:**

.. code-block:: powershell

   .\scripts\setup-dev.ps1

The setup script will automatically:

- Install the package in development mode with all dependencies
- Set up pre-commit hooks
- Run initial code quality checks
- Display helpful commands for development

Code Style and Quality
----------------------

We use automated code quality checks that run via pre-commit hooks:

- **Black**: Code formatting (line length: 120)
- **isort**: Import sorting
- **flake8**: Code linting
- **mypy**: Type checking
- **bandit**: Security scanning
- **prettier**: YAML/JSON formatting

These checks run automatically when you commit. You can also run them manually:

.. code-block:: bash

   # Run all pre-commit hooks
   pre-commit run --all-files

Testing
-------

**Important**: Always run tests before committing to ensure your changes work correctly.

.. code-block:: bash

   # Run all tests
   pytest

   # Run with verbose output
   pytest -v

**Note**: If ROS2 is not installed, ROS-related tests will be automatically skipped. The test suite is designed to work with or without ROS2 dependencies.

Version Management
------------------

This project uses `bump2version` for version management. It's automatically installed with dev dependencies.

.. code-block:: bash

   # Bug fixes (0.0.1 → 0.0.2)
   bump2version patch

   # New features (0.0.2 → 0.1.0)
   bump2version minor

   # Breaking changes (0.1.0 → 1.0.0)
   bump2version major

After bumping version, push changes and tags:

.. code-block:: bash

   git push && git push --tags

Submitting Changes
------------------

1. Create a new branch for your feature/fix
2. Make your changes and add tests
3. Run tests to ensure everything works
4. Update documentation if needed
5. Submit a pull request with:
   - Descriptive title and description
   - Reference to related issues
   - Tests for new features

Getting Help
------------

- Check existing `Issues <https://github.com/ZGCA-Forge/MsgCenterPy/issues>`_
