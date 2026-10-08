"""Check the figures of a blog post for text size and overlaps.

    python tools/figaudit.py content/blog/2026-10-07-slug.md          # text size of every SVG the post shows
    python tools/figaudit.py --run plots.py other_plots.py             # overlaps in matplotlib scripts

Text size: the blog column is 704 CSS px and body text is 18 px. Each SVG is scaled to the column, so its text renders
at (font size) x 704 / (SVG width). The check lists the smallest, the middle and the largest text of each figure and
flags a figure with text below MIN_PX or above MAX_PX. It reads font sizes from the SVG source (font-size attributes,
style properties and CSS font shorthands), so it works for matplotlib output and for the schematic-figure skill.

Overlaps: --run executes each script with matplotlib's Figure.savefig wrapped. Before a figure's first save, the
wrapper measures every visible text item and legend box. It reports two text items that overlap, and a data mark
(a scatter point, a line vertex, a bar area) under a text item or a legend. White text inside its own bar and pale
background bands (alpha below 0.3) are allowed. The audit first checks itself on a figure with known overlaps and stops
if it misses one, so "no overlaps found" can be trusted.
"""
import argparse
import itertools
import re
import runpy
import statistics as st
import sys
from pathlib import Path

COL, MIN_PX, MAX_PX = 704, 12, 20


# ------------------------------------------------------------------ text size
def svg_sizes(path):
    s = Path(path).read_text(encoding="utf-8")
    vb = re.search(r'viewBox="[\d.\s-]*?\s([\d.]+)\s+([\d.]+)"', s)
    width = float(vb.group(1)) if vb else float(re.search(r'width="([\d.]+)', s).group(1))
    sizes = [float(x) for x in re.findall(r'font-size[:=]\s*"?([\d.]+)', s)]
    sizes += [float(x) for x in re.findall(r'font:\s*(?:[a-z-]+\s+)*([\d.]+)px', s)]
    return [x * COL / width for x in sizes]


def check_post(md):
    md = Path(md)
    folder = md.parent / md.stem[11:]  # 2026-10-07-slug.md -> slug/
    body = re.sub(r"<!--.*?-->", "", md.read_text(encoding="utf-8"), flags=re.S)
    bad = 0
    print(f"{'figure':32s} text px: min / median / max")
    for name in re.findall(r"\]\(([^)\s]+\.svg)\)", body):
        px = svg_sizes(folder / name)
        if not px:
            print(f"{name:32s} no font sizes found")
            continue
        flag = "" if MIN_PX <= min(px) and max(px) <= MAX_PX else f"   <- outside {MIN_PX}-{MAX_PX} px"
        bad += bool(flag)
        print(f"{name:32s} {min(px):5.1f} / {st.median(px):5.1f} / {max(px):5.1f}{flag}")
    print(f"{bad} figure(s) with text outside {MIN_PX}-{MAX_PX} px")
    return bad


# ------------------------------------------------------------------ overlaps
def check_fig(fig, name):
    import matplotlib
    from matplotlib.collections import PathCollection
    from matplotlib.legend import Legend
    from matplotlib.lines import Line2D
    from matplotlib.patches import Rectangle
    from matplotlib.text import Text
    out = []
    fig.canvas.draw()
    T = [(t.get_text().strip().replace("\n", " ")[:30], t, t.get_window_extent())
         for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()]
    for (a, _, ba), (b, _, bb) in itertools.combinations(T, 2):
        if ba.overlaps(bb):
            out.append(f"{name}: text '{a}' overlaps text '{b}'")
    in_legend = {id(t) for lg in fig.findobj(Legend) for t in lg.get_texts()}
    white = {id(t) for _, t, _ in T if matplotlib.colors.to_hex(t.get_color()) == "#ffffff"}
    boxes = [(s, b) for s, t, b in T if id(t) not in in_legend | white]
    boxes += [("legend", lg.get_window_extent()) for lg in fig.findobj(Legend)]
    pts, bars = [], []
    for ax in fig.axes:
        for a in ax.get_children():
            if not a.get_visible():
                continue
            if isinstance(a, PathCollection) and len(a.get_offsets()):
                pts += list(a.get_offset_transform().transform(a.get_offsets()))
            elif isinstance(a, Line2D) and len(a.get_xydata()) < 200:
                pts += list(a.get_transform().transform(a.get_xydata()))
            elif (isinstance(a, Rectangle) and a is not ax.patch and a.get_width() * a.get_height() != 0
                  and (a.get_alpha() is None or a.get_alpha() >= 0.3)):
                bars.append(a.get_window_extent())
    for s, box in boxes:
        under = any(box.x0 + 1 < p[0] < box.x1 - 1 and box.y0 + 1 < p[1] < box.y1 - 1 for p in pts) or any(
            box.x0 + 1 < b.x1 and b.x0 < box.x1 - 1 and box.y0 + 1 < b.y1 and b.y0 < box.y1 - 1 for b in bars)
        if under:
            out.append(f"{name}: a data mark lies under '{s}'")
    return out


def selftest():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.bar([0], [1])
    ax.text(0, 0.5, "label on the bar")
    ax.text(0, 0.52, "second label")
    ax.legend(["x"], loc="center")
    got = check_fig(fig, "selftest")
    plt.close(fig)
    if not (any("overlaps text" in g for g in got) and any("lies under" in g for g in got)):
        raise SystemExit(f"self-test failed, the audit missed a known overlap: {got}")


def run_scripts(scripts):
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib.figure import Figure
    selftest()
    found, seen, current = [], set(), ["?"]
    orig = Figure.savefig

    def savefig(self, *a, **k):
        if id(self) not in seen:
            seen.add(id(self))
            found.extend(check_fig(self, current[0]))
        return orig(self, *a, **k)

    Figure.savefig = savefig
    for s in scripts:
        current[0] = Path(s).name
        sys.path.insert(0, str(Path(s).resolve().parent))
        runpy.run_path(s, run_name="__main__")
    Figure.savefig = orig
    print("\n".join(sorted(set(found))) or "no overlaps found")
    return len(found)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("post", nargs="?")
    ap.add_argument("--run", nargs="+", metavar="SCRIPT")
    a = ap.parse_args()
    bad = 0
    if a.post:
        bad += check_post(a.post)
    if a.run:
        bad += run_scripts(a.run)
    if not a.post and not a.run:
        ap.print_help()
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
