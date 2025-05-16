# Contributing to ResGuard

Thank you for considering contributing to ResGuard! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of others.

## How Can I Contribute?

### Reporting Bugs

- Check if the bug has already been reported in the [Issues](https://github.com/lakshyakumar90/Resguard--Resource-Management-System/issues)
- Use the bug report template to create a new issue
- Include detailed steps to reproduce the bug
- Include screenshots if applicable
- Specify your environment (OS, Python version, etc.)

### Suggesting Features

- Check if the feature has already been suggested in the [Issues](https://github.com/lakshyakumar90/Resguard--Resource-Management-System/issues)
- Use the feature request template to create a new issue
- Provide a clear description of the feature and its benefits
- Include examples of how the feature would be used

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes
4. Add or update tests as necessary
5. Run the tests to ensure they pass
6. Update documentation as needed
7. Submit a pull request

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/lakshyakumar90/Resguard--Resource-Management-System.git
   cd resguard
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a configuration file:
   ```bash
   cp config.json.example config.json
   ```

## Coding Guidelines

- Follow PEP 8 style guidelines
- Write docstrings for all functions, classes, and modules
- Include type hints where appropriate
- Write unit tests for new functionality
- Keep functions and methods small and focused
- Use meaningful variable and function names

## Git Workflow

1. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "Add your feature description"
   ```

3. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a pull request from your branch to the main repository

## Documentation

- Update the README.md file with any new features or changes
- Add docstrings to all new functions, classes, and modules
- Update any relevant documentation in the docs directory

Thank you for contributing to ResGuard!
