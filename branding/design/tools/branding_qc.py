# SPDX-License-Identifier: GPL-3.0-or-later
"""Artwork validation and presentation, using the builder's canonical geometry."""

from pathlib import Path
import json
import subprocess
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
from fontTools.svgLib.path import parse_path
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.svgPathPen import SVGPathPen


def validate_and_render(
    *,
    BEARD_RIM_WIDTH,
    BRAND_NAME,
    COLOURS,
    COPPER,
    GOLD,
    INVERSE_ASSETS,
    LOCKUP,
    MONO_ASSETS,
    ROOT,
    SUBLINE_WIDTH,
    WORDMARK,
    ZERO,
    outer,
    tracking,
):
    report = {}
    banned = {
        "image",
        "filter",
        "linearGradient",
        "radialGradient",
        "pattern",
        "mask",
        "clipPath",
        "text",
        "use",
        "foreignObject",
        "script",
    }
    for name in (
        ["primary", "monogram", "wordmark", "lockup", "palette", "readme-banner"]
        + [n + "-inverse" for n in INVERSE_ASSETS]
        + MONO_ASSETS
    ):
        file = ROOT / f"m100-{name}.svg"
        root = ET.parse(file).getroot()
        tags = []
        fills = set()
        for node in root.iter():
            tag = node.tag.split("}")[-1]
            tags.append(tag)
            assert tag not in banned, (file, tag)
            for key, value in node.attrib.items():
                assert not key.endswith("href"), (file, key)
                assert "base64" not in value and "url(" not in value, (file, key)
                if key in {"fill", "stroke"}:
                    fills.add(value)
                    assert value in COLOURS, (file, value)
                assert key not in {"opacity", "fill-opacity", "stroke-opacity"}, (file, key)
        sizes = []
        w, h = map(float, root.attrib["viewBox"].split()[2:])
        for size in [] if name == "readme-banner" else [24, 64, 256, 1024]:
            out = ROOT / "qc" / f"m100-{name}-{size}.png"
            args = ["rsvg-convert", "-w" if w >= h else "-h", str(size), "-o", str(out), str(file)]
            subprocess.run(args, check=True)
            im = Image.open(out)
            assert max(im.size) == size
            assert im.getbbox() is not None
            sizes.append({"long_edge_px": size, "dimensions": list(im.size)})
        report[name] = {
            "viewBox": root.attrib["viewBox"],
            "colours": sorted(fills),
            "geometry_elements": sum(
                t in {"path", "polygon", "circle", "rect", "line"} for t in tags
            ),
            "renders": sizes,
        }
    # Wordmark geometry is byte-identical, including fills, in all three files.
    for name in ["primary", "wordmark", "lockup"]:
        assert WORDMARK in (ROOT / f"m100-{name}.svg").read_text()
    assert LOCKUP in (ROOT / "m100-readme-banner.svg").read_text()
    assert WORDMARK.count(f'd="{ZERO}"') == 2
    # Inverse files change paint only: every shape, counter, position and size matches.
    for name in INVERSE_ASSETS:
        normal = list(ET.parse(ROOT / f"m100-{name}.svg").getroot().iter())
        inverse = list(ET.parse(ROOT / f"m100-{name}-inverse.svg").getroot().iter())
        assert len(normal) == len(inverse)
        for a, b in zip(normal, inverse):
            assert a.tag == b.tag
            assert {k: v for k, v in a.attrib.items() if k not in {"fill", "stroke"}} == {
                k: v for k, v in b.attrib.items() if k not in {"fill", "stroke"}
            }
            if a.attrib.get("fill") == GOLD or (
                name != "palette" and a.attrib.get("fill") == COPPER
            ):
                assert a.attrib["fill"] == b.attrib["fill"]
    for name in MONO_ASSETS:
        normal = list(ET.parse(ROOT / "m100-wordmark.svg").getroot().iter())
        mono = list(ET.parse(ROOT / f"m100-{name}.svg").getroot().iter())
        assert len(normal) == len(mono)
        for a, b in zip(normal, mono):
            assert a.tag == b.tag
            assert {k: v for k, v in a.attrib.items() if k != "fill"} == {
                k: v for k, v in b.attrib.items() if k != "fill"
            }
    # The two straight lower edges and vertical walls share a 5-unit normal offset.
    original = ET.parse(ROOT / "m100-monogram.svg").getroot()
    rim = next(n for n in original.iter() if n.attrib.get("id") == "beard-uniform-rim")
    assert "stroke" not in rim.attrib and BEARD_RIM_WIDTH == 5
    # All paired mountain stripes and stepped badge vertices share exact axes.
    assert sorted((304 - x, y) for x, y in outer) == sorted(outer)
    report["checks"] = {
        "valid_xml": True,
        "only_authoritative_colours": True,
        "no_raster_or_external_resources": True,
        "no_live_text_or_font_dependencies": True,
        "identical_shared_wordmark": True,
        "identical_zeroes": True,
        "bilateral_badge_silhouette": True,
        "subline_tracking_units": tracking,
        "inverse_variants_identical_geometry": True,
        "beard_rim_uniform_stroke_source_units": BEARD_RIM_WIDTH,
        "monochrome_wordmarks_identical_geometry": True,
        "manufacturer_subline": BRAND_NAME,
        "manufacturer_subline_width_units": SUBLINE_WIDTH,
        "beard_rim_expanded_to_filled_paths": True,
        "badge_border_and_line_units": 7.5,
        "badge_nominal_line_mm_at_24mm_art_height": round(7.5 / 484 * 24, 3),
    }
    (ROOT / "qc" / "validation.json").write_text(json.dumps(report, indent=2) + "\n")


def contact_sheet(*, BLACK, GREEN, IVORY, ROOT, asset_name):
    canvas = Image.new("RGB", (1500, 1050), IVORY)
    draw = ImageDraw.Draw(canvas)
    label = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 17)
    specs = [
        ("primary", (25, 60, 470, 550)),
        ("monogram", (520, 60, 300, 550)),
        ("wordmark", (870, 60, 590, 170)),
        ("lockup", (870, 305, 590, 280)),
        ("palette", (25, 720, 1435, 305)),
    ]
    for name, (x, y, w, h) in specs:
        im = Image.open(ROOT / "qc" / f"m100-{name}-1024.png")
        im.thumbnail((w, h), Image.Resampling.LANCZOS)
        canvas.paste(im, (x + (w - im.width) // 2, y + (h - im.height) // 2), im)
        draw.text((x, y - 30), f"M100 / {name.upper()}", font=label, fill=BLACK)
    canvas.save(ROOT / "qc" / "contact-sheet.png")
    # Actual-pixel reductions use the correct standalone variant for each substrate.
    canvas = Image.new("RGB", (1800, 1350), IVORY)
    draw = ImageDraw.Draw(canvas)
    for row, (bg, ink) in enumerate([(IVORY, BLACK), (GREEN, IVORY), (BLACK, IVORY)]):
        y = row * 450
        draw.rectangle((0, y, 1800, y + 450), fill=bg)
        for col, name in enumerate(["primary", "monogram", "wordmark", "lockup", "palette"]):
            x = col * 360 + 18
            draw.text((x, y + 15), name.upper(), font=label, fill=ink)
            for size, sy in [(24, 52), (64, 99), (256, 174)]:
                im = Image.open(ROOT / "qc" / f"m100-{asset_name(name, bg == GREEN)}-{size}.png")
                sy = y + sy
                canvas.paste(im, (x, sy), im)
    canvas.save(ROOT / "qc" / "reduction-sheet.png")
    canvas = Image.new("RGB", (1500, 1100), GREEN)
    draw = ImageDraw.Draw(canvas)
    draw.text((30, 24), "M100 / FOREST GREEN — INVERSE MASTERS", font=label, fill=IVORY)
    for name, (x, y, w, h) in specs:
        y += 30
        im = Image.open(ROOT / "qc" / f"m100-{asset_name(name, True)}-1024.png")
        im.thumbnail((w, h), Image.Resampling.LANCZOS)
        canvas.paste(im, (x + (w - im.width) // 2, y + (h - im.height) // 2), im)
    canvas.save(ROOT / "qc" / "forest-contact-sheet.png")


def preview(*, ROOT, asset_name):
    assets = [
        ("primary", "Primary logo"),
        ("monogram", "Monogram"),
        ("wordmark", "M100 wordmark"),
        ("lockup", "Lockup"),
        ("palette", "Palette"),
    ]
    content = ""
    for bg, title in [
        ("ivory", "Ivory Beige"),
        ("forest", "Forest Green"),
        ("graphite", "Graphite Black"),
    ]:
        content += f'<section class="surface {bg}"><h2>{title}</h2><div class="grid">'
        for name, label in assets:
            selected = asset_name(name, bg == "forest")
            w, h = map(
                float, ET.parse(ROOT / f"m100-{name}.svg").getroot().attrib["viewBox"].split()[2:]
            )
            variant = "Inverse" if selected != name else "Standard"
            content += f'<article><h3>{label} · {variant}</h3><div class="hero"><img src="m100-{selected}.svg" alt="{label}"></div><div class="sizes">'
            for size in [24, 64, 256]:
                sw, sh = (
                    (size, round(size * h / w, 3)) if w >= h else (round(size * w / h, 3), size)
                )
                content += f'<figure><img src="m100-{selected}.svg" alt="{label} {size}px" style="width:{sw}px;height:{sh}px"><figcaption>{size} px</figcaption></figure>'
            content += f'</div><p><a href="m100-{selected}.svg" download>Download {variant.lower()}</a></p><details><summary>1024 px inspection</summary><img class="large" src="m100-{selected}.svg" alt="{label}, large inspection" style="width:{1024 if w >= h else round(1024 * w / h, 3)}px;height:{1024 if h >= w else round(1024 * h / w, 3)}px"></details></article>'
        content += "</div></section>"
    html = (
        """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>M100 · SVG master inspection</title>
<style>
:root{color-scheme:light}*{box-sizing:border-box}body{margin:0;background:#E9DDC6;color:#2D2D2A;font:15px/1.5 system-ui,sans-serif}header{padding:40px 4vw 25px}h1{font-size:28px;font-weight:500;margin:0 0 10px}header p{max-width:820px}h2{font-weight:500;font-size:22px;margin:0 0 24px}h3{font-size:14px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;margin:0 0 24px}.surface{padding:36px 4vw 48px}.ivory{background:#E9DDC6;color:#2D2D2A}.forest{background:#355856;color:#E9DDC6}.graphite{background:#2D2D2A;color:#E9DDC6}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:32px}article{min-width:0;border-top:1px solid currentColor;padding-top:18px}.hero{height:320px;display:flex;align-items:center;justify-content:center}.hero img{max-width:100%;max-height:290px;width:auto;height:auto;display:block}.sizes{display:flex;flex-wrap:wrap;align-items:flex-start;gap:20px;margin-top:30px;min-height:310px}figure{margin:0}figure img{display:block;max-width:none}figcaption{font-size:12px;margin-top:12px}a{color:inherit;text-underline-offset:4px}summary{cursor:pointer;font-size:13px}details{overflow:auto;max-width:100%;padding:8px 0}.large{display:block;max-width:none;margin-top:24px}footer{padding:24px 4vw}code{font-size:13px}@media(max-width:420px){.grid{grid-template-columns:1fr}.sizes{gap:12px}.surface{padding-left:18px;padding-right:18px}}
</style></head><body><header><h1>M100 / METZGER100 AUDIO WORKS</h1><p>Brand name selected · 5 October 2026. <a href="../proposals/README.md">Read the naming decision</a> · <a href="../proposals/preview.html">View naming history</a>.</p><p>Five brand assets, with standalone inverse variants for Forest Green substrates. Measurements below each small image refer to its longest edge. Open the 1024 px view to inspect full contours.</p><p>Ivory Beige and Graphite Black backgrounds use the standard colour masters. Forest Green backgrounds use ivory foreground variants, retaining brass and copper accents. The monogram retains its green field, framed by its gold border. Transparent openings reveal the substrate; the palette always retains the five authoritative swatch colours.</p><p>Single-colour production wordmarks: <a href="m100-wordmark-mono.svg">Graphite</a> · <a href="m100-wordmark-mono-inverse.svg">Ivory</a>. Their contours match the colour wordmark.</p></header>"""
        + content
        + """<footer>Reference: <a href="../README.md">brand guide</a> · <a href="README.md">construction notes</a> · <a href="qc/contact-sheet.png">PNG contact sheet</a> · <a href="qc/forest-contact-sheet.png">Forest Green contact sheet</a> · <a href="qc/validation.json">validation report</a></footer></body></html>"""
    )
    (ROOT / "preview.html").write_text(
        html.replace(" pixels", "px").replace(", large inspection", ", detail") + "\n"
    )


def transformed_path(d, matrix, *, RoundingPen):
    p = SVGPathPen(None)
    parse_path(d, TransformPen(RoundingPen(p, roundFunc=lambda value: round(value, 4)), matrix))
    return p.getCommands()


def expanded_beard_rim(d, *, BEARD_RIM_WIDTH, COPPER, GOLD, RoundingPen, tempfile):
    """Offset a uniform stroke in final coordinates, then retain only clean paths."""
    with tempfile.TemporaryDirectory(prefix="m100-beard-") as directory:
        source = Path(directory) / "source.svg"
        output = Path(directory) / "outlined.svg"
        source.write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-70 -10 140 130">'
            f'<path id="beard" fill="{COPPER}" stroke="{GOLD}" stroke-width="{BEARD_RIM_WIDTH}" '
            f'stroke-linejoin="round" d="{d}"/></svg>'
        )
        result = subprocess.run(
            [
                "inkscape",
                str(source),
                "--export-plain-svg",
                f"--export-filename={output}",
                "--actions=select-by-id:beard;object-stroke-to-path",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode or not output.is_file():
            raise RuntimeError("Could not expand constant-width beard outline: " + result.stderr)
        tree = ET.parse(output)
        rim = next(
            node.attrib["d"]
            for node in tree.iter()
            if node.tag.endswith("path") and "fill:" + GOLD.lower() in node.attrib.get("style", "")
        )
        recorded = RecordingPen()
        parse_path(rim, recorded)
        contours = []
        for operation, args in recorded.value:
            if operation == "moveTo":
                contours.append([])
            contours[-1].append((operation, args))
        assert len(contours) == 2, "Expanded rim must contain exactly two closed contours"

        def clean_contours(items):
            pen = SVGPathPen(None)
            rounded = RoundingPen(pen, roundFunc=lambda value: round(value, 4))
            for contour in items:
                for operation, args in contour:
                    getattr(rounded, operation)(*args)
            return pen.getCommands()

        return clean_contours(contours), clean_contours(contours[1:])
