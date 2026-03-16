# tri-llm-debate-runner

Local research tool for orchestrating tri-model debates through official ChatGPT / Claude / Gemini web UIs only.

## Quick start
```bash
pnpm install
cp config.sample.json config.local.json
pnpm dev
```

## Workspace structure
- `apps/dashboard`: setup + operations UI
- `apps/runner`: debate runner state machine
- `packages/adapters`: Playwright provider adapters
- `packages/debate-engine`: canonical debate logic
- `packages/store`: SQLite persistence
- `packages/shared`: schemas and common types

## Compliance constraints (implemented)
- official UI only
- manual login/MFA/CAPTCHA
- visible DOM automation only
- local storage only

See `docs/` for architecture and operations.
