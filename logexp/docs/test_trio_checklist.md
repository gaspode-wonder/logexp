# Test Trio Checklist

This checklist ensures every commit is clean, deterministic, and aligned with
the project's quality guarantees. Run this trio before committing, pushing, or
opening a PR.

## 1. Lint (flake8)
Run static analysis to catch style, correctness, and structural issues.

    flake8

## 2. Typecheck (mypy)
Validate type correctness across the entire codebase.

    mypy .

## 3. Tests (pytest)
Run the full test suite to ensure functional correctness and determinism.

    pytest -q

## Expected Outcome
- No flake8 errors
- No mypy errors
- All tests pass consistently

If any step fails, fix the issue before committing.
