CosineAI Twitter → Telegram Notifier

This project checks CosineAI's X/Twitter account every 6 hours and sends a Telegram message for new original posts (not replies, not retweets, not quotes). If there are no new posts, no message is sent.

What it does
- Monitors: https://x.com/CosineAI
- Interval: every 6 hours (GitHub Actions cron)
- Sends to: your Telegram chat via a bot
- Filters: only original posts (excludes replies, retweets, and quotes)
- State: remembers the last seen tweet ID to avoid duplicates (committed back to the repo)

Quick setup
1) Create a new GitHub repository and add these files.
2) Create GitHub Secrets (Settings → Secrets and variables → Actions → New repository secret):
   - TWITTER_BEARER_TOKEN: Your Twitter/X API v2 Bearer token (App-only)
   - TELEGRAM_BOT_TOKEN: Your Telegram bot token (e.g., 1234567890:ABC...XYZ)
   - TELEGRAM_CHAT_ID: Your chat ID (e.g., 5929692957)
   - TWITTER_USERNAME: Optional (defaults to CosineAI)

3) Enable GitHub Actions
   - The included workflow runs on a schedule (every 6 hours) and can be run manually via “Run workflow.”
   - The workflow commits a small state file back to the repo to remember the last seen tweet. Ensure Actions has write permissions for contents (default for public repos; for private, set permissions in the workflow or repo settings).

Manual test message (no Twitter needed)
- You can manually send a “Test OK” message to your Telegram to verify configuration:
  - Go to the repo → Actions → “CosineAI Twitter → Telegram Notifier” → Run workflow
  - In the “send_test” input, choose “true” → Run
  - You should receive: “Test OK: CosineAI Twitter → Telegram Notifier is configured and can send messages.”
  - This doesn’t touch state and doesn’t call Twitter.

How to get required tokens/IDs
- Twitter/X API (Bearer):
  - Create a Twitter developer app and get the v2 Bearer token.
  - The app must have access to the v2 endpoints for user tweets (users/:id/tweets).
- Telegram bot token:
  - Talk to @BotFather on Telegram, create a bot, and copy the token.
- Telegram chat ID:
  - Send a message to your bot.
  - Visit https://api.telegram.org/bot<TOKEN>/getUpdates and find your numeric chat id in the JSON response.

Local testing (optional)
- Python 3.10+ required.
- Create a .env or export env vars:
  export TWITTER_BEARER_TOKEN=...
  export TELEGRAM_BOT_TOKEN=...
  export TELEGRAM_CHAT_ID=...
  export TWITTER_USERNAME=CosineAI

- Install and run:
  pip install -r requirements.txt
  python monitor.py

Notes
- First run: The workflow initializes by recording the current latest original post without sending Telegram messages (to avoid spamming historical posts). Future runs send only new posts since that point.
- Quotes filtering: The script excludes any tweet whose referenced_tweets include type="quoted".
- Rate limits and API changes: If Twitter/X modifies API access or rate limits, you may need to adjust app access or handling.

Security
- Do not commit secrets to the repository.
- Use GitHub Actions Secrets only.