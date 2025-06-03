from google.adk.agents import Agent
from .prompt import CHECKPOINT_GENERATOR_PROMPT
from .schemas import Checkpoints

checkpoint_generator_agent = Agent(
    name="checkpoint_generator_agent",
    model="gemini-2.0-flash",
    description=(
        "agent to generate a list of checkpoints based on learning objective"
    ),
    instruction=CHECKPOINT_GENERATOR_PROMPT,
    output_schema=Checkpoints
)