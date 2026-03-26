# Contributing to EcomAgent

Thank you for your interest in contributing to EcomAgent!

## How to Contribute

### Reporting Bugs

Open a [GitHub Issue](https://github.com/your-username/ecom-agent/issues/new?template=bug_report.md) with:
- Steps to reproduce
- Expected vs. actual behavior
- Your environment (OS, Python version, Docker version)

### Suggesting Features

Open an issue with the `feature-request` template. Describe the use case and why it would benefit other sellers.

### Adding a New Platform Adapter

This is the highest-value contribution. See the architecture section in README.md.

1. Fork the repo and create a branch: `feat/adapter-{platform}`
2. Create `backend/app/adapters/{platform}/`
3. Implement all methods in `BasePlatformAdapter`
4. Add tests in `backend/tests/adapters/test_{platform}.py`
5. Update `backend/app/adapters/__init__.py`
6. Add a section to README.md

### Improving Prompts

LLM prompts live in each module's main file (e.g., `modules/listing_generator/generator.py`). Better prompts = better output for everyone. Open a PR with before/after examples.

### Pull Request Process

1. Fork & clone the repo
2. Create a branch: `git checkout -b feat/my-feature`
3. Make your changes with tests
4. Run `cd backend && python -m pytest`
5. Open a PR against `main`

## Code Style

- Python: follow PEP 8, use type annotations
- TypeScript: strict mode, no `any`
- No unnecessary comments (code should be self-documenting)
- All new async functions should be `async def`

## Development Setup

See the **Development** section in README.md.

## License

By contributing, you agree your contributions will be licensed under MIT.
