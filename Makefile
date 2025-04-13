.PHONY: clean test install run lint format

# Default target
all: clean install test

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	python -m unittest discover tests

# Run the application
run:
	python main.py

# Run with web dashboard only
web:
	python main.py --web-only

# Run with desktop app only
desktop:
	python main.py --desktop-only

# Run with debug mode
debug:
	python main.py --debug

# Install development dependencies
dev-install:
	pip install -r requirements.txt
	pip install flake8 black mypy

# Lint the code
lint:
	flake8 .

# Format the code
format:
	black .

# Type check
typecheck:
	mypy .

# Create a distribution package
dist:
	python setup.py sdist bdist_wheel

# Help
help:
	@echo "Available targets:"
	@echo "  all        - Clean, install dependencies, and run tests"
	@echo "  clean      - Remove build artifacts"
	@echo "  install    - Install dependencies"
	@echo "  test       - Run tests"
	@echo "  run        - Run the application"
	@echo "  web        - Run web dashboard only"
	@echo "  desktop    - Run desktop app only"
	@echo "  debug      - Run with debug mode"
	@echo "  dev-install- Install development dependencies"
	@echo "  lint       - Lint the code"
	@echo "  format     - Format the code"
	@echo "  typecheck  - Type check the code"
	@echo "  dist       - Create a distribution package"
