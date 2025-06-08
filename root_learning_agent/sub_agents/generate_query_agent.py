from google.adk.agents import Agent
from pydantic import BaseModel, Field
from google.genai.types import Part,Content
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest


GENERATE_QUERY_PROMPT = """You will be given learning checkpoints for a topic.
Your goal is to generate search queries that will retrieve content matching each checkpoint's requirements from retrieval systems or web search.
Follow these steps:
1. Analyze each learning checkpoint carefully
2. For each checkpoint, generate ONE targeted search query that will retrieve:
   - Content for checkpoint verification
"""


class SearchQuery(BaseModel):
    """Structure for search query collection"""

    search_queries: list = Field(None, description="Search queries for retrieval.")

def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest):
    modified_system_prompt = llm_request.config.system_instruction
    modified_system_prompt = (
        modified_system_prompt
        + f"""
            \nLearning Checkpoints:\n
            {callback_context.state["checkpoints"]}
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
    name="generate_query_agent",
    model="gemini-2.0-flash",
    description=(
        "Generates search queries based on learning checkpoints from current state."
    ),
    instruction=GENERATE_QUERY_PROMPT,
    output_schema=SearchQuery,
    output_key="search_queries"
)
