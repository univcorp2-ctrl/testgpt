# Selector Strategy

- Keep provider-specific selectors under `packages/adapters`.
- Use semantic selectors first (`role`, accessible label, visible text).
- Fallback chain is ordered and test-injectable.
- CI validates parser logic with mock HTML fixtures only.
- If all selectors fail, return `ui_changed` and request manual review.
