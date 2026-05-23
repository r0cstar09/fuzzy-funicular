# Screenshot Plan for Astro Portfolio Entry

Use this checklist after cloning this repo into a temporary path from your Astro workspace.

## 1) Repo Structure

- Capture the project root with `README.md`, `lessons/`, `scripts/`, and `.github/`.
- Goal: communicate architecture quickly.

## 2) Workflow Automation

- Open `.github/workflows/send-daily-lesson.yml`.
- Capture env/cadence configuration and send steps.
- Goal: show CI/CD-style scheduling and delivery automation.

## 3) Delivery Script

- Open `scripts/send_daily_lesson.py`.
- Capture:
  - lesson selection logic
  - schema validation call path
  - send-email function area
- Goal: show production logic, not just content files.

## 4) Structured Lesson Content

- Open one representative lesson file:
  - `lessons/lesson-40/lesson.json` (good tense-pattern example)
  - optionally `lessons/lesson-25/lesson.json` (pronominal verbs model)
- Goal: show repeatable content schema and drill design.

## 5) Validation Command Output

Run in terminal:

```bash
source .venv/bin/activate && python scripts/send_daily_lesson.py --validate-all
```

Capture the successful `OK lesson-*` output.

## 6) Rendered Lesson Preview

Run:

```bash
source .venv/bin/activate && python scripts/send_daily_lesson.py --lesson-number 40 --dry-run
```

Capture a portion of the generated lesson output (title + one or two sections).

## Asset Naming Convention

Recommended filenames for Astro assets:

- `fuzzy-funicular-01-structure.png`
- `fuzzy-funicular-02-workflow.png`
- `fuzzy-funicular-03-script-selection.png`
- `fuzzy-funicular-04-lesson-json.png`
- `fuzzy-funicular-05-validate-output.png`
- `fuzzy-funicular-06-dryrun-preview.png`

## Notes

- Do not capture `.env` values or any secrets.
- Keep each screenshot focused on one idea for cleaner portfolio storytelling.

