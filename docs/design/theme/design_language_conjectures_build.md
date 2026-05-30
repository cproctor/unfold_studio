---
title: "Conjecture Mapping Unfold Studio's Design Language"
date: "2026-05-29"
bibliography: references.bib
csl: apa.csl
suppress-bibliography: false
---

```{=html}
<div id="main-wrap">
```

::: {.note style="border-left:3px solid #9494ff; padding:8px 14px; background:rgba(148,148,255,0.08); font-size:0.85em; margin:0 0 32px;"}
**Scope note:** Sandoval's [-@sandoval2014] conjecture mapping framework distinguishes the *embodiments* of a learning environment — its material and social features — from the mediating processes they are conjectured to activate and the learning outcomes those processes produce. A full conjecture map for Unfold Studio would cover the full range of embodiments across the platform. This document focuses on one subset: the *design language* — the aesthetic, typographic, interaction, and social design choices that constitute the site's ethos and the learning environment it creates. Decisions about *which* affordances to implement are addressed separately; what appears here is how those affordances are represented and surfaced in the UI.
:::

## High-Level Conjecture

A site's *design language* — its coherent system of visual, typographic, interaction, and social design choices — is not decorative. The embodiments of a learning environment shape what practices, identities, and critical possibilities are available to participants [@sandoval2014; @proctorpermeable2025]. The perceived affordances of the site shape rhetorical practices, which shape meanings and identities enacted there, which shape what is critically possible.

Unfold Studio's design language should be principled: following the permeable media framework [@proctorpermeable2025], it should invite users in, support them in making the practice part of themselves, and allow them to grow. Drawing on computational literacies [@kafai2021], it should support cognitive, situated, and critical engagement.

> **Conjecture:** *A design language that is retro and craft-centered — revealing rather than concealing its own construction — combined with social design that emphasizes authentic reader-writer relationships over metrics-driven engagement, will support users in developing positive and expanded CS identities and engaging in critical computational literacies through interactive storytelling.*

## Conjecture Map

```{.mermaid}
flowchart LR
    subgraph E["EMBODIMENTS"]
        retro["Retro monospace\naesthetic"]
        icons["Playful\npixel icons"]
        toggle["Immersion /\ninteractivity toggle"]
        rwui["Reader-writer\nrelationship UI"]
        errors["Warm, in-voice\nerror states"]
        genres["Embedded media\ngenre UI"]
    end
    subgraph M["MEDIATING PROCESSES"]
        hackable["Perceived\npermeability"]
        nostalgia["Pre-commercial\nweb evocation"]
        csid_q["CS identity\nbroadened"]
        craft["Sense of craft\nand human care"]
        oscil["Oscillating reader /\nauthor perspective"]
        demetrics["Writing without\nmetrics pressure"]
        normalized["Failure normalized\nas part of craft"]
        progdisc["Authentic CS patterns\nat low complexity"]
        novelized["Ironic framing of\nembedded genres"]
    end
    subgraph O["OUTCOMES"]
        perm["Permeable media\nengagement"]
        pos_csid["Positive / expanded\nCS identity"]
        belong["Sense of belonging\nin literacy space"]
        cdm["Critical discourse\nmodeling"]
        idauth["Identity\nauthorship"]
    end
    retro --> hackable --> perm
    retro --> nostalgia --> belong
    retro --> csid_q --> pos_csid
    icons --> craft
    craft --> belong
    craft --> idauth
    toggle --> oscil
    oscil --> cdm
    oscil --> perm
    rwui --> demetrics
    demetrics --> idauth
    demetrics --> belong
    errors --> normalized
    normalized --> pos_csid
    normalized --> belong
    toggle --> progdisc
    errors --> progdisc
    progdisc --> perm
    genres --> novelized
    novelized --> cdm
    novelized --> pos_csid
```

## Design Features (Embodiments)

---

### 1. Retro Monospace Aesthetic

```{=html}
<p><span class="tag">Typography</span> <span class="tag">Color</span> <span class="tag">Texture</span></p>
```

**What we will do:** Use a fixed-width (monospace) font throughout — Monaspace Neon is confirmed as the site's primary font. Near-monochrome palette anchored by `#231F20` near-black, `#ffe564` yellow (primary CTA), and `#9494ff` purple (secondary action). Background: repeating SVG graph-paper grid. Decorative elements: dithered bitmap images.

#### Mediating processes

**Perceived permeability of site infrastructure.** A smooth, polished interface presents a perfect surface that conceals construction. The retro aesthetic communicates instead that there is not much distance between what you see and how it works — the visible structure and texture invite users to look beneath the surface. This aligns with permeable media [@proctorpermeable2025], in which the interface invites users to extend themselves into the medium.

**Evocation of pre-commercial web.** The Web 1.0 aesthetic may evoke — for users who experienced it and for those who have absorbed its cultural mythology — an era of more authentic, creative, human online interaction before the commodification of attention [@zuboff2019age]. This positions Unfold Studio as an alternative to surveillance capitalism platforms.

**Challenge to narrow CS identity.** The site reads as a CS artifact (monospace fonts, structured layout, code-adjacent aesthetics) while the content — stories about identity, relationships, social experience — challenges the stereotype that CS is impersonal and only for certain people. This may support users who don't see themselves in mainstream CS culture in building more expansive CS identities [@kafai2021].

```{=html}
<div class="precedent-box">
<strong>Precedent: p5.js web editor (editor.p5js.org)</strong><br>
Monospace-first, split-pane layout. Signals "creative coding" without corporate polish. Neutral palette, dense information layout, visible tool structure.
</div>

<div class="example-box">
<p class="example-box-label">Wireframe: Story listing page</p>
<pre>
┌─────────────────────────────────────────────────────────────────┐
│ UNFOLD STUDIO                                [log in] [sign up] │
│ ──────────────────────────────────────────────────────────────  │
│ stories  · prompts  · explore  · about                          │
└─────────────────────────────────────────────────────────────────┘

¶ Recent Stories ________________________________________________

  [✎] The Last Train Home          by @marisolreads
      a ghost story set in a subway station

  [✎] Bilingual                    by @jayxyz
      what happens when you have two first languages
      ↳ forked from "Two Voices" by @marisolreads

  [✎] The Job Interview            by @studentwriter
      a simulation of how differently things go
      ↳ submitted to "Social Realities" prompt
</pre>
</div>
<div class="example-box">
<p class="example-box-label">Confirmed: Staging site design elements</p>
<table>
<thead><tr><th>Element</th><th>Value</th></tr></thead>
<tbody>
<tr><td>Primary font</td><td>Monaspace Neon (Regular / Medium / ExtraBold)</td></tr>
<tr><td>Near-black</td><td><code>#231F20</code> (warm, not pure black)</td></tr>
<tr><td>CTA yellow</td><td><code>#ffe564</code> → hover <code>#fff3a0</code></td></tr>
<tr><td>Secondary purple</td><td><code>#9494ff</code> → hover <code>#adadff</code></td></tr>
<tr><td>Background</td><td>SVG grid tile (repeating graph paper)</td></tr>
<tr><td>Decoration</td><td>Dithered PNG images (gradient, sphere, rect)</td></tr>
</tbody>
</table>
</div>
```

---

### 2. Playful Pixel Icons

```{=html}
<p><span class="tag">Iconography</span> <span class="tag">SVG</span> <span class="tag">Craft</span></p>
```

**What we will do:** Design custom pixel art icons for navigation, story metadata, and decorative elements (pilcrows, section markers, category indicators) in the tradition of Susan Kare's original Macintosh icons, the original NES *Legend of Zelda*'s item icons, and *Undertale*'s interface elements.

**Already established:** The staging site's navigation buttons are fully custom SVG pixel-art shapes — hand-drawn SVG polygons with a stepped 3D shadow, pixel-perfect chamfered corners, and specific accent colors. This is the craft-object approach in action. The full icon system should extend this vocabulary to all interactive elements. Note: the SVG approach is expressive but fragile — each button is a bespoke file with hard-coded dimensions. The same visual effect (chamfered corners via `clip-path: polygon(...)`, stepped shadow via `box-shadow` with zero blur or a pseudo-element offset) can be achieved robustly in CSS, making it trivially themeable, responsive, and applicable to any element without per-instance SVG authoring.

#### Mediating processes

**Sense of craft and human care.** Pixel art icons communicate that someone invested time in this specific space. They resist the visual language of corporate tech (Material Design, Font Awesome) and signal a community of makers rather than a product. This models a valuing of craft that may carry over into users' own story-making.

**Anti-corporate belonging.** The whimsical quality of hand-crafted icons positions the site as a place where idiosyncrasy is valued — where you do not need to be polished or professional to belong. This lowers the stakes for users who might feel intimidated by coding or by "real" writing.

**Worldbuilding through iconography.** As in Zelda or Undertale, icons carry narrative weight — they are part of the site's story about itself, contributing to a sense of place and identity across the site.

```{=html}
<div class="precedent-box">
<strong>Susan Kare — Original Macintosh icons (1983–84)</strong><br>
32×32 pixels. Humanistic warmth at tiny scale. The desktop metaphor invented through hand-crafted forms.<br><br>
<strong>Legend of Zelda, NES (1986)</strong><br>
8×8 and 16×16 pixel icons for inventory and UI. Each carries semantic and narrative weight. Players form emotional relationships with these marks.<br><br>
<strong>Undertale (2015)</strong><br>
Retro pixel aesthetics as vehicle for genuine emotion. Interface as narrative. Typography as character.
</div>

<div class="example-box">
<p class="example-box-label">Staging site: SVG pixel-art button (actual implementation)</p>
<p>The "Start writing" button is a 148×30px SVG polygon with a yellow <code>#ffe564</code> body, near-black <code>#231F20</code> shadow polygon offset 6px down-right, and 2px chamfered pixel-art corners. This SVG approach should extend to form inputs, cards, tabs, story player controls — all interactive elements.</p>
</div>

<div class="example-box">
<p class="example-box-label">Proposed icon vocabulary (16×16 pixel grid)</p>
<pre>
[✎]  quill/pen        — story editing
[◈]  open book        — reading
[▶]  play triangle    — story playback
[¶]  pilcrow          — section marker
[♦]  person outline   — author profile
[◆]  two people       — reader-writer pair
[✉]  envelope         — response/comment
[✦]  four-point star  — featured story
</pre>
</div>
```

---

### 3. Immersion / Interactivity Toggle

```{=html}
<p><span class="tag">Interaction</span> <span class="tag">Interface</span> <span class="tag">Permeability</span></p>
```

**What we will do:** Support oscillation between an immersive story mode (full-focus reading, minimal chrome) and a reflective mode (split-view with source code visible, structural annotations). Implementation approach — explicit toggle, progressive reveal, or story-authored reveal — to be determined through prototyping.

This enacts Ryan's (2001) immersion/interactivity tension productively: rather than resolving it, the design makes it available as a learning mechanism.

#### Mediating processes

**Oscillating reader/author perspective.** When readers can see a story's source code alongside its rendered form, they simultaneously inhabit reader and author/programmer positions. They discover that the story they are experiencing is also a text they could have written or modified — the "extending into the medium" dimension of permeable media [@proctorpermeable2025].

**Critical awareness of constructed interfaces.** Making the interface visible at key moments teaches users that all interfaces are designed artifacts with specific affordances and constraints. The habit of asking "how does this work?" is a form of critical computational literacy [@kafai2021].

**Note on Monaspace Neon:** Using the same monospace font in both story view and source view means the transition between reading and code feels like *zooming out*, not switching modes — the story is always already a text that could be read as code.

```{=html}
<div class="example-box">
<p class="example-box-label">Wireframe: Split view (reflective mode)</p>
<pre>
┌──────────────────────────────┬──────────────────────────────────┐
│ STORY                        │ SOURCE                           │
│ ──────────────────────────── │ ──────────────────────────────── │
│                              │                                  │
│ You walk into the classroom  │ === start ===                    │
│ and immediately know         │ You walk into the classroom      │
│ something is different.      │ and immediately know something   │
│                              │ is different.                    │
│ ─────────────────────────► ► │                                  │
│                              │ + Sit in the circle              │
│ + Sit in the circle    →     │   -> circle                      │
│ + Linger by the door   →     │ + Linger by the door             │
│ + Ask what's going on  →     │   -> door                        │
└──────────────────────────────┴──────────────────────────────────┘
</pre>
</div>

<div class="example-box">
<p class="example-box-label">Three implementation approaches</p>
<p><strong>Option A — Persistent toggle:</strong> <code>[◈ source]</code> button always visible; switches between full-width and split view. Simplest to implement.</p>
<p><strong>Option B — Progressive reveal:</strong> Story starts immersive; after completion, "how was this made?" prompt offers a replay with source visible.</p>
<p><strong>Option C — Story-authored reveal:</strong> Ink authors insert tags that trigger source visibility at dramatic moments. Most sophisticated; requires author tooling.</p>
</div>
```

---

### 4. Reader-Writer Relationship UI

```{=html}
<p><span class="tag">Social</span> <span class="tag">Community</span> <span class="tag">Anti-metrics</span></p>
```

**What we will do:** Design the social architecture to foreground human connections between specific readers and writers rather than aggregated metrics. Author attribution prominent; story pages surface who has read and responded; profiles show reading and writing history together; comments address the author directly; no like counts, follower counts, or trending sections.

#### Mediating processes

**Writing without metrics pressure.** When the site does not offer follower counts or like buttons, writers optimize for specific readers rather than for attention-maximizing content. This shifts the social frame from "content creation for an audience" toward "writing for people" — the dialogic, rhetorical view of writing [@bakhtin1981; @proctor_bhatt_rish_ms].

**Authentic community participation.** Reader-writer relationships that are personal rather than metric-mediated support an authentic community of practice [@lave1991]. Users are more likely to develop identities as participants in a literary community than as content creators — the situated framing of computational literacies [@kafai2021].

```{=html}
<div class="example-box">
<p class="example-box-label">Wireframe: Story page — after reading</p>
<pre>
┌─────────────────────────────────────────────────────────────────┐
│  BILINGUAL  ·  by Jay Chen (@jayxyz)                            │
│  written for ◈ "Two languages" prompt                           │
│                                                                  │
│  ▸ Play again    ▸ Read source    ▸ See other paths             │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  ¶ Leave a response for Jay                                      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  [text area — response addressed to the author]          │  │
│  └──────────────────────────────────────────────────────────┘  │
│  [submit response]                                              │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│  ¶ More by Jay Chen                                              │
│    [✎] The Last Day of School   [✎] Interview Simulation       │
└─────────────────────────────────────────────────────────────────┘
</pre>
</div>

<div class="example-box">
<p class="example-box-label">What the site omits (by design)</p>
<table>
<thead><tr><th>Omitted</th><th>Reason</th></tr></thead>
<tbody>
<tr><td>Like / star counts</td><td>Aggregate approval metrics reward attention-maximizing content</td></tr>
<tr><td>Follower / subscriber counts</td><td>Shift frame from writing-for-people to content-creation</td></tr>
<tr><td>Trending / algorithmic feeds</td><td>Amplify inflammatory content; obscure niche writing</td></tr>
<tr><td>Share / retweet mechanics</td><td>Virality architecture</td></tr>
<tr><td>Notification badges</td><td>Variable-ratio reinforcement encourages compulsive checking</td></tr>
</tbody>
</table>
</div>
```

---

### 5. Warm, In-Voice Error States

```{=html}
<p><span class="tag">Identity</span> <span class="tag">Belonging</span> <span class="tag">CS identity</span></p>
```

**What we will do:** When an Ink story fails to compile, the error state is rendered in the site's voice — a pixel art character, a message that treats the error as a normal moment of craft rather than a failure. The character might be a small creature that appears in the editor when things go wrong, says something specific to the error type, and offers a nudge toward the fix. The tone is warm and matter-of-fact: *of course* this happens; here's where to look.

Currently, Ink compilation errors surface as cold technical output — precisely the register that reinforces the stereotype that computing is impersonal, exacting, and not for people who make mistakes. For users who don't already identify as programmers, an opaque error message at a moment of creative investment is a high-stakes identity challenge: *maybe I'm not someone who can do this*. The design conjecture is that error states handled in the site's own voice — humanized, expected, even playful — defuse this and model a different relationship to failure.

#### Mediating processes

**Failure normalized as part of craft.** Every writer who codes will encounter compilation errors; every programmer who writes will revise. If the site's response to errors is consistent with its broader ethos — careful, human, a little whimsical — it communicates that encountering errors is not a sign of being in the wrong place. This is a specific, targeted intervention at one of the highest-anxiety moments in the user journey.

```{=html}
<div class="precedent-box">
<strong>Precedent: Undertale death screen</strong><br>
When the player dies, Undertale does not show a generic "Game Over." It shows a darkened screen, a small flower, and Flowey saying something specific to the context — sometimes mocking, sometimes almost tender. The death state is part of the narrative. The site's error state should be part of the site's narrative.
<br><br>
<strong>Precedent: GitHub's 404 / error pages (Octocat)</strong><br>
GitHub's error pages use the Octocat mascot in absurd illustrated scenes. The effect is that encountering an error feels like discovering a hidden part of the site's personality rather than hitting a wall.
<br><br>
<strong>Precedent: itch.io error and upload states</strong><br>
itch.io's interface speaks in a warm, slightly informal voice throughout — including error and confirmation states. This consistency creates a sense of a platform with a person behind it, not a service.
</div>

<div class="example-box">
<p class="example-box-label">Sketch: Ink compilation error state</p>
<pre>
  ┌──────────────────────────────────────────────────────────────┐
  │                                                              │
  │   [pixel art character — small, expressive, not alarming]   │
  │                                                              │
  │   Hmm. Line 14 doesn't know where to go.                    │
  │                                                              │
  │   You wrote: -> the_kitchen                                  │
  │   But I can't find a knot called "the_kitchen" anywhere.    │
  │   Did you mean to write === the_kitchen === somewhere?       │
  │                                                              │
  │   [→ jump to line 14]                                        │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘
</pre>
</div>
```

---

### 6. Embedded Media Genre UI

```{=html}
<p><span class="tag">Critical literacy</span> <span class="tag">Dialogism</span> <span class="tag">Partially implemented</span></p>
```

**What we will do:** Provide UI components that allow story authors to embed recognizable digital media genres within their narratives — text message conversations, social media post frames, chat interfaces, news article excerpts. SMS/text message speech bubbles are already supported; future extensions will include Instagram-style post frames, tweet-format components, and other visual artifacts of social media genres.

The mechanism is Bakhtinian: the novel has always had the capacity to incorporate, stylize, and put into dialogue other genres — speech genres, social registers, discourse types. Interactive storytelling inherits and extends this capacity to digital media. When a story embeds an SMS conversation, it does what Bakhtin described as "novelizing" a genre: fixing and stylizing it, making it "permeated with laughter, irony, humor, elements of self-parody" [@bakhtin1981]. The reader simultaneously recognizes the genre and sees it held at critical distance — which is exactly the condition needed for analysis.

This connects directly to the site's critical possibilities. The dissertation [@proctor2020b] documents how participants in early Unfold Studio workshops were drawn to embedding text messaging and social media speech genres in their stories — modeling bilingual conversations, microaggressions, social positioning. These stories worked as critical discourse models: simulations of social realities that make otherwise-invisible discourse dynamics visible and available for analysis. The visual genre component (the speech bubble that looks like iMessage) is not incidental to this effect; it is the trigger for recognition and the mechanism for critical distance.

#### Mediating processes

**Ironic framing of embedded genres.** Seeing a familiar genre inside an interactive story creates a productive double-awareness: the reader recognizes the genre and its conventions while also knowing it is authored and subject to the story's intent. This double-awareness is the condition for critical analysis — it transforms a form of media one passively inhabits into an object one can examine. The key design principle is that embedded genre components should be *recognizable but clearly constructed* — close enough to trigger recognition, not so accurate that they are mistaken for the real thing. The slight parody is not a failure of fidelity; it is the critical mechanism.

```{=html}
<div class="precedent-box">
<strong>Precedent: <em>Coming Out Simulator</em> — Nicky Case (2014)</strong><br>
Uses a text message interface that mimics a mobile phone UI. The recognition mechanism is central to the game's effect: you understand immediately what kind of conversation this is, what the stakes are, and what the genre normally permits. The game then uses those conventions to create dramatic constraint and to model how identity is negotiated within familiar discourse genres. The interface IS the argument.
<br><br>
<strong>Precedent: Early Unfold Studio workshops [@proctor2019a]</strong><br>
Workshop participants spontaneously requested the ability to embed text messaging speech bubbles and emoji. The paper describes this as appropriating "speech genres into their own storytelling," evoking Bakhtin's analysis of how the novel fixes and stylizes other genres while making them more flexible and ironic. Several participants wrote stories that modeled bilingual code-switching, using the SMS genre to simulate how register and identity interact in real conversations.
</div>

<div class="example-box">
<p class="example-box-label">Wireframe: SMS genre component embedded in a story</p>
<pre>
You approach your friend in the hallway after class.
Your phone buzzes.

  ┌────────────────────────────────┐
  │ Messages — Jaylen              │
  │ ────────────────────────────── │
  │                   you ok?  ●  │
  │ ● kinda. can we talk later?   │
  │                     sure  ●   │
  │                   when tho ●  │
  │ ● after school? my mom's out  │
  └────────────────────────────────┘

  + Reply now
  + Tell him later
  + Leave it
</pre>
</div>

<div class="example-box">
<p class="example-box-label">Possible future genre components</p>
<table>
<thead><tr><th>Genre</th><th>Visual conventions</th><th>Critical possibilities</th></tr></thead>
<tbody>
<tr><td>SMS / text message</td><td>Speech bubbles, read receipts, typing indicators</td><td>Intimacy, surveillance, digital silence</td></tr>
<tr><td>Social media post</td><td>Avatar, username, caption, like count, comments</td><td>Performing identity, engagement mechanics</td></tr>
<tr><td>News headline</td><td>Publication name, headline, byline</td><td>Framing, media bias, authority claims</td></tr>
<tr><td>Email thread</td><td>Subject, sender, reply chain</td><td>Institutional power, formality, archiving</td></tr>
<tr><td>Search results</td><td>Blue links, snippets, sponsored labels</td><td>Algorithmic curation, what gets found / buried</td></tr>
</tbody>
</table>
</div>
```

---


## References
