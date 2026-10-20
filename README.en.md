# Manga Colorization

**Color existing manga while preserving its drawing, lettering, acting, and color continuity across pages.**

[中文](README.md) · [Examples](examples/README.md) · [Tool reference](docs/tools.md) · [Report an issue](https://github.com/phonowell/manga-colorization/issues)

[![Checks](https://github.com/phonowell/manga-colorization/actions/workflows/validate.yml/badge.svg)](https://github.com/phonowell/manga-colorization/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An Agent Skills package with local review helpers. Your agent needs an authorized image-generation tool that accepts original images and relevant color references. You keep creative and selection control. The Python helpers inspect files and prepare requests; they do not call an image provider.

## Install

With Node.js 22.20+, run from your manga project:

```sh
npx skills add phonowell/manga-colorization --skill manga-colorization -a codex
```

Use `-a claude-code` for the Claude Code installation target, or let the installer offer compatible agents. Add `-g` for a user-wide install. Installer compatibility does not establish image-generation behavior in every agent. Open a new agent session after installation.

Manual alternative: copy this repository into the skill directory your agent supports, keeping `SKILL.md`, `references/`, `scripts/`, and `agents/` together. Git clone and agent instructions do not require Python; the optional Python tools do.

## Color a first page

Provide a monochrome original. Add official color references, an accepted preceding page, and your palette when available. For example:

```text
Use $manga-colorization to color ./originals/page-01.png.
Use the images in ./references/ for color and a bright watercolor finish.
Preserve lettering, expressions, eye states, hands, and panel layout.
Start with this page, review the actual result, and let me choose before batching.
```

A first-page task does not require a pre-existing Colorleaf ledger. The agent should record only the source bindings, palette decisions, feedback, and selected versions needed for the task. If an image tool is unavailable, it should state the missing capability and prepare useful inputs without pretending it generated artwork.

For correction, provide the original, the exact reviewed candidate, and feedback. Every new model target comes from the original. Colored candidates are color references only. Multiple candidates, complete-panel montages and assembly, and uniform whole-panel grading are supported; code-painted object colors are not.

## Try the local review tools

Python 3.10+; no API key or manga images are needed for the diagnostic demo:

```sh
git clone https://github.com/phonowell/manga-colorization.git
cd manga-colorization
python -m pip install -r requirements.txt
python scripts/quickstart.py --demo --out outputs/first-demo
```

Open `outputs/first-demo/inspection/contact-sheet.png` and `outputs/first-demo/fidelity/comparison/overview-inspection.png`.

![Synthetic geometric fixture: original, shifted candidate, and diagnostic edge differences](docs/assets/diagnostic-demo.png)

This is a synthetic drift diagnostic, not a manga coloring result. No artwork is generated and no image quality is automatically approved.

Inspect your own original and an existing same-size candidate:

```sh
python scripts/quickstart.py --source original.png --candidate candidate.png --out outputs/my-review
```

Inputs remain unchanged. Choose a new output directory for every run. Reports contain local paths; inspect them before sharing. Diagnostic maps are review evidence and must not be delivered as artwork.

## Expectations and troubleshooting

- Installation adds instructions; it does not provide a model, API credentials, a hosted app, or a Colorleaf runtime.
- Using instructions needs no Python packages. Running review helpers needs `requirements.txt`.
- No official color references? Use explicitly authored palette choices without presenting them as canon.
- `unverified` means visual review is still needed. Similarity scores do not certify lettering, expression, or semantic boundaries.
- Different image sizes? The quickstart refuses resizing or implicit alignment. Use the explicit padding format in [source fidelity](references/pixel-fidelity.md).
- Existing output directory? Keep the old evidence and choose a new `--out`.
- Skill not visible? Start a new session and verify installation with `npx skills list -a codex`.

## Development

```sh
python scripts/test-source-fidelity.py
python -m unittest discover -s tests -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for changes and issue reports, [docs/tools.md](docs/tools.md) for helper boundaries, and [docs/repository-design.md](docs/repository-design.md) for the repository research and validation limits. Some detailed guides are currently in Chinese; the agent-facing skill and references are in English.

Derived from Colorleaf; [SOURCE.json](SOURCE.json) records the original extracted hashes and standalone adaptations. MIT licensed. No private manga, user feedback, provider settings, or credentials are distributed.
