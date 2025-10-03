# Contributing to HSE ML Contrast Checker

Thank you for your interest in contributing to the HSE ML Contrast Checker project!

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/hse-ml-contrast-checker.git
   cd hse-ml-contrast-checker
   ```

3. Install in development mode:
   ```bash
   pip install -e .
   ```

4. Run tests to ensure everything works:
   ```bash
   python -m unittest discover tests -v
   ```

## Making Changes

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Write or update tests for your changes

4. Run tests to ensure they pass:
   ```bash
   python -m unittest discover tests -v
   ```

5. Commit your changes:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

7. Open a Pull Request

## Code Style

- Follow PEP 8 guidelines for Python code
- Use descriptive variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and modular

## Testing

- Write unit tests for new functionality
- Ensure all tests pass before submitting a PR
- Aim for good test coverage

Example test structure:
```python
import unittest
from contrast_checker import ContrastChecker

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        self.checker = ContrastChecker()
    
    def test_feature(self):
        result = self.checker.new_feature()
        self.assertTrue(result)
```

## Documentation

- Update README.md if you add new features
- Add examples if appropriate
- Update docstrings for any changed functions

## Questions?

If you have questions, please open an issue on GitHub.

## Course Project

This is a course project for HSE Applied ML Course 2024/25. Contributions from course participants are especially welcome!
