# Publishing Guide

This guide describes how to test the `doc-scraper` package locally and publish it to PyPI.

## Prerequisites

Ensure you have `build` and `twine` installed:

```bash
pip install build twine
```

## 1. Local Testing

Before publishing, it's good practice to install the package in editable mode and run tests.

### Install in Editable Mode
```bash
pip install -e .
```

### Run Tests
```bash
pytest
```

### Test CLI Manually
```bash
doc-scraper --help
doc-scraper https://example.com --output-dir ./test_context
```

## 2. Building the Package

To create the distribution artifacts (Source Distribution and Wheel), run:

```bash
python -m build
```

This will create a `dist/` directory containing:
- `doc_scraper-0.1.0.tar.gz` (Source)
- `doc_scraper-0.1.0-py3-none-any.whl` (Wheel)

## 3. Verifying the Build

Check that the distribution files are valid:

```bash
twine check dist/*
```

## 4. Publishing to PyPI

### TestPyPI (Recommended for first run)
Upload to TestPyPI to verify everything looks correct without affecting the real PyPI index.

```bash
twine upload --repository testpypi dist/*
```
You can then try installing it:
```bash
pip install --index-url https://test.pypi.org/simple/ doc-scraper
```

### PyPI (Production)
Once verified, upload to the official Python Package Index:

```bash
twine upload dist/*
```

## 5. Dependency Note
Remember that users will need to run `playwright install` after installing this package, as noted in the `README.md`.
