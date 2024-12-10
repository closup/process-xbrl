# How to Contribute

Thank you for your interest in contributing to our project! This document provides guidelines for contributing.

## Do you want to propose a significant new feature or an important refactoring?

Please contact closup-ixbrl@umich.edu

## Did you find a bug?

* First, search through [existing issues](https://github.com/closup/process-xbrl/issues) to see if the bug has already been reported.
* If not, create a new issue with a clear title and description.
* Include as much relevant information as possible:
  * Steps to reproduce the issue
  * Expected behavior
  * Actual behavior
  * Any error messages
  * Your environment (OS, Python version, etc.)
* If possible, add a minimal code example that demonstrates the issue

## Want to submit a pull request?

1. First, create an issue describing the change you want to make.
2. Fork the repository and create a new branch from `main`.
3. Make your changes following our coding conventions.
4. Write or update tests as needed.
5. Update documentation as needed.
6. Label your PR with one of the following categories:
   - `feature` or `enhancement` for new features and improvements
   - `fix`, `bugfix`, or `bug` for bug fixes
   - `chore`, `documentation`, `docs`, or `refactor` for maintenance tasks
7. Submit a pull request with a clear title and description.
8. Reference the issue number in your pull request description.

### Pull Request Guidelines

* Follow Python PEP 8 style guide
* Include tests for new features
* Update documentation as needed
* Keep commits focused and atomic
* Write clear commit messages
* Ensure all tests pass before submitting
* Properly label your PR for changelog categorization:
  - 🚀 Features: use `feature` or `enhancement` labels
  - 🐛 Bug Fixes: use `fix`, `bugfix`, or `bug` labels
  - 🧰 Maintenance: use `chore`, `documentation`, `docs`, or `refactor` labels
  - 📦 Other Changes: PRs without any of the above labels will be categorized here

### Code Review Process

1. At least one project maintainer will review your code
2. Changes may be requested
3. Once approved, a maintainer will merge your PR

## Minor Fixes

* Any functionality change should have a GitHub issue opened. For minor changes that affect documentation, you do not need to open up a GitHub issue. Instead you can prefix the title of your PR with "MINOR: " if meets one of the following:
  * Grammar, usage and spelling fixes that affect no more than 2 files
  * Documentation updates affecting no more than 2 files and not more than 500 words.
  * These should still be labeled with `documentation` or `docs` for proper changelog categorization

## Proposing Significant Changes

For significant changes (new features, major refactoring):

1. First, open an issue to discuss the proposal
2. Include:
   * Detailed description of the change
   * Motivation and use cases
   * Potential implementation approach
3. Wait for feedback from maintainers before starting implementation

## Licensing

* All contributions must be compatible with our license (see License.txt)
* By contributing, you agree that your contributions will be licensed under the same terms
* All new files should include the University of Michigan copyright notice:
  ```
  Copyright © <2024> The Regents of the University of Michigan
  ```

## How Contributors Will Be Credited

* All contributors will be acknowledged in our CHANGELOG.md

## Questions or Need Help?

* For questions about contributing, open an issue with the "question" label
* For bug reports, use the "bug" label
* For feature requests, use the "enhancement" label

## Development Setup

* Please refer to the README.md for the development setup

## Code Style

* Follow PEP 8 guidelines
* Use meaningful variable and function names
* Comment complex logic
* Keep functions focused and modular
* Use type hints where appropriate

## Documentation

* Refer to changelog.yml for the changelog when PRs are merged
* Document new features
* Update API documentation
* Include docstrings for new functions/classes


Thank you for contributing to our project! Your efforts help make this project better for everyone.
