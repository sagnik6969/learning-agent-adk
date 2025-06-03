from google.adk.agents import Agent
from .prompt import CHECKPOINT_GENERATOR_PROMPT
from .schemas import Checkpoints

root_agent = Agent(
    name="checkpoint_generator_agent",
    model="gemini-2.0-flash",
    description=(
        "Creates learning checkpoints based on given topic and goals."
    ),
    instruction=CHECKPOINT_GENERATOR_PROMPT,
    output_schema=Checkpoints
)