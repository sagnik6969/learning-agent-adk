import time
from typing import override
from google.adk.agents import BaseAgent, LlmAgent
from root_learning_agent.services.context_stope import ContextStore
from root_learning_agent.sub_agents.checkpoint_generator_agent import (
    agent as checkpoint_generator_agent,
)
from root_learning_agent.utils import format_checkpoint_for_display
from root_learning_agent.sub_agents.generate_query_agent import (
    agent as generate_query_for_web_search_agent,
)
from root_learning_agent.sub_agents.question_generator_agent import (
    agent as question_generator_agent,
)
from root_learning_agent.sub_agents.validatete_answer_agent import agent as validate_answer_agent
from google.adk.events import Event, EventActions
import uuid
from langchain_openai import OpenAIEmbeddings
from .services.chunk_context import chunk_context
from .services.search_web import search_web


embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
context_store = ContextStore()
# from .services.search_web import search_web


class LearningAgent(BaseAgent):
    generate_query_agent: LlmAgent
    # search_web_agent: LlmAgent
    # context_validation_agent: LlmAgent
    generate_checkpoints_agent: LlmAgent
    generate_question_agent: LlmAgent
    verify_answer_agent: LlmAgent
    # tech_concept_agent: LlmAgent

    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        generate_query_agent: LlmAgent,
        # search_web_agent: LlmAgent,
        # context_validation_agent: LlmAgent,
        generate_checkpoints_agent: LlmAgent,
        generate_question_agent: LlmAgent,
        verify_answer_agent: LlmAgent,
        # tech_concept_agent: LlmAgent,
    ):
        # content might be None or represent the action taken

        sub_agent_list = [
            generate_query_agent,
            # search_web_agent: LlmAgent,
            # context_validation_agent: LlmAgent,
            generate_checkpoints_agent,
            generate_question_agent,
            verify_answer_agent,
            # tech_concept_agent: LlmAgent,
        ]
        super().__init__(
            name=name,
            generate_query_agent=generate_query_agent,
            # search_web_agent=search_web_agent,
            # context_validation_agent=context_validation_agent,
            generate_checkpoints_agent=generate_checkpoints_agent,
            generate_question_agent=generate_question_agent,
            verify_answer_agent=verify_answer_agent,
            # tech_concept_agent=tech_concept_agent,
            sub_agents=sub_agent_list,
        )

    @override
    async def _run_async_impl(self, ctx):
        if (
            "previous_step" not in ctx.session.state
            or not ctx.session.state["previous_step"]
        ):
            async for event in self.generate_checkpoints_agent.run_async(ctx):
                event.content = None
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
                    "actions": {
                        "state_delta": {
                            "previous_step": checkpoint_generator_agent.name
                        },
                    },
                    "partial": False,
                    "turn_complete": True,
                }
            )

            return
        elif ctx.session.state["previous_step"] == checkpoint_generator_agent.name:
            user_input: str = ctx.session.events[-1].content.parts[0].text
            next_step: str | None = None

            if "no" in user_input.lower():
                next_step = "generate_query"
            else:
                next_step = "chunk_context"

            if next_step == "generate_query":
                async for event in self.generate_query_agent.run_async(ctx):
                    event.content = None
                    event.turn_complete = None
                    yield event

                state_changes = search_web(
                    search_queries=ctx.session.state["search_queries"],
                    context_store=context_store,
                    embeddings=embeddings,
                )

                actions_with_update = EventActions(state_delta=state_changes)
                system_event = Event(
                    invocation_id=str(uuid.uuid4()),
                    author=self.name,
                    actions=actions_with_update,
                    timestamp=time.time(),
                    turn_complete=None,
                )
                yield system_event

            else:
                state_changes = chunk_context(user_input)
                actions_with_update = EventActions(state_delta=state_changes)
                system_event = Event(
                    invocation_id=str(uuid.uuid4()),
                    author=self.name,
                    actions=actions_with_update,
                    timestamp=time.time(),
                )
                yield system_event

            async for event in self.generate_question_agent.run_async(ctx):
                event.content = None
                # event.turn_complete = False
                yield event

            yield Event(
                **{
                    "author": self.name,
                    "invocation_id": str(uuid.uuid4()),
                    "content": {
                        "parts": [
                            {"text": ctx.session.state["current_question"]["question"]},
                        ]
                    },
                    "actions": {
                        "state_delta": {
                            "previous_step": self.generate_question_agent.name
                        },
                    },
                    "partial": False,
                    "turn_complete": True,
                }
            )

        elif (
            ctx.session.state["previous_step"]
            == generate_query_for_web_search_agent.name
        ):
            users_answer = ctx.session.events[-1].content.parts[0].text

            current_checkpoint_idx = ctx.session.state["current_checkpoint"]
            checkpoint_info = ctx.session.state["checkpoints"].checkpoints[
                current_checkpoint_idx
            ]

            relevent_chunks = context_store.get_relevent_chunks(
                context_key=ctx.session.state["context_key"],
                embeddings=embeddings,
                query=checkpoint_info["verification"],
            )

            state_changes = {
                "current_answer": users_answer,
                "relevent_chunks": relevent_chunks,
            }

            actions_with_update = EventActions(state_delta=state_changes)
            system_event = Event(
                invocation_id=str(uuid.uuid4()),
                author=self.name,
                actions=actions_with_update,
                timestamp=time.time(),
                turn_complete=None,
            )
            yield system_event

            async for event in self.verify_answer_agent.run_async(ctx):
                yield event


root_agent = LearningAgent(
    name="learning_agent",
    generate_checkpoints_agent=checkpoint_generator_agent,
    generate_query_agent=generate_query_for_web_search_agent,
    generate_question_agent=question_generator_agent,
    verify_answer_agent=validate_answer_agent
)
