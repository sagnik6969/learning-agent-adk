from google.adk.agents import Agent
from pydantic import BaseModel, Field


CHECKPOINT_GENERATOR_PROMPT = """
ou will be given a learning topic title and learning objectives.
Your goal is to generate clear learning checkpoints that will help verify understanding and progress through the topic.
The output should be in the following dictionary structure:
checkpoint 
-> description (level checkpoint description)
-> criteria
-> verification (How to verify this checkpoint (Feynman Methods))
Requirements for each checkpoint:
- Description should be clear and concise
- Criteria should be specific and measurable (3-5 items)
- Verification method should be practical and appropriate for the level
- Verification will be checked by language model, so it must by in natural language
- All elements should align with the learning objectives
- Use action verbs and clear language
Ensure all checkpoints progress logically from foundation to mastery.
"""


class LearningCheckpoint(BaseModel):
    """Structure for a single checkpoint"""

    description: str = Field(..., description="Main checkpoint description")
    criteria: list[str] = Field(..., description="List of success criteria")
    verification: str = Field(..., description="How to verify this checkpoint")


class Checkpoints(BaseModel):
    """Main checkpoints container with index tracking"""

    checkpoints: list[LearningCheckpoint] = Field(
        ...,
        description="List of checkpoints covering foundation, application, and mastery levels",
    )


agent = Agent(
    name="checkpoint_generator_agent",
    model="gemini-2.0-flash",
    description=("Creates learning checkpoints based on given topic and goals."),
    instruction=CHECKPOINT_GENERATOR_PROMPT,
    output_schema=Checkpoints,
    output_key="checkpoints"

)
