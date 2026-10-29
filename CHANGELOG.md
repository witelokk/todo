# Changelog

## 0.2.0 — 2026-10-29

- Add GitHub Actions CI on every push and pull request for Python 3.11 and 3.12.
- Build distributions, generate API docs and test a localhost deployment.
- Automatically merge a tested development pull request into main.
- Preserve task text, permit tasks without a category and validate category ownership.
- Add six task regression tests; the full suite now contains 13 tests.
- Support DATABASE_URL for local SQLite demonstrations and use prebuilt PostgreSQL drivers.
