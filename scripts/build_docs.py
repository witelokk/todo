"""Generate offline API reference from the actual FastAPI OpenAPI schema."""
import html
import json
import os
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "documentation-build-key")

from todo.main import app

site = Path("site")
site.mkdir(exist_ok=True)
schema = app.openapi()
(site / "openapi.json").write_text(json.dumps(schema, ensure_ascii=False, indent=2))
rows = []
for path, operations in schema["paths"].items():
    for method, operation in operations.items():
        rows.append(f'<tr><td>{html.escape(method.upper())}</td><td>{html.escape(path)}</td>'
                    f'<td>{html.escape(operation.get("summary", ""))}</td></tr>')
page = f'''<!doctype html><html lang="en"><meta charset="utf-8">
<title>Todo API {app.version}</title>
<style>body{{font:16px system-ui;max-width:1000px;margin:40px auto}}td,th{{padding:12px;border:1px solid #ccc}}table{{border-collapse:collapse}}</style>
<h1>Todo API {app.version}</h1><p>Generated from the current application code.</p>
<p><a href="openapi.json">OpenAPI JSON</a> · <a href="guide.html">Developer guide</a></p>
<table><tr><th>Method</th><th>Path</th><th>Operation</th></tr>{''.join(rows)}</table></html>'''
(site / "index.html").write_text(page)
guide = Path("docs/ci-cd.md").read_text()
(site / "guide.html").write_text('<meta charset="utf-8"><title>Developer guide</title><pre>' + html.escape(guide) + '</pre>')
print(f"Generated documentation for version {app.version}: {len(rows)} operations")
