# Contributing to NOVA

We love your input! We want to make contributing to NOVA as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## 🚀 Getting Started

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/NOVA.git
   cd NOVA
   ```
3. **Set up the development environment:**
   ```bash
   scripts/setup.sh  # Linux/macOS
   scripts/setup.bat # Windows
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🎯 How to Contribute

### Reporting Bugs

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

**Use the bug report template:**

```markdown
**Bug Description**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear and concise description of what you expected to happen.

**Screenshots/Logs**
If applicable, add screenshots or log outputs to help explain your problem.

**Environment:**
- OS: [e.g. Windows 11, Ubuntu 20.04]
- Python Version: [e.g. 3.9.7]
- NOVA Version: [e.g. 0.1.0]

**Additional Context**
Add any other context about the problem here.
```

### Suggesting Features

We love feature suggestions! Please use the feature request template:

```markdown
**Feature Description**
A clear and concise description of what you want to happen.

**Problem Statement**
What problem does this feature solve? What use case does it enable?

**Proposed Solution**
Describe the solution you'd like in detail.

**Alternatives Considered**
Describe any alternative solutions or features you've considered.

**Additional Context**
Add any other context, mockups, or examples about the feature request here.
```

### Pull Requests

**Good Pull Requests** have:

1. **Clear description** of what the PR does
2. **Tests** for new functionality
3. **Documentation** updates if needed
4. **Small, focused changes** (one feature/fix per PR)
5. **Clean commit history**

#### Pull Request Process

1. **Update documentation** for any new or changed functionality
2. **Add tests** that cover your changes
3. **Ensure tests pass:** `pytest`
4. **Format your code:** `black . && flake8`
5. **Update the README** if you change functionality
6. **Reference any related issues** in your PR description

## 🧑‍💻 Development Guidelines

### Code Style

#### Python
- Follow **PEP 8** style guidelines
- Use **Black** for code formatting: `black .`
- Use **flake8** for linting: `flake8`
- Use **type hints** where possible
- Write **docstrings** for all public functions and classes

```python
def process_user_input(
    input_text: str, 
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process user input through NOVA's intelligence pipeline.
    
    Args:
        input_text: The user's input text
        context: Optional context dictionary
        
    Returns:
        Dictionary containing processed response and metadata
        
    Raises:
        ValueError: If input_text is empty
    """
    if not input_text.strip():
        raise ValueError("Input text cannot be empty")
    
    # Implementation here
    return {"response": "processed"}
```

#### JavaScript/TypeScript
- Use **Prettier** for formatting
- Use **ESLint** for linting
- Use **TypeScript** for type safety
- Follow **React** best practices for UI components

#### Documentation
- Use **clear, concise language**
- Include **code examples** where helpful
- Update **README** for user-facing changes
- Write **inline comments** for complex logic

### Testing

#### Writing Tests
- Write tests for **all new functionality**
- Use **pytest** for Python tests
- Aim for **>90% code coverage**
- Include **integration tests** for complex features

```python
import pytest
from core.brain import NOVABrain, NOVAConfig

@pytest.mark.asyncio
async def test_nova_brain_initialization():
    """Test NOVA brain initializes correctly."""
    config = NOVAConfig(debug_mode=True)
    brain = NOVABrain(config)
    
    success = await brain.initialize()
    assert success is True
    assert brain.state.value == "active"

@pytest.mark.asyncio
async def test_process_simple_input():
    """Test processing simple text input."""
    brain = NOVABrain(NOVAConfig())
    await brain.initialize()
    
    input_data = {
        "type": "text",
        "content": "Hello NOVA",
        "context": {}
    }
    
    response = await brain.process_input(input_data)
    assert "response" in response
    assert response["response"] is not None
```

#### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=agents --cov=interfaces

# Run specific test file
pytest tests/test_brain.py

# Run tests with verbose output
pytest -v

# Run tests and stop on first failure
pytest -x
```

### Commit Messages

Use **conventional commits** format:

```
type(scope): description

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(agents): add new research agent with web scraping capabilities

fix(memory): resolve memory leak in conversation storage

docs(readme): update installation instructions for Windows

test(core): add comprehensive tests for personality engine

refactor(api): simplify websocket connection management
```

## 🏗️ Architecture Guidelines

### Adding New Agents

1. **Inherit from BaseAgent:**
   ```python
   from core.orchestrator import BaseAgent, AgentType
   
   class MyCustomAgent(BaseAgent):
       def __init__(self):
           super().__init__(AgentType.CUSTOM)
           self.capabilities = [
               # Define agent capabilities
           ]
   ```

2. **Implement required methods:**
   ```python
   async def execute_task(self, task: Task) -> Dict[str, Any]:
       """Execute agent-specific tasks."""
       pass
   
   async def can_handle_task(self, task: Task) -> bool:
       """Check if agent can handle the task."""
       return task.type == self.agent_type
   ```

3. **Register with orchestrator**
4. **Add tests for new agent**
5. **Update documentation**

### Adding New Interfaces

1. **Create interface module** in `interfaces/`
2. **Follow existing patterns** for consistency
3. **Add error handling** and logging
4. **Include tests** for the interface
5. **Update API documentation**

### Security Considerations

- **Validate all inputs** before processing
- **Use encryption** for sensitive data
- **Implement rate limiting** for APIs
- **Log security events** appropriately
- **Follow principle of least privilege**

## 🧪 Testing Strategy

### Test Categories

1. **Unit Tests:** Test individual functions/methods
2. **Integration Tests:** Test component interactions
3. **End-to-End Tests:** Test complete user workflows
4. **Performance Tests:** Test system performance
5. **Security Tests:** Test security measures

### Test Data

- Use **fixtures** for reusable test data
- **Mock external dependencies** appropriately
- **Clean up** test data after tests
- **Don't commit** sensitive test data

```python
@pytest.fixture
def sample_nova_config():
    """Provide sample NOVA configuration for tests."""
    return NOVAConfig(
        personality="test",
        debug_mode=True,
        voice_enabled=False,
        vision_enabled=False
    )

@pytest.fixture
async def initialized_brain(sample_nova_config):
    """Provide initialized NOVA brain for tests."""
    brain = NOVABrain(sample_nova_config)
    await brain.initialize()
    yield brain
    await brain.shutdown()
```

## 📦 Release Process

### Version Numbering

We use **Semantic Versioning (SemVer)**:
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR:** Breaking changes
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes (backward compatible)

### Release Checklist

1. **Update version** in relevant files
2. **Update CHANGELOG.md** with new features/fixes
3. **Run full test suite**
4. **Update documentation**
5. **Create release tag**
6. **Build and test packages**
7. **Publish release**

## 🤝 Community

### Code of Conduct

Please note that this project is released with a [Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

### Communication

- **GitHub Issues:** Bug reports and feature requests
- **GitHub Discussions:** General questions and discussions
- **Pull Requests:** Code contributions
- **Documentation:** Updates and improvements

### Recognition

Contributors will be recognized in:
- **README.md** contributors section
- **Release notes** for significant contributions
- **Special recognition** for major features

## 📚 Resources

### Documentation
- [Development Guide](DEVELOPMENT.md)
- [API Documentation](API.md)
- [Architecture Overview](ARCHITECTURE.md)

### Useful Links
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Conventional Commits](https://conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [pytest Documentation](https://docs.pytest.org/)

## ❓ Questions?

Don't hesitate to ask questions! You can:

1. **Open an issue** for bug reports or feature requests
2. **Start a discussion** for general questions
3. **Check existing issues** - your question might already be answered

Thank you for contributing to NOVA! 🚀
