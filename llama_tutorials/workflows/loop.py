import random
import asyncio
from llama_index.core.workflow import (
    step,
    Workflow,
    StartEvent,
    StopEvent,
    Event,
)
from llama_index.utils.workflow import draw_all_possible_flows


class FirstEvent(Event):
    first_input: str


class SecondEvent(Event):
    second_input: str


class LoopEvent(Event):
    loop_input: str


class MyWorkflow(Workflow):
    @step
    async def first_step(self, event: StartEvent | LoopEvent) -> FirstEvent | LoopEvent:
        if isinstance(event, StartEvent):
            print(event.user_msg)
        else:
            print(event.loop_input)

        if random.randint(0, 1) == 0:
            return LoopEvent(loop_input="loop input message")
        else:
            return FirstEvent(first_input="first input message")

    @step
    async def second_step(self, event: FirstEvent) -> SecondEvent:
        print(event.first_input)
        return SecondEvent(second_input="second input message")

    @step
    async def third_step(self, event: SecondEvent) -> StopEvent:
        print(event.second_input)
        return StopEvent(result="final result")


async def main():
    workflow = MyWorkflow()
    result = await workflow.run(user_msg="user message", msg="msg....")
    print(result)

if __name__ == "__main__":
    draw_all_possible_flows(MyWorkflow, filename="loop.html")
    asyncio.run(main())
