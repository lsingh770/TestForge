# AI Design

## Separation of concerns

The AI system is intentionally decoupled from the execution engine. Generated tests are plain JSON-like dictionaries, so the CLI, FastAPI UI, batch runner, and future AI integrations can share the same execution path.


## Safety guidelines

* Never make execution depend on model availability or model-generated code at runtime.
* Keep generated assertions explicit and reviewable before a suite is executed.
* Treat API definitions and response bodies as untrusted input; validate structured data and escape values rendered into HTML.
* Keep credentials out of generated reports and avoid sending requests to an unintended base URL.

## Provider abstraction

The current MVP deliberately does not include a runtime AI provider. Test generation and execution are deterministic and work without external model credentials. A future provider should expose planning or explanation operations that return the existing suite and assertion structures, leaving HTTP execution in `testforge.execution`.

This keeps the platform open to future integrations without hard-wiring one vendor.
