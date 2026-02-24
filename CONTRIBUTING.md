# Contributing to Telegram Shop Bot 🤝

First off, thank you for considering contributing to this project! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Process](#development-process)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Coding Standards](#coding-standards)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)
- [Questions & Support](#questions--support)

## 📜 Code of Conduct

### Our Pledge
We as members, contributors, and leaders pledge to make participation in our community a harassment-free experience for everyone, regardless of age, body size, visible or invisible disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards
Examples of behavior that contributes to a positive environment:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

## 🚀 How Can I Contribute?

### Types of Contributions

#### 🐛 Bug Reports
- Ensure the bug was not already reported by searching on GitHub under [Issues](https://github.com/reza-khalili-dev/telegram-shop-bot/issues)
- If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/reza-khalili-dev/telegram-shop-bot/issues/new)
- Include a **clear title and description**, as much relevant information as possible
- Include a **code sample** or an **executable test case** demonstrating the expected behavior that is not occurring

#### ✨ Feature Requests
- Check if the feature has already been requested in [Issues](https://github.com/reza-khalili-dev/telegram-shop-bot/issues)
- Provide a clear and detailed explanation of the feature you want and why it's important
- Include examples of how the feature would be used
- Consider whether the feature aligns with the project's goals

#### 📝 Documentation Improvements
- Fix typos, clarify explanations, or add examples
- Translate documentation to other languages
- Add docstrings to functions and classes
- Improve README, CONTRIBUTING, or other documentation files

#### 💻 Code Contributions
- Fix bugs
- Implement new features
- Improve performance
- Refactor code for better readability
- Add tests

## 🔧 Development Process

### 1. Fork the Repository
```bash
# Clone your fork
git clone https://github.com/your-username/telegram-shop-bot.git
cd telegram-shop-bot

# Add upstream remote
git remote add upstream https://github.com/reza-khalili-dev/telegram-shop-bot.git

2. Create a Branch
# Create a branch for your feature/fix
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number

3. Set Up Development Environment
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If exists

# Copy environment variables
cp .env.example .env
# Edit .env with your values


4. Make Your Changes
Write clean, readable code

Follow coding standards

Add comments where necessary

Update documentation

Add tests for new features


5. Test Your Changes
# Run the bot
python manage.py runbot

# Run tests (if available)
python manage.py test

# Check for any errors


6. Commit Your Changes
# Stage your changes
git add .

# Commit with a meaningful message
git commit -m "feat: add new feature"  # Follow commit conventions


7. Push and Create Pull Request
# Push to your fork
git push origin feature/your-feature-name

# Go to GitHub and create a Pull Request


📥 Pull Request Guidelines
PR Checklist
Before submitting your PR, ensure:

Code follows the project's coding standards

Tests pass and are updated if needed

Documentation is updated

Branch is up to date with main/master

PR has a clear title and description

No merge conflicts


PR Template

## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactor
- [ ] Test update

## Related Issues
Fixes #(issue number)

## Testing
Describe how you tested your changes

## Screenshots (if applicable)

## Additional Notes


## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactor
- [ ] Test update

## Related Issues
Fixes #(issue number)

## Testing
Describe how you tested your changes

## Screenshots (if applicable)

## Additional Notes

Example
# Good ✅
def get_user_wallet(user):
    """
    Get or create wallet for a user.
    
    Args:
        user: Django User instance
        
    Returns:
        Wallet: User's wallet object
    """
    wallet, created = Wallet.objects.get_or_create(user=user)
    return wallet

# Bad ❌
def get_wallet(u):
    w = Wallet.objects.filter(user=u).first()
    if not w:
        w = Wallet(user=u)
        w.save()
    return w
"""


📝 Commit Message Guidelines
Format

<type>(<scope>): <subject>

<body>

<footer>


Types
feat: New feature

fix: Bug fix

docs: Documentation only changes

style: Changes that do not affect the meaning of the code

refactor: Code change that neither fixes a bug nor adds a feature

perf: Code change that improves performance

test: Adding missing tests or correcting existing tests

chore: Changes to the build process or auxiliary tools

Examples
feat(wallet): add charge amount selection options

Add inline keyboard with predefined amounts (50k, 100k, 200k, 500k)
for wallet charging. Users can now select amount instead of typing.

Closes #123


fix(bot): handle connection errors with proxy

Add retry mechanism for failed connections and improve
error handling when proxy is not available.

Fixes #456


🧪 Testing Guidelines
Types of Tests
Unit Tests: Test individual components

Integration Tests: Test component interactions

Functional Tests: Test end-to-end functionality

Running Tests


# Run all tests
python manage.py test

# Run specific app tests
python manage.py test wallet
python manage.py test shop
python manage.py test bot

# Run with coverage (if pytest-cov installed)
pytest --cov=.


Test Examples

from django.test import TestCase
from wallet.models import Wallet
from django.contrib.auth.models import User

class WalletTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass"
        )
    
    def test_wallet_creation(self):
        """Test wallet is created for new user"""
        wallet = Wallet.objects.get(user=self.user)
        self.assertEqual(wallet.balance, 0)
    
    def test_deposit(self):
        """Test deposit functionality"""
        wallet = Wallet.objects.get(user=self.user)
        wallet.deposit(1000)
        self.assertEqual(wallet.balance, 1000)