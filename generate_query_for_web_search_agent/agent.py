from google.adk.agents import Agent
from .prompt import GENERATE_QUERY_PROMPT
from .schemas import SearchQuery

root_agent = Agent(
    name="checkpoint_generator_agent",
    model="gemini-2.0-flash",
    description=(
        "Generates search queries based on learning checkpoints from current state."
    ),
    instruction=GENERATE_QUERY_PROMPT,
    output_schema=SearchQuery
)