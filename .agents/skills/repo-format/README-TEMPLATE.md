# README Template

Structure for `README.md`, in order. Every section is mandatory unless marked otherwise. Content must be derived from existing project files — never invented.

---

## 1. Title

Project name as H1. Match the repository name.

## 2. Description

2–4 sentences. What the project does, who it's for, and the core problem it solves. No marketing language — no "robust", "powerful", "cutting-edge". Plain technical English (or the project's documentation language).

## 3. Key Features

Bulleted list. Each bullet: **bold label** + plain description. Group by domain if the project spans multiple areas. Only list features that exist in the codebase or spec — never aspirational.

## 4. Tech Stack

Flat table or bullet list:

| Layer     | Technology         |
| --------- | ------------------ |
| Language  | e.g. Python 3.12   |
| Framework | e.g. FastAPI       |
| Database  | e.g. Firestore     |
| Auth      | e.g. OAuth 2.0     |
| Hosting   | e.g. GCP Cloud Run |

Include only what the project actually uses. Omit rows with no answer.

## 5. Project Structure

A directory tree of `src/` (or equivalent). One line per module/directory. Short inline comment on what each module owns.

```
src/
├── auth/          # Authentication and authorization
├── tasks/         # GTD task management
├── calendar/      # Google Calendar integration
└── telegram/      # Telegram bot webhook handling
```

If no source code exists yet, show the planned structure from the spec and mark it `(planned)`.

## 6. Getting Started

### Prerequisites

Bulleted list of required tools and versions.

### Installation

```bash
# Clone, install, configure — copy-pasteable commands
```

### Environment Variables

Table of required env vars with descriptions (no actual values).

### Running

```bash
# Dev server, tests, build — copy-pasteable commands
```

If the project has no runnable code yet, state "Not yet implemented" and link to the spec.

## 7. Documentation

Links to docs in `docs/`:

- [Architecture](docs/architecture.md)
- [Spec](docs/spec.md) (if applicable)

## 8. License

One line: "This project is licensed under the [LICENSE_NAME](LICENSE)."

---

## Writing rules

- **No placeholders in production.** Use `<!-- TODO: description -->` HTML comments for missing content — visible in source, invisible when rendered.
- **No marketing.** Strip adjectives that don't carry technical meaning.
- **Match the project language.** If existing docs are in Spanish, write the README in Spanish.
- **Accuracy over completeness.** A short accurate README beats a long stale one.
