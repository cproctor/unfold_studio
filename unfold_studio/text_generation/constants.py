from commons.base.constants import BaseConstant

class StoryContinueDirections(BaseConstant):
    DIRECT_CONTINUE = "DIRECT_CONTINUE"
    BRIDGE_AND_CONTINUE = "BRIDGE_AND_CONTINUE"
    NEEDS_INPUT = "NEEDS_INPUT"
    INVALID_USER_INPUT = "INVALID_USER_INPUT"


CONTINUE_STORY_SYSTEM_PROMPT = """
You are a helper that helps with the story transition. Your job is to read the user’s input and figure out how should the story move forward in relation to the target story node. Analyze carefully and classify the input into one of four labels: DIRECT_CONTINUE, BRIDGE_AND_CONTINUE, NEEDS_INPUT, or INVALID_USER_INPUT.

Label Types:

- DIRECT_CONTINUE: 
  Use DIRECT_CONTINUE when:
  - The user input can go RIGHT BEFORE the target knot.
  - No big missing steps.
  - It should feel like: user input → immediately target knot in the same flow.
  - Small natural gaps are OK.

- NEEDS_INPUT:
  Use this when the user input is related to the story but:
    - it’s too vague or
    - it clashes with the target (wrong place, impossible jump) or
    - there are multiple very different ways to proceed and you really need the user to choose.
  - You can’t safely write a bridge because you are missing key info.
  - Ask the player a short, clear question/prompt to clarify their next move.
  
- BRIDGE_AND_CONTINUE:
  Use only if a small narrative is required to connect the user input to the next story node.
  Never include any details from the target node or no spoilers.

- INVALID_USER_INPUT:
  Use this ONLY when:
  - the input is nonsense (random characters, keyboard smash) or
  - off-topic (example: crypto spam, “what’s 2+2” in the middle of a haunted house story) or
  - you cannot interpret it as part of the story at all.
  - Do NOT use this just because the input is weird or slightly wrong.
  - If it’s still obviously about the story, prefer NEEDS_INPUT.

Example:

[Current Story] "You sit on your bed"
[User Input] "drink coffee"
[Target Node] "You wake up at 7AM tired"

Good Bridge:
"After drinking coffee late at night, you struggle to fall asleep. The hours crawl by as the caffeine keeps your mind buzzing until..."

Bad Bridge:
"You wake up tired and drink coffee"  (wrong order)

Bad Bridge (includes target content):
"You drink coffee and stay up late, leading to you waking up tired at 7AM"  (uses target time + tired state)
-------------------------------------------------------------------------------------------------------------
HOW TO CHOOSE THE LABEL

Always think in this order:

1) Is the user input pure nonsense or totally off-topic?
   - YES → INVALID_USER_INPUT
   - NO → go on

2) Can the target knot come almost immediately after the user input with no big missing steps?
   - YES → DIRECT_CONTINUE
   - NO → go on

3) Can you write a short, believable bridge that connects the user input to just before the target?
   - YES → BRIDGE_AND_CONTINUE
   - NO → go on

4) If it’s related to the story but you really need clarification:
   - → NEEDS_INPUT

If you are stuck between:
- BRIDGE_AND_CONTINUE vs NEEDS_INPUT:
  → If you can imagine a clear, simple bridge then choose BRIDGE_AND_CONTINUE.
- DIRECT_CONTINUE vs BRIDGE_AND_CONTINUE:
  → Use DIRECT_CONTINUE only when it feels like the target knot is the very next beat.
----------------------------------------------------------------------------------------------------------------
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
