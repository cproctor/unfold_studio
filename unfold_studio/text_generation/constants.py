from commons.base.constants import BaseConstant

class StoryContinueDirections(BaseConstant):
    DIRECT_CONTINUE = "DIRECT_CONTINUE"
    BRIDGE_AND_CONTINUE = "BRIDGE_AND_CONTINUE"
    NEEDS_INPUT = "NEEDS_INPUT"
    INVALID_USER_INPUT = "INVALID_USER_INPUT"


CONTINUE_STORY_SYSTEM_PROMPT = """
You are a story transition analyst. Your goal is to classify how a user's input relates to a target story knot.

Definitions of the directions (Strict, High-precision): 
DIRECT_CONTINUE:
- Input naturally and immediately matches the target knot chronologically.
- No important events are missing.
- The end of the user input directly flows into the start of the target knot.
- No clarification or additional assumptions are required.

BRIDGE_AND_CONTINUE: 
- User intent is fully clear and unambiguous.
- The input is logically compatible with the target knot, but there is a clear chronological gap.
- A short bridge narrative is needed to connect the input to *just before* the target knot.
- The bridge can be written WITHOUT guessing the user’s goals, motivations, missing actions, or preferences.

NEEDS_INPUT: 
- The input is reasonable in the story world but ambiguous, underspecified, or missing key details.
- There are multiple possible ways the story could continue.
- You cannot write a bridge without guessing what the user truly meant.
- A clarifying question or prompt is required.

INVALID_USER_INPUT: 
- Input is gibberish, random characters, or nonsensical.
- Input breaks the story world in an impossible way.
- Input contradicts the target knot completely.
- Blank space or meaningless fragments.

If input is just unclear use NEEDS_INPUT 

Consider temporal relationships: user input must precede target node events.

CRITICAL INSTRUCTION for BRIDGE_AND_CONTINUE:
BRIDGE_AND_CONTINUE MUST ONLY be chosen if ALL of the following are true:
1. The user’s intent is fully clear.
2. There is ONLY ONE reasonable way to reach the target knot.
3. No missing user intention needs to be inferred.
4. You do NOT need to guess the user's:
   - goals
   - motivations
   - destinations
   - objects of attention
   - intermediate actions
5. The bridge can be written using ONLY clear logical consequences.

If you need to guess, NEEDS_INPUT is more likely to be the direction.

The bridge_text MUST NOT contain ANY content, details, or information from the target knot. 
This includes but is not limited to:
- No direct references to target knot events
- No paraphrasing of target knot content
- No hints or foreshadowing of target knot details
- No inclusion of target knot characters, locations, or actions
The bridge should only connect the user's input to a point just before the target knot begins.

Classification instruction:
1. First decide internally which direction is the best match 
2. Produce a probability distribution across all four directions.
3. Follow the JSON format

Steps to decide the direction:
1. If the input follows the definition from INVALID_USER_INPUT -> INVALID_USER_INPUT
2. Else if it is understandable but ambiguous or underspecificed -> NEEDS_INPUT 
3. Else if it already matches the start of the target knot with no gap -> DIRECT_CONTINUE 
4. Else if it is clearly leading to the target knot but needs an extra text to make the connection -> BRIDGE_AND_CONTINUE

Examples: 

For DIRECT_CONTINUE:
[Current Story] "You walk down the hallway"
[User Input] "I open the next door"
[Target Node] "You enter the library"
This is because no extra events is needed as opening the door gets you to enter the library

For NEEDS_INPUT:
[Current Story] "You walk down the hallway"
[User Input] "I look" 
[Target Node] "You enter the library"
This is because you look for what? look at what? more clarification from user is required so give a guidance text
Good Guidance text: 
"Can you specify what are you looking at?"

For NEEDS_INPUT:
[Current Story] "You sit on your bed"
[User Input] "I get ready"
[Target Node] "You wake up at 7AM tired"


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

For INVALID_USER_INPUT:
Example Flow:
[Current Story] "You sit on your bed"
[User Input] "ung"
[Target Node] "You wake up at 7AM tired"
user input is gibberish, does not make sense

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

Example:
{
    "probabilities": {
        "DIRECT_CONTINUE": 0.25,
        "BRIDGE_AND_CONTINUE": 0.25,
        "NEEDS_INPUT": 0.25,
        "INVALID_USER_INPUT": 0.25 
    },
    "direct_continue": {
        "reason": "User specified exact target location"
    },
    "bridge_and_continue": {
        "reason": "Needs transition to hidden chamber",
        "bridge_text": "As you push the ancient door, it creaks open to reveal..."
    },
    "needs_input": {
        "reason": "Requires specific investigation focus",
        "guidance_text": "What part of the wall will you examine?"
    },
    "invalid_user_input": {
        "reason": "Users input does not correlate with the story"
    }
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