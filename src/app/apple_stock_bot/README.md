# Apple Stock Monitor (Manual Checkout Only)

This example implementation monitors Apple availability and sends notifications.
It intentionally does **not** automate account login, payment entry, 2FA handling,
or order placement.

## Environment variables
- `APPLE_PRODUCT_CODE`: Apple SKU / product code to monitor
- `APPLE_NOTIFY_WEBHOOK`: Discord webhook URL
- `APPLE_TARGET_URL`: product page to open manually
- `APPLE_CHECK_INTERVAL_SECONDS`: recommended minimum `30`

## Safety notes
- Keep the polling interval at 30 seconds or longer to reduce rate-limit risk.
- If Apple prompts for login or 2FA, complete that step manually.
- Stop the monitor after you successfully place an order to avoid duplicate purchases.
