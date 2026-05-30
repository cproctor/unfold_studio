# Staging Site Analysis

Source: https://staging.unfoldstudio.net/ and https://app.staging.unfoldstudio.net/

The staging site represents an incomplete but directionally strong previous attempt at a new theme.
There are actually two separate surfaces: the marketing/documentation site at staging.unfoldstudio.net
(the new theme), and the application itself at app.staging.unfoldstudio.net (the old theme, unchanged).

## New theme (staging.unfoldstudio.net) — What's strong

### Monaspace Neon

The primary font is **Monaspace Neon** (GitHub's Monaspace family), loaded in three weights:
- Regular (400)
- Medium (500)  
- SemiWideExtraBold (800)

Monaspace Neon is a high-quality modern monospace with a distinctive "neon/electronic" texture — the
letterforms have a slight irregularity that feels hand-drawn at text sizes. It is designed for code but
reads well for prose. The Monaspace family also includes Argon, Xenon, Krypton, and Radon variants,
each with different stylistic textures — this could provide a vocabulary of related but distinct
monospace faces for different contexts (e.g., story text vs. source code).

This is a stronger choice than Courier Prime or IBM Plex Mono suggested in the retro_aesthetic.md
draft — Monaspace Neon is both modern enough to render well on contemporary screens and distinctive
enough to be recognizable as the site's identity font.

**Verdict: Keep. This is the right font choice.**

### Pixel-art SVG buttons

The nav buttons are the most remarkable design element: hand-drawn SVG polygons that create a
pixel-art 3D shadow effect, similar to classic Windows 3.1 buttons but more stylized — closer to
the Undertale UI button style. Each button is a fully custom SVG:

```
"Start writing" button — 148×30px SVG:
  - Body: yellow #ffe564 (hover: #fff3a0)
  - Shadow: near-black #231F20 polygon offset 6px down-right
  - Corners: clipped at 2px (pixel-art chamfer)

"About" button — 68×30px SVG:
  - Body: purple #9494ff (hover: #adadff)
  - Same shadow and corner style
  - Hover rule: +10% S in HSV
```

The SVG polygon approach means buttons are not CSS rectangles with border-radius — they are
hand-drawn shapes with pixel-perfect construction. This is exactly the kind of craft-objects
described in the icon conjecture: visible construction, non-generic, human-made.

**Verdict: Keep the aesthetic, but re-implement in CSS.** The SVG approach is expressive but
fragile — each button is a bespoke file with hard-coded pixel dimensions, making it difficult
to theme, resize, or apply consistently across new elements. The same visual effect is readily
achievable in CSS: chamfered corners via `clip-path: polygon(...)`, and the stepped shadow via
a `box-shadow` with zero blur radius or an absolutely-positioned `::after` pseudo-element offset
by a fixed number of pixels. A CSS implementation would be trivially themeable (change one
variable to recolor every button), responsive, and applicable to any element — inputs, cards,
tabs, story player controls — without per-instance SVG authoring.

### Dithered background images

The home page uses three dithered images as background decorations:
- `Dither_GradientCircle-600x600.png` — placed upper-left, 360px
- `Dither_Rect-80x160.png` — placed upper-right, 40px
- `Dither_Sphere-560x560.png` — placed lower-right, 280px

Dithering (converting a smooth gradient into a pattern of dots/pixels from a limited palette)
evokes early computer graphics, 1-bit displays, and risograph/zine printing aesthetics. It is
a specific and recognizable technique that extends the retro aesthetic beyond typography into
visual imagery. Dithering is also how gradients work in environments without gradient support
(old printers, early monitors, LED displays) — so it carries the "permeability" message at
the visual level: you can see how the image is constructed.

**Verdict: Keep. Dithered decorative images should be part of the visual system, not just
background decoration on the landing page.**

### Grid background

The site uses a repeating SVG grid tile (`gridFVS2.svg`, 140×140px) as the page background.
This creates a graph-paper/engineering-notebook aesthetic. Combined with the monospace font,
it connotes a technical workspace but one that is also a notebook — a place for making things,
not just using things.

**Verdict: Keep. The grid background is a distinctive element. Consider whether it should
appear in the app views or only on marketing pages.**

### Color system

```
Near-black:  #231F20  (slightly warm, not pure black)
Yellow CTA:  #ffe564  (primary action; hover #fff3a0)
Purple sec:  #9494ff  (secondary action; hover #adadff)
White:       #ffffff  (background)
```

Yellow and purple are complementary colors that evoke:
- Classic 8-bit/16-bit color palettes
- Gameboy and early handheld aesthetics  
- The warm/cool contrast of a well-lit workspace

The near-black (#231F20) is warmer than pure black — important detail that makes the
typography feel less harsh.

**Verdict: Keep this palette. It's specific and non-generic. May need 1–2 more tones
(a light gray for backgrounds/borders, a mid-tone for secondary text).**

## Old theme (app.staging.unfoldstudio.net) — For reference

The app itself still runs on the existing (old) theme:
- Font: `Courier, monospace` — the classic, system-default fallback
- Nav bar: `#444` dark gray with white text
- Links: `#3498db` (classic Bootstrap blue), visited `#2980b9`
- Container: `1000px` centered, `10px` padding
- Very utilitarian — functional but without aesthetic intention

The story card component (`.story-card`) has a reveal-on-hover pattern that shows a text
preview. This is worth preserving in the new theme.

**What the old theme establishes that should carry over:**
- Story card grid layout (`auto-fill, minmax(260px, 1fr)`)
- Story card reveal/preview interaction
- Story card metadata pattern (title, description, author, preview text)

## Gaps — What the staging site doesn't yet address

1. **Story listing and story page designs** — no app-level pages in the new theme
2. **Social UI** (reader-writer relationships, responses, profiles) — not present
3. **The immersion/interactivity split-view** — not present
4. **Icon system** beyond nav buttons — no story-type icons, pilcrows, etc.
5. **Form elements** — inputs, text areas, dropdowns in the new aesthetic
6. **Dark mode** — the new theme is light-only

## Summary of confirmed design decisions

| Element | Decision |
|---------|----------|
| Primary font | Monaspace Neon (Regular, Medium, ExtraBold) |
| Font system | Monaspace family (Neon + variants for different contexts) |
| Primary CTA color | #ffe564 yellow |
| Secondary action color | #9494ff purple |
| Near-black | #231F20 |
| Button style | SVG pixel-art polygons with stepped shadow |
| Background decoration | Dithered bitmap images |
| Page background texture | SVG grid tile (graph paper) |
| CSS framework | Tailwind CSS v4 |
