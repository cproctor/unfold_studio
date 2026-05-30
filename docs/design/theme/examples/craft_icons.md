# Craft Icons: Precedents and Direction

## Precedents

### Susan Kare — Original Macintosh Icons (1983–84)

Kare designed the visual language of the first Macintosh at 32×32 pixels. Key qualities:
- **Representational clarity at tiny scale**: the trash can, the document, the happy Mac — each instantly legible at 32 pixels
- **Humanistic warmth**: the icons feel hand-drawn even though they are pixel-perfect; they have personality
- **Metaphorical imagination**: the "desktop metaphor" was invented through these icons; they made a new kind of computer feel familiar
- **Craft at constraint**: working within severe pixel limits produced icons that are more expressive than most modern icons at any resolution

Reference: https://www.businessinsider.com/susan-kare-icons-2013-10

### Legend of Zelda (NES, 1986) — Item and UI Icons

The original Zelda used 8×8 and 16×16 pixel icons for inventory items (sword, shield, bow, boomerang) and UI elements (hearts, rupees, keys). Key qualities:
- **Iconic simplicity**: each item's icon is immediately recognizable and carries semantic weight (the heart = life, the key = access)
- **Consistent vocabulary**: icons share a visual language (outlined shapes, limited palette) that feels coherent across the UI
- **Narrative attachment**: players form emotional relationships with these icons because they represent things they've earned
- **Pixel grid as expressive constraint**: the 8×8 grid forces economy that produces memorable forms

### Undertale (2015) — Interface and Iconography

Toby Fox's RPG uses retro pixel aesthetics self-consciously — it references and subverts the conventions of 8-bit RPGs. Key qualities relevant to Unfold Studio:
- **Earnestness within irony**: Undertale uses retro aesthetics not as nostalgia but as a vehicle for genuinely emotional storytelling; the pixel art does not undercut the feeling
- **Interface as narrative**: the battle UI (the heart, the bullet patterns, the ACT/ITEM/MERCY options) is part of the story, not separate from it
- **Typography as character**: Undertale uses Comic Sans for friendly characters and Papyrus for its most earnest character — typeface as personality
- **Whimsy without condescension**: the game is playful without being childish

Reference: https://undertale.com/

## Icon Design Vocabulary for Unfold Studio

Proposed pixel grid: **16×16** pixels (large enough to show detail, small enough to require economy)

### Proposed Icon Set

**Story-related:**
```
[✎] quill/pen          — story authoring, editing
[◈] open book          — reading a story
[▶] play triangle      — playing an interactive story
[⟳] branching arrows   — nonlinear story structure
[◉] magnifying glass   — explore/search
```

**Social/community:**
```
[♦] person outline     — profile/author
[◆] two people         — reader-writer pair
[✉] envelope           — response/comment
[↩] reply arrow        — responding to a story
```

**Navigation/chrome:**
```
[¶] pilcrow            — section break, "new section"
[✦] four-pointed star  — featured/highlighted
[◇] diamond bullet     — list item marker
[─] horizontal rule    — section separator (drawn, not CSS)
```

**Story mechanics (visible in source view):**
```
[→] arrow              — knot redirect in Ink source
[+] plus               — choice option in Ink source
[~] tilde              — variable/logic in Ink source
[=] equals             — knot definition in Ink source
```

The last category is important: the icons in the source code view should be the same icons as in the story view, reinforcing that reading and writing use the same vocabulary.

## ASCII Approximation of Icon Grid

A sample of what 16×16 pixel icons might look like at high zoom, described in terms of pixel blocks:

**Quill/Pen icon (16×16):**
```
. . . . . . . . # # # . . . . .
. . . . . . . # . . # . . . . .
. . . . . . # . . . . # . . . .
. . . . . # . . . . . . # . . .
. . . . # . . . . . . . . # . .
. . . # . . . . . . . . . . # .
. . # . . . . . . . . . . . . #
. # . . . . . . . . . . . . . .
# # . . . . . . . . . . . . . .
. # # . . . . . . . . . . . . .
. . # . . . . . . . . . . . . .
. . . . . . . . . . . . . . . .
```
(Illustrative only — actual icons would be hand-designed)

## Relationship to Retro Aesthetic

The pixel icons work with the monospace font system: both operate at a grid-constrained scale, both have visible construction (you can see the pixels, you can see the character cells), and both carry the sense that someone made this carefully within constraints. The icons should feel *of a piece* with the typography — like they were designed in the same era or with the same tools.

The pilcrow (¶) as a recurring motif is particularly apt: it is a typographic mark that signals "here begins something new," it has a long history in manuscript culture, and it is pleasingly weird — it says this site knows its typography history.
