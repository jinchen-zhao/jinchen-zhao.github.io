"""Live editor for blog posts: Markdown on the left, the built post on the right.

    python editor.py            # http://localhost:8001

Saves the post as you type and patches the preview in place: only the edited
post goes through pandoc (the same filters and citations as build.py), math goes
to a MathJax process that stays loaded (mathjax-live.mjs), and only the blocks
that changed are swapped in the page, so images and galleries do not flicker.
A full `build.py --drafts` follows a few seconds after typing stops, and at once
when the front matter changes. Local use only: it binds 127.0.0.1 and writes
only content/blog/*.md.
"""

import http.server
import json
import re
import subprocess
import sys
import threading
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import build as site_build  # noqa: E402

BLOG = ROOT / "content" / "blog"
OUT = ROOT / "_site"
PORT = 8001
FULL_BUILD_DELAY = 3.0  # seconds after the last save
build_lock = threading.Lock()
build_timer = None
front_seen = {}  # post name -> front matter text at the last render


class MathWorker:
    """mathjax-live.mjs kept running; restarted if it dies."""

    def __init__(self):
        self.proc = None
        self.lock = threading.Lock()

    def render(self, html_text):
        with self.lock:
            if self.proc is None or self.proc.poll() is not None:
                self.proc = subprocess.Popen(["node", str(ROOT / "mathjax-live.mjs")], cwd=ROOT,
                                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                             text=True, encoding="utf-8", bufsize=1)
            self.proc.stdin.write(json.dumps({"html": html_text}) + "\n")
            self.proc.stdin.flush()
            line = self.proc.stdout.readline()
        return json.loads(line) if line else {"error": "MathJax worker exited"}


math = MathWorker()


def front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else ""


def render_body(path):
    """The post's body HTML as build.py would write it, without touching _site/."""
    site = yaml.safe_load((ROOT / "content" / "site.yaml").read_text(encoding="utf-8"))
    try:
        post = site_build.read_post(path, site)
    except SystemExit as e:  # build.pandoc() exits on a pandoc error
        return {"error": str(e)}
    body, css = post["body"], ""
    if 'class="math' in body:
        r = math.render(body)
        if "error" in r:
            return {"error": "MathJax: " + r["error"]}
        body, css = r["html"], r["css"]
    return {"body": site_build.external_links_new_tab(body, site["url"]), "css": css}


def schedule_full_build():
    global build_timer
    if build_timer:
        build_timer.cancel()
    build_timer = threading.Timer(FULL_BUILD_DELAY, build)
    build_timer.daemon = True
    build_timer.start()


def post_path(name):
    p = (BLOG / name).resolve()
    if p.parent != BLOG.resolve() or p.suffix != ".md":
        raise ValueError(f"not a post: {name}")
    return p


def build():
    with build_lock:
        r = subprocess.run([sys.executable, str(ROOT / "build.py"), "--drafts"],
                           capture_output=True, text=True, timeout=120)
    return r.returncode == 0, (r.stdout + r.stderr).strip()


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Post editor</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root { --bg:#fbfaf7; --text:#1c1c1a; --muted:#6c6a64; --rule:#e4e0d7; --pane:#f3f1ec; --ok:#2e7d4f; --err:#b3261e;
  --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace; --sans: Inter, -apple-system, system-ui, sans-serif; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg:#151514; --text:#e7e5df; --muted:#a3a097; --rule:#2c2b28; --pane:#1f1e1c; --ok:#7fcf9f; --err:#f2b8b5; } }
* { box-sizing: border-box; }
html, body { height: 100%; margin: 0; background: var(--bg); color: var(--text); font-family: var(--sans); }
body { display: grid; grid-template-rows: auto 1fr; }
header { display: flex; gap: 12px; align-items: center; padding: 8px 14px; border-bottom: 1px solid var(--rule); font-size: 13px; }
select, button { font: inherit; color: inherit; background: var(--pane); border: 1px solid var(--rule); border-radius: 6px; padding: 3px 8px; }
#status { margin-left: auto; color: var(--muted); }
#status.ok { color: var(--ok); } #status.err { color: var(--err); }
main { display: grid; grid-template-columns: var(--split, 50%) 6px 1fr; min-height: 0; }
textarea { width: 100%; height: 100%; resize: none; border: 0; outline: 0; padding: 18px 20px; background: var(--pane); color: var(--text);
  font: 14px/1.6 var(--mono); tab-size: 2; }
#drag { cursor: col-resize; background: var(--rule); }
#right { position: relative; min-height: 0; }
iframe { width: 100%; height: 100%; border: 0; background: var(--bg); }
#log { position: absolute; left: 0; right: 0; bottom: 0; max-height: 45%; overflow: auto; margin: 0; padding: 10px 14px;
  background: var(--pane); color: var(--err); border-top: 1px solid var(--rule); font: 12px/1.5 var(--mono); white-space: pre-wrap; display: none; }
@media (max-width: 800px) { main { grid-template-columns: 1fr; grid-template-rows: 1fr 1fr; } #drag { display: none; } }
</style></head>
<body>
<header>
  <select id="file"></select>
  <button id="save" title="Save and rebuild now (Cmd/Ctrl+S)">Save</button>
  <span id="status">loading</span>
</header>
<main>
  <textarea id="src" spellcheck="true"></textarea>
  <div id="drag"></div>
  <div id="right"><iframe id="view"></iframe><pre id="log"></pre></div>
</main>
<script>
const $ = (id) => document.getElementById(id);
const src = $("src"), view = $("view"), status = $("status"), log = $("log"), file = $("file");
let name = null, mtime = null, dirty = false, saving = false, timer = null;

function setStatus(text, cls) { status.textContent = text; status.className = cls || ""; }

async function api(path, body) {
  const r = await fetch(path, body ? {method: "POST", body: JSON.stringify(body)} : {});
  return r.json();
}

async function load(n) {
  const d = await api("/api/post?name=" + encodeURIComponent(n));
  name = n; mtime = d.mtime; src.value = d.text; dirty = false;
  try { localStorage.setItem("editor.post", n); } catch (e) {}
  showPreview(true);
  setStatus("saved", "ok");
}

// The preview page's post body as it was last rendered, before any script ran on
// it (the gallery script rewrites its own markup). Diffs run against this copy.
let lastRaw = null;

function pageUrl() { return "/blog/" + name.slice(11, -3) + "/"; }

function showPreview(fresh) {
  let y = 0;
  try { y = view.contentWindow.scrollY; } catch (e) {}
  lastRaw = null;
  view.onload = async () => {
    if (!fresh) try { view.contentWindow.scrollTo(0, y); } catch (e) {}
    const html = await (await fetch(pageUrl() + "?raw=" + Date.now())).text();
    const prose = new DOMParser().parseFromString(html, "text/html").querySelector(".prose");
    if (prose) { lastRaw = document.createElement("template"); lastRaw.innerHTML = prose.innerHTML; }
  };
  view.src = pageUrl() + "?t=" + Date.now();
}

const CONTAINERS = new Set(["SECTION", "DIV", "BLOCKQUOTE", "UL", "OL"]);

function initGalleries(node, win) {
  if (node.nodeType !== 1 || !win.initGallery) return;
  if (node.matches(".gallery")) win.initGallery(node);
  node.querySelectorAll(".gallery").forEach((g) => win.initGallery(g));
}

// Make `live` (the page) match `neu`, given that it currently matches `old`.
// Unchanged leading and trailing children are left alone; a changed container
// of the same kind is patched recursively; anything else is replaced.
function patch(old, neu, live, doc) {
  const o = [...old.childNodes], n = [...neu.childNodes], l = [...live.childNodes];
  if (o.length !== l.length) { live.replaceChildren(...n.map((x) => doc.importNode(x, true))); n.length && [...live.childNodes].forEach((c) => initGalleries(c, doc.defaultView)); return; }
  let a = 0;
  while (a < o.length && a < n.length && o[a].isEqualNode(n[a])) a++;
  let b = 0;
  while (b < o.length - a && b < n.length - a && o[o.length - 1 - b].isEqualNode(n[n.length - 1 - b])) b++;
  const om = o.slice(a, o.length - b), nm = n.slice(a, n.length - b), lm = l.slice(a, l.length - b);
  const same = om.length === nm.length && om.every((x, k) => x.nodeType === 1 && nm[k].nodeType === 1 &&
    x.tagName === nm[k].tagName && CONTAINERS.has(x.tagName) && !x.classList.contains("gallery"));
  if (same) {
    om.forEach((x, k) => {
      for (const at of [...lm[k].attributes]) if (!nm[k].hasAttribute(at.name)) lm[k].removeAttribute(at.name);
      for (const at of [...nm[k].attributes]) lm[k].setAttribute(at.name, at.value);
      patch(x, nm[k], lm[k], doc);
    });
    return;
  }
  const ref = b ? l[l.length - b] : null;
  lm.forEach((x) => x.remove());
  nm.forEach((x) => { const c = doc.importNode(x, true); live.insertBefore(c, ref); initGalleries(c, doc.defaultView); });
}

function applyBody(body, css) {
  const doc = view.contentDocument, prose = doc && doc.querySelector(".prose");
  if (!prose || !lastRaw) return showPreview(false);
  const neu = document.createElement("template");
  neu.innerHTML = body;
  patch(lastRaw.content, neu.content, prose, doc);
  lastRaw = neu;
  if (css) {
    let st = doc.getElementById("mjx-live");
    if (!st) { st = doc.createElement("style"); st.id = "mjx-live"; doc.head.appendChild(st); }
    if (st.textContent !== css) st.textContent = css;
  }
}

async function save() {
  if (!name) return;
  if (saving) { dirty = true; return; }
  clearTimeout(timer);
  saving = true; dirty = false;
  setStatus("rendering...");
  const d = await api("/api/save", {name, text: src.value, mtime});
  saving = false;
  if (d.conflict) {
    setStatus("changed on disk", "err");
    log.textContent = "The file was edited outside this page since it was loaded. Nothing was saved.\n" +
      "Copy your text if you need it, then pick the post again to reload it from disk.";
    log.style.display = "block"; dirty = true; return;
  }
  mtime = d.mtime;
  if (d.ok) {
    log.style.display = "none";
    if (d.reload) showPreview(false); else applyBody(d.body, d.css);
    setStatus(dirty ? "unsaved" : "saved", dirty ? "" : "ok");
  } else { log.textContent = d.log; log.style.display = "block"; setStatus("error (text saved)", "err"); }
  if (dirty) schedule();
}

function schedule() { clearTimeout(timer); timer = setTimeout(save, 400); }

src.addEventListener("input", () => { dirty = true; setStatus("unsaved"); schedule(); });
src.addEventListener("keydown", (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === "s") { e.preventDefault(); save(); }
  if (e.key === "Tab") { e.preventDefault(); document.execCommand("insertText", false, "  "); }
});
$("save").onclick = save;
file.onchange = async () => { if (dirty) await save(); load(file.value); };
window.addEventListener("beforeunload", (e) => { if (dirty) { e.preventDefault(); e.returnValue = ""; } });

// Draggable split between editor and preview.
$("drag").addEventListener("mousedown", (e) => {
  e.preventDefault(); view.style.pointerEvents = "none";
  const move = (m) => document.body.style.setProperty("--split", Math.min(85, Math.max(15, m.clientX / innerWidth * 100)) + "%");
  const up = () => { removeEventListener("mousemove", move); removeEventListener("mouseup", up); view.style.pointerEvents = ""; };
  addEventListener("mousemove", move); addEventListener("mouseup", up);
});

(async () => {
  const posts = await api("/api/posts");
  for (const p of posts) file.add(new Option(p, p));
  let want = null;
  try { want = localStorage.getItem("editor.post"); } catch (e) {}
  if (!posts.includes(want)) want = posts[0];
  file.value = want; load(want);
})();
</script>
</body></html>
"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(OUT), **k)

    def log_message(self, *a):
        pass

    def reply(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        path, _, query = self.path.partition("?")
        if path in ("/edit", "/edit/"):
            body = PAGE.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/api/posts":
            self.reply(sorted((p.name for p in BLOG.glob("*.md")), reverse=True))
        elif path == "/api/post":
            from urllib.parse import parse_qs
            p = post_path(parse_qs(query)["name"][0])
            front_seen[p.name] = front_matter(p.read_text(encoding="utf-8"))
            self.reply({"text": p.read_text(encoding="utf-8"), "mtime": str(p.stat().st_mtime_ns)})
        else:
            super().do_GET()

    def do_POST(self):
        if self.path != "/api/save":
            return self.reply({"error": "not found"}, 404)
        d = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        p = post_path(d["name"])
        if str(p.stat().st_mtime_ns) != d["mtime"]:
            return self.reply({"conflict": True})
        p.write_text(d["text"], encoding="utf-8")
        mtime = str(p.stat().st_mtime_ns)
        front = front_matter(d["text"])
        if front != front_seen.get(d["name"]):
            # Title, authors or date changed: the page header needs a real rebuild.
            front_seen[d["name"]] = front
            ok, log = build()
            return self.reply({"ok": ok, "log": log, "mtime": mtime, "reload": True})
        r = render_body(p)
        schedule_full_build()
        if "error" in r:
            return self.reply({"ok": False, "log": r["error"], "mtime": mtime})
        self.reply({"ok": True, "mtime": mtime, **r})

if __name__ == "__main__":
    ok, log = build()
    print(log)
    print(f"editor at http://localhost:{PORT}/edit  (Ctrl+C to stop)")
    http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
