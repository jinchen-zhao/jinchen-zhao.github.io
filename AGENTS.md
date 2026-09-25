# jinchen-zhao.github.io

Personal homepage and blog. Source lives here; GitHub Actions builds `_site/` on every push to `main` and publishes it with GitHub Pages (`.github/workflows/deploy.yml`).

This repository is public. Private notes about the site (what to keep off it and why, account details) do not belong here.

## Map

| Path | What |
|---|---|
| `content/site.yaml` | Bio, links, experience, honors, service, blog license |
| `content/publications.yaml` | Publication list (newest first), thumbnail slug and alt text; keep in step with the academic CV |
| `content/blog/*.md` | Posts: `YYYY-MM-DD-slug.md` with YAML front matter |
| `content/blog/<slug>/` | Images and files for that post, copied next to it |
| `content/blog/refs.bib`, `aps.csl` | Shared bibliography; numeric APS-like citation style |
| `templates/` | Jinja page templates; `pandoc-body.html` splits the TOC from the body |
| `filters/figures.lua` | Pandoc filter: numbered figures and `@fig:` references |
| `static/` | Copied verbatim: `style.css`, `profile.jpg`, `cv.pdf`, `favicon.svg`, `pubs/<slug>.svg` |
| `build.py` | Pandoc (Markdown, citeproc) + Jinja, then `mathjax.mjs` renders TeX to static HTML |

## Writing a post

`content/blog/YYYY-MM-DD-slug.md`, files it uses in `content/blog/<slug>/`. Front matter:

| Field | Meaning |
|---|---|
| `title`, `date` | required |
| `summary` | one line: blog index, feed, preview card |
| `authors` | list; default the site owner. Joint lab posts list everyone |
| `affiliation` | shown after the authors, e.g. `LGW Lab, Yale University` |
| `image` | preview-card image in the post folder; must be PNG/JPG (an `.svg` falls back to a same-name `.png`, else the portrait) |
| `doi` | once assigned (e.g. by Rogue Scholar): shown in the byline, BibTeX and `citation_doi` |
| `toc`, `draft` | table of contents; drafts never publish (`--drafts` previews them) |

Math is ordinary LaTeX: `$..$`, `$$..$$`, `\begin{equation}`/`align` with `\label{}` and `\eqref{}` (AMS numbering per post, rendered at build time by MathJax; KaTeX was rejected because it has no `\label`/`\eqref`). Cite papers with `[@key]` from `refs.bib`; the reference list lands under a final `## References` heading. Figures: `![Caption.](file.svg){#fig:name}` is numbered "Figure N." and `@fig:name` becomes a link; add `width=55%` to shrink, `.wide` to break out of the text column. SVGs from the schematic-figure skill recolour for dark mode automatically.

Every post ends with a "Cite as" line, BibTeX with a copy button and the license line; the head carries `citation_*` tags for Zotero and Google Scholar. Posts are CC BY 4.0 (`license` in `site.yaml`), which Rogue Scholar requires for DOIs. Google Scholar does not index blogs directly: a post gains a Scholar entry only when indexed papers cite it (or by "Add article manually" on a profile).

## Build and preview

    npm install                      # once, for MathJax
    python build.py --serve          # drafts included, http://localhost:8000
    python build.py                  # what CI runs

The visit counter is configured by the `GOATCOUNTER` repository variable, not in the repository. Needs Python with `jinja2` and `pyyaml`, Node, and pandoc 3.x (`--math-method`, `--syntax-highlighting`); CI pins pandoc 3.11. If pandoc is not on PATH, set `$PANDOC`.

## Conventions

- No plain email address in the page source: the Email link is assembled in the browser from `site.yaml`.
- Links to other sites and PDFs open in a new tab (`external_links_new_tab` in `build.py`); the stylesheet link carries a content hash so style changes reach returning visitors at once.
- Thumbnails (`static/pubs/`, drawn separately) use only the shared palette hexes listed in `THUMB_DARK`: `build.py` recolours exactly those per theme (`THUMB_LIGHT` deepens blue and orange to 3:1 on the paper tone; `THUMB_DARK` maps every colour), and any other hex looks wrong in one theme.
