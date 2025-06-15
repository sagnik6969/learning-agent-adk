from google.adk.agents import Agent
from pydantic import BaseModel
from google.genai.types import Part,Content
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest


TEACH_CONCEPT_PROMPT = """You will be given verification results, checkpoint criteria, and learning context.
Your goal is to create a Feynman-style teaching explanation for concepts that need reinforcement.
The explanation should include:
1. Simplified explanation without technical jargon
2. Concrete, relatable analogies
3. Key concepts to remember
Output should follow the Feynman technique:
- simplified_explanation: clear, jargon-free explanation
- key_concepts: list of essential points
- analogies: list of relevant, concrete comparisons
Focus on making complex ideas accessible and memorable."""


class FeynmanTeaching(BaseModel):
    """Structure for Feynman teaching method"""
    simplified_explanation: str
    key_concepts: list[str]
    analogies: list[str]


def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest):

    current_checkpoint_idx = callback_context.state["current_checkpoint"] 
    checkpoint_info = callback_context.state["checkpoints"][current_checkpoint_idx]

    input = f"""
        Criteria: {checkpoint_info['criteria']}
        Verification: {callback_context.state['verifications']}
        Context:
        {callback_context.state['context_chunks']}
        Create a Feynman teaching explanation."""


    modified_system_prompt = llm_request.config.system_instruction
    modified_system_prompt = (
        modified_system_prompt
        + f"""
            \nInput:
            \n{input}
        """
    )
    llm_request.config.system_instruction = modified_system_prompt
    llm_request.contents = []
    llm_request.contents.append(
        Content(parts=[
        Part(text="Handle the requests as specified in the System Instruction.")
        ],
        role='user')
    )

agent = Agent(
    name="teach_concept_agent",
    model="gemini-2.0-flash",
    description=(
        "Creates simplified Feynman-style explanations for concepts that need reinforcement."
    ),
    instruction=TEACH_CONCEPT_PROMPT,
    output_schema=FeynmanTeaching,
    output_key="teach_concept_result"
)
