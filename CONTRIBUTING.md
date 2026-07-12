# Contributing to xEnco

First off, thank you for considering contributing to xEnco! It's people like you that make xEnco such a great tool.

## What is a Contributing Guide?

This document explains how you can help improve xEnco. Whether you're fixing bugs, adding features, improving documentation, or sharing ideas - your contributions are welcome!

## Ways to Contribute

### 🐛 Report Bugs
Found something broken? Let us know!

- **Check existing issues** first to avoid duplicates
- **Use the latest version** to verify the bug still exists
- Include:
  - What you expected to happen
  - What actually happened
  - Steps to reproduce
  - Your Python version and OS

### 💡 Suggest Features
Have an idea? We'd love to hear it!

- Open an issue with the "feature request" label
- Explain your use case
- Describe how it would work

### 📝 Improve Documentation
Spotted a typo? Think something could be clearer?

- Fix typos directly via pull request
- For larger changes, open an issue first

### 🔧 Submit Code Changes

#### Setting Up Development Environment

```bash
# 1. Fork the repository on GitHub

git clone https://github.com/YOUR_USERNAME/xenco.git
git clone https://github.com/YOUR_USERNAME/xenco.git
cd xenco

# 3. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install in development mode
pip install -e .

# 5. Install test dependencies
pip install pytest pytest-cov
```

#### Making Changes

1. **Create a branch**
   ```bash
   git checkout -b feature/my-new-feature
   # or
   git checkout -b fix/bug-description
   ```

2. **Make your changes**
   - Follow PEP 8 style guidelines
   - Add docstrings to new functions/classes
   - Update tests if needed

3. **Run tests**
   ```bash
   # Run all tests
   pytest
   
   # Run with coverage
   pytest --cov=xenco
   
   # Run specific test file
   pytest tests/test_keygen.py
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description of what you did"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/my-new-feature
   ```

6. **Open a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Describe your changes

## Code Standards

### Python Style
- Follow [PEP 8](https://pep8.org/)
- Use meaningful variable names
- Keep functions focused and small
- Add type hints where appropriate

### Documentation
- Update README.md if adding features
- Update CHANGELOG.md under `[Unreleased]`
- Add docstrings with examples

### Testing
- Write tests for new features
- Ensure all tests pass before submitting
- Aim for 80%+ coverage

## Pull Request Process

1. Update documentation
2. Add/update tests
3. Ensure CI passes (if enabled)
4. Request review from maintainers
5. Address feedback
6. Merge!

## Questions?

- **Email:** w4d4f4k@gmail.com
- **Website:** https://grandekos.com
- **Issues:** Open a GitHub issue

## Code of Conduct

This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). 
Please read it before participating.

## Recognition

Contributors will be recognized in our README.md (with permission).

---

Thank you for helping make xEnco better! 🎉
