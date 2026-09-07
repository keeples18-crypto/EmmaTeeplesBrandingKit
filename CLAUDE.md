# CLAUDE.md

Context for every session in this repository. Read this before starting work.

## What this repo is

Brand and design assets for **Emma Teeples**, a PGA Associate golf instructor at
The Golf Club Tierra Oaks in Redding, California. Instagram: `@emmateeples.golf`.

This repo is asset generation — typographic marks, covers, templates, print-ready PDFs.
It is not a web app and has no runtime. Output is files a human uploads somewhere else.

Kale builds; Emma is the subject-matter authority and the final approver. When something
is a matter of taste or voice, it's Emma's call, not ours.

## Credential language — get this exactly right

- Correct: **"PGA Associate"** or **"Registered PGA Associate · Northern California PGA Section"**
- Never: "PGA Professional", "PGA Member", "PGA Pro"

She is pursuing membership; the Playing Ability Test is still pending. Overstating the
credential is a real problem, not a stylistic one.

## Brand tokens

```
Cream          #F5F1E8
Antique Gold   #B8924A
Charcoal       #1A1A1A
```

Heritage extension, for badge and crest work only:

```
Deep Forest    #1F382C
Bone           #E8E2D5
```

Any single design uses two or three of these, never all five.

**Type:** Playfair Display for display, Montserrat for body and labels. DM Serif Display
and Cormorant Garamond are acceptable for heritage/collegiate directions.

**House style:** thin hairline rules, generous letterspacing on uppercase micro-labels,
italic gold Playfair for emphasis, wide margins. Restraint over ornament.

**Never:** photographs in marks, stock icons, clip-art golf clubs, gradients, drop
shadows, textures, script fonts, emoji in artwork, anything that reads as a stock template.

## Fonts — how to get them

Download to `/tmp/fonts/` from `raw.githubusercontent.com/google/fonts/...`.
Google's own font CDN is blocked; the GitHub mirror is reachable.

Two PIL gotchas that will silently ruin output:

- **Variable fonts open at their thinnest weight.** Montserrat's variable file loads at
  100 unless you call `font.set_variation_by_axes([500])`.
- **PIL has no letter-spacing.** Draw tracked type character by character with a manual
  gap. Arched type means rotating each glyph around the circle center.

## Instagram highlight covers

Canvas **1080 × 1920 PNG**. Instagram crops to a circle, so all artwork must sit inside a
**640 px diameter circle centered at (540, 960)**. The rest is flat background.

The six covers, in profile order. Numbers are file order only and never appear in the
artwork (see the highlight-order mechanic below):

```
01 START      02 DRILLS     03 COMEBACK
04 PRO SHOP   05 WELLNESS   06 OFF COURSE
```

Instagram truncates the highlight name under the circle at roughly 9-15 characters
depending on device, so labels stay short and sit on one line. "OFF COURSE" is the one
exception at 10 characters; if a device truncates it, the cover artwork still carries
the full word.
Auto-fit by measuring rendered width against the safe circle's chord at the line's
height and stepping the size down. Never hard-code a size per word. Keep the two-line
fallback in the fitter, but no current label should need it.

Emma chose "OFF COURSE" over "OFF DUTY": the pun over truncation safety. Decided
Sept 7, 2026. It is a single constant in `src/covers.py`.

### The 68 px test — distinctiveness and cohesion, not legibility

Covers display at roughly **68 px** on a phone, and Instagram prints the highlight name
underneath each circle. So the word on the cover does not need to be readable at that
size. The cover is an icon.

What has to survive at 68 px:

- **Distinctiveness.** The construction (ring, halo, badge structure, saturated ground)
  should still be recognisable as a deliberate mark, not a dark blob with a smudge in it.
- **Cohesion.** The six should read as one system at a glance. Same silhouette, same
  weight, same ground.

Rendering the PNGs is not finishing the job. Build a contact sheet showing each cover
circle-cropped at both ~220 px and 68 px, open it, and look at it. A direction whose
covers become indistinguishable from any other dark-disc-with-text account at 68 px fails.

## Highlight order mechanic — affects design decisions

Instagram has no drag-to-reorder. Highlights sort by most recently updated, newest first,
left to right. Editing any highlight — including changing its cover — bumps it to
position one.

Consequence for design: **numbered covers are fragile.** The moment a highlight gets
bumped, "04" is sitting in position two and the system reads as broken. Only use numerals
if the order is being actively maintained.

## PDF output

WeasyPrint, not wkhtmltopdf (which can't handle CSS custom properties). Declare fonts via
`@font-face` with `file:///tmp/fonts/...` URIs.

Emoji do not render in WeasyPrint at any font tried. Use bracketed text markers in print
and note that the real glyphs go in the live asset.

Iteration loop that works: render → `pdftoppm -jpeg` → PIL contact sheet → view the image
→ trim CSS or prose → rebuild. Fix orphan pages by tightening prose, not by shrinking
font sizes, which breaks the type scale.

## Working style

Direct, no preamble, no motivational filler. Lead with the actionable thing. Name risks
plainly. When a direction isn't working, say so and say why — don't produce six
enthusiastic paragraphs about six mediocre options. Recommend one, and name the one to drop.
