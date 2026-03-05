# arche

When self-studying university courses (e.g. CMU 15-411, MIT 6.824), you often
get lecture slides but no lecture videos. The slides alone are rarely
self-contained: professors design them as visual aids for a spoken lecture, not
as standalone reading material. So you scroll through a PDF, hit a slide you
don't understand, and have no way to hear the explanation that was supposed to
go with it.

arche fills that gap. Point it at a lecture PDF, tell it which slides you're
stuck on, and it generates a professor-style explanation. It reads all prior
slides for context (not just the ones you asked about), so it understands the
narrative arc of the lecture before explaining your target slides.

## Two ways to use it

### Claude Code (recommended)

If you use [Claude Code](https://docs.anthropic.com/en/docs/claude-code),
the `/slides` skill lets Claude read the slide images directly, no API key
needed:

```
/slides lecture.pdf 15
/slides lecture.pdf 10-15
/slides lecture.pdf 3,7,12 What is the connection between these three slides?
```

This extracts pages 1 through the last requested page as PNGs, loads them
into Claude's context, and explains the target slides with full awareness of
everything that came before.

To make `/slides` available globally (not just inside the arche project):

```sh
mkdir -p ~/.claude/skills/slides
cp .claude/skills/slides/SKILL.md ~/.claude/skills/slides/SKILL.md
```

### Standalone CLI

For terminal use without Claude Code. Requires an
[Anthropic API key](https://console.anthropic.com/):

```sh
export ANTHROPIC_API_KEY="sk-ant-..."

arche lecture.pdf 15
arche lecture.pdf 3-7
arche lecture.pdf 1,3,5
arche lecture.pdf 1-3,5,7-9
```

The CLI sends all slides from page 1 through your last requested page to
Claude's vision API and streams the explanation to stdout.

Options:

```
--model MODEL       Claude model to use (default: claude-sonnet-4-6)
--prompt PROMPT     Custom prompt (default: "Explain these slides.")
--max-tokens N      Maximum tokens in the response (default: 8192)
```

Examples:

```sh
arche lecture.pdf 12 --prompt "Summarize the key equations on this slide."
arche lecture.pdf 1-10 --max-tokens 16384
```

## Installation

Requires Python 3.12+.

```sh
# From GitHub
uv tool install git+https://github.com/fadli0029/arche.git

# Or from a local clone
git clone https://github.com/fadli0029/arche.git
cd arche
uv tool install .
```

## Development

```sh
git clone https://github.com/fadli0029/arche.git
cd arche
uv sync

# Run quality checks
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy
uv run pytest
```

## License

MIT. See [LICENSE](LICENSE).
