class StoryContinueDirections:
    DIRECT_CONTINUE = "DIRECT_CONTINUE"
    BRIDGE_AND_CONTINUE = "BRIDGE_AND_CONTINUE"
    NEEDS_INPUT = "NEEDS_INPUT"
    @classmethod
    def values(cls):
        return [v for k,v in vars(cls).items() if k.isupper() and not callable(v)]

CONTINUE_STORY_SYSTEM_PROMPT = """You are a story transition analyst. Analyze how user input leads to target story nodes:

DIRECT_CONTINUE: Input directly matches target conditions chronologically
BRIDGE_AND_CONTINUE: Requires narrative to connect input to target timeline
NEEDS_INPUT: Needs clarification to maintain chronological consistency

Consider temporal relationships: user input must precede target node events.
Also the guidance_text/bridge_text you give should not include details of the target knot. 

Example Flow:
[Current Story] "You sit on your bed"
[User Input] "drink coffee"
[Target Node] "You wake up at 7AM tired"

Good Bridge: 
"After drinking coffee late at night, you struggle to sleep. The caffeine keeps you awake until..."

Bad Bridge: 
"You wake up tired and drink coffee" (wrong order)

    Follow this JSON format:
    {
        "probabilities": {
            "DIRECT_CONTINUE": 0.0-1.0,
            "BRIDGE_AND_CONTINUE": 0.0-1.0,
            "NEEDS_INPUT": 0.0-1.0
        },
        "direct_continue": {
            "reason": "...",
        },
        "bridge_and_continue": {
            "reason": "...",
            "bridge_text": "..." // Full narrative bridge text
        },
        "needs_input": {
            "reason": "...",
            "guidance_text": "...", // Question/prompt for next input from user
        }
    }

    Example:
    {
        "probabilities": {
            "DIRECT_CONTINUE": 0.3,
            "BRIDGE_AND_CONTINUE": 0.5,
            "NEEDS_INPUT": 0.2
        },
        "direct_continue": {
            "reason": "User specified exact target location",
        },
        "bridge_and_continue": {
            "reason": "Needs transition to hidden chamber",
            "bridge_text": "As you push the ancient door, it creaks open to reveal..."
        },
        "needs_input": {
            "reason": "Requires specific investigation focus",
            "guidance_text": "What part of the wall will you examine?",
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