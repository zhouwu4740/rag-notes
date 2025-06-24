import random
import asyncio
from llama_index.core.workflow import (
    step,
    Event,
    Workflow,
    StartEvent,
    StopEvent,
)
from llama_index.utils.workflow import draw_all_possible_flows


class BranchA1Event(Event):
    message: str


class BranchA2Event(Event):
    message: str


class BranchB1Event(Event):
    message: str


class BranchB2Event(Event):
    message: str


class MyWorkflow(Workflow):

    @step
    async def start(self, event: StartEvent) -> BranchA1Event | BranchB1Event:
        print(event.user_msg)
        if random.randint(0, 1) == 0:
            return BranchA1Event(message="Branch A1")
        else:
            return BranchB1Event(message="Branch B1")

    @step
    async def step_a1(self, event: BranchA1Event) -> BranchA2Event:
        print(event.message)
        return BranchA2Event(message="Branch A2")

    @step
    async def step_a2(self, event: BranchA2Event) -> StopEvent:
        print(event.message)
        return StopEvent(result="final result from Branch A")

    @step
    async def step_b1(self, event: BranchB1Event) -> BranchB2Event:
        print(event.message)
        return BranchB2Event(message="Branch B2")

    @step
    async def step_b2(self, event: BranchB2Event) -> StopEvent:
        print(event.message)
        return StopEvent(result="final result from Branch B")


async def main():
    workflow = MyWorkflow()
    result = await workflow.run(user_msg="user message")
    print(result)

if __name__ == "__main__":
    draw_all_possible_flows(MyWorkflow, filename="branch.html")
    asyncio.run(main())
