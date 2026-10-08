"""Plot style for figures in blog posts.

    import sys; sys.path.insert(0, "<website>/tools")
    from plotstyle import W, F, SKILL, apply, save_svg
    apply()                                   # sizes, font and colours for every later plot
    fig, ax = plt.subplots(figsize=(W, W * 0.6))
    ...
    save_svg(fig, "content/blog/<slug>/plot_x.svg")

The blog column is 704 CSS px wide and body text is 18 px. A plot drawn W inches wide shows 1 pt as about 1.53 px.
So text set to TEXT_PT renders at 15 px and panel titles at 16 px. These are the sizes of the schematic-figure skill's
drawings, so plots and schematics read as one set. Draw every plot at width W, never narrower: the page stretches a
narrow plot and its text grows with it. Keep the height between 0.5 W and 0.65 W where the content allows.
"""
import re
from pathlib import Path

W = 6.4
TEXT_PT, TITLE_PT = 9.8, 10.5
# Colours: with and without an intervention, a reference (for example a published figure), ink, muted ink, grid.
SKILL, PLAIN, PUB, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#6b6a64", "#1f1f1e", "#76756d", "#e4e3dc"
# Dark mode: the SVGs are transparent and carry this colour map, the way the site themes the schematics.
DARK = {INK: "#e6e4de", MUTED: "#a8a59c", GRID: "#3a3935", PUB: "#9c9a91", "#ffffff": "#1d1c1a"}


def F(x):
    """Return a standard size: the title size for 9 pt or more, else the text size."""
    return TITLE_PT if x >= 9 else TEXT_PT


def apply():
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": TEXT_PT, "axes.titlesize": TITLE_PT, "axes.labelsize": TEXT_PT, "xtick.labelsize": TEXT_PT,
        "ytick.labelsize": TEXT_PT, "legend.fontsize": TEXT_PT, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
        "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK, "axes.spines.top": False,
        "axes.spines.right": False, "svg.fonttype": "none"})


def themed_svg(path):
    """Add the dark-mode colour map to a saved SVG."""
    path = Path(path)
    svg = path.read_text(encoding="utf-8")
    rules = "".join(f'[style*="fill: {a}"]{{fill:{b}!important}}[style*="stroke: {a}"]{{stroke:{b}!important}}'
                    for a, b in DARK.items())
    svg = re.sub(r"(<svg\b[^>]*>)", lambda m: m.group(1) + f"<style>@media (prefers-color-scheme: dark){{{rules}}}</style>",
                 svg, count=1)
    path.write_text(svg, encoding="utf-8")


def save_svg(fig, path, png=True):
    """Save a transparent, dark-mode-ready SVG (and a white PNG beside it for review). Never crop with bbox_inches:
    cropping changes the width, and so the text size on the page."""
    import matplotlib.pyplot as plt
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, transparent=True)
    themed_svg(path)
    if png:
        fig.savefig(path.with_suffix(".png"), dpi=200, facecolor="white")
    plt.close(fig)
