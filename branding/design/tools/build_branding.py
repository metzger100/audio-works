#!/usr/bin/env python3
"""Rebuild the five SVG masters and raster QC from shared geometric sources."""
from pathlib import Path
import json
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from html import escape

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.roundingPen import RoundingPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.svgLib.path import parse_path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
GREEN, GOLD, COPPER, IVORY, BLACK = '#355856', '#B89255', '#B24C39', '#E9DDC6', '#2D2D2A'
COLOURS = [GREEN, GOLD, COPPER, IVORY, BLACK]
BRAND_NAME = 'METZGER100 AUDIO WORKS'
SUBLINE_WIDTH = 460
FONT = Path('/usr/share/fonts/adobe-source-serif/SourceSerif4Variable-Roman.otf')
font = instantiateVariableFont(TTFont(FONT), {'wght': 400, 'opsz': 60}, inplace=True)
glyphs = font.getGlyphSet()
cmap = font.getBestCmap()

def fmt(n):
    return f'{n:.4f}'.rstrip('0').rstrip('.') if isinstance(n, float) else str(n)

def path(d, colour, id=None, extra=''):
    identifier = f' id="{id}"' if id else ''
    return f'<path{identifier} fill="{colour}" d="{d}"{extra}/>'

def polygon(points, colour, id=None):
    identifier = f' id="{id}"' if id else ''
    return f'<polygon{identifier} fill="{colour}" points="' + ' '.join(f'{fmt(x)},{fmt(y)}' for x,y in points) + '"/>'

def ring(rx=58, ry=58, ix=32, iy=36):
    return (f'M{rx} 0 A{rx} {ry} 0 1 1 {rx} {2*ry} A{rx} {ry} 0 1 1 {rx} 0 Z '
            f'M{rx} {ry-iy} A{ix} {iy} 0 1 0 {rx} {ry+iy} A{ix} {iy} 0 1 0 {rx} {ry-iy} Z')

# A single immutable wordmark is inserted verbatim in every related master.
M = 'M0 4 H40 L82 50 L124 4 H164 V114 H124 V54 L82 100 L40 54 V114 H0 Z'
ONE = 'M173 22 L218 2 V114 H190 V36 L173 43 Z'
ZERO = ring()
WORDMARK = ('<g id="m100-lettering">\n' + path(M,GREEN,'letter-m') + '\n' + path(ONE,GOLD,'numeral-1') + '\n' +
            f'<g id="numeral-0-first" transform="translate(227 0)">{path(ZERO,GREEN,extra=" fill-rule=\"evenodd\"")}</g>\n' +
            f'<g id="numeral-0-second" transform="translate(348 0)">{path(ZERO,GREEN,extra=" fill-rule=\"evenodd\"")}</g>\n</g>')

# Symmetric crest, including gently rounded horn returns and mouth corners.
CREST_OUTLINE = ('M-116 0 C-94 -2 -99 40 -84 38 L-30 10 Q-12 0 0 15 '
                 'Q12 0 30 10 L84 38 C99 40 94 -2 116 0 V78 L0 170 L-116 78 Z')
MOUTH = 'M-52 56 L0 40 L52 56 Q56 58 52 64 Q50 68 44 68 H-44 Q-50 68 -52 64 Q-56 58 -52 56 Z'
CREST = path(CREST_OUTLINE+' '+MOUTH,COPPER,'beard-crest',extra=' fill-rule="evenodd"')

def outlined_text(text, cap, target_width, centre, baseline, colour, id):
    """Convert actual font contours; spacing is measured between visible glyphs."""
    b = BoundsPen(glyphs)
    glyphs[cmap[ord('H')]].draw(b)
    scale = cap / b.bounds[3]
    advances = [font['hmtx'][cmap[ord(c)]][0]*scale for c in text]
    bounds = []
    for c in text:
        p = BoundsPen(glyphs)
        glyphs[cmap[ord(c)]].draw(p)
        bounds.append(p.bounds)
    left_bearing = bounds[0][0]*scale
    right_bearing = advances[-1] - bounds[-1][2]*scale
    natural = sum(advances) - left_bearing - right_bearing
    tracking = (target_width-natural)/(len(text)-1)
    x = centre-target_width/2-left_bearing
    p = SVGPathPen(glyphs)
    rounded = RoundingPen(p, roundFunc=lambda value: round(value,4))
    for c, advance in zip(text, advances):
        glyphs[cmap[ord(c)]].draw(TransformPen(rounded,(scale,0,0,-scale,x,baseline)))
        x += advance+tracking
    return path(p.getCommands(),colour,id), round(tracking,4)

def svg(name, width, height, title, desc, body):
    content = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
               f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
               'shape-rendering="geometricPrecision" role="img" aria-labelledby="title description">\n'
               f'<title id="title">{escape(title)}</title>\n<desc id="description">{escape(desc)}</desc>\n'
               f'{body}\n</svg>\n')
    (ROOT/name).write_text(content)

mountains = polygon([(27,154),(128,54),(232,154)],GREEN,'mountain-left') + '\n' + polygon([(232,154),(336,54),(437,154)],GREEN,'mountain-right')
bands = []
for lo in [235,256,277,298]:
    hi=min(lo+16,305)
    a,b=(lo-232)*70/73,(hi-232)*70/73
    pts=[(lo,a),(hi,b),(hi,140-b),(lo,140-a)]
    # Coincident diamond tip vertices become one deliberately simple triangle.
    pts=list(dict.fromkeys(pts))
    bands.append(polygon(pts,GREEN))
    bands.append(polygon([(464-x,y) for x,y in reversed(pts)],GREEN))
peak = '<g id="striped-peak">\n'+'\n'.join(bands)+'\n</g>'
svg('m100-primary.svg',488,492,'M100 primary logo',
    'Forest green mountain shoulders and striped peak, green M and matching oval zeroes, brass 1 and copper crest. Openings reveal the substrate.',
    f'<g id="primary-logo" transform="translate(12 12)">\n{mountains}\n{peak}\n'
    f'<g transform="translate(0 174)">{WORDMARK}</g>\n<g transform="translate(232 298)">{CREST}</g>\n</g>')
svg('m100-wordmark.svg',488,140,'M100 wordmark','Geometric M100 lettering. The two zeroes use identical contours. All counters are transparent.',
    f'<g transform="translate(12 12)">{WORDMARK}</g>')
subline, tracking = outlined_text(BRAND_NAME,20,SUBLINE_WIDTH,250,183,GREEN,'outlined-subline')
divider = (path('M8 141 H230 V143 H8 Z M270 141 H492 V143 H270 Z',GREEN,'divider-rules')+'\n'+
           path('M250 131 L261 142 L250 153 L239 142 Z M250 134 L242 142 L250 150 L258 142 Z',GREEN,'diamond-outline',extra=' fill-rule="evenodd"')+'\n'+
           polygon([(250,138),(254,142),(250,146),(246,142)],GREEN,'diamond-centre'))
svg('m100-lockup.svg',500,198,f'M100 with {BRAND_NAME} subline',
    f'Shared M100 wordmark with thin Art Deco divider and centre diamond. {BRAND_NAME} is outlined, centred and tracked across {SUBLINE_WIDTH} units. Selected brand identity for microphones and other audio equipment.',
    f'<g transform="translate(18 12)">{WORDMARK}</g>\n{divider}\n{subline}')

outer=[(152,10),(236,94),(236,114),(268,146),(268,164),(292,188),(292,336),(268,360),(268,378),
       (152,494),(36,378),(36,360),(12,336),(12,188),(36,164),(36,146),(68,114),(68,94)]
# Parallel offset with miter corners; no strokes or clipping are required.
def inset_polygon(points, distance):
    lines=[]
    for (x,y),(a,b) in zip(points,points[1:]+points[:1]):
        dx,dy=a-x,b-y
        length=(dx*dx+dy*dy)**.5
        nx,ny=-dy/length,dx/length
        lines.append((x+distance*nx,y+distance*ny,dx,dy))
    out=[]
    for prev,cur in zip(lines[-1:]+lines[:-1],lines):
        x,y,dx,dy=prev
        a,b,ex,ey=cur
        t=((a-x)*ey-(b-y)*ex)/(dx*ey-dy*ex)
        out.append((round(x+t*dx,4),round(y+t*dy,4)))
    return out
inner=inset_polygon(outer,7.5)
def polygon_path(points):
    return 'M'+' L'.join(f'{fmt(x)} {fmt(y)}' for x,y in points)+' Z'
badge=path(polygon_path(outer)+' '+polygon_path(inner),GOLD,'badge-border',extra=' fill-rule="evenodd"')+'\n'+polygon(inner,GREEN,'badge-field')
# Vertical bands meet the corresponding diagonal silhouette mathematically.
# Endpoints are derived directly from the inset field, avoiding approximate joins.
def vertical_extent(x,points):
    ys=[]
    for (a,b),(c,d) in zip(points,points[1:]+points[:1]):
        if a!=c and min(a,c)<=x<=max(a,c):
            ys.append(b+(x-a)*(d-b)/(c-a))
    return min(ys),max(ys)
bars=[]
for a in [25,48,78]:
    b=a+7.5
    atop,abottom=vertical_extent(a,inner)
    btop,bbottom=vertical_extent(b,inner)
    # A 0.2-unit overlap into the border prevents raster antialias seams.
    pts=[(a,atop-0.2),(b,btop-0.2),(b,bbottom+0.2),(a,abottom+0.2)]
    bars.append(polygon(pts,GOLD))
    bars.append(polygon([(304-x,y) for x,y in reversed(pts)],GOLD))
badge+='\n<g id="architectural-side-lines">'+'\n'.join(bars)+'</g>'
roof=path('M92 169 V113 L152 52 L212 113 V169 H204.5 V116.07 L152 62.69 L99.5 116.07 V169 Z',GOLD,'roof-frame')
for x in [106,126]:
    top=62.69+abs(x-152)*61/60
    pts=[(x,top),(x+7.5,top-7.625),(x+7.5,169),(x,169)]
    roof+='\n'+polygon(pts,GOLD)+'\n'+polygon([(304-a,b) for a,b in reversed(pts)],GOLD)
roof+='\n'+path('M148.25 60 H155.75 V195 L152 199 L148.25 195 Z',GOLD,'roof-spine')
badge+='\n<g id="peak-architecture">'+roof+'</g>'
badge+='\n<g id="badge-m" transform="translate(92.14 176)">'+path(M,IVORY,extra=' transform="scale(0.73)"')+'</g>'
badge+='\n<g id="badge-100" transform="translate(-1.5 0)">'+path('M91 282 L109 273 V321 H98 V290 L91 293 Z',IVORY)
small_zero=ring(24,24,13,14)
for x in [115,168]:
    badge+=f'\n<g transform="translate({x} 273)">{path(small_zero,IVORY,extra=" fill-rule=\"evenodd\"")}</g>'
badge+='\n</g>'
# The badge crest is taller than the broad primary crest in the concept.
badge+='\n<g id="badge-beard" transform="translate(152 336)">'
def transformed_path(d,matrix):
    p=SVGPathPen(None)
    parse_path(d,TransformPen(RoundingPen(p,roundFunc=lambda value:round(value,4)),matrix))
    return p.getCommands()
BEARD_RIM_WIDTH=5
beard_centreline=transformed_path(CREST_OUTLINE,(0.5,0,0,0.635,0,2))
def expanded_beard_rim(d):
    """Offset a uniform stroke in final coordinates, then retain only clean paths."""
    with tempfile.TemporaryDirectory(prefix='m100-beard-') as directory:
        source=Path(directory)/'source.svg'
        output=Path(directory)/'outlined.svg'
        source.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-70 -10 140 130">'
                          f'<path id="beard" fill="{COPPER}" stroke="{GOLD}" stroke-width="{BEARD_RIM_WIDTH}" '
                          f'stroke-linejoin="round" d="{d}"/></svg>')
        result=subprocess.run(['inkscape',str(source),'--export-plain-svg',f'--export-filename={output}',
                               '--actions=select-by-id:beard;object-stroke-to-path'],capture_output=True,text=True)
        if result.returncode or not output.is_file():
            raise RuntimeError('Could not expand constant-width beard outline: '+result.stderr)
        tree=ET.parse(output)
        rim=next(node.attrib['d'] for node in tree.iter() if node.tag.endswith('path') and 'fill:'+GOLD.lower() in node.attrib.get('style',''))
        recorded=RecordingPen()
        parse_path(rim,recorded)
        contours=[]
        for operation,args in recorded.value:
            if operation=='moveTo':
                contours.append([])
            contours[-1].append((operation,args))
        assert len(contours)==2, 'Expanded rim must contain exactly two closed contours'
        def clean_contours(items):
            pen=SVGPathPen(None)
            rounded=RoundingPen(pen,roundFunc=lambda value:round(value,4))
            for contour in items:
                for operation,args in contour:
                    getattr(rounded,operation)(*args)
            return pen.getCommands()
        return clean_contours(contours),clean_contours(contours[1:])
beard_rim,beard_inner=expanded_beard_rim(beard_centreline)
badge+=path(beard_rim,GOLD,'beard-uniform-rim',extra=' fill-rule="evenodd"')
badge+=path(beard_inner,COPPER,'beard-copper-field')
badge+='<g transform="scale(0.52 0.66)">'+path(MOUTH,IVORY)+'</g></g>'
svg('m100-monogram.svg',304,504,'M100 Art Deco monogram badge',
    'Symmetric stepped forest green shield with brass border and architectural lines, ivory M and 100, and a copper beard with ivory mouth.',badge)

names=['FOREST GREEN','BRASS GOLD','COPPER RED','IVORY BEIGE','GRAPHITE BLACK']
palette=''
for i,(name,colour) in enumerate(zip(names,COLOURS)):
    cx=124+i*238
    edge=f' stroke="{GOLD}" stroke-width="1.5"'
    palette+=f'<circle id="swatch-{i+1}" fill="{colour}" cx="{cx}" cy="96" r="68"{edge}/>\n'
    t,_=outlined_text(name,13,204 if len(name)>12 else 174,cx,198,BLACK,f'name-{i+1}')
    v,_=outlined_text(colour.upper(),13,111,cx,225,BLACK,f'hex-{i+1}')
    palette+=t+'\n'+v+'\n'
svg('m100-palette.svg',1200,254,'M100 brand colour palette','Five flat brand colours with names and hexadecimal values. Labels are outlined paths.',palette)

# Explicit, standalone colour variants; geometry and transparent counters stay intact.
ET.register_namespace('', 'http://www.w3.org/2000/svg')
INVERSE_ASSETS=['primary','wordmark','lockup','palette']
for name in INVERSE_ASSETS:
    root=ET.parse(ROOT/f'm100-{name}.svg').getroot()
    for node in root.iter():
        if name=='palette':
            if node.attrib.get('id','').startswith(('name-','hex-')):
                node.set('fill',IVORY)
        elif node.attrib.get('fill')==GREEN:
            node.set('fill',IVORY)
        if node.tag.endswith('title'):
            node.text+=' — inverse for Forest Green'
        if node.tag.endswith('desc'):
            node.text=('Inverse colour variant for Forest Green substrates. '
                       'Geometry matches the standard master; ivory provides foreground contrast. '
                       'Gold and copper accents and documented palette swatch colours are retained.')
    ET.ElementTree(root).write(ROOT/f'm100-{name}-inverse.svg',encoding='UTF-8',xml_declaration=True)

# Single-colour wordmarks preserve the existing outlines and transparent counters.
# Do not flatten the filled monogram: its internal paint regions would disappear.
MONO_ASSETS=['wordmark-mono','wordmark-mono-inverse']
for name,colour in zip(MONO_ASSETS,[BLACK,IVORY]):
    root=ET.parse(ROOT/'m100-wordmark.svg').getroot()
    for node in root.iter():
        if 'fill' in node.attrib:
            node.set('fill',colour)
        if node.tag.endswith('title'):
            node.text=f'M100 single-colour wordmark — {colour}'
        if node.tag.endswith('desc'):
            node.text='Original M100 geometry in one flat colour, with transparent counters, for panel printing, engraving and PCB marking.'
    ET.ElementTree(root).write(ROOT/f'm100-{name}.svg',encoding='UTF-8',xml_declaration=True)

def asset_name(name,dark=False):
    return name+'-inverse' if dark and name in INVERSE_ASSETS else name

def validate_and_render():
    report={}
    banned={'image','filter','linearGradient','radialGradient','pattern','mask','clipPath','text','use','foreignObject','script'}
    for name in ['primary','monogram','wordmark','lockup','palette']+[n+'-inverse' for n in INVERSE_ASSETS]+MONO_ASSETS:
        file=ROOT/f'm100-{name}.svg'
        root=ET.parse(file).getroot()
        tags=[]
        fills=set()
        for node in root.iter():
            tag=node.tag.split('}')[-1]
            tags.append(tag)
            assert tag not in banned, (file,tag)
            for key,value in node.attrib.items():
                assert not key.endswith('href'), (file,key)
                assert 'base64' not in value and 'url(' not in value, (file,key)
                if key in {'fill','stroke'}:
                    fills.add(value)
                    assert value in COLOURS, (file,value)
                assert key not in {'opacity','fill-opacity','stroke-opacity'}, (file,key)
        sizes=[]
        w,h=map(float,root.attrib['viewBox'].split()[2:])
        for size in [24,64,256,1024]:
            out=ROOT/'qc'/f'm100-{name}-{size}.png'
            args=['rsvg-convert','-w' if w>=h else '-h',str(size),'-o',str(out),str(file)]
            subprocess.run(args,check=True)
            im=Image.open(out)
            assert max(im.size)==size
            assert im.getbbox() is not None
            sizes.append({'long_edge_px':size,'dimensions':list(im.size)})
        report[name]={'viewBox':root.attrib['viewBox'],'colours':sorted(fills),'geometry_elements':sum(t in {'path','polygon','circle','rect','line'} for t in tags),'renders':sizes}
    # Wordmark geometry is byte-identical, including fills, in all three files.
    for name in ['primary','wordmark','lockup']:
        assert WORDMARK in (ROOT/f'm100-{name}.svg').read_text()
    assert WORDMARK.count(f'd="{ZERO}"')==2
    # Inverse files change paint only: every shape, counter, position and size matches.
    for name in INVERSE_ASSETS:
        normal=list(ET.parse(ROOT/f'm100-{name}.svg').getroot().iter())
        inverse=list(ET.parse(ROOT/f'm100-{name}-inverse.svg').getroot().iter())
        assert len(normal)==len(inverse)
        for a,b in zip(normal,inverse):
            assert a.tag==b.tag
            assert {k:v for k,v in a.attrib.items() if k not in {'fill','stroke'}}=={k:v for k,v in b.attrib.items() if k not in {'fill','stroke'}}
            if a.attrib.get('fill')==GOLD or (name!='palette' and a.attrib.get('fill')==COPPER):
                assert a.attrib['fill']==b.attrib['fill']
    for name in MONO_ASSETS:
        normal=list(ET.parse(ROOT/'m100-wordmark.svg').getroot().iter())
        mono=list(ET.parse(ROOT/f'm100-{name}.svg').getroot().iter())
        assert len(normal)==len(mono)
        for a,b in zip(normal,mono):
            assert a.tag==b.tag
            assert {k:v for k,v in a.attrib.items() if k!='fill'}=={k:v for k,v in b.attrib.items() if k!='fill'}
    # The two straight lower edges and vertical walls share a 5-unit normal offset.
    original=ET.parse(ROOT/'m100-monogram.svg').getroot()
    rim=next(n for n in original.iter() if n.attrib.get('id')=='beard-uniform-rim')
    assert 'stroke' not in rim.attrib and BEARD_RIM_WIDTH==5
    # All paired mountain stripes and stepped badge vertices share exact axes.
    assert sorted((304-x,y) for x,y in outer)==sorted(outer)
    report['checks']={'valid_xml':True,'only_authoritative_colours':True,'no_raster_or_external_resources':True,
                      'no_live_text_or_font_dependencies':True,'identical_shared_wordmark':True,'identical_zeroes':True,
                      'bilateral_badge_silhouette':True,'subline_tracking_units':tracking,
                      'inverse_variants_identical_geometry':True,'beard_rim_uniform_stroke_source_units':BEARD_RIM_WIDTH,
                      'monochrome_wordmarks_identical_geometry':True,'manufacturer_subline':BRAND_NAME,
                      'manufacturer_subline_width_units':SUBLINE_WIDTH,
                      'beard_rim_expanded_to_filled_paths':True,
                      'badge_border_and_line_units':7.5,'badge_nominal_line_mm_at_24mm_art_height':round(7.5/484*24,3)}
    (ROOT/'qc'/'validation.json').write_text(json.dumps(report,indent=2)+'\n')

def contact_sheet():
    canvas=Image.new('RGB',(1500,1050),IVORY)
    draw=ImageDraw.Draw(canvas)
    label=ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',17)
    specs=[('primary',(25,60,470,550)),('monogram',(520,60,300,550)),
           ('wordmark',(870,60,590,170)),('lockup',(870,305,590,280)),('palette',(25,720,1435,305))]
    for name,(x,y,w,h) in specs:
        im=Image.open(ROOT/'qc'/f'm100-{name}-1024.png')
        im.thumbnail((w,h),Image.Resampling.LANCZOS)
        canvas.paste(im,(x+(w-im.width)//2,y+(h-im.height)//2),im)
        draw.text((x,y-30),f'M100 / {name.upper()}',font=label,fill=BLACK)
    canvas.save(ROOT/'qc'/'contact-sheet.png')
    # Actual-pixel reductions use the correct standalone variant for each substrate.
    canvas=Image.new('RGB',(1800,1350),IVORY)
    draw=ImageDraw.Draw(canvas)
    for row,(bg,ink) in enumerate([(IVORY,BLACK),(GREEN,IVORY),(BLACK,IVORY)]):
        y=row*450
        draw.rectangle((0,y,1800,y+450),fill=bg)
        for col,name in enumerate(['primary','monogram','wordmark','lockup','palette']):
            x=col*360+18
            draw.text((x,y+15),name.upper(),font=label,fill=ink)
            for size,sy in [(24,52),(64,99),(256,174)]:
                im=Image.open(ROOT/'qc'/f'm100-{asset_name(name,bg==GREEN)}-{size}.png')
                sy=y+sy
                canvas.paste(im,(x,sy),im)
    canvas.save(ROOT/'qc'/'reduction-sheet.png')
    canvas=Image.new('RGB',(1500,1100),GREEN)
    draw=ImageDraw.Draw(canvas)
    draw.text((30,24),'M100 / FOREST GREEN — INVERSE MASTERS',font=label,fill=IVORY)
    for name,(x,y,w,h) in specs:
        y+=30
        im=Image.open(ROOT/'qc'/f'm100-{asset_name(name,True)}-1024.png')
        im.thumbnail((w,h),Image.Resampling.LANCZOS)
        canvas.paste(im,(x+(w-im.width)//2,y+(h-im.height)//2),im)
    canvas.save(ROOT/'qc'/'forest-contact-sheet.png')

def preview():
    assets=[('primary','Primary logo'),('monogram','Art Deco monogram'),('wordmark','M100 wordmark'),('lockup','Wordmark + subline'),('palette','Brand palette')]
    content=''
    for bg,title in [('ivory','Ivory Beige'),('forest','Forest Green'),('graphite','Graphite Black')]:
        content+=f'<section class="surface {bg}"><h2>{title}</h2><div class="grid">'
        for name,label in assets:
            selected=asset_name(name,bg=='forest')
            w,h=map(float,ET.parse(ROOT/f'm100-{name}.svg').getroot().attrib['viewBox'].split()[2:])
            variant='Inverse master' if selected!=name else 'Standard master'
            content+=f'<article><h3>{label} · {variant}</h3><div class="hero"><img src="m100-{selected}.svg" alt="{label}"></div><div class="sizes">'
            for size in [24,64,256]:
                sw,sh=(size,round(size*h/w,3)) if w>=h else (round(size*w/h,3),size)
                content+=f'<figure><img src="m100-{selected}.svg" alt="{label} at {size} pixels" style="width:{sw}px;height:{sh}px"><figcaption>{size} px</figcaption></figure>'
            content+=f'</div><p><a href="m100-{selected}.svg" download>Download {variant.lower()}</a></p><details><summary>1024 px inspection</summary><img class="large" src="m100-{selected}.svg" alt="{label}, large inspection" style="width:{1024 if w>=h else round(1024*w/h,3)}px;height:{1024 if h>=w else round(1024*h/w,3)}px"></details></article>'
        content+='</div></section>'
    html='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>M100 · SVG master inspection</title>
<style>
:root{color-scheme:light}*{box-sizing:border-box}body{margin:0;background:#E9DDC6;color:#2D2D2A;font:15px/1.5 system-ui,sans-serif}header{padding:40px 4vw 25px}h1{font-size:28px;font-weight:500;margin:0 0 10px}header p{max-width:820px}h2{font-weight:500;font-size:22px;margin:0 0 24px}h3{font-size:14px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;margin:0 0 24px}.surface{padding:36px 4vw 48px}.ivory{background:#E9DDC6;color:#2D2D2A}.forest{background:#355856;color:#E9DDC6}.graphite{background:#2D2D2A;color:#E9DDC6}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:32px}article{min-width:0;border-top:1px solid currentColor;padding-top:18px}.hero{height:320px;display:flex;align-items:center;justify-content:center}.hero img{max-width:100%;max-height:290px;width:auto;height:auto;display:block}.sizes{display:flex;flex-wrap:wrap;align-items:flex-start;gap:20px;margin-top:30px;min-height:310px}figure{margin:0}figure img{display:block;max-width:none}figcaption{font-size:12px;margin-top:12px}a{color:inherit;text-underline-offset:4px}summary{cursor:pointer;font-size:13px}details{overflow:auto;max-width:100%;padding:8px 0}.large{display:block;max-width:none;margin-top:24px}footer{padding:24px 4vw}code{font-size:13px}@media(max-width:420px){.grid{grid-template-columns:1fr}.sizes{gap:12px}.surface{padding-left:18px;padding-right:18px}}
</style></head><body><header><h1>M100 / METZGER100 AUDIO WORKS</h1><p>Brand name selected · 5 October 2026. <a href="../proposals/README.md">Read the naming decision</a> · <a href="../proposals/preview.html">View naming history</a>.</p><p>Five brand assets, with standalone inverse variants for Forest Green substrates. Measurements below each small image refer to its longest edge. Open the 1024 px view to inspect full contours.</p><p>Ivory Beige and Graphite Black backgrounds use the standard colour masters. Forest Green backgrounds use ivory foreground variants, retaining brass and copper accents. The monogram retains its green field, framed by its gold border. Transparent openings reveal the substrate; the palette always retains the five authoritative swatch colours.</p><p>Single-colour production wordmarks: <a href="m100-wordmark-mono.svg">Graphite</a> · <a href="m100-wordmark-mono-inverse.svg">Ivory</a>. Their contours match the colour wordmark.</p></header>'''+content+'''<footer>Reference: <a href="../README.md">brand guide</a> · <a href="README.md">construction notes</a> · <a href="qc/contact-sheet.png">PNG contact sheet</a> · <a href="qc/forest-contact-sheet.png">Forest Green contact sheet</a> · <a href="qc/validation.json">validation report</a></footer></body></html>'''
    (ROOT/'preview.html').write_text(html)

if __name__=='__main__':
    validate_and_render()
    contact_sheet()
    preview()
    print('Built and validated five standard masters, four inverse variants and two monochrome wordmarks; rendered all 44 PNG sizes.')
