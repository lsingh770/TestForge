# Minimal UI

This is a lightweight web UI for viewing generated tests and their execution results.

## Start the UI

```bash
uvicorn testforge.ui.app:app --reload --port 8000
```

Then open:

- http://localhost:8000/ui
- http://localhost:8000/ui/test/TC-001
