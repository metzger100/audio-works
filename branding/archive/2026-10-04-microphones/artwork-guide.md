# M100 / METZGER100 MICROPHONES SVG masters

Artwork reconstructed from the original approved brand concept. Brand strategy and usage rules are maintained in the [brand guide](../README.md). The concept's flat silhouette and hierarchy are preserved; its lighting, material simulation and incidental asymmetries are omitted.

## Master files

| Filename | viewBox | Intended use |
| --- | --- | --- |
| `m100-primary.svg` | `0 0 488 492` | Complete identity: mountains, striped peak, M100 and copper beard. Packaging, website, print and larger equipment markings. |
| `m100-monogram.svg` | `0 0 304 504` | Tall stepped badge for a microphone body, enamel or a machined badge; intended artwork height 20–30 mm. |
| `m100-wordmark.svg` | `0 0 488 140` | Compact product marking, PCB silkscreen, engraving and horizontal branding. |
| `m100-lockup.svg` | `0 0 500 198` | M100 above the divider and full manufacturer name. Packaging and microphone body engraving, including a placement rotated as a whole along the body. |
| `m100-palette.svg` | `0 0 1200 254` | Documentation: five swatches with outlined names and hexadecimal values. |

All five files are independent standalone SVGs. They have no fixed width or height and scale through their viewBox. The SVG masters contain editable vector shapes and outlined lettering; the raster QC files are previews only.

For Forest Green substrates, use the additional standalone variants below. Graphite Black uses the standard masters, as requested. Their viewBoxes and geometry match the corresponding standard masters exactly.

| Filename | Dark-background treatment |
| --- | --- |
| `m100-primary-inverse.svg` | Ivory mountains, striped peak, M and zeroes; brass 1 and copper beard. |
| `m100-wordmark-inverse.svg` | Ivory M and zeroes; brass 1. |
| `m100-lockup-inverse.svg` | Inverse wordmark with ivory divider, diamond and outlined subline. |
| `m100-palette-inverse.svg` | Original five swatch colours, with ivory documentation lettering. |

The monogram already has ivory lettering and a gold perimeter framing its green field, so `m100-monogram.svg` works on both light and dark substrates.

## Authoritative colours

| Name | Value |
| --- | --- |
| Forest Green | `#355856` |
| Brass Gold | `#B89255` |
| Copper Red | `#B24C39` |
| Ivory Beige | `#E9DDC6` |
| Graphite Black | `#2D2D2A` |

These are the only paint values in the masters. No gradients, shading, filters, textures, opacity effects, masks, clipping, bitmap content or external resources are present. Brass is a flat colour. The documentation palette uses thin brass swatch outlines so green, ivory and graphite remain distinguishable against matching backgrounds.

## Shared construction and inferred decisions

- The common lettering uses a one-unit construction grid with major dimensions in four-unit increments. Its nominal envelope is 464 × 116 units. The M is 164 units wide with 40-unit stems, mirrored diagonal notches and straight edges. The narrow 1 occupies a 45-unit envelope and has an angled flag without an added foot.
- Both primary zeroes use the same exact path: a circular 116-unit outside contour with a vertically oval 64 × 72-unit counter. The curves in the concept suggested this circular outside / oval inside relationship. Small round overshoots extend two units below the M and 1 baseline.
- The M-to-1 gap is nine units, the 1-to-first-zero gap is nine units, and the zero-to-zero gap is five units. These reflect the reference's broad M, narrow 1 and compact paired rounds. All three related masters insert the same complete lettering group verbatim; they differ only in its placement. The full wordmark envelope and mountain/crest axis share the same mathematical centre.
- The primary mark has a local centre axis at x = 232; the SVG axis is x = 244 after its 12-unit margin. The two mountain shoulders are mirrored triangles with a common horizontal baseline at local y = 154.
- The central peak is a 146 × 140-unit diamond articulated by eight mirrored green bands. Full bands are 16 units wide on a 21-unit pitch; the central gap is six units. The outermost bands terminate in triangles, derived directly from the diamond edges. All intervening spaces are true cutouts, showing ivory on an ivory substrate and the substrate colour elsewhere.
- The primary beard is 232 × 170 units, centred under the wordmark. A symmetric pair of restrained Bézier horn returns and two small top lobes preserve the reference's beard character. The lower shield is a straight-edged pentagon. Its mouth is a compound-path hole with a peaked upper edge and softened lower corners. It contains no ivory rectangle or simulated background.
- The monogram is constructed independently around x = 152. Its stepped silhouette, inset border, paired side bands and roof ribs are mirrored. Its visible shield is 280 × 484 units within the padded viewBox. Border and main gold line widths are 7.5 units, a deliberate increase over ambiguous fine details in the reference. Side-line endpoints are calculated from the inset silhouette, with a 0.2-unit overlap into the border to suppress antialias seams. Borders are actual compound rings, rather than a full gold shield hidden under a green duplicate.
- The badge uses an ivory M with the same angular profile, separately proportioned ivory 100 and a taller version of the copper beard, as shown in the concept. The beard's gold rim is now constructed from one symmetric centreline with a uniform **5-unit stroke in final badge coordinates**, then expanded into a filled compound path using Inkscape. Round joins maintain an even rim around the horn returns and central notch. The copper field follows the expanded rim's actual inner contour. This replaces the previous independently scaled inner/outer silhouettes, whose separation varied around the curves. There is no remaining live stroke or non-uniform scaling of the rim. Its ivory mouth is an intentionally filled element on the green badge field.
- The lockup's thin horizontal rules surround a small outlined diamond with a solid centre diamond. Forest Green is used for the subline, matching the concept. The reference visibly uses tracked serif capitals; Source Serif 4, regular display proportions, retains that character without substituting another manufacturer's lettering. The subline has a nominal 20-unit cap height, fits a measured 480-unit visible width and uses uniform added tracking. Its actual glyph contours are converted to paths with FontTools, with coordinates rounded to four decimals.
- Source Serif 4 is an open-source font under the SIL Open Font License 1.1. It is used only for the manufacturer subline and palette labels. M100 is custom geometric artwork. There are no font files, live text elements, or runtime font dependencies in any SVG. The local font licence is included in `tools/SourceSerif-LICENSE.md` for provenance.

## Backgrounds and reproduction limits

`preview.html` selects the standard masters on Ivory Beige and Graphite Black, and the inverse masters on Forest Green, with 24, 64 and 256 px samples plus expandable 1024 px inspections. Each card labels and links the actual standalone SVG variant it uses. Size labels refer to the longest viewBox edge, preserving the aspect ratio. Inverse variants replace green foreground artwork with ivory while retaining brass and copper. Their contours and transparent counters remain identical. Palette variants change documentation lettering only; swatch values stay authoritative. The monogram uses the same corrected master in all three settings. This is an explicit colour application system, with no CSS filtering, backing rectangles or geometry changes to simulate contrast.

At 24 px the wordmark remains identifiable, but individual primary peak gaps, badge roof ribs and the manufacturer subline cannot all resolve on the pixel grid. The monogram is recognizable by its silhouette, M and crest at that size. Its thickened main lines resolve substantially better at 64 px; use 128 px or more for clear inspection of the complete badge. Use the standalone wordmark for very small digital branding, and allow about 256 px lockup width for comfortable subline reading. Palette labels are documentation text and also require the larger previews. No alternate or simplified identity is substituted in the small samples.

At a 20 / 24 / 30 mm visible badge height, a 7.5-unit main line is approximately 0.31 / 0.37 / 0.46 mm wide. The roof's closest major gap is 6.5 units, approximately 0.27 / 0.32 / 0.40 mm at those heights. The uniform 5-unit beard rim is approximately 0.21 / 0.25 / 0.31 mm wide at those heights. The artwork has not been physically manufactured; final engraving depth, enamel clearances and PCB printing tolerances depend on the chosen process. Retain actual shape dimensions when specifying a fabricator's minimum feature widths. The masters provide flat colour regions, rather than toolpaths or engraving-depth instructions.

## Validation and review

- All five standard masters and four inverse variants parse as valid XML and use `shape-rendering="geometricPrecision"`.
- Automated checks verify the colour allowlist, absence of prohibited effects/resources, absence of live text, exact reuse of the shared wordmark, identical zero paths, bilateral shield silhouette and identical geometry between standard/inverse variants. The beard rim is generated from a documented uniform-width stroke and verified as an expanded compound path.
- Each master and inverse variant was rendered through librsvg at 24, 64, 256 and 1024 px longest edge. All 36 PNGs are saved in `qc/`.
- Visual review compared the primary logo and badge with the concept, then inspected the contact sheet and size/background reductions. It corrected intersecting outer peak tips and imprecise side-line junctions before delivery.
- `qc/contact-sheet.png` shows all five assets on ivory. `qc/forest-contact-sheet.png` shows the corrected Forest Green application. `qc/reduction-sheet.png` shows 24, 64 and 256 px reductions using the appropriate variants on all three backgrounds. `qc/validation.json` contains the machine-readable checks and raster dimensions. Raster antialiasing can produce intermediate pixel colours; those are renderer outputs, not paints in the SVG masters.

## Rebuilding

`tools/build_branding.py` holds the shared geometry, outlined-label construction, constant-width beard rim expansion, inverse variant generation, rendering, preview generation and integrity checks. Run it with Python containing FontTools and Pillow, with `rsvg-convert` and `inkscape` on the executable path. It expects the installed Source Serif 4 variable font at `/usr/share/fonts/adobe-source-serif/SourceSerif4Variable-Roman.otf`. Only rebuilding needs that font and Inkscape; opening, editing and reproducing the finished SVG masters does not. The README and font provenance are maintained separately.
