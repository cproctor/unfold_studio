# Retro Aesthetic: Wireframes and Precedents

## Precedent: p5.js Web Editor

The [p5.js editor](https://editor.p5js.org/) is the closest existing precedent. It uses:
- Monospace font (Source Code Pro) throughout, not just for code
- Dark/light toggle with neutral palette
- Minimal color; function names and keywords get accent color, text stays neutral
- Dense, information-rich layout without visual decoration
- Visible structure (panes, rulers, status bars) that feels like a tool, not an app

The p5.js editor signals "creative coding space" without corporate polish or consumer-app aesthetics. It feels like a place where you make things.

## Typography Direction

Primary typeface: a monospace font used broadly (not just code). Candidates:
- **Courier Prime** – warm, slightly humanist version of Courier; newspaper-adjacent
- **IBM Plex Mono** – clean, tech-adjacent but with character
- **Iosevka** – narrow, efficient; very "terminal"
- **iA Writer Mono** – optimized for reading prose in monospace; literary feel

The key choice is whether the monospace font should feel more literary (Courier) or more technical (Iosevka). Given that the site centers writing and story, Courier Prime or IBM Plex Mono may be more appropriate.

Accent/display use: consider a bitmap/pixel font for headings and site chrome (see craft_icons.md for the pixel aesthetic).

## Color Palette Direction

Near-monochrome with deliberate minimal accent color. Possible palette families:

**Option A: Green terminal**
```
Background:  #0d1117  (near-black)
Text:        #c9d1d9  (light gray)
Accent:      #3fb950  (terminal green)
Borders:     #30363d
```

**Option B: Paper/sepia**
```
Background:  #faf7f0  (warm off-white)
Text:        #1a1a1a  (near-black)
Accent:      #5c4a1e  (dark sepia/ink)
Borders:     #d4c9b0
```

**Option C: Blueprint**
```
Background:  #0a1628  (dark navy)
Text:        #e0e8f0  (pale blue-white)
Accent:      #4a9eff  (electric blue)
Borders:     #1e3a5f
```

The paper/sepia option may best serve the site's dual identity as a writing space and a coding space—it evokes both typewritten manuscripts and early computer manuals.

## Wireframe: Story Listing Page

```
┌─────────────────────────────────────────────────────────────────┐
│ UNFOLD STUDIO                                [log in] [sign up] │
│ ──────────────────────────────────────────────────────────────  │
│ stories  · prompts  · explore  · about                          │
└─────────────────────────────────────────────────────────────────┘

¶ Recent Stories ________________________________________________

  [✎] The Last Train Home                   by @marisolreads
      a ghost story set in a subway station
      played 47 times  ·  3 responses  ·  est. 8 min

  [✎] Bilingual                             by @jayxyz
      what happens when you have two first languages
      played 103 times  ·  11 responses  ·  est. 4 min

  [✎] The Job Interview                     by @studentwriter
      a simulation of how differently things go
      played 22 times  ·  1 response  ·  est. 6 min

  ────────────────────────────────────────────────────────────
  [see all stories →]


¶ Active Prompts _________________________________________________

  [◈] Write a story where the reader has to choose
      between two registers of language
      → 4 stories submitted

  [◈] Simulate a conversation that goes wrong
      → 7 stories submitted
```

Notes on this wireframe:
- `¶` (pilcrow) as section marker — part of the playful icon system
- `[✎]` and `[◈]` as pixel-art-style icons for story types
- Humanistic metrics: "3 responses" not "3 likes"; "played 47 times" not "47 views"
- No like counts, no trending, no algorithm-curated "popular" section
- Dense but not cramped; grid feels like a printed index


## Wireframe: Story Page Header

```
┌─────────────────────────────────────────────────────────────────┐
│ ← back to stories                                [source] [▶]  │
│ ─────────────────────────────────────────────────────────────── │
│ BILINGUAL                                                        │
│ a story by @jayxyz                                               │
│ written for the "two languages" prompt                           │
│                                                                  │
│ ▸ Play story    ▸ Read source    ▸ Leave a response             │
└─────────────────────────────────────────────────────────────────┘
```

The `[source]` button in the header makes source code access always one click away — part of the immersion/interactivity toggle (see immersion_interactivity.md).
