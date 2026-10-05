#!/usr/bin/env python3
"""Build reproducible naming comparisons from the shared vector artwork."""
from pathlib import Path
import json
import runpy
import shutil
import subprocess
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

DESIGN = Path(__file__).resolve().parents[1]
PROPOSALS = DESIGN.parent / 'proposals'
ARCHIVE = DESIGN.parent / 'archive' / '2026-10-04-microphones'
PROPOSALS.mkdir(exist_ok=True)
# Reuse the actual lettering conversion and source geometry, rather than redraw.
shared = runpy.run_path(str(DESIGN / 'tools' / 'build_branding.py'))
outlined_text = shared['outlined_text']
ET.register_namespace('', 'http://www.w3.org/2000/svg')
NS = '{http://www.w3.org/2000/svg}'
GREEN, GOLD, COPPER, IVORY, BLACK = (shared[n] for n in ['GREEN', 'GOLD', 'COPPER', 'IVORY', 'BLACK'])

alternatives = [
    ('audio', 'METZGER100 AUDIO', 20, 360),
    ('studio-equipment', 'METZGER100 STUDIO EQUIPMENT', 18, 480),
]
report = {}
for slug, name, cap, width in alternatives:
    root = ET.parse(DESIGN / 'm100-lockup.svg').getroot()
    root.find(NS + 'title').text = f'M100 / {name} — naming alternative'
    root.find(NS + 'desc').text = 'Comparison-only proposal. Original M100 lettering and Art Deco divider, with an outlined alternative brand name.'
    old = next(n for n in root if n.attrib.get('id') == 'outlined-subline')
    label, tracking = outlined_text(name, cap, width, 250, 183, GREEN, 'outlined-subline')
    root.remove(old)
    # Parse in an SVG namespace so the standalone XML remains correct.
    wrapped = ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{label}</svg>')
    root.append(wrapped[0])
    target = PROPOSALS / f'm100-lockup-{slug}.svg'
    ET.ElementTree(root).write(target, encoding='UTF-8', xml_declaration=True)
    original = ET.parse(DESIGN / 'm100-lockup.svg').getroot()
    for a, b in zip(list(original)[2:-1], list(root)[2:-1]):
        assert ET.tostring(a) == ET.tostring(b), 'Alternative modified non-subline geometry'
    for n in root.iter():
        assert n.tag.split('}')[-1] in {'svg', 'title', 'desc', 'g', 'path', 'polygon'}
        assert not any(k.endswith('href') for k in n.attrib)
        assert n.attrib.get('fill', GREEN) in {GREEN, GOLD, COPPER, IVORY, BLACK}
    report[slug] = {'name': name, 'cap_height_units': cap, 'subline_width_units': width, 'tracking_units': tracking,
                    'valid_vector_xml': True, 'shared_geometry_preserved': True}

# Preserve the existing comparison link as an exact copy of the selected master.
shutil.copyfile(DESIGN / 'm100-lockup.svg', PROPOSALS / 'm100-lockup-audio-works.svg')
report['audio-works'] = {'name': shared['BRAND_NAME'], 'status': 'selected',
                        'cap_height_units': 20, 'subline_width_units': shared['SUBLINE_WIDTH'],
                        'tracking_units': shared['tracking'], 'identical_to_active_master': True}

cards = [
    ('PREVIOUS', 'Metzger100 Microphones', ARCHIVE / 'm100-lockup.svg', 'A microphone-only manufacturer subline.'),
    ('SELECTED', 'Metzger100 Audio Works', DESIGN / 'm100-lockup.svg', 'Independent workshop identity across audio equipment.'),
    ('EARLIER PROPOSAL', 'Metzger100 Audio', PROPOSALS / 'm100-lockup-audio.svg', 'The shorter name considered before Audio Works.'),
    ('ALTERNATIVE', 'Metzger100 Studio Equipment', PROPOSALS / 'm100-lockup-studio-equipment.svg', 'Explicit scope, with a longer name.'),
]

def relative(file):
    import os
    return os.path.relpath(file, PROPOSALS)

content = ''.join(
    f'<article class="card {"recommended" if eyebrow == "SELECTED" else ""}">'
    f'<p class="eyebrow">{eyebrow}</p><h2>{name}</h2>'
    f'<img class="lockup" src="{relative(file)}" alt="M100 above {name}">'
    f'<p>{description}</p><a href="{relative(file)}">Open outlined SVG</a></article>'
    for eyebrow, name, file, description in cards)

html = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>M100 · Audio Works naming decision</title><style>
*{box-sizing:border-box}body{margin:0;background:#E9DDC6;color:#2D2D2A;font:16px/1.5 system-ui,sans-serif}
main{max-width:1280px;margin:auto;padding:36px 28px 60px}h1{font-weight:500;font-size:clamp(28px,4vw,44px);margin:8px 0 16px}h2{font-weight:500;font-size:23px;margin:5px 0 26px}.intro{max-width:830px}.eyebrow{text-transform:uppercase;letter-spacing:.14em;font-size:12px;margin:0;color:#355856}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px;margin:32px 0}.card{padding:24px;border:1px solid #B89255;min-width:0}.recommended{border:3px solid #355856;padding:22px}.lockup{display:block;width:100%;height:210px;object-fit:contain}a{color:#355856;text-underline-offset:4px}.equipment{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;margin:20px 0}.device{background:#2D2D2A;color:#E9DDC6;padding:24px 20px}.device img{display:block;width:155px;max-width:100%;margin-bottom:30px}.device p{font-size:14px}.device strong{display:block;font-size:18px;font-weight:500}.note{font-size:14px;max-width:840px}.links{display:flex;flex-wrap:wrap;gap:16px}.compact{display:block;width:340px;max-width:100%;margin:24px 0}@media(max-width:700px){.grid,.equipment{grid-template-columns:1fr}.lockup{height:auto}main{padding:24px 18px}.device{padding:22px}}
</style></head><body><main><p class="eyebrow">Brand name selected · 5 October 2026</p><h1>M100, from signal to sound.</h1><p class="intro">Selected full name: <strong>METZGER100 AUDIO WORKS</strong>. Keep the existing M100 mark, mountain, beard and colours. <strong>Audio electronics &amp; acoustics.</strong> Use <strong>M100 + family + equipment identifier + technical variant</strong>, with a plain functional descriptor explaining what each device does.</p><p class="links"><a href="README.md">Read the naming decision</a><a href="product-naming.md">Extended families and model naming proposal</a><a href="../README.md">Brand guide</a><a href="../design/preview.html">All artwork and backgrounds</a></p><div class="grid">'''+content+'''</div><h2>One mark. Different equipment.</h2><p class="note">Conceptual identity placements. The scope includes microphones, preamps, amplifiers, loudspeakers and other audio equipment; future projects, names and technical variants remain open.</p><div class="equipment"><div class="device"><img src="../design/m100-wordmark-mono-inverse.svg" alt="M100 in ivory"><strong>MERIDIAN</strong><p>Condenser microphone</p></div><div class="device"><img src="../design/m100-wordmark-mono-inverse.svg" alt="M100 in ivory"><strong>FUTURE PRODUCT</strong><p>Analog microphone preamp</p></div><div class="device"><img src="../design/m100-wordmark-mono-inverse.svg" alt="M100 in ivory"><strong>FUTURE PRODUCT</strong><p>Audio interface</p></div></div><p class="note">The horizontal wordmark suits electronics panels. The tall badge remains useful on microphone bodies and vertical markings. Functional labels should stay easy to read.</p><h2>Precision. Character. Built to last.</h2><p class="note">Suggested tagline. Precision and repairability belong to the whole brand; warmth or coloration belongs in each product's design brief. The Art Deco character stays in the identity.</p><img class="compact" src="../design/m100-wordmark-mono.svg" alt="M100 single-colour graphite wordmark"><p class="note">New single-colour production treatment: the existing M100 contours in one ink, for panel printing, engraving and PCB marking. Full-colour SVG background rules remain in the artwork guide.</p></main></body></html>'''
(PROPOSALS / 'preview.html').write_text(html)

# A static comparison artifact for direct review in chat, generated from the SVGs.
canvas = Image.new('RGB', (1440, 1320), IVORY)
draw = ImageDraw.Draw(canvas)
font = '/usr/share/fonts/TTF/DejaVuSans.ttf'
title_font, heading_font, text_font, small_font = [ImageFont.truetype(font, size) for size in [35, 25, 20, 16]]
draw.text((48, 30), 'M100 / AUDIO WORKS IDENTITY', font=title_font, fill=GREEN)
draw.text((48, 86), 'One identity for recording, amplification and playback.', font=text_font, fill=BLACK)
draw.text((48, 122), 'Brand name selected / 5 October 2026', font=small_font, fill=BLACK)
for i, (eyebrow, name, file, description) in enumerate(cards):
    x, y = 48 + (i % 2) * 690, 184 + (i // 2) * 390
    draw.rectangle((x, y, x + 654, y + 362), outline=GREEN if i == 1 else GOLD, width=3 if i == 1 else 1)
    draw.text((x + 22, y + 18), eyebrow, font=small_font, fill=GREEN)
    draw.text((x + 22, y + 47), name, font=heading_font, fill=BLACK)
    raster = PROPOSALS / f'comparison-{i}.png'
    subprocess.run(['rsvg-convert', '-w', '580', '-o', str(raster), str(file)], check=True)
    im = Image.open(raster)
    canvas.paste(im, (x + (654 - im.width) // 2, y + 93), im)
    draw.text((x + 22, y + 332), description, font=small_font, fill=BLACK)
    raster.unlink()
draw.text((48, 978), 'Precision. Character. Built to last.', font=heading_font, fill=GREEN)
draw.text((48, 1022), 'Same brand mark. Family names, equipment types and technical variants.', font=text_font, fill=BLACK)
wordmark = Image.open(DESIGN / 'qc' / 'm100-wordmark-mono-inverse-1024.png')
wordmark.thumbnail((210, 70), Image.Resampling.LANCZOS)
for i, (name, category) in enumerate([('MERIDIAN', 'Condenser microphone'), ('FUTURE PRODUCT', 'Analog microphone preamp'), ('FUTURE PRODUCT', 'Audio interface')]):
    x, y = 48 + i * 460, 1070
    draw.rectangle((x, y, x + 424, y + 188), fill=BLACK)
    canvas.paste(wordmark, (x + 24, y + 20), wordmark)
    draw.text((x + 24, y + 99), name, font=text_font, fill=IVORY)
    draw.text((x + 24, y + 139), category, font=small_font, fill=IVORY)
draw.text((48, 1282), 'Category placements are concepts; future products are unassigned.', font=small_font, fill=BLACK)
canvas.save(PROPOSALS / 'branding-comparison.png')
(PROPOSALS / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
print('Built naming-history artwork and previews with Audio Works marked as selected.')
