# Unfold Studio Design Language — Implementation v0

*Branch: `design_language` · Begun: 2026-05-30*

This document records what was actually implemented, file by file, as a companion to the design conjecture map (`design_language_conjectures.v0.md`).

---

## Design decisions implemented

### 1. Font: Monaspace Neon

**File:** `unfold_studio/unfold_studio/templates/base/base.html`

Monaspace Neon (GitHub's Monaspace family) loaded in three weights via the fontsource CDN:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/monaspace-neon@5/400.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/monaspace-neon@5/500.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/monaspace-neon@5/800.css">
```

CSS variable: `--font: 'Monaspace Neon', 'Courier New', Courier, monospace`

Applied globally to `body`, `pre`, `textarea`, `input`, `button`, `select`. This establishes the monospace-first aesthetic across the entire site: navigation, content, forms, and error states all use the same typeface.

The 800-weight is used for h1 and the site name in the nav bar. The 400-weight handles all body text.

**Why this matters:** The retro monospace aesthetic is the primary mechanism for evoking the "visible construction" and "pre-commercial web" mediating processes. Unlike Courier, Monaspace Neon renders crisply on contemporary displays while retaining the distinctly non-corporate, non-polished character of a monospace typeface.

---

### 2. Color palette

**File:** `unfold_studio/static/base/base_style.css` — `:root` section

```css
--ink:             #231F20   /* near-black, slightly warm */
--page:            #ffffff   /* white */
--cta:             #ffe564   /* yellow — primary action */
--cta-hover:       #fff3a0
--secondary:       #9494ff   /* purple — secondary/link */
--secondary-hover: #adadff
--border:          #d4d0cc   /* warm light gray */
--surface:         #f5f2ee   /* warm off-white for code blocks, messages */
--muted:           #6b6868   /* muted text, labels */
--danger:          #b82020
--success:         #2a7a34
```

The `--ink` color is `#231F20` (warm near-black, not pure black). The yellow and purple are complementary and evoke classic 8-bit/16-bit color palettes. The border and surface values are warm-toned to avoid the cold, clinical feel of pure grays.

---

### 3. Graph paper background texture

**Files:** 
- `unfold_studio/static/base/grid.svg` — graph paper SVG tile (40×40px, nested major/minor grid)
- `unfold_studio/static/base/base_style.css` — `body { background-image: url('/static/base/grid.svg') }`

The body background uses the graph paper texture. The `#container` element (1000px centered) has `background: white`, so the texture shows only in the margins — in the negative space between the content and the browser edges.

This creates a "working notebook" quality: the content sits on graph paper, evoking an engineering notebook or sketchpad. The graph paper is visible on wider viewports and reduces to nothing on mobile (where content fills the viewport).

**Not yet decided:** Whether to show the graph paper as a visible page background inside the main content area on select pages (e.g., profile pages, about pages). Currently it is only a margin texture.

---

### 4. Navigation bar

**Files:** 
- `unfold_studio/unfold_studio/templates/base/menu.html`
- `unfold_studio/static/base/base_style.css` — `#menu` section

Changes:
- Background: `--ink` (warm near-black) — consistent with staging site
- Site name "UNFOLD STUDIO" styled in uppercase, 800-weight, white
- Nav links in `rgba(255,255,255,0.75)` with hover to full white
- "New Story" link gets class `.menu-cta`, styled as a yellow chamfered CTA button (see §5)
- Height: 46px fixed
- Logout is a `<button>` styled as an inline text action (not a boxed button)

---

### 5. Pixel-art chamfered buttons

**File:** `unfold_studio/static/base/base_style.css` — `.btn, button[type="submit"], input[type="submit"]`

The core button style uses:
- `clip-path: polygon(...)` with 3px chamfer at all 8 corners — creates the pixel-art chamfered look without border-radius
- `filter: drop-shadow(4px 4px 0 var(--ink))` — creates a 1-color stepped shadow that exactly follows the clipped shape (drop-shadow respects clip-path, unlike box-shadow which does not)
- Hover: `transform: translate(2px, 2px)` + `filter: drop-shadow(2px 2px 0 var(--ink))` — simulates pressing the button in by shifting toward the shadow
- Active: `filter: none; transform: translate(4px, 4px)` — fully pressed

Primary variant: yellow (`--cta`) fill, dark text.  
Secondary variant: `.btn-secondary` — purple (`--secondary`) fill, white text.

The `.menu-cta` nav button uses the same clip-path but with a smaller shadow (3px) and a semi-transparent dark shadow instead of the full `--ink` color, since it sits against the dark nav background.

**Inline link forms** (`form.link input[type=submit]`) are excluded from the chamfered style — they reset to plain link appearance with `clip-path: none; filter: none`. This is important for actions like love/fork/delete that appear inline in prose.

---

### 6. Form elements

**File:** `unfold_studio/static/base/base_style.css` — form section

- No `border-radius` on inputs, textareas, or selects
- All form elements use `--font` (monospace)
- Focus state: `border-color: var(--ink); border-width: 2px` (no outline glow)
- Labels inside `form.new_story_form` use uppercase, 0.07em letter-spacing, `--muted` color — functional but clearly secondary to the content
- Genre pills: rectangular chips (`border: 1px solid var(--border)`) with selection state showing `background: var(--ink); color: var(--cta)` — the retro inverse-video highlight

---

### 7. Story cards

**Files:**
- `unfold_studio/static/base/base_style.css` — `.story-card` section
- `unfold_studio/unfold_studio/templates/unfold_studio/home.html` — removed flip markup
- `unfold_studio/unfold_studio/templates/unfold_studio/list_stories.html` — removed flip markup

**Removed:** The hover flip/reveal animation (`.story-card__reveal` with dark gradient overlay, `opacity: 0` → `opacity: 1` on hover, body-main fade-out). This is the primary change from the prior aesthetic.

**Replaced with:** A border-accent hover state:
- Default: `border: 1px solid var(--border); border-top: 3px solid var(--border)` — clean, understated
- Hover: `border-color: var(--ink); border-top-color: var(--cta)` — the yellow accent bar reveals itself at the top of the card on hover

This approach:
- Reads as "here is a thing you can interact with" without hiding the content
- Uses the CTA yellow as an accent rather than a dominant color
- Avoids the hover-dark-overlay pattern which obscures the story content

---

### 8. Browse page redesign

**File:** `unfold_studio/unfold_studio/templates/unfold_studio/list_stories.html`

Changes:
- Sidebar: no `border-radius`, no `box-shadow`, flat border
- Search bar: integrated into a bordered container (input + button share one outer border)
- Genre filter chips: rectangular, `--cta` yellow for active state
- Sort tabs: dark active state (`--ink` background, `--cta` text)
- Removed pagination "Page X of Y" from the `description` class; now uses `page-browse-pagination` with `--muted` color

---

### 9. Books page redesign

**File:** `unfold_studio/unfold_studio/templates/unfold_studio/book_list.html`

Changes:
- Removed rounded corners from all card elements
- Removed `box-shadow` from book cards
- **Removed the hover overlay** on book cards (`.book-card-hover { display: none }`) — the dark gradient overlay that appeared on hover revealed a story list, but the hover-flip pattern is inconsistent with the design philosophy
- Added `border-top: 3px solid var(--border)` → `border-top-color: var(--cta)` on hover — consistent with story card behavior
- Genre section headers use small-caps uppercase style
- Sidebar refine box: rectangular, no border-radius
- Search input + button: share one outer border (same as browse page)

---

### 10. Groups page alignment

**File:** `unfold_studio/static/style/groups.css`

The groups page was already the closest to the target aesthetic (clean borders, uppercase labels, no rounded cards). Changes made were minimal color alignment:
- Replaced hardcoded `#3498db` (Bootstrap blue) with `var(--secondary)` (purple)
- Replaced `#8a8a8a`, `#7d7d7d` with `var(--muted)`
- Replaced `#c0392b` (danger red) with `var(--danger)`
- Replaced `#2e7d32` (success green) with `var(--success)`
- Replaced `#d8d8d8`, `#e6e6e6`, `#e2e2e2` with `var(--border)`

The groups page layout and component structure is unchanged — it already exemplified the target aesthetic.

---

## Pages/features not yet implemented

| Feature | Status | Notes |
|---------|--------|-------|
| Immersion/interactivity toggle | Not started | See `examples/immersion_interactivity.md` |
| Reader-writer relationship UI | Not started | Profile pages, notification feed |
| Story page header redesign | Minimal | Current story page is functional but not restyled |
| Profile pages | Not started | `user_detail.html`, `user_self_detail.html` need work |
| Error pages (400, 403, 404, 500) | Not started | Currently use base template, unstyled |
| Custom pixel icon system | Not started | Only the logo/favicon + `.menu-cta` button style |
| Warm in-voice error messages | Not started | Currently plain Django error messages |
| Embedded genre UI | Not started | Story metadata display |
| Dark mode | Not started | Design language is light-only |
| Mobile responsiveness | Partial | Some responsive rules, not comprehensive |

---

## Technical notes

### CSS architecture
All site-wide design tokens and base styles live in `unfold_studio/static/base/base_style.css`. Per-page styles are defined in `{% block style %}` blocks within their templates. Per-app styles (like `groups.css`) live in `unfold_studio/static/style/`.

The `clip-path` + `filter: drop-shadow()` button technique is the key implementation insight: `box-shadow` does not follow `clip-path` (it produces a rectangle regardless), but `filter: drop-shadow()` does. This is what enables the stepped pixel-art shadow on chamfered-corner buttons.

### Font loading
Monaspace Neon is loaded from jsDelivr CDN (fontsource package). If self-hosting is desired, the font files can be downloaded from the `@fontsource/monaspace-neon` npm package and served from `unfold_studio/static/base/fonts/`.

### No `!important` in templates
Per-page inline CSS in templates would override base_style.css rules (same or lower specificity, later in cascade). The templates were rewritten to use the design language CSS variables (`var(--border)`, etc.) directly rather than relying on `!important` overrides in base_style.css.
