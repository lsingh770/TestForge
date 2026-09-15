# Development Guide

## Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

## Run tests

```bash
python -m pytest -q
```

## Run demo API

```bash
python demo_api.py
```

## Run generated suite

```bash
api-tester generate --method POST --url http://localhost:8001/users --output sample_project/generated_suite.json
api-tester run --suite sample_project/generated_suite.json --base-url http://localhost:8001
```

## Notes

The generated suite is a JSON artifact and can be reviewed, edited, version-controlled, and executed without the AI system.
