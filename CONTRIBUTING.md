# Contributing to Cyber Incident Response OpenEnv

We appreciate your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/cyber-incident-openenv.git
   cd cyber-incident-openenv
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install development dependencies**:
   ```bash
   pip install -r requirements.txt[dev]
   ```

## Development Workflow

### Code Style
- Follow PEP 8 conventions
- Use type hints for all functions and methods
- Format code with `black`:
  ```bash
  black .
  ```
- Lint with `flake8`:
  ```bash
  flake8 .
  ```

### Testing
Run tests before submitting a PR:
```bash
pytest
```

### Documentation
- Add docstrings to all classes and functions
- Update README.md if adding new features
- Document API changes in code comments

### Commit Messages
- Use clear, descriptive commit messages
- Start with a verb: "Add", "Fix", "Improve", "Refactor"
- Example: `Add CORS middleware to server.py`

## Submitting Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and test thoroughly

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Open a Pull Request** with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots/examples if applicable

## Reporting Issues

When reporting issues, include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or error messages

## Code Review Process

- Maintainers will review your PR
- Address feedback and request re-review
- PR must pass all tests and linting checks
- Squash commits if requested

## Areas for Contribution

- **Bug fixes**: Fix issues and edge cases
- **Tests**: Add or improve test coverage
- **Documentation**: Improve clarity and completeness
- **Features**: Implement new scenarios or task types
- **Performance**: Optimize slow operations
- **Docker**: Improve containerization and deployment

## Questions?

Feel free to:
- Open an issue for discussions
- Tag maintainers with @mentions
- Reference existing documentation

Thank you for contributing!
