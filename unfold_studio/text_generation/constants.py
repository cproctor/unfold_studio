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
    Example: 
    [Current Story] "You are in the kitchen"
    [User Input] "I open the fridge"
    [Target Node] "You open the fridge and see some ingredients"
    --> Label: DIRECT_CONTINUE

- NEEDS_INPUT:
  Use this when the input is ambiguous, incomplete, or missing key actions.
  - Ask the player a short, clear question/prompt to clarify their next move.
  - Keep it engaging, so the reader can provide meaningful input without the AI filling in the story.
    Example:
    [Current Story] "You are in the kitchen"
    [User Input] "I'm hungry"
    [Target Node] "She goes to Joe's Pizza"
    --> Label: NEEDS_INPUT
    Guidance Text: "Where do you want to go to eat?"

- BRIDGE_AND_CONTINUE:
  Use only if a small narrative is required to connect the user input to the next story node.
  Never include any details from the target node or no spoilers.
  Example:
      [Current Story] "You are in the kitchen"
      [User Input] "look around"
      [Target Node] "You open the fridge and see some ingredients"
      --> Bridge: "You glance at the fridge and decide to open it…"

- INVALID_USER_INPUT:
  Use only if the input is completely unrelated, nonsensical, or impossible in context.
   Example:
    [Current Story] "You are in the kitchen"
    [User Input] "Punch the wall!"
    [Target Node] "You open the fridge and see some ingredients"
    --> Label: INVALID_USER_INPUT

PRIORITY RULES (PLS FOLLOW STRICTLY!!:

You should try to continue the story whenever possible instead of asking for more input.

1. DIRECT_CONTINUE
   Choose this when the user performs an action that directly reaches the target step OR is strongly aligned with it.

2. BRIDGE_AND_CONTINUE
   Choose this when:
   - the user attempted an action,
   - the action is relevant and meaningful,
   - but it does not exactly reach the target,
   and a small, minimal connective sentence is required.

3. NEEDS_INPUT
   Choose this ONLY when the user input provides no actionable story content:
   - No action
   - No movement
   - No intention
   - No decision
   - Only feelings, statements, questions, or incomplete thoughts

   DO NOT choose NEEDS_INPUT if the user provided ANY action verb or movement.

4. INVALID_USER_INPUT
   Choose only if the input is nonsense, completely off-topic, or impossible.

Key Rule:
If the user gives ANY action (look, walk, open, go, run, inspect, move, touch, pick up, etc.), then the choice MUST be between DIRECT_CONTINUE or BRIDGE_AND_CONTINUE. NEVER NEEDS_INPUT.

NEEDS_INPUT should be rare, only when the input contains NO action at all.

EXAMPLES:

Example Flow 1:
[Current Story] "You sit on your bed"
[User Input] "drink coffee"
[Target Node] "You wake up at 7AM tired"

Good NEEDS_INPUT:
"What will you do after drinking coffee?"

Example Flow 2:
[Current Story] "You are in the kitchen"
[User Input] "I open the fridge"
[Target Node] "You open the fridge and see some ingredients"
Good DIRECT_CONTINUE:
The input already completes the step. No extra text needed.

Example Flow 3:
[Current Story] "You are in the kitchen"
[User Input] "I look around"
[Target Node] "You open the fridge and see some ingredients"
Good Bridge:
"You glance at the fridge and decide to open it…"

Example Flow 4:
[Current Story] "You are in the kitchen"
[User Input] "Punch the wall!"
[Target Node] "You open the fridge and see some ingredients"
Invalid Input:
"Punch the wall!"

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
