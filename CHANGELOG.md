# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-03-05

Initial release.

### Added

- CLI tool (`chalk`) for explaining lecture slides via Claude's vision API.
- Extraction tool (`chalk-extract`) for rendering PDF pages to PNG files.
- Claude Code `/slides` skill for interactive slide explanation.
- Page specification syntax: single pages, ranges, comma-separated, mixed.
- Context-aware explanations (all prior slides loaded, not just targets).
- Configurable model, prompt, and max token parameters.

[0.1.0]: https://github.com/fadli0029/chalk/releases/tag/v0.1.0
