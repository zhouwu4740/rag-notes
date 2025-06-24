import asyncio
from llama_index.core.workflow import (
    step,
    Event,
    Context,
    Workflow,
    StartEvent,
    StopEvent,
)
from llama_index.llms.openai import OpenAI

from llama_index.utils.workflow import draw_all_possible_flows


class FirstEvent(Event):
    message: str


class SecondEvent(Event):
    message: str


class ProgressEvent(Event):
    message: str


class MyWorkflow(Workflow):
    @step
    async def step_1(self, ctx: Context, event: StartEvent) -> FirstEvent:
        ctx.write_event_to_stream(ProgressEvent(message="Step 1 started\n"))
        return FirstEvent(message="Step 1 completed\n")

    @step
    async def step_2(self, ctx: Context, event: FirstEvent) -> SecondEvent:
        llm = OpenAI(model="gpt-4o-mini", max_tokens=500)
        generator = await llm.astream_complete("请介绍一下中国的赛龙舟起源、发展、现状")
        async for chunk in generator:
            ctx.write_event_to_stream(ProgressEvent(message=chunk.delta))
        return SecondEvent(message="Step 2 completed\n")

    @step
    async def step_3(self, ctx: Context, event: SecondEvent) -> StopEvent:
        ctx.write_event_to_stream(ProgressEvent(message="Step 3 started"))
        return StopEvent(result="Step 3 completed\n")


async def main():
    workflow = MyWorkflow()
    handler = workflow.run(user_msg="user message")
    async for event in handler.stream_events():
        if isinstance(event, ProgressEvent):
            print(event.message, end="", flush=True)

    result = await handler
    print("final result", result)

    draw_all_possible_flows(MyWorkflow, filename="streaming_event.html")


if __name__ == "__main__":
    asyncio.run(main())
