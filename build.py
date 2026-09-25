"""Build the site into _site/.

    python build.py            # production build (drafts excluded)
    python build.py --drafts   # include posts marked `draft: true`
    python build.py --serve    # build with drafts, then serve on http://localhost:8000

Needs Python (jinja2, pyyaml, markdown-free: Markdown goes through pandoc),
pandoc >= 3 on PATH or at $PANDOC, and `npm install` for MathJax.
"""

import argparse
import datetime as dt
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import jinja2
import yaml

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
BLOG = CONTENT / "blog"
OUT = ROOT / "_site"


def pandoc_bin():
    if os.environ.get("PANDOC"):
        return os.environ["PANDOC"]
    found = shutil.which("pandoc")
    if found:
        return found
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "Pandoc" / "pandoc.exe"
    if local.exists():
        return str(local)
    sys.exit("pandoc not found: install it or set $PANDOC")


def pandoc(args, text):
    r = subprocess.run([pandoc_bin(), *args], input=text, capture_output=True,
                       text=True, encoding="utf-8", cwd=BLOG)
    if r.returncode:
        sys.exit(f"pandoc failed:\n{r.stderr}")
    if r.stderr.strip():
        print(r.stderr.strip(), file=sys.stderr)
    return r.stdout


def md_inline(text):
    """Short Markdown (bio paragraphs, list items) to HTML."""
    out = pandoc(["-f", "markdown", "-t", "html", "--wrap=none"], text).strip()
    # One-paragraph snippets are used inline; strip the wrapping <p>.
    if out.startswith("<p>") and out.endswith("</p>") and out.count("<p>") == 1:
        out = out[3:-4]
    return out


def read_post(path, site):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", raw, re.S)
    if not m:
        sys.exit(f"{path.name}: missing front matter")
    meta = yaml.safe_load(m.group(1))
    date = meta["date"]
    if isinstance(date, str):
        date = dt.date.fromisoformat(date)
    slug = meta.get("slug") or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
    args = ["-f", "markdown+tex_math_dollars+raw_tex", "-t", "html5",
            "--math-method=mathjax", "--wrap=none", "--section-divs",
            "--lua-filter", str(ROOT / "filters" / "figures.lua"),
            "--citeproc", "--bibliography", str(BLOG / "refs.bib"), "--csl", str(BLOG / "aps.csl"),
            "--metadata", "link-citations=true",
            "--metadata", "reference-section-title=",
            "--syntax-highlighting=pygments"]
    if meta.get("toc"):
        args += ["--toc", "--toc-depth=2", "--template", str(ROOT / "templates" / "pandoc-body.html")]
    body = pandoc(args, raw)
    toc = ""
    if meta.get("toc"):
        toc, _, body = body.partition("<!--BODY-->")
    authors = meta.get("authors") or [site["name"]]
    if isinstance(authors, str):
        authors = [authors]
    image = meta.get("image")
    # Preview cards need a raster image: for an SVG use a PNG of the same name
    # next to it if there is one, else fall back to the portrait.
    if image and image.lower().endswith(".svg"):
        png = image[:-4] + ".png"
        image = png if (BLOG / slug / png).exists() else None
    return {
        "title": meta["title"], "date": date, "slug": slug,
        "summary": meta.get("summary", ""), "draft": bool(meta.get("draft")),
        "toc": toc.strip(), "body": body, "url": f"/blog/{slug}/",
        "src": path.name, "authors": authors,
        "affiliation": meta.get("affiliation", ""), "doi": meta.get("doi", ""),
        # Preview-card image: a file in content/blog/<slug>/, else the portrait.
        "image": f"/blog/{slug}/{image}" if image else None,
    }


def surname_first(name):
    parts = name.split()
    return f"{parts[-1]}, {' '.join(parts[:-1])}" if len(parts) > 1 else name


def citation(post, site):
    """The "Cite as" line and BibTeX for a post (Lil'Log's pattern)."""
    host = site["url"].split("//", 1)[1]
    url = site["url"] + post["url"]
    d = post["date"]
    names = [surname_first(post["authors"][0])] + post["authors"][1:]
    who = names[0] if len(names) == 1 else ", ".join(names[:-1]) + (", and " if len(names) > 2 else " and ") + names[-1]
    title_word = re.sub(r"[^a-z0-9]", "", post["title"].split()[0].lower()) or "post"
    key = f"{re.sub(r'[^a-z]', '', post['authors'][0].split()[-1].lower())}{d.year}{title_word}"
    line = f"{who}. ({d.strftime('%b %Y')}). {post['title']}. {host}. "
    line += f"https://doi.org/{post['doi']}" if post["doi"] else url
    fields = [("title", post["title"]),
              ("author", " and ".join(surname_first(a) for a in post["authors"])),
              ("journal", host), ("year", str(d.year)), ("month", d.strftime("%b")),
              ("url", url)]
    if post["doi"]:
        fields.append(("doi", post["doi"]))
    width = max(len(k) for k, _ in fields)
    bib = f"@article{{{key},\n" + ",\n".join(
        f"  {k.ljust(width)} = {{{v}}}" for k, v in fields) + "\n}"
    return line, bib


def bold_me(authors, me):
    a = html.escape(authors)
    return a.replace(html.escape(me), f"<strong>{html.escape(me)}</strong>")


# Dark-mode palette for the publication thumbnails (their shared drawing palette).
# Injected into each SVG as CSS, so the image follows the reader's OS theme
# even when shown through <img>. Role hues are only lifted a little.
THUMB_DARK = {
    "#F4F2ED": "#1D1C1A",   # paper background
    "#FFFFFF": "#2B2A27", "#FFF": "#2B2A27",
    "#E4E6EA": "#393C41",
    "#C8D3D8": "#4F5961",
    "#3D4652": "#D7DBE0",   # ink
    "#3A8FD0": "#5AA8E8",
    "#D9822B": "#EC9A4E",
    "#D93A3A": "#F06060",
    "#9DC4E6": "#3E7099",   # off-palette pale blue (granular-drag)
}


# Light mode deepens the two role hues so they reach 3:1 contrast on the paper
# tone (orange was 2.6:1, blue 3.1:1). Sources keep the original hexes.
THUMB_LIGHT = {
    "#3A8FD0": "#2F80C4",
    "#D9822B": "#C8701C",
}


def _recolour(mapping):
    return "".join(
        f'[fill="{k}" i]{{fill:{v}}}[stroke="{k}" i]{{stroke:{v}}}[stop-color="{k}" i]{{stop-color:{v}}}'
        for k, v in mapping.items())


def darkmode_svg(path):
    # Dark rules come last so they win over the light remap in dark mode.
    style = (f"<style>{_recolour(THUMB_LIGHT)}"
             f"@media (prefers-color-scheme: dark){{{_recolour(THUMB_DARK)}}}</style>")
    svg = path.read_text(encoding="utf-8")
    svg = re.sub(r"(<svg\b[^>]*>)", lambda m: m.group(1) + style, svg, count=1)
    path.write_text(svg, encoding="utf-8")


def external_links_new_tab(html_text, site_url):
    """Open links to other sites (and PDFs such as the CV) in a new tab;
    links within the site keep the browser default (same tab)."""
    def fix(m):
        tag = m.group(0)
        href = re.search(r'href="([^"]*)"', tag)
        if not href or "target=" in tag or 'id="email"' in tag:
            return tag
        url = href.group(1)
        external = url.startswith(("http://", "https://")) and not url.startswith(site_url)
        if external or url.lower().endswith(".pdf"):
            return tag[:-1] + ' target="_blank" rel="noopener">'
        return tag
    return re.sub(r"<a\b[^>]*>", fix, html_text)


def atom_feed(site, posts):
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    items = []
    for p in posts[:20]:
        ts = f"{p['date'].isoformat()}T00:00:00Z"
        items.append(
            f"<entry><title>{html.escape(p['title'])}</title>"
            f"<link href=\"{site['url']}{p['url']}\"/><id>{site['url']}{p['url']}</id>"
            f"<updated>{ts}</updated>"
            + "".join(f"<author><name>{html.escape(a)}</name></author>" for a in p["authors"])
            + f"<summary>{html.escape(p['summary'])}</summary>"
            f"<content type=\"html\">{html.escape(p['body'])}</content></entry>")
    return ("<?xml version=\"1.0\" encoding=\"utf-8\"?>"
            "<feed xmlns=\"http://www.w3.org/2005/Atom\">"
            f"<title>{html.escape(site['name'])}</title>"
            f"<link href=\"{site['url']}/blog/\"/><link rel=\"self\" href=\"{site['url']}/feed.xml\"/>"
            f"<id>{site['url']}/</id><updated>{now}</updated>"
            f"<author><name>{html.escape(site['name'])}</name></author>"
            f"<rights>{html.escape(site['license']['name'])}: {site['license']['url']}</rights>"
            + "".join(items) + "</feed>\n")


def build(drafts):
    site = yaml.safe_load((CONTENT / "site.yaml").read_text(encoding="utf-8"))
    # Visit counter: set in the CI environment (a repository variable), not in
    # the repository, so local previews and forks count nothing.
    site["goatcounter"] = os.environ.get("GOATCOUNTER", "")
    pubs = yaml.safe_load((CONTENT / "publications.yaml").read_text(encoding="utf-8"))

    site["bio_html"] = pandoc(["-f", "markdown", "-t", "html", "--wrap=none"], site["bio"])
    for key in ("experience", "education"):
        for e in site.get(key, []):
            e["note_html"] = md_inline(e["note"]) if e.get("note") else ""
    site["service_html"] = [md_inline(s) for s in site.get("service", [])]
    for p in pubs["papers"]:
        p["authors_html"] = bold_me(p["authors"], pubs["me"])
        # Thumbnail art: static/pubs/<slug>.svg with alt text from the YAML.
        # A missing SVG leaves an empty tile.
        slug = p.get("thumb")
        if slug and (ROOT / "static" / "pubs" / f"{slug}.svg").exists():
            p["thumb_url"] = f"/pubs/{slug}.svg"
            p["thumb_alt"] = p.get("thumb_alt") or p["title"]

    posts = [read_post(f, site) for f in sorted(BLOG.glob("*.md"))]
    for p in posts:
        p["cite_line"], p["bibtex"] = citation(p, site)
    posts = [p for p in posts if drafts or not p["draft"]]
    posts.sort(key=lambda p: p["date"], reverse=True)

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(ROOT / "templates"),
                             autoescape=jinja2.select_autoescape(["html"]))
    env.filters["longdate"] = lambda d: f"{d.day} {d.strftime('%B %Y')}"
    # Fingerprint the stylesheet so browsers fetch it again whenever it changes
    # (GitHub Pages lets them cache it for 10 minutes otherwise).
    import hashlib
    css_v = hashlib.sha1((ROOT / "static" / "style.css").read_bytes()).hexdigest()[:8]
    ctx = {"site": site, "year": dt.date.today().year, "css_v": css_v,
           "updated": dt.date.today().strftime("%B %Y")}

    # Empty _site/ rather than delete it: on Windows a running preview server
    # (or OneDrive) holds the directories open and rmtree fails.
    if OUT.exists():
        for f in OUT.rglob("*"):
            if f.is_file():
                f.unlink()
        for d in sorted((d for d in OUT.rglob("*") if d.is_dir()), key=lambda d: len(d.parts), reverse=True):
            try:
                d.rmdir()
            except OSError:
                pass
    shutil.copytree(ROOT / "static", OUT, dirs_exist_ok=True)
    (OUT / ".nojekyll").write_text("")
    for svg in (OUT / "pubs").glob("*.svg"):
        darkmode_svg(svg)

    def write(rel, text):
        dest = OUT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if rel.endswith(".html"):
            text = external_links_new_tab(text, site["url"])
        dest.write_text(text, encoding="utf-8")
        return dest

    write("index.html", env.get_template("home.html").render(
        **ctx, papers=pubs["papers"], posts=posts[:3], page="home"))
    write("blog/index.html", env.get_template("blog.html").render(
        **ctx, posts=posts, page="blog"))
    math_pages = []
    for p in posts:
        dest = write(f"blog/{p['slug']}/index.html",
                     env.get_template("post.html").render(**ctx, post=p, page="post"))
        if 'class="math' in p["body"]:
            math_pages.append(str(dest))
        # Images and data next to a post live in content/blog/<slug>/.
        assets = BLOG / p["slug"]
        if assets.is_dir():
            shutil.copytree(assets, OUT / "blog" / p["slug"], dirs_exist_ok=True)
            # SVGs drawn by the schematic-figure skill (root carries data-name)
            # use the thumbnail palette, so they follow the theme the same way.
            for svg in (OUT / "blog" / p["slug"]).rglob("*.svg"):
                if re.search(r"<svg\b[^>]*\bdata-name=", svg.read_text(encoding="utf-8")[:2000]):
                    darkmode_svg(svg)
    write("404.html", env.get_template("404.html").render(**ctx, page="404"))
    write("feed.xml", atom_feed(site, [p for p in posts if not p["draft"]]))

    if math_pages:
        r = subprocess.run(["node", str(ROOT / "mathjax.mjs"), *math_pages])
        if r.returncode:
            sys.exit("MathJax rendering failed")

    print(f"built {OUT} ({len(posts)} post(s), {len(math_pages)} with math)")


def serve():
    import functools
    import http.server
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    print("serving http://localhost:8000  (Ctrl+C to stop)")
    http.server.ThreadingHTTPServer(("127.0.0.1", 8000), handler).serve_forever()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--drafts", action="store_true")
    ap.add_argument("--serve", action="store_true")
    a = ap.parse_args()
    build(a.drafts or a.serve)
    if a.serve:
        serve()
