# Development and CI/CD

Python 3.11 or 3.12 and Poetry 2.2.1 are used. Install dependencies with
`poetry install`. Run tests with `poetry run pytest -v`.
Tests default to isolated SQLite databases and use a test-only signing key.
Production still supports POSTGRES_USERNAME, POSTGRES_PASSWORD, POSTGRES_HOST,
POSTGRES_PORT and SECRET_KEY; alternatively set DATABASE_URL explicitly.
Never use the test signing key in production.

CI runs for every pushed branch, tag and pull request. Both Python versions
must pass tests, package build, documentation generation and a real uvicorn
startup with HTTP checks on localhost. The ephemeral runner is the test server.
The uploaded artifacts contain JUnit results, wheel/sdist, generated API
reference and the server log. There is no persistent production deployment.

The Auto merge workflow handles successful pull-request CI runs. It merges
only a non-draft development -> main PR from this same repository, and only
when its current head SHA equals the tested SHA. It does not check out PR code
or download artifacts. Forks and stale results cannot trigger a merge.
The standard repository allow_auto_merge setting is not required: the workflow
calls the GitHub merge API after CI has completed successfully.
A merge made with GITHUB_TOKEN does not trigger another push workflow;
the release branch and version tag are pushed by the developer and do trigger CI.

Prepare a version on `release`, update the Poetry package version and changelog,
run CI, then publish the version tag. Tag CI verifies the source and uploads the
same documentation and distributable artifacts. No PyPI upload is configured.

Build docs: `poetry run python scripts/build_docs.py`. Open `site/index.html`.
To view offline docs over HTTP: `python -m http.server --directory site 8080`.
The runtime interactive Swagger UI is at /docs, and OpenAPI JSON at /openapi.json.
