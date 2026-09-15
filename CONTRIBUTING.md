# Contributing

## Workflow

1. Keep the generated test suite independent from AI runtime logic.
2. Prefer deterministic logic and explicit assertions.
3. Add tests for every significant behavior change.
4. Keep modules small and focused.
5. Document architectural decisions in the markdown docs in the repo root.

## Validation

Run the project test suite before concluding work is complete:

```bash
python -m pytest -q
```
