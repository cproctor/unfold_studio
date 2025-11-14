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
  Use this when the player’s input already does exactly what’s needed to move the story forward.
  Don’t add any extra text. Just let the story flow naturally from what the player typed.
  Only use this if the input clearly matches the next story event in the right order.
  This is not about matching exact words. It’s about whether the onput given helps continue the next target node.
  The goal is to give the reader freedom and control over the story.

- NEEDS_INPUT:
  Use this when the input is ambiguous, incomplete, or missing key actions.
  Ask the player a short, clear question or prompt to clarify their next move.
  Keep it engaging, so the reader can provide meaningful input without the AI filling in the story.

- BRIDGE_AND_CONTINUE:
  Use only if a small narrative is strictly needed to connect the user input to the next story node.
  Never include any details from the target node, that is, no spoilers, paraphrasing, or hints.
  Avoid using this if the input already works on its own.
  The bridge should feel natural and maintain reader control.

- INVALID_USER_INPUT:
  Use only if the input is completely unrelated, nonsensical, or impossible in context.
  Do not use for minor mistakes because that is for NEEDS_INPUT.

GENERAL_RULES:

- Always prioritize the reader's control and freedom.
- Prioritize DIRECT_CONTINUE or NEEDS_INPUT over bridges whenever you can.
- Bridges text should always be short, natural and not include a spoiler.
- Only add text when it's necessary for the story to make sense.
- If you’re unsure between DIRECT_CONTINUE and BRIDGE_AND_CONTINUE, lean toward NEEDS_INPUT. This way, a chance is given to the reader to clarify or expand their action/input text instead of automatically moving the story to the target knot.

EXAMPLES:

Example Flow 1:
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

Example Flow 2:
[Current Story] "You are in the kitchen"
[User Input] "I open the fridge"
[Target Node] "You open the fridge and see some ingredients"
Good DIRECT_CONTINUE:
The input already completes the step. Avoid adding narrative or changing the story — just let it flow.

Example Flow 3:
[Current Story] "You are in the kitchen"
[User Input] "I'm hungry"
[Target Node] "She goes to Joe's Pizza"
Good NEEDS_INPUT:
"What do you want to do to help with your hunger?"
(This prompts the reader to decide instead of moving directly to the target.)

BRIDGE_AND_CONTINUE
Use this only if a small piece of narrative is strictly needed to connect the player’s input to the next story step. Never include any details from the target node — no spoilers, no paraphrasing, no hints. For example:

Example Flow 4:
[Current Story] "You are in the kitchen"
[User Input] "I look around"
[Target Node] "You open the fridge and see some ingredients"
Good Bridge:
"You look at the fridge and decide to open it…"
(Connects their input to the next step without taking control away from the reader.)

Bad Bridge (wrong order):
"You open the fridge and then glance around"

Bad Bridge (includes target content):
"You open the fridge and see some ingredients"
(Includes target details. NEVER DO THIS!)

Example Flow 5:
[Current Story] "You are in the kitchen"
[User Input] "Punch the wall!"
[Target Node] "You open the fridge and see some ingredients"
Invalid Input:
"Punch the wall!"
(Completely unrelated to the story context)

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
