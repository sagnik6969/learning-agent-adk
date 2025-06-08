from typing import override
from google.adk.agents import BaseAgent, LlmAgent
from root_learning_agent.sub_agents.checkpoint_generator_agent import (
    agent as checkpoint_generator_agent,
)
import logging
from root_learning_agent.utils import format_checkpoint_for_display
from google.adk.events import Event, EventActions
import uuid


class LearningAgent(BaseAgent):
    # generate_query_agent: LlmAgent
    # search_web_agent: LlmAgent
    # context_validation_agent: LlmAgent
    generate_checkpoints_agent: LlmAgent
    # generate_question_agent: LlmAgent
    # verify_answer_agent: LlmAgent
    # tech_concept_agent: LlmAgent

    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        # generate_query_agent: LlmAgent,
        # search_web_agent: LlmAgent,
        # context_validation_agent: LlmAgent,
        generate_checkpoints_agent: LlmAgent,
        # generate_question_agent: LlmAgent,
        # verify_answer_agent: LlmAgent,
        # tech_concept_agent: LlmAgent,
    ):
        super().__init__(
            name=name,
            # generate_query_agent=generate_query_agent,
            # search_web_agent=search_web_agent,
            # context_validation_agent=context_validation_agent,
            generate_checkpoints_agent=generate_checkpoints_agent,
            # generate_question_agent=generate_question_agent,
            # verify_answer_agent=verify_answer_agent,
            # tech_concept_agent=tech_concept_agent,
        )

    @override
    async def _run_async_impl(self, ctx):
        if (
            "previous_step" not in ctx.session.state
            or not ctx.session.state["previous_step"]
        ):
            async for event in self.generate_checkpoints_agent.run_async(ctx):
                # event.content = None
                yield event

            yield Event(
                **{
                    "author": self.name,
                    "invocation_id": str(uuid.uuid4()),
                    "content": {
                        "parts": [
                            {
                                "text": format_checkpoint_for_display(
                                    ctx.session.state["checkpoints"]
                                )
                            },
                            {
                                "text": "Do You Have any preffered notes you want to share? If yes paste the note in the chatbox else reply with 'No'"
                            },
                        ]
                    },
                    # "actions": {
                    #     "state_delta": {
                    #         "previous_step": checkpoint_generator_agent.name
                    #     },
                    # },
                    "partial": False,
                    "turn_complete": True,
                }
            )

            return


root_agent = LearningAgent(
    name="learning_agent", generate_checkpoints_agent=checkpoint_generator_agent
)

x = 0
