import time
from typing import override
from google.adk.agents import BaseAgent, LlmAgent
from root_learning_agent.services.context_stope import ContextStore
from root_learning_agent.sub_agents.checkpoint_generator_agent import (
    agent as checkpoint_generator_agent,
)
from root_learning_agent.utils import (
    format_checkpoint_for_display,
    format_teaching_results,
    format_verification_results,
)
from root_learning_agent.sub_agents.generate_query_agent import (
    agent as generate_query_for_web_search_agent,
)
from root_learning_agent.sub_agents.question_generator_agent import (
    agent as question_generator_agent,
)
from root_learning_agent.sub_agents.validatete_answer_agent import (
    agent as validate_answer_agent,
)
from root_learning_agent.sub_agents.teach_concept_agent import (
    agent as teach_concept_agent,
)
from google.adk.events import Event, EventActions
import uuid
from langchain_openai import OpenAIEmbeddings
from .services.chunk_context import chunk_context
from .services.search_web import search_web
from google.genai.types import Content, Part

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
    teach_concept_agent: LlmAgent

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
        teach_concept_agent: LlmAgent,
    ):
        # content might be None or represent the action taken

        sub_agent_list = [
            generate_query_agent,
            # search_web_agent: LlmAgent,
            # context_validation_agent: LlmAgent,
            generate_checkpoints_agent,
            generate_question_agent,
            verify_answer_agent,
            teach_concept_agent,
        ]
        super().__init__(
            name=name,
            generate_query_agent=generate_query_agent,
            # search_web_agent=search_web_agent,
            # context_validation_agent=context_validation_agent,
            generate_checkpoints_agent=generate_checkpoints_agent,
            generate_question_agent=generate_question_agent,
            verify_answer_agent=verify_answer_agent,
            teach_concept_agent=teach_concept_agent,
            sub_agents=sub_agent_list,
        )

    def get_ai_text_message_event(self, texts: list[str]):
        return Event(
            author=self.name,
            invocation_id=str(uuid.uuid4()),
            content=Content(parts=[Part(text=text) for text in texts]),
            partial=False,
            turn_complete=True,
        )

    def get_state_update_event(self, state_changes: dict):
        actions_with_update = EventActions(state_delta=state_changes)
        return Event(
            invocation_id=str(uuid.uuid4()),
            author=self.name,
            actions=actions_with_update,
            timestamp=time.time(),
            turn_complete=None,
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

            formatted_checkpoints = format_checkpoint_for_display(
                ctx.session.state["checkpoints"]
            )

            yield self.get_ai_text_message_event(
                [
                    formatted_checkpoints,
                    "Do You Have any preffered notes you want to share? If yes paste the note in the chatbox else reply with 'No'",
                ]
            )
            yield self.get_state_update_event(
                {"previous_step": checkpoint_generator_agent.name}
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

                yield self.get_state_update_event(state_changes)

            else:
                state_changes = chunk_context(user_input)
                print(state_changes)
                yield self.get_state_update_event(state_changes)

            if "current_checkpoint" not in ctx.session.state:
                yield self.get_state_update_event({"current_checkpoint": 0})

            async for event in self.generate_question_agent.run_async(ctx):
                event.content = None
                yield event

            yield self.get_ai_text_message_event(
                [ctx.session.state["current_question"]["question"]]
            )
            yield self.get_state_update_event(
                {"previous_step": self.generate_question_agent.name}
            )

        elif ctx.session.state["previous_step"] == self.generate_question_agent.name:
            users_answer = ctx.session.events[-1].content.parts[0].text

            current_checkpoint_idx = ctx.session.state["current_checkpoint"]
            checkpoint_info = ctx.session.state["checkpoints"]["checkpoints"][
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

            yield self.get_state_update_event(state_changes)

            async for event in self.verify_answer_agent.run_async(ctx):
                event.content = None
                yield event

            yield self.get_ai_text_message_event(
                [format_verification_results(ctx.session.state["verifications"])]
            )

            if ctx.session.state["verifications"]["understanding_level"] < 0.7:
                # Teach concept if unterstanding level is bellow threshold
                async for event in self.teach_concept_agent.run_async(ctx):
                    # event.content = None
                    yield event
                
                yield self.get_ai_text_message_event(
                [format_teaching_results(ctx.session.state["teach_concept_result"])]
            )

                

            if current_checkpoint_idx + 1 < len(
                ctx.session.state["checkpoints"]["checkpoints"]
            ):
                # Go to next check point
                state_changes = {"current_checkpoint": current_checkpoint_idx + 1}
                yield self.get_state_update_event(state_changes)

                async for event in self.generate_question_agent.run_async(ctx):
                    event.content = None
                    yield event

                yield self.get_ai_text_message_event(
                    [ctx.session.state["current_question"]["question"]]
                )
                yield self.get_state_update_event(
                    {"previous_step": self.generate_question_agent.name}
                )

            else:
                ## __END__
                yield self.get_ai_text_message_event(
                    ["All the concepts are taught successfully.!! 🥳🥳🥳"]
                )
                yield self.get_state_update_event({"previous_step": "END"})

        elif ctx.session.state["previous_step"] == "END":
            yield self.get_ai_text_message_event(
                ["All the concepts are taught successfully.!! 🥳🥳🥳"]
            )


root_agent = LearningAgent(
    name="learning_agent",
    generate_checkpoints_agent=checkpoint_generator_agent,
    generate_query_agent=generate_query_for_web_search_agent,
    generate_question_agent=question_generator_agent,
    verify_answer_agent=validate_answer_agent,
    teach_concept_agent=teach_concept_agent,
)
