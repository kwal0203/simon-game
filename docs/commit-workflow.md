# Commit Workflow

Use this flow to avoid the "commit twice" loop:

1. Run lint auto-fixes.
2. Run formatting.
3. Run tests.
4. Stage files.
5. Commit once.

Commands:

```bash
uv run ruff check . --fix
uv run ruff format .
uv run python -m pytest -q
git add -A
git commit -m "your message"
```

Notes:

- Pre-commit should be a safety net, not the primary fixer.
- If pre-commit changes files, re-run the commands above before committing.
