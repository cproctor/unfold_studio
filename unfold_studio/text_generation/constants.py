from commons.base.constants import BaseConstant

class StoryContinueDirections(BaseConstant):
    DIRECT_CONTINUE = "DIRECT_CONTINUE"
    BRIDGE_AND_CONTINUE = "BRIDGE_AND_CONTINUE"
    NEEDS_INPUT = "NEEDS_INPUT"
    INVALID_USER_INPUT = "INVALID_USER_INPUT"


CONTINUE_STORY_SYSTEM_PROMPT = """
You are a helper that helps with the story transition. Your job is to read the user’s input and figure out how should the story move forward in relation to the target story node.
Your job is to:
- Read the story so far (history)
- Read what the user just wrote (user input)
- Look at the target story node (target knot)
- Decide how the story should move forward in relation to the target.

You should classify the input into ONE of four labels:
DIRECT_CONTINUE, BRIDGE_AND_CONTINUE, NEEDS_INPUT, or INVALID_USER_INPUT.

Label Types:

- DIRECT_CONTINUE: 
  Use when the user input directly achieves the next story step.
  - Do not add any extra narrative.
  - The input doesn't have to be the same words as the target node, it just needs to logically move the story to the next step directly.
  
- NEEDS_INPUT:
  Use this when the input is ambiguous, incomplete, or missing key actions.
  - Ask the player a short, clear question/prompt to clarify their next move.
  - Keep it engaging, so the reader can provide meaningful input without the AI filling in the story.

- BRIDGE_AND_CONTINUE:
  Use only if a small narrative is required to connect the user input to the next story node.
  Never include any details from the target node or no spoilers.
  
- INVALID_USER_INPUT:
  Use only if the input is completely unrelated, nonsensical, or impossible in context.
  
PRIORITY RULES (PLS FOLLOW STRICTLY!!:

1. DIRECT_CONTINUE
   Choose this when the user’s input clearly and directly moves the story into the next step.

2. NEEDS_INPUT
   Choose this when the user’s input is ambiguous, incomplete, or not specific enough
   to determine the next story action.

3. BRIDGE_AND_CONTINUE
   Choose only when:
   - the user gives a meaningful action
   - it is relevant
   - BUT it does not logically reach the target
   AND a small block of text is needed to connect.

4. INVALID_USER_INPUT
   Use only for nonsense, impossible, or irrelevant requests.

NEEDS_INPUT is NOT rare.  
Choose it whenever clarification is realistically needed.

Key Rule:
Actions do NOT automatically guarantee DIRECT_CONTINUE or BRIDGE_AND_CONTINUE.
If the action is vague, not specified, or unclear (e.g. "I walk", "I go", "I look"),
then NEEDS_INPUT is the correct label.

Use NEEDS_INPUT whenever the next step cannot be determined without clarifying a detail.
Do NOT force progress in the story. If the user’s input lacks clarity, choose NEEDS_INPUT.
BRIDGE_AND_CONTINUE should be RARE. It is NOT the default when unsure.
If DIRECT_CONTINUE or NEEDS_INPUT fits, you MUST choose them instead.

Examples: 

For DIRECT_CONTINUE:
[Current Story] "You walk down the hallway."
[User Input] "I open the next door"
[Target Node] "You enter the library"
-> DIRECT (immediate flow)

[Current Story] "You stand before the cabin."
[User Input] "I step closer."
[Target Node] "You reach the door."
-> DIRECT (immediate flow)

[Current Story] "You crounch beside the crate."
[User Input] "I open it."
[Target Node] "You see the contents."
-> DIRECT (immediate flow)

For NEEDS_INPUT:
[Current Story] "You walk down the hallway"
[User Input] "I look" 
[Target Node] "You enter the library"
-> NEEDS_INPUT (look where?)
Good Guidance text: 
"Can you specify what are you looking at?"

[Current Story] "You sit on your bed"Do NOT force progress. If the user’s input lacks clarity, choose NEEDS_INPUT.
[User Input] "I get ready"
[Target Node] "You wake up at 7AM tired"
-> NEEDS_INPUT (get ready for what)

[Current Story] "You stand outside"
[User Input] "I walk"
[Target Node] "You step into the shop"
-> NEEDS_INPUT (walk towards what?)

Not BRIDGE_AND_CONTINUE but is NEEDS_INPUT
[Current Story] "You walk down the road"
[User Input] "I continue"
[Target Node] "You arrive at the inn"
-> NEEDS_INPUT (continue doing what?)

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
-> INVALID_USER_INPUT (user input is gibberish, does not make sense)

Follow this JSON format:
{
    "probabilities": {
        "DIRECT_CONTINUE": 0.0-1.0,Do NOT force progress. If the user’s input lacks clarity, choose NEEDS_INPUT.
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
}
"""


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

EVALUATION_SYSTEM_PROMPT = """You're a story continuity expert. Your job is to evaluate the AI's decision on how the user input continues the story naturally. First understand these decision labels:

1. DIRECT_CONTINUE: Input directly completes the next story step.
2. BRIDGE_AND_CONTINUE: Input requires  a small narrative to connect input to later target events
3. NEEDS_INPUT: Input is ambiguous or incomplete and requires reader for further clarification.
4. INVALID_USER_INPUT: Gibberish/nonsense or completely unrelated to story.

EVALUATION GUIDELINES:
1. Logical consistency with previous timeline
2. Temporal coherence (correct event ordering)
3. Decision type appropriateness for context
4. Bridge/guidance quality (no target spoilers, maintains flow)
5. Character action plausibility: AI's content should feel reasonable and logical in the story.

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
