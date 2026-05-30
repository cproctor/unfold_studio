# Reader-Writer Relationship UI: Wireframes

## Design Principle

The social architecture of a platform shapes what kinds of relationships are possible within it. Mainstream social media platforms are designed around attention metrics: follower counts, like counts, algorithmic amplification, trending content. These affordances reward inflammatory and attention-maximizing content and encourage users to perform for an abstract audience rather than write for specific people.

Unfold Studio's conjecture is that removing these affordances and replacing them with features that foreground specific reader-writer relationships will support identity authorship (Holland et al. 1998) and authentic community participation (Lave & Wenger 1991).

The dissertation frames this as a design choice about what a literacy space values: "What we call identities remain dependent upon social relations and material conditions. If these relations and material conditions change, they must be 'answered'" (Holland et al. 1998, p. 189). The site's social architecture is part of its material conditions.

## What the Site Omits (by design)

- **Like counts / star counts**: aggregate approval metrics
- **Follower counts / subscriber counts**: audience size metrics  
- **Trending / popular / algorithm-curated feeds**: attention-maximizing recommendation
- **Share/retweet mechanics**: virality architecture
- **Notification counts that reward frequent checking**: variable-ratio reinforcement

The absence of these features is not a limitation — it is an argument about what matters in this literacy space.

## What the Site Provides Instead

- **Direct responses**: readers write short responses to specific stories, addressed to the author
- **Reading history**: a record of what you have read, accessible to you and shared with authors whose stories you've read
- **Writer attribution on every story page**: author name is prominent, links to author profile, shows author's other stories
- **Prompt attribution**: if a story was written for a prompt, that is displayed — connecting the story to the assignment and to other stories in the same thread
- **"Also by this author"**: on story pages, surfacing the author's other work encourages readers to know writers as people with multiple works, not as sources of content

## Wireframe: Story Page — Reader-Writer Context

```
┌─────────────────────────────────────────────────────────────────┐
│ ← back                                                          │
│                                                                  │
│  BILINGUAL                                                       │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  written by  @jayxyz                                            │
│              Jay Chen · 10th grade · East High School           │
│              [see all Jay's stories →]                          │
│                                                                  │
│  written for  ◈ "Two languages" prompt                          │
│               [see other stories for this prompt →]             │
│                                                                  │
│  ▸ Play story (est. 4 min)    ▸ Read source                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Wireframe: Story Page — After Reading

```
┌─────────────────────────────────────────────────────────────────┐
│ [you finished the story]                                         │
│ ──────────────────────────────────────────────────────────────  │
│                                                                  │
│ ▸ Play again    ▸ Read source    ▸ See other paths              │
│                                                                  │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│ ¶ Leave a response for Jay                                       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                                                          │  │
│  │  [text area — response addressed to the author]          │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│  [submit response]                                              │
│                                                                  │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│ ¶ More by Jay Chen                                               │
│                                                                  │
│   [✎] The Last Day of School                                    │
│   [✎] Interview Simulation                                      │
│   [✎] 3 more →                                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

Notes:
- "Leave a response **for Jay**" — the response is addressed to a person, not posted to a feed
- No count of existing responses shown before you write (reduces social proof effects)
- The "more by Jay" section positions the author as a person with a body of work

## Wireframe: Author Profile Page

```
┌─────────────────────────────────────────────────────────────────┐
│ ♦ Jay Chen  ·  @jayxyz                                          │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│ East High School · 10th grade                                   │
│                                                                  │
│ "I write about language because I grew up with two of them."    │
│                                                                  │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│ ¶ Stories                                                        │
│                                                                  │
│   [✎] Bilingual                  4 responses · played 103×     │
│   [✎] The Last Day of School     1 response  · played 22×      │
│   [✎] Interview Simulation       2 responses · played 31×      │
│                                                                  │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│ ¶ Recently read                                                  │
│                                                                  │
│   [◈] The Last Train Home  by @marisolreads                     │
│   [◈] Saturday Morning     by @studentwriter                    │
│   [◈] 8 more →                                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

Notes:
- **No follower count, no following count** — these numbers are not displayed anywhere
- "Recently read" section makes reading public and reciprocal — it is as much part of a user's identity as their writing
- Play counts and response counts are shown for authors on their own profile (useful feedback) but not displayed as a ranking metric on public-facing story listings
- Short bio is prominent — the person is more important than the metrics

## Relationship to the Retro Aesthetic

The reader-writer UI design avoids the card-based, metric-heavy visual language of social platforms (Twitter/X cards, TikTok metrics bars, Goodreads rating stars). The flat, text-first, monospace presentation gives no visual weight to numbers. This is a subtle design argument: the metrics that are present (play counts, response counts) appear in the same visual register as the other text rather than in highlighted badges or large numerals. The design does not direct attention toward them.
