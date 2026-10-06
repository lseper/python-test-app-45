# python-test-app-45

Minimal FastAPI service exposing `GET /ping` (returns `"pong"`), running on Python 3.14.

## Development

```
uv sync                         # install (creates .venv, provisions Python 3.14)
uv run uvicorn main:app         # run on http://localhost:8000
uv run pytest                   # tests
uv run ruff check .             # lint
uv run ruff format --check .    # format check
```
