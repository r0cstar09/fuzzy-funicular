#!/usr/bin/env python3
"""Send a daily Spanish lesson email from lesson JSON files."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from markdown import markdown as render_markdown


DEFAULT_RECIPIENT = "patullikayla1991@gmail.com"
LESSON_FILE_NAME = "lesson.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send one daily Spanish lesson email from lessons/lesson-*/lesson.json."
    )
    parser.add_argument(
        "--lessons-root",
        default=os.getenv("LESSONS_ROOT", "lessons"),
        help="Directory containing lesson-* folders.",
    )
    parser.add_argument(
        "--lesson-number",
        type=int,
        default=None,
        help="Send a specific lesson number (e.g. 1 for lessons/lesson-1/lesson.json).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print selected lesson and markdown output without sending email.",
    )
    parser.add_argument(
        "--validate-all",
        action="store_true",
        help="Validate all lesson JSON files and exit.",
    )
    return parser.parse_args()


def _lesson_number_from_dir(path: Path) -> int | None:
    match = re.fullmatch(r"lesson-(\d+)", path.name)
    if not match:
        return None
    return int(match.group(1))


def discover_lesson_files(lessons_root: Path) -> list[tuple[int, Path]]:
    if not lessons_root.exists():
        raise FileNotFoundError(f"Lessons root not found: {lessons_root}")

    lesson_files: list[tuple[int, Path]] = []
    for child in lessons_root.iterdir():
        if not child.is_dir():
            continue
        lesson_number = _lesson_number_from_dir(child)
        if lesson_number is None:
            continue
        lesson_file = child / LESSON_FILE_NAME
        if lesson_file.exists():
            lesson_files.append((lesson_number, lesson_file))

    lesson_files.sort(key=lambda item: item[0])
    return lesson_files


def select_lesson_file(
    lesson_files: list[tuple[int, Path]], requested_lesson_number: int | None
) -> tuple[int, Path] | None:
    if not lesson_files:
        raise RuntimeError(
            "No lesson JSON files found. Add files like lessons/lesson-1/lesson.json."
        )

    if requested_lesson_number is not None:
        for lesson_number, lesson_file in lesson_files:
            if lesson_number == requested_lesson_number:
                return lesson_number, lesson_file
        raise RuntimeError(
            f"Requested lesson-{requested_lesson_number} not found with {LESSON_FILE_NAME}."
        )

    raw_start_date_value = os.getenv("LESSON_START_DATE")
    start_date_value = (
        raw_start_date_value.strip()
        if raw_start_date_value and raw_start_date_value.strip()
        else dt.date.today().isoformat()
    )
    start_date = dt.date.fromisoformat(start_date_value)
    today = dt.date.today()
    day_delta = (today - start_date).days
    if day_delta < 0:
        return None

    cadence_days_raw = os.getenv("LESSON_CADENCE_DAYS", "1").strip()
    cadence_days = int(cadence_days_raw)
    if cadence_days <= 0:
        raise RuntimeError("LESSON_CADENCE_DAYS must be a positive integer.")

    start_lesson_number_raw = os.getenv("LESSON_START_LESSON_NUMBER", "1").strip()
    start_lesson_number = int(start_lesson_number_raw)
    if start_lesson_number <= 0:
        raise RuntimeError("LESSON_START_LESSON_NUMBER must be a positive integer.")

    start_index = None
    for index, (lesson_number, _) in enumerate(lesson_files):
        if lesson_number == start_lesson_number:
            start_index = index
            break
    if start_index is None:
        raise RuntimeError(
            f"Configured LESSON_START_LESSON_NUMBER={start_lesson_number} not found."
        )

    if day_delta % cadence_days != 0:
        return None

    lesson_offset = day_delta // cadence_days

    no_wrap = os.getenv("LESSON_NO_WRAP", "false").lower() == "true"
    if no_wrap and start_index + lesson_offset >= len(lesson_files):
        raise RuntimeError(
            "All lessons have already been sent and LESSON_NO_WRAP=true is enabled."
        )

    selected_index = (start_index + lesson_offset) % len(lesson_files)
    return lesson_files[selected_index]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, dict):
        raise ValueError(f"Invalid lesson JSON (expected object): {path}")
    return payload


def require(payload: dict[str, Any], key: str) -> Any:
    if key not in payload:
        raise ValueError(f"Missing required key '{key}'")
    return payload[key]


def validate_lesson_schema(payload: dict[str, Any], source: str) -> None:
    require(payload, "tags")
    require(payload, "difficulty")
    require(payload, "pattern_id")
    require(payload, "source_files")
    require(payload, "target_pattern")
    lesson = require(payload, "lesson")

    if not isinstance(lesson, dict):
        raise ValueError(f"{source}: 'lesson' must be an object.")

    required_sections = [
        "cognitive_shift",
        "controlled_recombination",
        "pattern_mutation",
        "contrastive_discrimination",
        "guided_personal_writing",
        "reverse_conceptual_expression",
        "common_errors",
        "answer_key",
    ]
    for section in required_sections:
        if section not in lesson:
            raise ValueError(f"{source}: missing lesson section '{section}'.")


def enumerate_lines(items: list[str]) -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(items, 1))


def render_markdown_lesson(lesson_number: int, payload: dict[str, Any]) -> str:
    lesson = payload["lesson"]
    cognitive = lesson["cognitive_shift"]
    controlled = lesson["controlled_recombination"]
    mutation = lesson["pattern_mutation"]
    contrastive = lesson["contrastive_discrimination"]
    guided = lesson["guided_personal_writing"]
    reverse_expr = lesson["reverse_conceptual_expression"]
    common_errors = lesson["common_errors"]
    answer_key = lesson["answer_key"]

    cognitive_examples = enumerate_lines(cognitive["natural_examples"])
    controlled_prompts = enumerate_lines(controlled["prompts_en"])
    mutation_drills = enumerate_lines(mutation["drills"])
    contrastive_prompts = enumerate_lines(contrastive["prompts"])
    guided_prompts = enumerate_lines(guided["prompts"])
    reverse_prompts = enumerate_lines(reverse_expr["prompts_en"])

    common_error_lines = []
    for index, entry in enumerate(common_errors, 1):
        common_error_lines.append(f"{index}. Error: {entry['mistake']}")
        common_error_lines.append(f"   Why: {entry['why_it_happens']}")
        common_error_lines.append(f"   Correct: {entry['correct_spanish']}")
    common_errors_block = "\n".join(common_error_lines)

    answer_controlled = enumerate_lines(answer_key["controlled_recombination"])
    answer_mutation = enumerate_lines(answer_key["pattern_mutation"])
    answer_contrastive = enumerate_lines(answer_key["contrastive_discrimination"])
    answer_reverse = enumerate_lines(answer_key["reverse_conceptual_expression"])

    formulas = cognitive["target_pattern_formula"]
    if isinstance(formulas, list):
        formulas_text = "\n".join(f"- {line}" for line in formulas)
    else:
        formulas_text = f"- {formulas}"

    tags = payload.get("tags", [])
    tags_text = ", ".join(tags) if isinstance(tags, list) else str(tags)

    return f"""# Spanish Daily Lesson {lesson_number}

**Pattern ID:** {payload['pattern_id']}
**Difficulty:** {payload['difficulty']}
**Target Pattern:** {payload['target_pattern']}
**Tags:** {tags_text}

## 1) cognitive_shift

- **English trap:** {cognitive['english_trap']}
- **Spanish logic:** {cognitive['spanish_logic']}
- **target pattern/formula:**
{formulas_text}

### 5 natural examples
{cognitive_examples}

## 2) controlled_recombination

{controlled['instructions']}

{controlled_prompts}

## 3) pattern_mutation

{mutation['instructions']}

{mutation_drills}

## 4) contrastive_discrimination

{contrastive['instructions']}

{contrastive_prompts}

## 5) guided_personal_writing

{guided['instructions']}

{guided_prompts}

## 6) reverse_conceptual_expression

{reverse_expr['instructions']}

{reverse_prompts}

## 7) common_errors

{common_errors_block}

## 8) answer_key

### controlled_recombination
{answer_controlled}

### pattern_mutation
{answer_mutation}

### contrastive_discrimination
{answer_contrastive}

### reverse_conceptual_expression
{answer_reverse}
"""


def build_message(
    sender: str, recipient: str, subject: str, markdown_content: str
) -> EmailMessage:
    body_html = render_markdown(markdown_content, extensions=["extra", "sane_lists"])
    html_content = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{subject}</title>
    <style>
      body {{
        margin: 0;
        padding: 0;
        background: #f3f4f6;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
        color: #111827;
        line-height: 1.55;
      }}
      .shell {{
        width: 100%;
        padding: 24px 12px;
        box-sizing: border-box;
      }}
      .container {{
        max-width: 760px;
        margin: 0 auto;
        background: #ffffff;
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
      }}
      .header {{
        background: linear-gradient(120deg, #0f172a, #1d4ed8);
        padding: 28px 24px 18px;
      }}
      .eyebrow {{
        color: #bfdbfe;
        font-size: 12px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 0 0 8px;
      }}
      .title {{
        color: #ffffff;
        font-size: 28px;
        line-height: 1.2;
        margin: 0;
        font-weight: 700;
      }}
      .subtitle {{
        color: #dbeafe;
        margin: 8px 0 0;
        font-size: 14px;
      }}
      .content {{
        padding: 26px 24px 10px;
      }}
      h1 {{
        font-size: 25px;
        margin: 0 0 14px;
        line-height: 1.25;
      }}
      h2 {{
        margin-top: 30px;
        margin-bottom: 10px;
        font-size: 20px;
        line-height: 1.3;
        color: #0f172a;
        border-left: 4px solid #1d4ed8;
        padding-left: 10px;
      }}
      h3 {{
        margin-top: 20px;
        margin-bottom: 8px;
        font-size: 17px;
        color: #1f2937;
      }}
      p {{
        margin: 0 0 12px;
      }}
      ul, ol {{
        margin: 0 0 16px;
        padding-left: 22px;
      }}
      li {{
        margin: 0 0 8px;
      }}
      strong {{
        color: #111827;
      }}
      code {{
        background: #eff6ff;
        color: #1e3a8a;
        border-radius: 4px;
        padding: 1px 5px;
        font-size: 0.92em;
      }}
      hr {{
        border: 0;
        border-top: 1px solid #e5e7eb;
        margin: 28px 0;
      }}
      .footer {{
        padding: 16px 24px 22px;
        font-size: 12px;
        color: #6b7280;
      }}
      @media (max-width: 640px) {{
        .header {{
          padding: 20px 16px 14px;
        }}
        .title {{
          font-size: 23px;
        }}
        .content {{
          padding: 20px 16px 8px;
        }}
        .footer {{
          padding: 14px 16px 20px;
        }}
      }}
    </style>
  </head>
  <body>
    <div class="shell">
      <div class="container">
        <div class="header">
          <p class="eyebrow">Spanish Writing Trainer</p>
          <h1 class="title">{subject}</h1>
          <p class="subtitle">Daily pattern-based lesson for automatic sentence building</p>
        </div>
        <div class="content">
          {body_html}
        </div>
        <div class="footer">
          You are receiving this lesson from your automated Spanish daily lesson generator.
        </div>
      </div>
    </div>
  </body>
</html>
"""
    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(markdown_content)
    message.add_alternative(html_content, subtype="html")
    return message


def send_email(message: EmailMessage, smtp_user: str, smtp_password: str) -> None:
    smtp_host = os.getenv("SMTP_HOST", "smtp.mail.me.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    with smtplib.SMTP(smtp_host, smtp_port) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(smtp_user, smtp_password)
        smtp.send_message(message)


def validate_all(lesson_files: list[tuple[int, Path]]) -> None:
    if not lesson_files:
        raise RuntimeError("No lesson files found to validate.")

    for lesson_number, lesson_file in lesson_files:
        payload = load_json(lesson_file)
        validate_lesson_schema(payload, str(lesson_file))
        print(f"OK lesson-{lesson_number}: {lesson_file}")


def main() -> int:
    args = parse_args()
    lessons_root = Path(args.lessons_root)
    lesson_files = discover_lesson_files(lessons_root)

    if args.validate_all:
        validate_all(lesson_files)
        return 0

    selected_lesson = select_lesson_file(lesson_files, args.lesson_number)
    if selected_lesson is None:
        print("No lesson scheduled for today based on LESSON_START_DATE/LESSON_CADENCE_DAYS.")
        return 0

    lesson_number, lesson_file = selected_lesson
    payload = load_json(lesson_file)
    validate_lesson_schema(payload, str(lesson_file))
    markdown_content = render_markdown_lesson(lesson_number, payload)

    print(f"Selected lesson file: {lesson_file}")
    if args.dry_run:
        print(markdown_content)
        return 0

    sender = os.getenv("ICLOUD_EMAIL", "")
    smtp_password = os.getenv("ICLOUD_APP_PASSWORD", "")
    recipient = os.getenv("RECIPIENT_EMAIL", DEFAULT_RECIPIENT)

    if not sender:
        raise RuntimeError("Missing ICLOUD_EMAIL environment variable.")
    if not smtp_password:
        raise RuntimeError("Missing ICLOUD_APP_PASSWORD environment variable.")

    subject = f"Spanish Daily Lesson {lesson_number} - {payload['pattern_id']}"
    message = build_message(sender, recipient, subject, markdown_content)
    send_email(message, sender, smtp_password)
    print(f"Email sent to {recipient} from {sender}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
