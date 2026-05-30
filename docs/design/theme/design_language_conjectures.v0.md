# Conjecture Mapping Unfold Studio's Design Language

## High-Level Conjecture

A site's *design language* — its coherent system of visual, typographic, interaction, and social design choices — is not decorative. The embodiments of a learning environment shape what practices, identities, and critical possibilities are available to participants (Sandoval 2014; Proctor, Paljor, & Bhatt 2025). The perceived affordances of the site shape the rhetorical practices of its users, which shape the meanings and identities enacted there, which shape what is critically possible.

Unfold Studio's design language should be principled: following the permeable media framework (Proctor, Paljor, & Bhatt 2025), it should invite users in, support them in making the practice part of themselves, and allow them to grow. Drawing on computational literacies (Kafai & Proctor 2022), it should support cognitive, situated, and critical engagement.

**Conjecture:** *A design language that is retro and craft-centered — revealing rather than concealing its own construction — combined with social design that emphasizes authentic reader-writer relationships over metrics-driven engagement, will support users in developing positive and expanded CS identities and engaging in critical computational literacies through interactive storytelling.*

## Conjecture Map

{% conjectures(title="Conjecture Map: Unfold Studio Design Language") %}

retro[Retro monospace aesthetic]
icons[Playful pixel icons]
toggle[Immersion / interactivity toggle]
rwui[Reader-writer relationship UI]
errors[Warm, in-voice error states]
genres[Embedded media genre UI]

hackable[Perceived permeability of site infrastructure]
nostalgia[Evocation of pre-commercial web]
csid_q[Challenge to narrow CS identity]
craft[Sense of craft and human care]
oscil[Oscillating reader / author perspective]
demetrics[Writing without metrics pressure]
normalized[Failure normalized as part of craft]
progdisc[Authentic CS patterns at low complexity]
novelized[Ironic framing of embedded genres]

perm[Permeable media engagement]
pos_csid[Positive / expanded CS identity]
belong[Sense of belonging in literacy space]
cdm[Critical discourse modeling]
idauth[Identity authorship]

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

{% end %}

## Design Features (Embodiments)

### 1. Retro Monospace Aesthetic

**What we will do:** Use a fixed-width (monospace) font in most contexts, particularly for story content, navigation, and UI chrome. Use a near-monochrome palette with minimal accent color. The overall visual feel will be reminiscent of Web 1.0 or early terminal interfaces—deliberately non-corporate and non-polished.

**Mediating processes:**

*Perceived permeability of site infrastructure.* A smooth, polished interface (exemplified by Apple's design philosophy) presents a perfect surface that conceals its construction. The retro aesthetic communicates instead that there is not much distance between what you see and how it works. The visible structure and rough edges invite users to look beneath the surface—to ask "how does this work?" This aligns with permeable media (Proctor, Paljor, & Bhatt 2025), in which the interface invites users to extend themselves into the medium and come to understand it.

*Evocation of pre-commercial web.* The Web 1.0 aesthetic may evoke—for users who experienced it and for users who have absorbed its cultural mythology—an era of more authentic, creative, and human online interaction before the commodification of attention (Zuboff 2019). This temporal association positions Unfold Studio as an alternative to surveillance capitalism platforms.

*Challenge to narrow CS identity.* The site reads as a CS artifact (monospace fonts, structured layout) while the content—stories about identity, relationships, social experience—challenges the stereotype that CS is impersonal and only for certain people. This may support users who don't see themselves in mainstream CS culture in building more expansive CS identities (Kafai & Proctor 2022).

**Precedent:** The [p5.js web editor](https://editor.p5js.org/) uses a similar monospace-first, split-pane layout that signals "creative coding" without corporate polish.

**Font confirmed:** The staging site (staging.unfoldstudio.net) has already established **Monaspace Neon** as the site's primary font — a modern, high-quality monospace from GitHub's Monaspace family with a distinctive "neon" texture that reads well at text sizes. This is the right choice. The Monaspace family (Neon, Argon, Xenon, Krypton, Radon) offers a vocabulary of related but distinct monospace faces for different contexts.

**Color system confirmed:** The staging site uses near-black `#231F20` (slightly warm, not pure black), white backgrounds, yellow `#ffe564` as the primary CTA color, and purple `#9494ff` as a secondary action color. This palette is specific, retro, and non-generic.

**Background texture confirmed:** The staging site uses a repeating SVG grid tile (graph paper texture) as the page background, and dithered bitmap images (gradient circle, rectangle, sphere) as decorative elements. Dithering — converting smooth gradients to limited-palette dot patterns — extends the "visible construction" principle from typography into imagery.

See: [examples/staging_site_analysis.md](examples/staging_site_analysis.md)

![Retro aesthetic wireframe and precedent](examples/retro_aesthetic.md)

---

### 2. Playful Pixel Icons

**What we will do:** Design custom pixel art icons for navigation, story metadata, and decorative elements (pilcrows, section markers, category indicators). These will be in the tradition of Susan Kare's original Macintosh icons, the original NES *Legend of Zelda*'s item and UI icons, and *Undertale*'s interface elements—not generic icon libraries.

**Already implemented:** The staging site's navigation buttons are fully custom SVG pixel-art shapes — not CSS rectangles with border-radius, but hand-drawn SVG polygons with a stepped 3D shadow, pixel-perfect chamfered corners, and specific accent colors. This is exactly the craft-object approach described here. The full icon system should extend this vocabulary to all interactive elements and decorative marks. Note: the SVG approach is expressive but fragile — each button is a bespoke file with hard-coded dimensions. The same visual effect (chamfered corners via `clip-path: polygon(...)`, stepped shadow via `box-shadow` with zero blur or a pseudo-element offset) can be achieved robustly in CSS, making it trivially themeable, responsive, and applicable to any element without per-instance SVG authoring.

**Mediating processes:**

*Sense of craft and human care.* Pixel art icons communicate that someone invested time in this specific space. They resist the visual language of corporate tech (Material Design, Font Awesome) and signal a community of makers rather than a product. This models a valuing of craft that may carry over into users' own story-making—the site demonstrates that careful, detailed work is worth doing.

*Anti-corporate belonging.* The whimsical quality of hand-crafted icons positions the site as a place where idiosyncrasy is valued—where you do not need to be polished or professional to belong. This lowers the stakes for users who might feel intimidated by coding or by "real" writing.

*Worldbuilding through iconography.* As in Zelda or Undertale, icons carry narrative weight—they are part of the site's story about itself. This contributes to a sense of place and identity continuity across the site, making it a figured world (Holland et al. 1998) with its own aesthetic culture.

![Craft icon examples and precedents](examples/craft_icons.md)

---

### 3. Immersion / Interactivity Toggle

**What we will do:** The story-reading interface will support oscillation between an immersive mode (full-focus reading, minimal UI chrome) and a reflective mode (split-view with source code visible, interface annotations, "how this works" affordances). The exact implementation—explicit toggle, progressive reveal, persistent side panel—is to be determined through prototyping.

This design feature directly enacts the tension Ryan (2001) identifies between immersion (being drawn into the story world) and interactivity (heightened awareness of the interface). Rather than resolving this tension, the site makes it productive: readers can move between being inside the story and understanding how it works.

**Mediating processes:**

*Oscillating reader/author perspective.* When readers can see a story's source code alongside its rendered form, they simultaneously inhabit reader and author/programmer positions. They discover that the story they are experiencing is also a text they could have written or modified. This is the "extending into the medium" dimension of permeable media (Proctor, Paljor, & Bhatt 2025)—the boundary between reader and author becomes permeable.

*Critical awareness of constructed interfaces.* Making the interface visible at key moments teaches users that all interfaces are constructed artifacts with specific affordances and constraints. The habit of asking "how does this work?" when encountering an engaging interface is a form of critical computational literacy—it is how students come to understand that the smooth surface of social media is a designed object, not a natural fact (Kafai & Proctor 2022).

![Immersion/interactivity wireframes](examples/immersion_interactivity.md)

---

### 4. Reader-Writer Relationship UI

**What we will do:** Design the social architecture of the site to foreground human connections between specific readers and writers, rather than aggregated metrics. Author attribution is prominent; story pages surface who has read and responded; profiles show reading and writing history in dialogue; comments are addressed to the author rather than broadcast to a feed. The site deliberately omits features that reward attention-maximizing behavior: no like counts, no follower counts, no trending sections.

**Mediating processes:**

*Writing without metrics pressure.* When the site does not offer follower counts or like buttons, writers are less likely to optimize for attention-maximizing content and more likely to write for specific imagined readers. This shifts the social frame from "content creation for an audience" to "writing for people"—closer to the dialogic, rhetorical view of writing (Bakhtin 1981; Proctor et al. 2026) and further from the extractive dynamics of commercial platforms.

*Authentic community participation.* Reader-writer relationships that are personal rather than metric-mediated support the development of an authentic community of practice (Lave & Wenger 1991; Holland et al. 1998). Users are more likely to develop identities as participants in a literary community than as content creators or followers. This supports the situated framing of computational literacies (Kafai & Proctor 2022): learning to write interactive stories means becoming someone who writes interactive stories for other people who read them.

![Reader-writer UI wireframes](examples/reader_writer_ui.md)
