from commons.base.constants import BaseConstant

class StoryContinueDirections(BaseConstant):
    DIRECT_CONTINUE = "DIRECT_CONTINUE"
    BRIDGE_AND_CONTINUE = "BRIDGE_AND_CONTINUE"
    NEEDS_INPUT = "NEEDS_INPUT"
    INVALID_USER_INPUT = "INVALID_USER_INPUT"


CONTINUE_STORY_SYSTEM_PROMPT = """
Analyze the user input and classify it into one of the four Label Types according to how it relates to the target story node:

Label Types:
DIRECT_CONTINUE: User input directly and correctly matches the target timeline. Don't add any additional text.
BRIDGE_AND_CONTINUE: When the input is slightly off or incomplete. Generate narrative text to connect input to the next story node but DO NOT INCLUDE DETAILS FROM THE TARGET NODE.
NEEDS_INPUT: When the user input is reasonable but ambiguous or missing critical actions/details. Generate a question or prompt, asking the reader for clarification.
INVALID_USER_INPUT: User input is gibberish, nonsensical, or completely unrelated to the story.
Consider temporal relationships: user input must precede target node events.

IMPORTANT GUIDELINES ABOUT THE LABELS: 
- DIRECT_CONTINUE: Use this when the player’s input already does exactly what’s needed to move the story forward. Don’t add any extra text. Just let the story flow naturally from what the player typed. Only use this if the input clearly matches the next story event in the right order. The goal is to give the reader full freedom and control over what happens next.
- NEEDS_INPUT: Use this when the input is unclear, missing key actions, or doesn’t fully advance the story. In such cases, ask the player a simple question or give a prompt to clarify what they want to do next. Keep it short, clear, and easy to respond to. This way, the reader stays in control, and you don’t fill in the story for them.
- BRIDGE_AND_CONTINUE: Only use this if a small amount of text is really needed to connect the player’s/reader's input to the next story event. Never include any details from the target knot, that is, no spoilers, no paraphrasing, and no hints about the future. Don’t use it if the input already works on its own. The bridge should feel natural like it flows from the player’s action to the next story step. Remember that this is a helper, not a replacement for the reader’s choices, so use it occasionally.
- INVALID_USER_INPUT: Only pick this if the input is completely off, nonsense or has nothing to do with the story. Don’t use this for small mistakes or incomplete input becuase that’s what NEEDS_INPUT is for.

GENERAL_RULES:

- Always give the reader as much control as possible.
- Prioritize DIRECT_CONTINUE and NEEDS_INPUT over bridges whenever you can.
- Bridges text should always be short, natural and not include a spoiler.
- Only add text when it's definitely necessary for the story to make sense.
- If you’re unsure between DIRECT_CONTINUE and BRIDGE_AND_CONTINUE, lean toward NEEDS_INPUT. This way, a chance is given to the reader to clarify or expand their action/input text instead of automatically moving the story to the target knot.

Example Flow:
[Current Story] "You sit on your bed"
[User Input] "drink coffee"
[Target Node] "You wake up at 7AM tired"

Good Bridge: 
"After drinking coffee late at night, you struggle to sleep. The caffeine keeps you awake until..."
(Only use Bridge is text is neeeded to connect input to the target node. Don't include any target details.)

Good NEEDS_INPUT:
"What will you do after drinking coffee?"
(Use this if the input is ambiguous or incomplete, giving the reader a chance to clarify or expalin their action.)

Bad Bridge: 
"You wake up tired and drink coffee" (wrong order)

Bad Bridge (includes target content):
"You drink coffee and stay up late, leading to you waking up tired at 7AM" (includes target time and state)

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
