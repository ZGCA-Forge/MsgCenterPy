Contributing to MsgCenterPy
===========================

Thank you for your interest in contributing to MsgCenterPy! This document provides guidelines for contributing to the project.

For detailed contribution guidelines, please see our `Contributing Guide <https://github.com/ZGCA-Forge/MsgCenterPy/blob/main/.github/CONTRIBUTING.md>`_ on GitHub.

Quick Links
-----------

- `GitHub Repository <https://github.com/ZGCA-Forge/MsgCenterPy>`_
- `Issue Tracker <https://github.com/ZGCA-Forge/MsgCenterPy/issues>`_
- `Pull Requests <https://github.com/ZGCA-Forge/MsgCenterPy/pulls>`_
- `Discussions <https://github.com/ZGCA-Forge/MsgCenterPy/discussions>`_

Development Setup
-----------------

1. Fork the repository on GitHub
2. Clone your fork locally
3. Install in development mode:

.. code-block:: bash

   git clone https://github.com/YOUR-USERNAME/MsgCenterPy.git
   cd MsgCenterPy
   pip install -e .[dev]

4. Set up pre-commit hooks:

.. code-block:: bash

   pre-commit install

Code Style and Quality
----------------------

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **pytest**: Testing

Run quality checks:

.. code-block:: bash

   # Format code
   black msgcenterpy tests
   isort msgcenterpy tests

   # Type checking
   mypy msgcenterpy

   # Run tests
   pytest

Testing
-------

Please ensure all tests pass and add tests for new features:

.. code-block:: bash

   # Run all tests
   pytest

   # Run with coverage
   pytest -v

   # Run specific test file
   pytest tests/test_specific_module.py

Version Management
------------------

This project uses `bump2version` for semantic version management. The tool is included in development dependencies and automatically manages version numbers across the codebase.

**Setup**

bump2version is automatically installed when you install development dependencies:

.. code-block:: bash

   pip install -e .[dev]

**Configuration**

Version configuration is stored in `.bumpversion.cfg`:

- **Single source of truth**: `msgcenterpy/__init__.py`
- **Auto-commit**: Creates commit with version bump
- **Auto-tag**: Creates git tag for new version
- **Semantic versioning**: Follows MAJOR.MINOR.PATCH format

**Usage**

.. code-block:: bash

   # Bug fixes (0.0.1 → 0.0.2)
   bump2version patch

   # New features (0.0.2 → 0.1.0)
   bump2version minor

   # Breaking changes (0.1.0 → 1.0.0)
   bump2version major

**Release Workflow**

1. Make your changes and commit them
2. Choose appropriate version bump type
3. Run bump2version command
4. Push changes and tags:

.. code-block:: bash

   git push && git push --tags

**Version Bump Guidelines**

- **patch**: Bug fixes, documentation updates, internal refactoring
- **minor**: New features, backward-compatible API additions
- **major**: Breaking changes, API removals or modifications

**Notes**

- Only developers need bump2version (it's in dev dependencies only)
- Version numbers are automatically synchronized across all files
- Git working directory must be clean before version bump
- Each version bump creates a commit and git tag automatically

Submitting Changes
------------------

1. Create a new branch for your feature/fix
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation if needed
6. Submit a pull request

Pull Request Guidelines
-----------------------

- Use descriptive titles and descriptions
- Reference related issues
- Include tests for new features
- Update documentation as needed
- Follow the existing code style

Getting Help
------------

If you need help:

- Check existing `Issues <https://github.com/ZGCA-Forge/MsgCenterPy/issues>`_
- Start a `Discussion <https://github.com/ZGCA-Forge/MsgCenterPy/discussions>`_
- Contact the maintainers
