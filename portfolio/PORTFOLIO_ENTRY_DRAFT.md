# fuzzy-funicular

Automated daily Spanish lesson delivery with structured writing drills and GitHub Actions scheduling.

## Overview

`fuzzy-funicular` is a Python-based automation project that turns lesson source material into structured daily writing practice emails. The system validates lesson schemas, chooses the correct lesson by date rules, renders learner-friendly Markdown/HTML, and sends through iCloud SMTP on a schedule.

This started as a consistency problem: lesson delivery was manual and easy to skip. The project now enforces repeatable cadence and quality checks so learners get practical sentence-building drills every run.

## What I Built

- A normalized lesson format (`lesson.json`) with drill-first sections:
  - cognitive shift
  - controlled recombination
  - pattern mutation
  - contrastive discrimination
  - guided personal writing
  - reverse conceptual expression
  - common errors
  - answer key
- A delivery script (`scripts/send_daily_lesson.py`) that:
  - validates schema consistency
  - selects lessons by date/cadence
  - renders Markdown + HTML email content
  - sends via SMTP
- A GitHub Actions workflow that:
  - runs on cron + manual dispatch
  - validates all lessons before attempting send
  - reads configuration from secrets/env values

## Key Engineering Decisions

- **Structured content over free text:** JSON schema keeps lessons machine-checkable and reusable.
- **Fail fast validation:** the pipeline validates all lessons before sending to prevent bad production sends.
- **Configurable cadence:** start date, starting lesson number, and cadence days let me pause/resume progression without rewriting logic.
- **Separation of concerns:** source PDFs remain reference material; normalized JSON drives automation.

## Outcomes

- Built a reusable lesson-delivery pipeline with automated scheduling.
- Currently maintains `63` lesson folders with JSON + Markdown artifacts.
- Supports flexible pacing (including non-daily schedules) while preserving lesson order.

## Stack

Python, GitHub Actions, JSON, Markdown, SMTP (iCloud), cron-based automation.

## Repository

<https://github.com/r0cstar09/fuzzy-funicular>

## Suggested Screenshots

1. Workflow file (`.github/workflows/send-daily-lesson.yml`) showing scheduled automation.
2. Lesson generator script (`scripts/send_daily_lesson.py`) around selection/validation logic.
3. Sample lesson JSON (`lessons/lesson-40/lesson.json`) showing structured drill model.
4. Terminal output from `--validate-all` showing lesson checks passing.
5. One rendered lesson email preview from `--dry-run`.

