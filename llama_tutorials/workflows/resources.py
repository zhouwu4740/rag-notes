import random
from typing import Annotated, Union
from llama_index.core.memory import Memory
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.workflow.resource import Resource
from llama_index.core.workflow import (
    step,
    Event,
    Workflow,
    StartEvent,
    StopEvent,
)
import asyncio

RANDOM_MESSAGES = [
    "Hello World!",
    "Python is a great language!",
    "Resources are great!",
    "Go is a great language!",
]


def get_memory(*args, **kwargs) -> Memory:
    return Memory.from_defaults("user_id_123", token_limit=60000)


resource = Annotated[Memory, Resource(get_memory)]


class CustomStartEvent(StartEvent):
    message: str


class SecondEvent(Event):
    message: str


class ThirdEvent(Event):
    message: str


class WorkflowWithMemory(Workflow):
    @step
    async def step1(self,
                    event: CustomStartEvent,
                    memory: Annotated[Memory, Resource(get_memory)]
                    ) -> SecondEvent:
        await memory.aput(ChatMessage.from_str(role=MessageRole.USER, content="First step: " + event.message))

        return SecondEvent(message=RANDOM_MESSAGES[random.randint(0, len(RANDOM_MESSAGES) - 1)])

    @step
    async def step2(self, event: SecondEvent, memory: Annotated[Memory, Resource(get_memory)]) -> ThirdEvent:
        await memory.aput(ChatMessage.from_str(role=MessageRole.USER, content="Second step: " + event.message))

        if random.randint(0, 1) == 0:
            return ThirdEvent(message=RANDOM_MESSAGES[random.randint(0, len(RANDOM_MESSAGES) - 1)])
        else:
            messages = await memory.aget_all()
            return StopEvent(result=messages)

    @step
    async def step3(self, event: ThirdEvent, memory: Annotated[Memory, Resource(get_memory)]) -> StopEvent:
        await memory.aput(ChatMessage.from_str(role=MessageRole.USER, content="Third step: " + event.message))
        messages = await memory.aget_all()
        return StopEvent(result=messages)


async def main():
    workflow = WorkflowWithMemory()
    messages = await workflow.run(start_event=CustomStartEvent(message="Hello World!"))
    for message in messages:
        print(message)

if __name__ == "__main__":
    asyncio.run(main())
