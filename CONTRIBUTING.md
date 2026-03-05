# Contributing to chalk

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Setup

```sh
git clone https://github.com/fadli0029/chalk.git
cd chalk
uv sync
```

## Quality checks

All of these must pass before submitting a PR:

```sh
uv run ruff check src/ tests/    # lint
uv run ruff format --check src/ tests/  # format
uv run mypy                       # type check (strict mode)
uv run pytest                     # tests
```

To auto-fix lint and formatting issues:

```sh
uv run ruff check --fix src/ tests/
uv run ruff format src/ tests/
```

## Code standards

- All functions must have type annotations.
- `mypy --strict` must pass with zero errors.
- `ruff check` must pass with zero warnings.
- Use `pathlib` over `os.path`.
- No `print()` in production code (use `sys.stdout.write` or `sys.stderr.write`).
- No bare `# type: ignore`; always specify the error code.

## Submitting changes

1. Fork the repository and create a branch from `main`.
2. Make your changes.
3. Ensure all quality checks pass.
4. Open a pull request against `main`.
