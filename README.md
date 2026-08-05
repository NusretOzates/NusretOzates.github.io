# NusretOzates.github.io

Personal portfolio and blog.

## Branches

| Branch | Stack | Role |
|--------|-------|------|
| `main` | [Quarto](https://quarto.org) | Production source (`posts/`, `_quarto.yml`, …) |
| `astro-portfolio-redesign` | [Astro](https://astro.build) | Redesign WIP (`astro-site/`) |
| `gh-pages` | Static HTML | **Published site** (do not edit by hand) |

Keep Quarto on `main` and Astro on the redesign branch until cutover. Merge only when you are ready to switch stacks.

## Quarto (`main`)

```bash
git checkout main
quarto render
# publish build output to gh-pages (your existing workflow)
```

Google Analytics (`G-FVW7859HWV`) is configured in `_quarto.yml`.

## Astro (`astro-portfolio-redesign`)

```bash
git checkout astro-portfolio-redesign
cd astro-site && npm install
npm run dev          # from repo root
npm run build        # writes to docs/ (for preview or future publish)
```

Google Analytics is in `astro-site/src/layouts/BaseLayout.astro` (production builds only).

Typography: **Geist** for UI/prose; **JetBrains Mono** for code. Fenced blocks use [Expressive Code](https://expressive-code.com/) (editor/terminal frames, dual light/dark themes, copy button).

## Publishing

The live site is on **`gh-pages`**. Today that branch is built from Quarto on `main`. After Astro cutover, build with `npm run build` and push the output to `gh-pages` instead.
