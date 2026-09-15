# AI Design

## Separation of concerns

The AI system is intentionally decoupled from the execution engine.


## Safety guidelines


## Provider abstraction

The current MVP deliberately does not include a runtime AI provider. Test generation and execution are deterministic and work without external model credentials. AI-assisted planning can be added later behind a separate integration boundary.

This keeps the platform open to future integrations without hard-wiring one vendor.
