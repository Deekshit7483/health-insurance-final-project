# Contributing to HealthClaim Portal

Thank you for your interest in contributing to HealthClaim Portal! This document provides guidelines and instructions for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- Git
- Basic knowledge of React and Python

### Development Setup

1. **Fork and Clone**

   ```bash
   git clone https://github.com/yourusername/health-project.git
   cd health-project
   ```

2. **Install Dependencies**

   ```bash
   # Frontend dependencies
   npm install

   # Python dependencies
   pip install -r requirements.txt
   ```

3. **Start Development**

   ```bash
   # Start frontend development server
   npm run dev

   # Run Python tests
   pytest
   ```

## 📋 Development Guidelines

### Code Style

#### Frontend (React/JavaScript)

- Use ESLint configuration provided
- Follow React best practices and hooks patterns
- Use Tailwind CSS for styling
- Maintain component modularity
- Write descriptive component and function names

#### Backend (Python)

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write comprehensive docstrings
- Maintain high test coverage (>90%)
- Use meaningful variable and function names

### Commit Messages

Use conventional commit messages:

```
feat: add new claim processing feature
fix: resolve login authentication issue
docs: update installation instructions
test: add unit tests for claim processor
refactor: improve database query performance
```

## 🧪 Testing

### Frontend Testing

```bash
# Run frontend tests (when available)
npm test

# Run linting
npm run lint
```

### Backend Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=python_src

# Run specific test file
pytest python_tests/unit/test_claim_processor.py
```

### Test Requirements

- All new features must include tests
- Maintain minimum 90% code coverage
- Include both unit and integration tests
- Test edge cases and error conditions

## 📝 Pull Request Process

1. **Create Feature Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**

   - Write code following style guidelines
   - Add comprehensive tests
   - Update documentation if needed

3. **Test Your Changes**

   ```bash
   # Run all tests
   npm test
   pytest

   # Check code style
   npm run lint
   flake8 python_src/
   ```

4. **Commit Changes**

   ```bash
   git add .
   git commit -m "feat: your descriptive commit message"
   ```

5. **Push and Create PR**

   ```bash
   git push origin feature/your-feature-name
   ```

6. **Pull Request Checklist**
   - [ ] Tests pass locally
   - [ ] Code follows style guidelines
   - [ ] Documentation updated (if needed)
   - [ ] Commit messages follow convention
   - [ ] No merge conflicts
   - [ ] Screenshots included (for UI changes)

## 🏗️ Project Structure

```
health-project/
├── src/                    # Frontend React components
├── python_src/            # Python backend code
├── python_tests/          # Python test suite
├── docs/                  # Project documentation
└── scripts/               # Build and deployment scripts
```

## 🎯 Contribution Areas

### High Priority

- [ ] User authentication improvements
- [ ] Claim processing optimization
- [ ] Mobile responsiveness
- [ ] API documentation
- [ ] Performance optimization

### Medium Priority

- [ ] Additional dashboard features
- [ ] Report generation
- [ ] Data visualization
- [ ] Integration tests
- [ ] Security enhancements

### Good First Issues

- [ ] UI component improvements
- [ ] Documentation updates
- [ ] Test coverage improvements
- [ ] Code refactoring
- [ ] Bug fixes

## 🐛 Bug Reports

When reporting bugs, please include:

- Steps to reproduce
- Expected vs actual behavior
- Screenshots/error messages
- Environment details (OS, browser, versions)
- Minimal code example (if applicable)

## 💡 Feature Requests

For new features:

- Describe the problem it solves
- Provide use cases and examples
- Consider alternative solutions
- Discuss implementation approach

## 🔍 Code Review Guidelines

### For Authors

- Keep PRs focused and small
- Write descriptive PR descriptions
- Respond to feedback promptly
- Update documentation as needed

### For Reviewers

- Be constructive and respectful
- Focus on code quality and maintainability
- Check for test coverage
- Verify documentation updates
- Test the changes locally

## 📚 Resources

- [React Documentation](https://reactjs.org/docs/)
- [Python Style Guide](https://pep8.org/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Pytest Documentation](https://docs.pytest.org/)
- [Git Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows)

## 🤝 Community

- Be respectful and inclusive
- Help newcomers get started
- Share knowledge and best practices
- Participate in discussions
- Follow the code of conduct

## 📞 Support

- Create GitHub issues for bugs/features
- Join project discussions
- Contact maintainers for urgent issues
- Check existing issues before creating new ones

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to HealthClaim Portal! 🚀
