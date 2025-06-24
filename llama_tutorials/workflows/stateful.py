import asyncio
from llama_index.core.workflow import (
    step,
    Event,
    Workflow,
    StartEvent,
    StopEvent,
    Context
)

from llama_index.utils.workflow import draw_all_possible_flows


class SetupEvent(Event):
    pass


class FirstEvent(Event):
    message: str


class SecondEvent(Event):
    message: str


class MyWorkflow(Workflow):
    @step
    async def start(self, ctx: Context, event: StartEvent) -> FirstEvent:
        await ctx.set("database", "sqlite")
        return FirstEvent(message="first message")

    @step
    async def first(self, ctx: Context, event: FirstEvent) -> SecondEvent:
        print(event.message)
        return SecondEvent(message="second message")

    @step
    async def second(self, ctx: Context, event: SecondEvent) -> StopEvent:
        print(event.message)
        print(await ctx.get("database"))
        return StopEvent(result="final result")


async def main():
    workflow = MyWorkflow()
    result = await workflow.run(user_msg="user message")
    print(result)


if __name__ == "__main__":
    draw_all_possible_flows(MyWorkflow, filename="stateful.html")
    asyncio.run(main())
