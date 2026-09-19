# TestForge Architecture

## Goal

TestForge is an AI-assisted REST API quality platform whose core artifact is a standalone executable test suite. The AI layer helps design, explain, and refine tests, but the final suite must run without any AI dependency.

## Principles

* The generated suite is the durable artifact; execution never requires an AI provider.
* Input parsing, test generation, execution, reporting, and presentation remain separate layers.
* Assertions are explicit data in each test case so results are reproducible and inspectable.
* External HTTP calls are isolated in the execution layer and failures become test results.

## MVP layer boundaries

### 1. Input layer

The CLI and FastAPI routes accept cURL, OpenAPI documents, catalog JSON, or normalized API specifications.
### 2. Contract layer

`testforge.contracts` normalizes OpenAPI paths and catalog method entries into endpoint definitions, preserving method, URL, headers, and request data.
### 3. Generation layer

`testforge.generation.test_generator` creates executable test dictionaries, including positive, negative, and contract cases with assertion metadata.
### 4. Execution layer

`testforge.execution.runner` sends requests, evaluates assertions, captures response details and latency, and feeds reports and exporters.
### 5. AI layer

The repository currently has no runtime AI provider. The boundary is reserved for future planning or explanation features that emit the same deterministic suite format.
## Future-phase additions

- AI-assisted test planning and failure analysis
- Streaming execution events for richer clients.
- Pluggable persistence for suites and historical results.
