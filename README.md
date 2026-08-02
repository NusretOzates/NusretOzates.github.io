# NusretOzates.github.io

Personal portfolio and blog built with [Astro](https://astro.build).

## Quick start

```bash
cd astro-site && npm install
npm run dev          # from repo root
```

## Build for GitHub Pages

```bash
npm run build        # migrates content, builds to docs/, indexes search
```

The site publishes from the `docs/` directory on `main`.

## Content

| Type | Source | Astro collection |
|------|--------|------------------|
| Blog posts | `posts/*/index.qmd` | `astro-site/src/content/posts/` |
| Notes | `notes/*/index.qmd` | `astro-site/src/content/notes/` |
| Talks | `talks.yml` | `astro-site/src/content/talks/` |
| Videos | `videos.yml` | `astro-site/src/content/videos/` |

Run `python3 scripts/migrate_to_astro.py` after editing Quarto sources, or edit Astro content directly.

## Scripts

- `scripts/migrate_to_astro.py` — sync QMD/YAML into Astro collections
- `scripts/polish_site.py` — Medium link + attribution footer for QMD posts
- `scripts/medium_import/` — import new Medium articles
- `scripts/audit_truncated_posts.py` — detect truncated imports
