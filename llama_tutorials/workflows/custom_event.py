from llama_index.core.workflow import (
    step,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
)
from llama_index.utils.workflow import draw_all_possible_flows

import asyncio


class FirstEvent(Event):
    first_input: str


class SecondEvent(Event):
    second_input: str


class ThirdEvent(Event):
    third_input: str


class MyWorkflow(Workflow):
    @step
    async def first_step(self, event: StartEvent) -> FirstEvent:
        print(event.user_msg)
        print(event.msg)
        return FirstEvent(first_input="first input message")

    @step
    async def second_step(self, event: FirstEvent) -> SecondEvent:
        print(event.first_input)
        return SecondEvent(second_input="second input message")

    @step
    async def third_step(self, event: SecondEvent) -> ThirdEvent:
        print(event.second_input)
        return ThirdEvent(third_input="third input message")

    @step
    async def final_step(self, event: ThirdEvent) -> StopEvent:
        print(event.third_input)
        return StopEvent(result="final result")


workflow = MyWorkflow()


async def main():
    result = await workflow.run(user_msg="user message", msg="msg....")
    print(f"Workflow result: {result}")


if __name__ == "__main__":
    draw_all_possible_flows(MyWorkflow, filename="custom_event.html")
    asyncio.run(main())
