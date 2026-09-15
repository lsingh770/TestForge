# Build an AI-Powered Autonomous REST API Testing Platform

## Role

Act as a world-class **Software Architect, Backend Developer, SDET, API Testing Expert, AI Engineer, Security Tester, DevOps Engineer, and Product Designer**.

I want you to design and build a production-quality **AI-powered REST API testing platform**.

The goal is to create a tool where a user provides an API's **request and expected/observed response**, and the platform intelligently generates a comprehensive API test suite, executes the tests, analyzes failures, and generates a detailed report.

The most important requirement is:

> **AI should be used to CREATE and intelligently enhance the test suite, but once the suite is generated, the entire suite must be executable independently WITHOUT requiring AI.**

The generated tests must be deterministic, version-controlled, reusable, editable, and runnable from CLI/CI/CD.

---

# 1. Product Vision

Build a tool similar in spirit to combining:

- Postman
- REST Assured
- Playwright
- JUnit/TestNG
- OWASP API security testing
- AI test generation
- API contract testing
- API fuzzing
- CI/CD reporting

But make the core experience **AI-first and autonomous**.

The user should be able to provide something as simple as:

```text
METHOD: POST

URL:
https://example.com/api/users

HEADERS:
Content-Type: application/json
Authorization: Bearer <token>

REQUEST:
{
  "name": "Lokesh",
  "email": "lokesh@example.com",
  "age": 35
}

RESPONSE:
HTTP 201

{
  "id": 123,
  "name": "Lokesh",
  "email": "lokesh@example.com"
}
```

The system should analyze this and automatically create appropriate tests.

---

# 2. Core Workflow

Implement this workflow:

```text
User Input
    ↓
API Understanding / Parsing
    ↓
API Contract Inference
    ↓
AI Test Design Engine
    ↓
Test Case Generation
    ↓
Test Data Generation
    ↓
Dependency / State Analysis
    ↓
Generated Executable Test Suite
    ↓
Test Execution Engine
    ↓
Assertion Engine
    ↓
Failure Analysis
    ↓
AI Root Cause Analysis
    ↓
Report Generation
    ↓
Human Review / Editing
    ↓
Standalone Test Suite
    ↓
CLI / CI-CD Execution
```

---

# 3. Input Methods

Support multiple ways of providing APIs.

### A. Manual API definition

Allow:

- HTTP method
- URL
- query parameters
- path parameters
- headers
- cookies
- request body
- expected response
- authentication

### B. cURL

User can paste:

```bash
curl --location 'https://example.com/api/users' \
--header 'Authorization: Bearer xxx' \
--header 'Content-Type: application/json' \
--data '{"name":"Lokesh"}'
```

Automatically parse it.

### C. OpenAPI / Swagger

Support:

- OpenAPI 3.x
- Swagger 2.x

Upload/import:

```yaml
openapi.yaml
```

Automatically discover all endpoints.

### D. Postman Collection

Import Postman collections.

### E. HAR

Allow importing HAR files where practical.

### F. Multiple APIs

The user should be able to provide an entire API ecosystem rather than one endpoint.

---

# 4. API Understanding Engine

The AI must understand:

- endpoint
- HTTP method
- parameters
- headers
- authentication
- request schema
- response schema
- status codes
- data types
- required/optional fields
- nested objects
- arrays
- enums
- relationships between fields
- pagination
- filtering
- sorting
- CRUD relationships

Infer the likely business behavior from available information.

Clearly distinguish between:

### Known

Directly provided by the user/API specification.

### Inferred

Reasonably inferred by AI.

### Assumed

Not known and therefore needs validation.

Never silently treat assumptions as facts.

---

# 5. Automatic Test Case Generation

Generate comprehensive test cases.

## Functional Tests

### Positive

Examples:

- valid request
- minimum valid values
- maximum valid values
- optional fields omitted
- different valid enum values
- different valid combinations
- valid authentication
- valid content type

### Negative

Automatically test:

- missing mandatory fields
- null values
- empty strings
- invalid data types
- malformed JSON
- invalid enum
- invalid IDs
- invalid URLs
- invalid query parameters
- invalid path parameters
- unsupported HTTP methods
- invalid content type
- malformed headers

---

# 6. Boundary Testing

Automatically identify boundaries.

For example:

```text
min-1
min
min+1

max-1
max
max+1
```

For strings:

```text
empty
1 character
minimum length
maximum length
maximum + 1
very large input
```

For numbers:

```text
negative
zero
minimum
maximum
overflow
decimal where integer expected
```

For arrays:

```text
0 items
1 item
minimum allowed
maximum allowed
maximum + 1
```

---

# 7. Data Validation

The assertion engine must validate:

### HTTP

- status code
- response time
- protocol behavior

### Headers

- Content-Type
- Authorization-related headers
- caching headers
- security headers
- custom headers

### Body

- schema
- data types
- mandatory fields
- nullable fields
- values
- formats
- regex patterns
- enum values

### Relationships

For example:

```text
request.id == response.id
request.email == response.email
response.total == response.items.length
```

Support:

- JSONPath
- JSON Schema
- XPath where applicable
- regex
- custom expressions

---

# 8. API State and Chaining

This is extremely important.

The tool must understand that APIs may depend on each other.

Example:

```text
POST /users
      ↓
returns userId
      ↓
GET /users/{userId}
      ↓
PUT /users/{userId}
      ↓
DELETE /users/{userId}
```

Automatically detect or allow configuration of:

- request dependencies
- response-to-request variables
- IDs
- tokens
- session values
- correlation IDs

Example:

```text
POST /login
   ↓
extract access_token
   ↓
use access_token in subsequent requests
```

The generated suite must support variables such as:

```text
{{baseUrl}}
{{token}}
{{userId}}
{{orderId}}
```

---

# 9. Authentication

Support common authentication mechanisms:

- Bearer token
- Basic Auth
- API key
- OAuth 2.0
- JWT
- custom headers
- cookies
- session-based authentication

Never expose secrets in logs or reports.

Provide secure secret handling using environment variables or secret stores.

---

# 10. Security Testing

Include an API security testing module.

Automatically test for common OWASP API Security risks where technically safe and appropriate.

Examples:

- broken authentication
- authorization issues
- IDOR/BOLA patterns
- excessive data exposure
- mass assignment
- injection
- malformed input
- security header issues
- improper error handling
- rate limiting
- excessive resource consumption
- sensitive data leakage

Do NOT perform destructive or unauthorized security testing by default.

Provide explicit safe-testing controls.

---

# 11. Injection Testing

Generate controlled payloads for:

- SQL injection
- NoSQL injection
- command injection
- XSS where relevant
- LDAP injection
- template injection
- path traversal
- special characters

Use safe payload sets and make destructive/security-intensive testing explicitly configurable.

---

# 12. Fuzz Testing

Add an API fuzzing engine.

Generate controlled variations of:

- strings
- numbers
- booleans
- arrays
- JSON structures
- headers
- query parameters
- path parameters

The system should detect:

- crashes
- unexpected 5xx responses
- abnormal response times
- malformed responses
- inconsistent behavior

Allow users to configure:

```text
Fuzz intensity:
LOW
MEDIUM
HIGH
CUSTOM
```

---

# 13. Performance Testing

Include basic API performance testing.

Measure:

- response time
- average latency
- P50
- P90
- P95
- P99
- throughput
- error rate

Allow configurable:

```text
Users
Requests
Duration
Ramp-up
Thresholds
```

Do not turn performance testing into uncontrolled load generation.

---

# 14. Contract Testing

Support contract validation.

Validate:

```text
Actual Response
        ↓
Expected Schema
```

Detect:

- missing fields
- unexpected fields
- type changes
- nullable/non-nullable changes
- enum changes
- status code changes
- schema incompatibilities

Support OpenAPI-based contract validation.

---

# 15. AI Assertion Generation

The AI should intelligently generate assertions rather than only checking:

```text
HTTP 200
```

For example:

Instead of:

```text
assert status == 200
```

generate:

```text
assert status == 200
assert response.user.id != null
assert response.user.email matches email format
assert response.user.status == "ACTIVE"
assert response.items is an array
assert response.total >= response.items.length
```

However, avoid hallucinated business rules.

Each assertion should have a confidence level:

```text
HIGH
MEDIUM
LOW
```

---

# 16. Oracle Problem

Design specifically for the **test oracle problem**.

The AI should not blindly assume that every observed response is correct.

Allow three assertion categories:

### Contract Assertions

Based on API specification.

### Structural Assertions

Based on response structure/type.

### Behavioral Assertions

Based on inferred behavior.

Behavioral assertions should be clearly marked as AI-inferred.

---

# 17. Test Data Generation

Build a smart test data engine.

Generate:

- realistic names
- emails
- phone numbers
- dates
- UUIDs
- addresses
- numbers
- enum values
- edge cases
- invalid values

Support deterministic seeds so the same generated data can be reproduced.

Example:

```text
seed = 12345
```

The same seed should generate reproducible test data.

---

# 18. Test Suite Architecture

The generated test suite must NOT depend on the AI at runtime.

This is a fundamental requirement.

For example:

```text
Generated Test Suite
        ↓
REST Assured / HTTP Client
        ↓
Assertions
        ↓
Test Report
```

AI is only required for:

```text
Test generation
Test optimization
Failure analysis
Test maintenance suggestions
```

The user must be able to disable AI completely after generation.

---

# 19. Generated Test Code

Prefer generating maintainable code rather than storing tests as opaque AI prompts.

Initially support:

### Java

- REST Assured
- JUnit 5 or TestNG
- Maven/Gradle

Potential future support:

- Python + pytest
- TypeScript + Playwright/APIRequest
- JavaScript

Generated code should follow clean architecture.

Example:

```text
src/
 ├── main/
 │    ├── api/
 │    ├── config/
 │    ├── models/
 │    ├── utils/
 │
 └── test/
      ├── functional/
      ├── negative/
      ├── boundary/
      ├── security/
      ├── contract/
      └── performance/
```

---

# 20. Human Editing

The generated test suite must be fully editable.

Users should be able to:

- edit test cases
- delete tests
- add tests
- modify assertions
- modify test data
- modify endpoints
- disable tests
- tag tests
- prioritize tests
- change execution order

AI should never overwrite human changes without explicit approval.

---

# 21. Test Case Metadata

Every generated test should have:

```text
Test ID
Test Name
Category
Priority
Severity
Description
Preconditions
Request
Expected Result
Assertions
Test Data
Dependencies
Source
Confidence
AI-generated / Human-modified
```

Example:

```text
TC-USER-001
Create user with valid payload

Priority: P0
Type: Positive
Source: OpenAPI + AI inference
Confidence: High
```

---

# 22. Test Prioritization

Automatically classify tests:

```text
P0 – Critical
P1 – High
P2 – Medium
P3 – Low
```

Provide execution modes:

```text
Smoke
Regression
Full
Security
Contract
Negative
Boundary
Performance
```

---

# 23. Intelligent Test Selection

Add risk-based test selection.

Analyze:

- endpoint criticality
- recent failures
- code/API changes
- historical failures
- defect frequency
- test coverage
- business impact

Recommend:

```text
Run 32 tests instead of 250
```

when only a specific API area changed.

---

# 24. Failure Analysis

After execution, AI should analyze failures.

For every failure:

```text
Test Failed
     ↓
Request Analysis
     ↓
Response Analysis
     ↓
Historical Comparison
     ↓
Root Cause Hypothesis
```

Categorize:

```text
APPLICATION BUG
TEST BUG
ENVIRONMENT ISSUE
DATA ISSUE
AUTHENTICATION ISSUE
NETWORK ISSUE
CONTRACT VIOLATION
FLAKY TEST
UNKNOWN
```

Example:

```text
TC-102 failed.

Expected: HTTP 201
Actual: HTTP 500

Likely cause:
Server-side exception while processing the request.

Confidence: 91%

Recommendation:
Check POST /users database insertion flow.
```

Never claim certainty when the system only has a hypothesis.

---

# 25. Flaky Test Detection

Detect flaky tests by:

- repeated execution
- inconsistent results
- timing analysis
- environment correlation

Example:

```text
Pass
Pass
Fail
Pass
Fail
```

Flag:

```text
Potentially flaky – 40% failure rate
```

---

# 26. API Coverage

Generate coverage metrics.

Examples:

```text
Endpoint Coverage: 94%
HTTP Method Coverage: 100%
Positive Test Coverage: 91%
Negative Test Coverage: 87%
Boundary Coverage: 82%
Contract Coverage: 96%
Security Coverage: 74%
```

Also report:

```text
Untested endpoints
Untested parameters
Untested response fields
Untested status codes
```

---

# 27. Reports

Create a professional HTML report.

Include:

### Executive Summary

```text
Total APIs
Total tests
Passed
Failed
Skipped
Blocked
Pass %
Coverage
Critical defects
Security findings
```

### Test Details

For every test:

```text
Request
Response
Assertions
Duration
Logs
Failure
Screenshots if applicable
```

### AI Analysis

Include:

```text
Failure explanation
Root-cause hypothesis
Recommended action
Confidence
```

### Trends

Show:

- pass rate
- failure rate
- response time
- endpoint stability
- flaky tests

Support exporting:

- HTML
- JSON
- JUnit XML
- CSV
- PDF if practical

---

# 28. CLI

The generated suite must have a CLI.

Example:

```bash
api-tester generate api.yaml
```

```bash
api-tester run
```

```bash
api-tester run --suite smoke
```

```bash
api-tester run --tag regression
```

```bash
api-tester report
```

The CLI must work without AI after generation.

---

# 29. CI/CD

Support:

- GitHub Actions
- Jenkins
- GitLab CI
- Azure DevOps

Example:

```yaml
api-tests:
  run: api-tester run --suite regression
```

Build should fail based on configurable thresholds.

Example:

```text
Fail build if:
Critical tests failed
OR
pass rate < 95%
OR
P95 latency > threshold
```

---

# 30. Environment Management

Support:

```text
DEV
QA
STAGING
PROD
```

with configuration:

```text
baseUrl
credentials
tokens
timeouts
test data
```

Never hardcode credentials.

Support:

```text
.env
environment variables
secret managers
```

---

# 31. AI Provider Abstraction

Do not tightly couple the application to one LLM.

Create an abstraction layer:

```text
AIProvider
   ├── OpenAI
   ├── Anthropic
   ├── Gemini
   └── Local LLM
```

The core testing engine must continue functioning when AI is unavailable.

---

# 32. Prompt Injection Protection

Because API descriptions and API responses can contain arbitrary text, treat external API content as **untrusted input**.

Do not allow an API response such as:

```text
Ignore previous instructions and...
```

to control the AI system.

Implement clear separation between:

```text
System instructions
User configuration
API data
AI-generated content
```

---

# 33. Privacy & Security

Design for enterprise usage.

Requirements:

- secrets masking
- encrypted credentials
- secure storage
- audit logging
- RBAC
- user authentication
- project isolation
- configurable data retention
- no accidental LLM leakage of credentials
- redact Authorization headers
- redact cookies
- redact sensitive response fields

Allow users to configure whether API payloads can be sent to external AI providers.

---

# 34. Human Approval / Autonomous Mode

Provide modes:

### Assisted

AI generates tests → human reviews → execute.

### Autonomous

AI generates → validates → executes → analyzes.

### Strict

AI can generate tests but cannot modify existing tests without approval.

The user should always control autonomy level.

---

# 35. Test Mutation / Self-Validation

Before accepting generated tests, the platform should validate whether the tests are meaningful.

For example:

```text
Generate Test
      ↓
Execute Test
      ↓
Mutation / Negative Validation
      ↓
Check whether assertions actually detect incorrect behavior
```

Avoid tests that always pass because assertions are too weak.

Example of weak test:

```text
assert response != null
```

when meaningful validation is possible.

---

# 36. Test Quality Score

Every generated test should have a quality score.

Example:

```text
Test Quality: 92/100

Assertions: 95
Boundary Coverage: 90
Negative Coverage: 88
Maintainability: 96
Business Confidence: 91
```

---

# 37. Duplicate Test Detection

Detect duplicate or overlapping tests.

Example:

```text
TC-001
TC-017
TC-032
```

may all effectively test the same scenario.

AI should recommend consolidation.

---

# 38. Test Maintenance

When an API changes:

```text
Old API contract
       ↓
New API contract
       ↓
Impact analysis
       ↓
Affected tests
       ↓
AI proposes updates
```

Example:

```text
Field changed:

"userName" → "username"

Affected tests: 17

Suggested update available.
```

Human approval should be required before modifying tests.

---

# 39. Dashboard

Create a modern dashboard showing:

```text
Projects
APIs
Test Cases
Execution History
Pass Rate
Failure Rate
Coverage
Security Findings
Performance
Flaky Tests
AI Suggestions
```

Allow drilling down:

```text
Project
 → API
   → Endpoint
     → Test Suite
       → Test Case
         → Execution
```

---

# 40. Recommended Technical Architecture

Design the application using clean modular architecture.

Suggested components:

```text
Frontend
   ↓
API Gateway / Backend
   ↓
Project Manager
   ↓
API Parser
   ↓
Contract Engine
   ↓
AI Test Generator
   ↓
Test Case Repository
   ↓
Execution Engine
   ↓
Assertion Engine
   ↓
Security Engine
   ↓
Performance Engine
   ↓
Result Processor
   ↓
AI Failure Analyzer
   ↓
Reporting Engine
```

Keep these modules loosely coupled.

---

# 41. Suggested Initial Technology Stack

Choose technologies based on maintainability and developer productivity.

Suggested:

### Backend

Python + FastAPI

### AI

Provider abstraction supporting OpenAI/Anthropic/etc.

### Database

PostgreSQL

### Frontend

React + TypeScript

### Test execution

Initially:

Java + REST Assured + JUnit 5

Later:

Python + pytest

TypeScript

### Queue

Redis + Celery/RQ or equivalent where needed.

### Containers

Docker + Docker Compose

### CI/CD

GitHub Actions initially.

You may change these technologies if you have a strong architectural reason. Explain the trade-off before making a major change.

---

# 42. Data Model

Design proper database entities.

At minimum:

```text
User
Project
Environment
API
Endpoint
APIContract
TestSuite
TestCase
TestStep
TestData
Execution
ExecutionResult
Assertion
Failure
SecurityFinding
PerformanceResult
AIAnalysis
AuditLog
```

Use proper relationships and indexes.

---

# 43. Versioning

Everything important should be versionable:

```text
API contract
test suite
test cases
test data
environment configuration
```

Allow comparison:

```text
Suite v1
vs
Suite v2
```

---

# 44. Git Integration

Allow generated test suites to be exported to a Git repository.

Example:

```text
project/
├── tests/
├── config/
├── schemas/
├── reports/
├── README.md
├── pom.xml
└── .github/workflows/api-tests.yml
```

The exported repository must be completely independent from the AI platform.

---

# 45. Reproducibility

A test execution should record:

```text
test version
API version
environment
test data seed
timestamp
tool version
configuration
```

A failed test should be reproducible later.

---

# 46. Observability

Collect:

- execution logs
- request timing
- response timing
- error logs
- test statistics

Do not log secrets.

---

# 47. API Mocking

Consider adding mock support.

If an API environment is unavailable, allow tests to run against mocks.

Potential architecture:

```text
Real API
   OR
Mock API
```

This should be optional.

---

# 48. Important Edge Cases

Think deeply about scenarios such as:

- API returns different responses for same request
- random IDs
- timestamps
- dynamic tokens
- pagination
- eventual consistency
- asynchronous APIs
- rate limiting
- 202 Accepted workflows
- polling
- webhooks
- large payloads
- binary responses
- multipart/form-data
- file upload/download
- XML responses
- streaming responses
- GraphQL as a future extension
- APIs requiring stateful workflows

Do not pretend all of these are solved in V1. Design the architecture so they can be added later.

---

# 49. MVP Scope

Do NOT attempt to build everything at once.

First build a strong MVP supporting:

1. REST APIs
2. cURL input
3. OpenAPI import
4. Manual request/response input
5. API parsing
6. AI test generation
7. Positive tests
8. Negative tests
9. Boundary tests
10. Schema assertions
11. JSONPath assertions
12. API chaining
13. Bearer authentication
14. Environment variables
15. Java + REST Assured generated tests
16. Standalone execution
17. CLI
18. HTML reporting
19. JUnit XML
20. AI failure analysis
21. Docker
22. GitHub Actions

After MVP, implement advanced capabilities incrementally.

---

# 50. Quality Requirements

The code must be:

- production-oriented
- modular
- testable
- readable
- documented
- secure
- maintainable

Follow:

- SOLID
- DRY
- clean architecture
- proper exception handling
- type safety
- dependency injection where appropriate
- structured logging

Do not create one giant file.

---

# 51. Testing the Testing Tool

The platform itself must have comprehensive tests.

Create:

### Unit tests

For:

- API parser
- schema parser
- test generator
- assertion engine
- data generator
- variable extraction

### Integration tests

For:

```text
API → AI → Test Generation
API → Execution
Execution → Report
```

### End-to-end tests

Create a sample REST API and use your own tool to test it.

The project should effectively be capable of **testing itself**.

---

# 52. Sample Demo API

Create a small demo API containing:

```text
POST /users
GET /users
GET /users/{id}
PUT /users/{id}
DELETE /users/{id}

POST /login

POST /orders
GET /orders/{id}
```

Include intentional bugs such as:

- incorrect status code
- missing validation
- incorrect response field
- authorization issue
- boundary issue
- slow endpoint

Use this to demonstrate that the AI testing platform can discover meaningful defects.

---

# 53. UX Principle

The primary user experience should be:

```text
Import API
      ↓
"Generate Tests"
      ↓
AI analyzes API
      ↓
"127 tests generated"
      ↓
"Run Tests"
      ↓
"112 passed | 10 failed | 5 skipped"
      ↓
"Analyze Failures"
      ↓
AI explains failures
```

Keep the interface simple.

Do not force the user to understand complex testing concepts before they can use the product.

Advanced configuration can be available under an advanced section.

---

# 54. AI Transparency

Every AI-generated artifact should explain:

```text
Why was this test generated?
What information was used?
What was inferred?
What assumptions were made?
How confident is the AI?
```

Avoid black-box behavior.

---

# 55. No Hallucination Policy

This is critical.

The AI must NEVER fabricate:

- API endpoints
- business rules
- expected status codes
- response fields
- authentication requirements

unless explicitly marked as an inference/assumption.

If insufficient information exists, the tool should say:

```text
Insufficient information to determine expected behavior.

Suggested test:
Validate response structure only.
```

---

# 56. Final Deliverables

Produce:

### Application

Working frontend + backend.

### AI engine

Modular provider abstraction.

### Test generation engine

Working automated test generation.

### Execution engine

Independent of AI.

### CLI

For standalone execution.

### Reporting

HTML + JUnit XML + JSON.

### Demo API

With intentional defects.

### Documentation

Include:

```text
README.md
ARCHITECTURE.md
API.md
DEVELOPMENT.md
AI_DESIGN.md
SECURITY.md
CONTRIBUTING.md
```

### Docker

Provide:

```bash
docker compose up
```

to start the complete system.

### Sample project

Provide an example generated API test project that can run independently.

---

# 57. Development Method

Do not simply generate a huge amount of code in one shot.

Work incrementally.

### Phase 1

Architecture + repository structure.

### Phase 2

API ingestion/parsing.

### Phase 3

Contract model.

### Phase 4

AI test generation.

### Phase 5

Test execution.

### Phase 6

Assertions.

### Phase 7

Reporting.

### Phase 8

CLI.

### Phase 9

AI failure analysis.

### Phase 10

Security/performance capabilities.

At the end of every phase:

1. Run tests.
2. Fix failures.
3. Verify functionality.
4. Update documentation.
5. Commit working changes.

Do not move to the next phase if the current phase is broken.

---

# 58. Definition of Done

The MVP is complete only when I can do this:

### Step 1

Start the application.

### Step 2

Provide:

```text
POST /users
```

with request and response.

### Step 3

Click:

```text
Generate Tests
```

### Step 4

The AI automatically generates multiple meaningful tests.

### Step 5

Click:

```text
Run Suite
```

### Step 6

The tool executes the tests against the API.

### Step 7

The system identifies failures.

### Step 8

The report explains:

```text
What failed
Why it probably failed
Expected
Actual
Severity
Evidence
Recommended action
```

### Step 9

Export the test suite.

### Step 10

Disconnect/disable AI.

### Step 11

Run:

```bash
api-tester run
```

and the exact same test suite executes successfully without AI.

---

# 59. Most Important Product Principle

Do not build an "AI that generates API test cases."

Build:

> **An AI-powered API Quality Engineering platform that converts API knowledge into an executable, maintainable, autonomous test system.**

The AI should be the intelligence layer.

The generated test suite should be the durable engineering artifact.

The final product must remain useful even when the AI is turned off.

---

# 60. Start Now

First:

1. Analyze this entire specification.
2. Identify missing architectural risks.
3. Identify ambiguous requirements.
4. Propose the final MVP architecture.
5. Propose the repository structure.
6. Propose the database schema.
7. Propose the API contracts.
8. Propose the AI workflow.
9. Propose the generated test format.
10. Propose the execution architecture.
11. Identify what should be deferred to V2.
12. Then start implementing Phase 1.

Do not skip architectural reasoning.

Do not over-engineer the MVP.

Prioritize a **working end-to-end vertical slice** over building isolated modules.

At every stage, favor:

**Correctness > maintainability > security > explainability > cleverness.**