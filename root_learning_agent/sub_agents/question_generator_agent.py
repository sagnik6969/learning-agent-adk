from google.adk.agents import Agent
from pydantic import BaseModel
from google.genai.types import Part,Content
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest


QUESTION_GENERATOR_AGENT_PROMPT = """You will be given a checkpoint description, success criteria, and verification method.
Your goal is to generate an appropriate question that aligns with the checkpoint's verification requirements.
The question should:
1. Follow the specified verification method
2. Cover all success criteria
3. Encourage demonstration of understanding
4. Be clear and specific
Output should be a single, well-formulated question that effectively tests the checkpoint's learning objectives."""


class QuestionOutput(BaseModel):
    """Structure for question generation output"""
    question: str


def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest):

    current_checkpoint = callback_context.state["current_checkpoint"] if "current_checkpoint" in callback_context.state else 0
    next_checkpoint = current_checkpoint + 1

    checkpoint_info = callback_context.state["checkpoints"][current_checkpoint]
    callback_context.state["current_checkpoint"] = next_checkpoint

    formatted_checkpoit = f"""Checkpoint Description: {checkpoint_info['description']}
        Success Criteria:
        {chr(10).join(f"- {c}" for c in checkpoint_info['criteria'])}
        Verification Method: {checkpoint_info['verification']}"""


    modified_system_prompt = llm_request.config.system_instruction
    modified_system_prompt = (
        modified_system_prompt
        + f"""
            \nCheckpoint Details:\n
            {formatted_checkpoit}
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
    name="question_generator_agent",
    model="gemini-2.0-flash",
    description=(
        "Generates assessment questions based on current checkpoint verification requirements."
    ),
    instruction=QUESTION_GENERATOR_AGENT_PROMPT,
    output_schema=QuestionOutput,
    output_key="current_question"
)
