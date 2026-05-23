# fuzzy-funicular

Daily Spanish lesson emailer using Python + GitHub Actions.

## License

This repository is licensed under `CC BY-NC 4.0` (Creative Commons
Attribution-NonCommercial 4.0 International).

- You can copy, share, and adapt the project.
- You must provide attribution.
- You cannot use it for commercial purposes.

See `LICENSE` for details.

## Lesson JSON format

Each lesson folder should contain:

- `lessons/lesson-<n>/master<n> summary.pdf` (source content)
- `lessons/lesson-<n>/lesson.json` (structured lesson used for email delivery)

The sender reads `lesson.json` files and renders a Markdown email automatically.

## Local usage

Validate all lesson JSON files:

```bash
python scripts/send_daily_lesson.py --validate-all
```

Preview the selected daily lesson without sending:

```bash
python scripts/send_daily_lesson.py --dry-run
```

Send a specific lesson (example lesson 1):

```bash
ICLOUD_EMAIL="you@icloud.com" \
ICLOUD_APP_PASSWORD="app-specific-password" \
RECIPIENT_EMAIL="patullikayla1991@gmail.com" \
python scripts/send_daily_lesson.py --lesson-number 1
```

## GitHub Actions setup

Workflow file: `.github/workflows/send-daily-lesson.yml`

Set these repository **Secrets**:

- `ICLOUD_EMAIL` -> your iCloud address (sender)
- `ICLOUD_APP_PASSWORD` -> iCloud app-specific password
- `RECIPIENT_EMAIL` -> `patullikayla1991@gmail.com` (or any destination)

Optional repository **Variables**:

- `LESSON_START_DATE` -> ISO date like `2026-05-15` (daily lesson index anchor)
- `LESSON_NO_WRAP` -> `true` to stop after the last lesson, otherwise it loops

The workflow:

- Runs daily at 12:00 UTC
- Supports manual dispatch with an optional `lesson_number`
- Validates all lesson JSON files before sending

## iCloud SMTP details

- Host: `smtp.mail.me.com`
- Port: `587`
- Security: STARTTLS
- Login: iCloud email + app-specific password
