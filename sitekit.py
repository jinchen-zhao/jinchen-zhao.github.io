"""Shared by the personal site and the LGW Lab blog: dark mode for SVG figures.

The source of truth is this file in the personal site. The lab blog keeps an exact copy (its sync_shared.py), because
each site builds from its own repository. Edit here, then sync.

An SVG drawn by the schematic-figure skill (or a publication thumbnail) uses one shared palette. theme_svg injects CSS
into the SVG, so the drawing follows the reader's OS theme even inside <img>:
  - light mode maps the palette hexes in `light` (deeper role hues),
  - dark mode maps the palette hexes in `dark`, flips the lightness of every other colour (keeping its hue),
    and gives the figure's background rectangle the page tone `page`.
"""
import colorsys
import re


def recolour(mapping):
    return "".join(
        f'[fill="{k}" i]{{fill:{v}}}[stroke="{k}" i]{{stroke:{v}}}[stop-color="{k}" i]{{stop-color:{v}}}'
        for k, v in mapping.items())


def flip(hexc):
    """Dark-mode colour for a colour off the palette: flip the lightness, keep the hue. Near-black ink becomes
    near-white, pale fills become deep tones just above the page, and strong mid-tone accents are lifted a little."""
    h = hexc.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hue, light, sat = colorsys.rgb_to_hls(r, g, b)
    if sat > 0.35 and 0.3 < light < 0.7:
        light = min(light + 0.12, 0.78)
    else:
        light = 0.11 + (1 - light) * 0.82    # 1 -> page tone, 0 -> 0.93
    r, g, b = colorsys.hls_to_rgb(hue, light, sat)
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def off_palette(svg, dark):
    found = set(re.findall(r'(?:fill|stroke|stop-color)="(#[0-9A-Fa-f]{6}|#[0-9A-Fa-f]{3})"', svg))
    known = {k.upper() for k in dark}
    return {c: flip(c) for c in sorted(found) if c.upper() not in known}  # sorted: the same build twice gives the same bytes


def theme_svg(path, dark, light, page):
    """Add the light and dark colour rules to the SVG at path. Dark rules come last, so they win in dark mode."""
    svg = path.read_text(encoding="utf-8")
    general = recolour(off_palette(svg, dark)) + f'rect[data-role="background"][fill]{{fill:{page}}}'
    style = f"<style>{recolour(light)}@media (prefers-color-scheme: dark){{{general}{recolour(dark)}}}</style>"
    svg = re.sub(r"(<svg\b[^>]*>)", lambda m: m.group(1) + style, svg, count=1)
    path.write_text(svg, encoding="utf-8")
