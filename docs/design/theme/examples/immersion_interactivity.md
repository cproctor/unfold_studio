# Immersion / Interactivity Toggle: Wireframes

## The Theoretical Tension

Ryan (2001) contrasts two rhetorical modes in interactive storytelling:

- **Immersion**: the reader constructs a world of meanings around herself, experiencing being *inside* the story. The interface recedes; the story world is total.
- **Interactivity**: the reader is aware of the interface, of her own choices, of the simulation running beneath the text. The interface is *present*; the story world is something she is operating.

These modes are in tension — heightened interactivity breaks immersion; deep immersion suppresses the meta-awareness that makes interactivity interesting. But Unfold Studio's design conjecture is that this tension, made productive, is *the point*: it is how readers begin to see stories as made objects, and how they begin to want to make objects themselves.

This is also the core mechanism of permeable media (Proctor, Paljor, & Bhatt 2025): the "extending into the medium" dimension happens exactly at the boundary where immersion shades into interactivity, where a reader notices the mechanism and wonders how it works.

## Current Interface (as-is)

Currently, Unfold Studio shows story source code in a separate tab or split view that the user must explicitly navigate to. The story play interface is clean but does not actively encourage oscillation. The split view is functional but not aesthetically integrated.

## Wireframe: Immersive Mode (story play)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                    [◈ source]   │
│                                                                  │
│                                                                  │
│   You walk into the classroom and immediately know something     │
│   is different. The desks are arranged in a circle.             │
│                                                                  │
│   Ms. Reyes is standing at the front. She is not smiling.       │
│                                                                  │
│   ──────────────────────────────────────────────────────────    │
│                                                                  │
│   + Sit in the circle                                           │
│   + Linger by the door                                          │
│   + Ask what's going on                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

Notes:
- Minimal chrome; story text centered with generous margins
- The `[◈ source]` button is always visible but subtle — one click away, not intrusive
- Choice options use `+` prefix, mirroring Ink source syntax (a small but consistent detail)
- No progress bar, no chapter count, no other meta-information that breaks the story world

## Wireframe: Reflective Mode (split view)

```
┌──────────────────────────────┬──────────────────────────────────┐
│ STORY                        │ SOURCE                           │
│ ──────────────────────────── │ ──────────────────────────────── │
│                              │                                  │
│ You walk into the classroom  │ === start ===                    │
│ and immediately know         │ You walk into the classroom      │
│ something is different. The  │ and immediately know something   │
│ desks are arranged in a      │ is different. The desks are      │
│ circle.                      │ arranged in a circle.            │
│                              │                                  │
│ Ms. Reyes is standing at     │ Ms. Reyes is standing at the     │
│ the front. She is not        │ front. She is not smiling.       │
│ smiling.                     │                                  │
│                              │ + Sit in the circle              │
│ ────────────────────────── ► │   -> circle                      │
│                              │ + Linger by the door             │
│ + Sit in the circle    →     │   -> door                        │
│ + Linger by the door   →     │ + Ask what's going on           │
│ + Ask what's going on  →     │   -> ask                         │
│                              │                                  │
└──────────────────────────────┴──────────────────────────────────┘
```

Notes:
- The split is symmetrical; source and story scroll in sync
- When the reader makes a choice, both panes advance together
- Arrows (`→`) in the story pane align with `-> knot` redirects in the source pane
- The reader can watch, in real time, how her choices route the story
- No syntax highlighting needed — the monospace font and consistent indentation makes the structure legible

## Implementation Approaches

**Option A: Persistent toggle** — A `[◈ source]` button always visible in story view, switching between full-width story and split view. Simple to implement; most explicit.

**Option B: Progressive reveal** — Story starts in immersive mode; after the reader completes a story, a "how was this made?" prompt appears, offering to replay with source visible. Preserves immersion on first read; rewards curiosity.

**Option C: Story-authored reveal** — The Ink author can insert a tag or knot that triggers source visibility at a dramatic moment. (E.g., "at this point, you can see that the story has branched in a way that cannot be undone.") Most sophisticated; requires author support.

The conjecture map points toward **Option B or C** as most likely to produce the oscillation effect — they make the reveal meaningful rather than always-available. Option A is the safer implementation for the initial version.

## Relationship to the Retro Aesthetic

The split-view interface is a classic programming environment design (going back to early text editors and IDEs). Its use here connects story-reading to the history of people looking at code. The monospace font throughout means the source view does not feel like a foreign mode — it is the same visual language as the story, just with more structure visible.

This is the aesthetic argument for monospace fonts in story display: when the reading font and the source font are the same, the transition between reading and source feels like zooming out, not switching modes. The story is always already a text that could be read as code.
