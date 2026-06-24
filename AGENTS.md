# Repository Guidelines

## Project Structure & Module Organization

This is a Python FastAPI application with database migrations and server-rendered UI assets. Application code lives under `app/`: `main.py` wires middleware, static files, and routers; `routers/` contains HTTP endpoints and DTOs; `model/` contains SQLAlchemy entities; `repository/` contains persistence helpers; `config/` holds database and app configuration; `utils/` contains shared helpers. UI templates are in `app/templates/`, browser assets are in `app/static/`, and Alembic migrations are in `migration/versions/`. Infrastructure and setup notes are documented in `README.md`; local secrets should stay in `.env`, copied from `.env.example`.

## Build, Test, and Development Commands

- `uv sync`: create or update the local virtual environment from `pyproject.toml` and `uv.lock`.
- `docker compose up -d`: start local dependencies such as PostgreSQL, MinIO, Neo4j, and Redis when a compose file is available.
- `uv run uvicorn app.main:app --reload`: run the FastAPI app locally with reload.
- `uv run alembic upgrade head`: apply database migrations.
- `uv run alembic revision --autogenerate -m "describe change"`: generate a schema migration after model changes.
- `uv run pytest`: run the test suite.

## Coding Style & Naming Conventions

Use Python 3.14 syntax and standard PEP 8 formatting with 4-space indentation. Prefer explicit imports and type hints for route signatures, repository methods, DTO conversion, and SQLAlchemy `Mapped[...]` fields. Keep module names lowercase with underscores, such as `documents_router.py` and `document_repository.py`. Name routers and repositories after the resource they serve, and keep template filenames aligned with page names.

## Testing Guidelines

`pytest` is the expected test runner, but no test directory is currently committed. Add tests under `tests/` using filenames like `test_documents_router.py` or `test_document_repository.py`. Cover route responses, DTO mapping, repository queries, and migration-sensitive model behavior. For database tests, isolate fixtures and avoid depending on a developer's `.env` values.

## Commit & Pull Request Guidelines

Recent commits use short, imperative summaries such as `Show backend documents in UI` and `Fix document model relationships and API response`. Keep commits focused on one behavior or fix. Pull requests should include a brief description, linked issue when applicable, migration notes for schema changes, screenshots for UI changes, and the exact validation commands run, especially `uv run pytest` and any Alembic commands.

## Security & Configuration Tips

Do not commit `.env`, credentials, database dumps, or generated local caches. Keep configuration defaults in `.env.example` and document any new required variables in `README.md`.
