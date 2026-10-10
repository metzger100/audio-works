# M100 / METZGER100 AUDIO WORKS artwork

[Brand guide](../README.md) · [Preview](preview.html) · [Naming decision](../proposals/README.md) · [Validation](qc/validation.json)

Selected identity, 5 October 2026: METZGER100 AUDIO WORKS subline, custom M100 lettering, mountain and copper beard. Flat vector geometry follows the original concept. Original microphone-specific artwork remains in the [archive](../archive/2026-10-04-microphones/README.md).

## Master files

| Master | viewBox | Use |
| --- | --- | --- |
| [Primary](m100-primary.svg) | `0 0 488 492` | Full identity; packaging, print and larger markings |
| [Monogram](m100-monogram.svg) | `0 0 304 504` | Stepped equipment badge; intended visible height 20–30mm |
| [Wordmark](m100-wordmark.svg) | `0 0 488 140` | Compact panels, engraving and PCB markings |
| [Manufacturer lockup](m100-lockup.svg) | `0 0 500 198` | M100, divider and full manufacturer name |
| [Palette](m100-palette.svg) | `0 0 1200 254` | Outlined colour names and hexadecimal values |
| [README banner](m100-readme-banner.svg) | `0 0 1200 240` | Shared standard lockup on Ivory in both GitHub themes |

Standalone SVGs scale through viewBox without fixed dimensions. Lettering is outlined; raster QC is preview evidence. No live text, bitmap content, external resources, gradients, filters, masks, clipping, opacity effects or material simulation appears in masters. The only paint values are those in the [brand palette](../README.md#visual-identity); brass remains flat colour. Palette outlines distinguish matching substrate/swatches.

| Substrate / process | Artwork |
| --- | --- |
| Ivory or Graphite | Standard masters |
| Forest Green | [Primary inverse](m100-primary-inverse.svg), [wordmark inverse](m100-wordmark-inverse.svg), [lockup inverse](m100-lockup-inverse.svg), [palette inverse](m100-palette-inverse.svg) |
| Single-colour production | [Graphite wordmark](m100-wordmark-mono.svg) or [Ivory wordmark](m100-wordmark-mono-inverse.svg) |
| Monogram on any of the three backgrounds | Same monogram; ivory lettering and gold perimeter frame its green field |

Inverse geometry/viewBoxes match standard counterparts; green foreground becomes ivory, while brass/copper remain. Palette inverse changes labels only. Mono wordmarks use the same outlines and transparent counters in one colour, including the 1. Choose actual ink/substrate contrast and process dimensions.

## Shared construction and inferred decisions

The [builder](tools/build_branding.py) owns common geometry. All related masters reuse the complete wordmark; badge lettering is separately proportioned. The reconstruction infers dimensions from the concept and establishes no physical production qualification.

| Element | Construction |
| --- | --- |
| Lettering | One-unit grid; major dimensions in four-unit increments; envelope 464×116. M width164 / stems 40; 1 envelope 45 with angled flag and no foot |
| Zeroes | Identical paths: circular outer 116, oval counter 64×72; overshoot 2 below M/1 baseline |
| Spacing | M–1 gap 9, 1–zero 9, zero–zero 5; lettering and mountain axis share centre |
| Primary mountains | Local centre x232, SVG centre x244 after margin12; mirrored shoulders at baseline y154 |
| Central peak | Diamond 146×140; eight mirrored bands width 16 / pitch 21; central gap 6; triangular tips and true cutouts |
| Primary beard | Symmetric 232×170; Bézier horn returns/two top lobes, pentagonal lower shield; compound mouth cutout with peaked edge/soft corners |
| Monogram | Centre x152; mirrored stepped shield 280×484; main border / lines 7.5; side-line overlap 0.2 prevents seams; compound border rings |
| Badge beard rim | Uniform 5-unit stroke in final badge coordinates, round joins, expanded by Inkscape to a filled compound path; copper follows inner contour; ivory mouth filled on green |
| Lockup | Divider rules and outlined/solid-centre diamond; tracked Source Serif4 subline cap height 20 / visible width 460, centre x250; established wordmark/divider/viewBox retained |
| Outlined labels | FontTools glyph paths rounded to four decimals; Source Serif4 supplies manufacturer/palette labels, M100 remains custom geometry |

[Source Serif licence](tools/SourceSerif-LICENSE.md): SIL OFL 1.1. The local font licence retains provenance. Finished SVGs have no font-file or runtime font dependency. Uniform rim expansion replaces earlier separately scaled inner/outer silhouettes; no live rim stroke or nonuniform rim scaling remains.

## Backgrounds and reproduction limits

The [preview](preview.html) links actual variants on Ivory, Graphite and Forest at 24,64,256px, with expandable1024px inspection. Size means longest viewBox edge. Geometry stays unchanged; no CSS filtering or backing shapes simulate contrast.

At 24px, wordmark/silhouette remain identifiable; fine peak/badge gaps and manufacturer text cannot all resolve. Badge lines improve at 64px; use ≥128px for full badge inspection and approximately 256px lockup width for readable subline. Palette labels need larger previews. Small samples substitute no simplified identity.

| Feature | At 20 / 24 / 30mm visible badge height |
| --- | --- |
| Main line 7.5 units | 0.31 /0.37 /0.46mm |
| Closest major roof gap 6.5 units | 0.27 /0.32 /0.40mm |
| Uniform beard rim 5 units | 0.21 /0.25 /0.31mm |

Artwork has not been physically manufactured. Fabricator-specific engraving depth, enamel clearance and PCB printing tolerances remain unresolved. Specify actual minimum features; SVG colour regions are not toolpaths or depth instructions.

## Validation and review

The builder checks XML, `shape-rendering="geometricPrecision"`, allowed paints/effects/resources, outlined text, shared wordmark/zero geometry, shield symmetry and equal inverse/mono contours. Rim review verifies documented uniform expansion. Original review corrected peak tips and side-line junctions; the 5 October revision reviewed updated lockup, naming comparison and reductions.

All eleven standard/inverse/mono assets were rendered through librsvg at 24, 64, 256, 1024px: 44 PNGs in `qc/`. [Ivory contact sheet](qc/contact-sheet.png), [Forest sheet](qc/forest-contact-sheet.png), [reductions](qc/reduction-sheet.png) and [machine-readable checks](qc/validation.json) retain review evidence. Antialias colours are renderer outputs rather than master paints.

## Rebuilding

Run [build_branding.py](tools/build_branding.py) with Python, FontTools, Pillow, `rsvg-convert` and Inkscape. It expects `/usr/share/fonts/adobe-source-serif/SourceSerif4Variable-Roman.otf`. The builder generates shared geometry, outlined labels, expanded rim, inverse variants, banner, previews/renders and checks. Finished artwork needs neither that font nor Inkscape to open or reproduce. README and font provenance are maintained separately.

## Naming comparison rebuild

After the main build, run [build_branding_proposal.py](tools/build_branding_proposal.py) with the same dependencies. It generates two unselected naming lockups, selected comparison copy, history preview and image. Both builders preserve archived originals.
