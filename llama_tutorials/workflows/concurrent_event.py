import asyncio
import random
from llama_index.core.workflow import (
    step,
    Event,
    Context,
    Workflow,
    StartEvent,
    StopEvent,
)
from llama_index.utils.workflow import draw_all_possible_flows


class Step2Event(Event):
    message: str


class Step3Event(Event):
    message: str


class ParallelWorkflow(Workflow):
    @step
    async def start(self, ctx: Context, event: StartEvent) -> Step2Event:
        # 同时发出3个事件
        ctx.send_event(Step2Event(message="message 1"))
        ctx.send_event(Step2Event(message="message 2"))
        ctx.send_event(Step2Event(message="message 3"))

    @step
    async def step2(self, ctx: Context, event: Step2Event) -> Step3Event:
        await asyncio.sleep(random.randint(1, 5))
        print(f"step2: {event.message}")
        return Step3Event(message="message 3 for step3")

    @step
    async def step3(self, ctx: Context, event: Step3Event) -> StopEvent:
        result = ctx.collect_events(event, [Step3Event] * 3)
        if result is None:
            return None
        return StopEvent(result="all done")


async def main():
    workflow = ParallelWorkflow()
    result = await workflow.run()
    print("result: ", result)

if __name__ == "__main__":
    asyncio.run(main())
    draw_all_possible_flows(ParallelWorkflow, "concurrent_event.html")
