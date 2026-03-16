# Live Testing

CI must not interact with provider UIs.

Use manual test command only when intentionally running local UI automation:

```bash
pnpm --filter @tri/runner dev -- --live-ui
```

Manual checklist:
- confirm each provider opens dedicated profile directory
- confirm prompt send + completion wait
- confirm screenshot creation
- confirm invalid schema triggers single repair attempt
