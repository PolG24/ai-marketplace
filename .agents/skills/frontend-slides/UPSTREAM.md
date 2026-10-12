# Frontend Slides in this repository

Source: https://github.com/zarazhangrui/frontend-slides
Revision: `9906a34d640d2111f724544cbc50f7f130569ae1`
Upstream path: `plugins/frontend-slides/skills/frontend-slides/`
License: MIT (see [LICENSE](LICENSE)).

The complete upstream skill package is vendored here without modifications,
including its support documents, CSS, stage JavaScript, 34 bold template
preview/design pairs, and three helper scripts. The upstream root README and
license are included alongside it. This file documents the local installation.

## Use

This is a repository-local skill in `.agents/skills/frontend-slides/`.
It will be available on your next turn. Ask the coding agent:

> Use the frontend-slides skill to turn docs/design.md into a speaker-led
> interview presentation. Start with three visual style previews.

If the agent does not discover skills automatically, point it directly to
`.agents/skills/frontend-slides/SKILL.md`. Resolve the skill's supporting-file
and script paths relative to this directory, not the repository root.

## Optional helper dependencies

Creating HTML slides requires no npm packages or build tools. Helpers have
additional requirements only when used:

- PowerPoint extraction: Python and `python-pptx`.
- PDF export: Node.js/npm; the export script installs Playwright and Chromium.
- Deployment: Node.js/npm and a Vercel account; the script uses the Vercel CLI.

These optional dependencies have not been installed as part of vendoring the
skill. To export a generated presentation from the repository root:

```sh
bash .agents/skills/frontend-slides/scripts/export-pdf.sh docs/presentation.html docs/presentation.pdf
```
