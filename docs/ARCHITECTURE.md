# tri-llm-debate-runner Architecture

## Goals
- Local-only single-user orchestration of a 3-model debate using official web UIs (ChatGPT, Claude, Gemini).
- Resumable step machine with durable checkpoints in SQLite.
- Clear separation of concerns: adapters (UI automation) vs engine (debate logic) vs runner (orchestration) vs dashboard (operations).

## Monorepo Layout
- `apps/runner`: Node process that executes the state machine, drives adapters, persists checkpoints.
- `apps/dashboard`: Vite + React operational UI (setup + controls + transcript/export view).
- `packages/adapters`: Provider adapters and selector strategy config.
- `packages/debate-engine`: Canonical state, prompt composition, schema validation, claim graph updates.
- `packages/store`: SQLite repository and checkpoint/event persistence.
- `packages/shared`: Shared types, Zod schemas, constants.

## Runtime Overview
1. User completes setup in dashboard (workspace URLs + profile dirs).
2. Runner launches Playwright persistent contexts (one per provider profile).
3. Runner executes step state machine:
   - choose next speaker
   - compose prompt from canonical state
   - adapter open/send/wait/read
   - parse + validate debate schema
   - optional repair prompt once
   - update engine state + persist checkpoint
4. Dashboard polls local state endpoint and displays status/screenshots/transcript.

## Reliability & Recovery
- Every step writes checkpoint rows in SQLite (`debate_checkpoints`).
- On restart, runner loads latest checkpoint and resumes idempotently.
- Failure classifications: login_required, captcha, rate_limited, ui_changed, timeout, invalid_schema.
- Escalation policy: single repair attempt, then `manual_takeover_required` state.

## Security & Compliance Constraints
- Official web UI only; no hidden/internal API invocation.
- Visible DOM only, no OCR/click-by-coordinate.
- Human handles login/MFA/CAPTCHA/subscription steps.
- All artifacts are local (`./artifacts`, `./data`, `./profiles`).

## Selector Strategy
- Semantic first: role/label/text selectors.
- Fallback chain defined in JSON per provider and injectable in tests.
- Obfuscated classes may only appear as last-resort optional fallback.

## Data Model (high level)
- `debates`: metadata, theme, status.
- `debate_state`: serialized canonical state snapshot.
- `debate_checkpoints`: step logs with payload + timestamps.
- `provider_sessions`: workspace URL, profile path, health.
- `artifacts`: screenshots and traces paths.

## Testing Strategy
- Unit tests for schema parser/validator and engine transitions.
- Adapter parser tests against static HTML fixtures (no live provider calls in CI).
- Manual live testing allowed only with `--live-ui` flag.
