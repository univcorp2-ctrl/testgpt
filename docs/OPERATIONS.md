# Operations Guide

## First Run
1. `pnpm install`
2. Copy `config.sample.json` to `config.local.json` and set workspace URLs.
3. Start dashboard: `pnpm --filter @tri/dashboard dev`
4. Start runner: `pnpm --filter @tri/runner dev`
5. Complete login/MFA manually in opened provider windows, then use dashboard "Login complete".

## Profiles
- `./profiles/chatgpt`
- `./profiles/claude`
- `./profiles/gemini`

## Blocked/Manual Takeover
When blocked state is detected, runner sets `manual_takeover_required`. Human should:
- fix login/captcha/upgrade manually in official UI
- resume runner afterwards

## Persistence & Recovery
- SQLite DB: `./data/debate.db`
- Screenshots: `./artifacts/*.png`
- Restarting runner resumes from latest stored canonical state.
