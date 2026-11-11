# Contributing to hledger-mcp-server

Thank you for your interest in contributing! Your help is essential for keeping
this project great.

Please note that this project is released with a
[Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating you agree to
abide by its terms.

## Issues

Issues are the best way to report bugs or suggest new features. Before opening a
new issue, please search existing ones to avoid duplicates.

When reporting a bug, include:

- Steps to reproduce the problem
- What you expected to happen
- What actually happened
- Your Python version and OS

When suggesting a feature, describe the use case and why it would be useful.

## Pull Requests

Pull requests are welcome. For non-trivial changes, please open an issue first
to discuss your approach.

### Getting Started

1. Fork and clone the repository
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Make sure [hledger](https://hledger.org/install.html) is installed and in your `PATH` (the test suite shells out to it)
4. Verify lint and tests pass:
   ```bash
   uv run ruff check src tests
   uv run pytest -q
   ```
5. Create a new branch from `main`:
   ```bash
   git checkout -b feat/your-feature main
   ```
6. Make your changes, add tests, and ensure lint and all tests pass
7. Push to your fork and submit a pull request (never push directly to `main`)

### Branch Naming

Use lowercase with hyphens and a descriptive prefix:

- `feat/` for new features
- `fix/` for bug fixes
- `docs/` for documentation changes

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) standard:

```
<type>: <short summary>
```

**Types:** `feat`, `fix`, `docs`, `test`, `style`, `refactor`, `chore`

Guidelines:

- Use the imperative mood ("add feature" not "added feature")
- Keep the summary under 72 characters
- Do not end the summary with a period
- Add a blank line and a body for complex changes

Examples:

```
feat: expose output_format on report tools
fix: reject ambiguous search_text in edit
docs: simplify README examples
test: cover dry_run on temporary journals
```

### Code Style

- Write all code, comments, and docstrings in English
- Add docstrings to functions, classes, and modules
- Follow the existing code style and conventions
- Ensure `uv run ruff check src tests` and `uv run pytest -q` pass before submitting

## Resources

- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [GitHub Pull Request documentation](https://docs.github.com/en/pull-requests)
