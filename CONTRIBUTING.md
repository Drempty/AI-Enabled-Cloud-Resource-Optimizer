# Contributing to Cloud Resource Optimizer

First off, thank you for considering contributing to Cloud Resource Optimizer! It's people like you that make this tool better for everyone.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include screenshots if possible
* Include your environment details (OS, Python version, Node version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Follow the Python and JavaScript styleguides
* Include thoughtfully-worded, well-structured tests
* Document new code
* End all files with a newline

## Development Setup

### Prerequisites

* Python 3.9+
* Node.js 16+
* Docker and Docker Compose (optional but recommended)

### Local Development

1. Fork the repo
2. Clone your fork:
```bash
git clone https://github.com/your-username/cloud-optimizer.git
cd cloud-optimizer
```

3. Set up backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. Set up frontend:
```bash
cd frontend
npm install
```

5. Create a branch:
```bash
git checkout -b feature/amazing-feature
```

### Running Tests

#### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

#### Frontend Tests
```bash
cd frontend
npm test
```

### Code Style

#### Python
We use:
* Black for code formatting
* Flake8 for linting
* MyPy for type checking

Run before committing:
```bash
cd backend
black app/
flake8 app/
mypy app/
```

#### JavaScript/React
We use:
* ESLint for linting
* Prettier for formatting

Run before committing:
```bash
cd frontend
npm run lint
npm run format
```

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

Examples:
```
Add LSTM model for time-series prediction

- Implement LSTM neural network
- Add training pipeline
- Include model evaluation metrics

Fixes #123
```

## Project Structure

```
cloud-optimizer/
├── backend/
│   ├── app/
│   │   ├── core/           # Configuration and database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routers/        # API endpoints
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   ├── tests/              # Test files
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
│   └── package.json
└── docs/                   # Documentation
```

## Adding New Features

### Backend API Endpoint

1. Create a new router in `backend/app/routers/`
2. Define Pydantic schemas in `backend/app/schemas/`
3. Implement business logic in `backend/app/services/`
4. Add tests in `backend/tests/`
5. Update API documentation

### Frontend Component

1. Create component in `frontend/src/components/` or page in `frontend/src/pages/`
2. Add routing if needed in `App.js`
3. Create API service methods in `frontend/src/services/`
4. Add tests
5. Update user documentation

### ML Model

1. Implement model in `backend/app/services/ml_service.py`
2. Add model training pipeline
3. Include evaluation metrics
4. Document model architecture and performance
5. Add tests for predictions

## Documentation

* Update README.md if needed
* Update API.md for API changes
* Add JSDoc comments for JavaScript functions
* Add docstrings for Python functions
* Update CHANGELOG.md

## Testing Guidelines

### Unit Tests
* Test individual functions and methods
* Mock external dependencies
* Aim for >80% code coverage

### Integration Tests
* Test API endpoints end-to-end
* Test database operations
* Test ML model predictions

### Frontend Tests
* Test component rendering
* Test user interactions
* Test API integration

## Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create a release branch
4. Run all tests
5. Create a pull request to main
6. Tag the release after merge

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

## Recognition

Contributors will be recognized in:
* README.md Contributors section
* Release notes
* Project website (if applicable)

Thank you for contributing! 🎉
