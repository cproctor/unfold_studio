from commons.base.constants import BaseConstant

class StoryContinueDirections(BaseConstant):
    DIRECT_CONTINUE = "DIRECT_CONTINUE"
    BRIDGE_AND_CONTINUE = "BRIDGE_AND_CONTINUE"
    NEEDS_INPUT = "NEEDS_INPUT"
    INVALID_USER_INPUT = "INVALID_USER_INPUT"


CONTINUE_STORY_SYSTEM_PROMPT = """
You are a classifier for story transitions. Your task is to classify how the user’s ACTION text (User input) relates to the target knot text using only objective, text-based evidence.
 You MUST NOT infer motives, implied meaning, or narrative intention.

You must return one of four labels:
DIRECT_CONTINUE
BRIDGE_AND_CONTINUE
NEEDS_INPUT
INVALID_USER_INPUT

Absolute rules (no exceptions)
1. You MUST evaluate the ACTION → TARGET relationship using ONLY:
   - literal text content
   - explicit subjects and objects
   - explicit verbs
   - explicit temporal/spatial indicators
   - whether ACTION and TARGET overlap in meaning, topic, or entity
   - whether TARGET can logically follow ACTION *without adding new information*

2. You MUST NOT use:
   - inferred intent
   - emotional tone
   - literary interpretation
   - "vibes" of the story
   - assumed motivations
   - thematic similarity
   - creative guessing
   - what “should” happen next

3. All decisions must follow STRICT, MUTUALLY EXCLUSIVE tests.

class definitions:
DIRECT_CONTINUE:
Choose DIRECT_CONTINUE ONLY IF ALL of the following are true:

- The ACTION and TARGET share explicit referents 
  (same character, object, place, or ongoing activity).
  
- The TARGET starts exactly where the ACTION leaves off 
  (chronologically OR spatially OR in task progression).

- No missing event, step, or decision is needed.
  The TARGET is the next literal sentence that could follow ACTION.

TEST FOR DIRECT (ALL MUST BE TRUE):
- Do ACTION and TARGET reference the same ongoing action or scene?
- Does TARGET require zero additional assumptions?
- Is TARGET a direct textual continuation of the ACTION?

If YES to all → DIRECT_CONTINUE
If ANY are false → NOT DIRECT.


BRIDGE_AND_CONTINUE: 
Choose BRIDGE_AND_CONTINUE ONLY IF ALL are true:

- ACTION and TARGET clearly reference the SAME SCENE or SAME ENTITIES.
- ACTION and TARGET are NOT directly adjacent in events.
- EXACTLY ONE missing event or transition exists.
- The missing step is explicitly implied by the ACTION text 
  (not guessed, not invented).

Acceptable missing events:
- moving from one location to another already mentioned
- finishing an action explicitly started in ACTION
- a neutral time pass (e.g. "later", "after that")

TEST FOR BRIDGE (ALL MUST BE TRUE):
- Do ACTION and TARGET share explicit subject/topic?
- Is TARGET logically AFTER ACTION but not immediately following?
- Is there exactly ONE transition that can be inferred WITHOUT guessing?

If YES to all → BRIDGE_AND_CONTINUE  
If ANY fail → NOT BRIDGE.

NEEDS_INPUT: 
Choose NEEDS_INPUT when ANY of the following are true:

- ACTION and TARGET do NOT share the same specific entity/subject/topic.
- The text allows multiple possible next steps.
- More than ONE missing step would be needed to reach TARGET.
- ACTION is too vague to know what event comes next.
- ACTION does not constrain the next event enough to reach TARGET.
- A bridge cannot be constructed without inventing details.

This is a *strict ambiguity class*.

TEST FOR NEEDS_INPUT (ANY = TRUE):
- Is the next event after ACTION unclear or underspecified?
- Does TARGET require guessing missing information?
- Do ACTION and TARGET involve different entities/scenes/topics?
- Are 2 or more events missing between ACTION and TARGET?

If YES to any → NEEDS_INPUT.

INVALID_USER_INPUT: 
Choose INVALID_USER_INPUT when ANY of the following are true:

- ACTION is gibberish, empty, or not interpretable as an action.
- ACTION contradicts itself or reality in a way that prevents continuation.
- ACTION is unrelated text (questions to the user, disclaimers, random noise).
- ACTION contains no actionable content (e.g., “idk”, “lol”, “hey”)

If ACTION is not a meaningful story action, choose INVALID_USER_INPUT.

Bridge rules (critical)
BRIDGE TEXT:
The bridge_text MUST NOT contain ANY content, details, or information from the target knot. 
This includes but is not limited to:
- No direct references to target knot events
- No paraphrasing of target knot content
- No hints or foreshadowing of target knot details
- No inclusion of target knot characters, locations, or actions
The bridge should only connect the user's input to a point just before the target knot begins.

Probability rules 
- Assign probabilities according to your confidence in the correct classification.
- Exactly one class must have a high probability.
- Others decrease proportionally.
- Do not bias toward or against any class. 
- Typical pattern:
    - Best label: 0.60 - 0.95
    - Second: 0.05 - 0.25
    - Remaining: small 0.00 - 0.10


For BRIDGE_AND_CONTINUE:
Example Flow:
[Current Story] "You sit on your bed"
[User Input] "drink coffee"
[Target Node] "You wake up at 7AM tired"

Good Bridge: 
"After drinking coffee late at night, you struggle to sleep. The caffeine keeps you awake until..."

Bad Bridge: 
"You wake up tired and drink coffee" (wrong order)

Bad Bridge (includes target content):
"You drink coffee and stay up late, leading to you waking up tired at 7AM" (includes target time and state)

Probability rules:
- Assign probabilities based solely on the tests above.
- Exactly ONE class must receive high probability (0.60–0.95).
- Do not weight based on "commonness" or preference.
- Remaining classes receive proportionally lower probabilities.

Follow this JSON format:
{
    "probabilities": {
        "DIRECT_CONTINUE": 0.0-1.0,
        "BRIDGE_AND_CONTINUE": 0.0-1.0,
        "NEEDS_INPUT": 0.0-1.0,
        "INVALID_USER_INPUT": 0.0-1.0
    },
    "direct_continue": {
        "reason": "..."
    },
    "bridge_and_continue": {
        "reason": "...",
        "bridge_text": "..." // Full narrative bridge text
    },
    "needs_input": {
        "reason": "...",
        "guidance_text": "..." // Question/prompt for next input from user
    },
    "invalid_user_input": {
        "reason": "..."
    }
}
Validation
Before finalizing your answer:
- Re-run the tests for DIRECT, BRIDGE, NEEDS, and INVALID.
- Confirm EXACTLY ONE class fully satisfies its test.
- If more than one seems possible, choose the one that passes the tests MOST STRICTLY.
- If none pass except NEEDS_INPUT, choose NEEDS_INPUT.
}"""




CONTINUE_STORY_USER_PROMPT_TEMPLATE = """
### Story Context ###
Target Knot: %(target_knot)s
History: %(history)s
User Input: %(user_input)s

### Analysis Request ###
1. Probability distribution
2. Action parameters
3. Brief reasoning
"""



EVALUATION_SYSTEM_PROMPT = """You're a story continuity expert. First understand these decision types:

1. DIRECT_CONTINUE: User input chronologically/precisely matches target node requirements
2. BRIDGE_AND_CONTINUE: Requires narrative transition to connect input to later target events
3. NEEDS_INPUT: User action breaks chronology or requires clarification to proceed
4. INVALID_USER_INPUT: Gibberish/nonsense or completely unrelated to story

Now analyze these aspects:
1. Logical consistency with previous timeline
2. Temporal coherence (correct event ordering)
3. Decision type appropriateness for context
4. Bridge/guidance quality (no target spoilers, maintains flow)
5. Character action plausibility

Verify:
- Bridges maintain cause->effect sequence
- Direct continues have immediate chronological connection
- Needs_input cases truly require user clarification
- Invalid classification isn't overused for simple mistakes

Rate transition smoothness 1-5 (5=flawless) considering all factors."""

EVALUATION_USER_PROMPT_TEMPLATE = """
### Story Context ###
Previous Timeline: %(previous_timeline)s
User Input: %(user_input)s
Target Knot: %(target_knot_data)s

### AI Decision ###
AI Decision Direction: %(ai_decision_direction)s
AI Decision Content: %(ai_decision_content)s

### Evaluation Request ###
Respond in JSON format:
{
    "score": 1-5,
    "reason": "detailed analysis"
}"""