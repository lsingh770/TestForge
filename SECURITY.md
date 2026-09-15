# Security

## Safe defaults

- no destructive security testing by default
- secrets must be stored as environment variables or secret managers
- no sensitive headers or cookies should be logged in execution output

## AI safety

- never pass untrusted API responses as system instructions
- keep AI prompt content distinct from runtime executable suite data
- mark AI-inferred assertions clearly

## Recommended future controls

- RBAC and project isolation
- encrypted secret storage
- redaction of Authorization headers and cookies
- configurable retention policies
