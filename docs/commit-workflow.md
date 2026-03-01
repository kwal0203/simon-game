# Commit Workflow

Use this flow to avoid the "commit twice" loop:

1. Run lint auto-fixes.
2. Run formatting.
3. Run end-of-file fixer.
4. Trim trailing whitespace.
5. Run tests.
6. Stage files.
7. Commit once.

Commands:

```bash
uv run ruff check . --fix
uv run ruff format .
pre-commit run end-of-file-fixer --all-files
pre-commit run trailing-whitespace --all-files
npm --prefix apps/web run test:run
uv run python -m pytest -q
git add -A
git commit -m "your message"
```

Notes:

- Pre-commit should be a safety net, not the primary fixer.
- If pre-commit changes files, re-run the commands above before committing.
