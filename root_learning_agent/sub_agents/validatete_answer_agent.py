from google.adk.agents import Agent
from pydantic import BaseModel
from google.genai.types import Part, Content
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from pydantic import Field


VALIDATE_ANSWER_PROMPT = """You will be given a student's answer, question, checkpoint details, and relevant context.
Your goal is to analyze the answer against the checkpoint criteria and provided context.
Analyze considering:
1. Alignment with verification method specified
2. Coverage of all success criteria
3. Use of relevant concepts from context
4. Depth and accuracy of understanding
Output should include:
- understanding_level: float between 0 and 1
- feedback: detailed explanation of the assessment
- suggestions: list of specific improvements
- context_alignment: boolean indicating if the answer aligns with provided context"""


class LearningVerification(BaseModel):
    """Structure for verification results"""

    understanding_level: float = Field(..., ge=0, le=1)
    feedback: str
    suggestions: list[str]
    context_alignment: bool


def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest):
    current_checkpoint_idx = callback_context.state["current_checkpoint"]
    checkpoint_info = callback_context.state["checkpoints"][current_checkpoint_idx]
    relevant_chunks = callback_context.state["relevant_chunks"]

    input = f"""
        Question: {callback_context.state["current_question"]}
        Answer: {callback_context.state["current_answer"]}
        Checkpoint Description: {checkpoint_info.description}
        Success Criteria:
        {chr(10).join(f"- {c}" for c in checkpoint_info.criteria)}
        Verification Method: {checkpoint_info.verification}
        Context:
        {chr(10).join(relevant_chunks)}
        Assess the answer."""

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
        Content(
            parts=[
                Part(text="Handle the requests as specified in the System Instruction.")
            ],
            role="user",
        )
    )


agent = Agent(
    name="question_generator_agent",
    model="gemini-2.0-flash",
    description=(
        "Generates assessment questions based on current checkpoint verification requirements."
    ),
    instruction=VALIDATE_ANSWER_PROMPT,
    output_schema=LearningVerification,
    output_key="current_question",
)
