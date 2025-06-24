import asyncio
from llama_index.core.workflow import (
    step,
    Event,
    Context,
    Workflow,
    StartEvent,
    StopEvent
)
from llama_index.utils.workflow import draw_all_possible_flows


class StepAEvent(Event):
    message: str


class StepBEvent(Event):
    message: str


class StepCEvent(Event):
    message: str


class StepACompleteEvent(Event):
    message: str


class StepBCompleteEvent(Event):
    message: str


class StepCCompleteEvent(Event):
    message: str


class ParallelWorkflow(Workflow):

    @step
    async def start(self, ctx: Context, event: StartEvent) -> StepAEvent | StepBEvent | StepCEvent:
        ctx.send_event(StepAEvent(message="message 1"))
        ctx.send_event(StepBEvent(message="message 2"))
        ctx.send_event(StepCEvent(message="message 3"))

    @step
    async def step_a(self, ctx: Context, event: StepAEvent) -> StepACompleteEvent:
        print(f"step_a: {event.message}")
        return StepACompleteEvent(message="message 1 for step_a_complete")

    @step
    async def step_b(self, ctx: Context, event: StepBEvent) -> StepBCompleteEvent:
        print(f"step_b: {event.message}")
        return StepBCompleteEvent(message="message 2 for step_b_complete")

    @step
    async def step_c(self, ctx: Context, event: StepCEvent) -> StepCCompleteEvent:
        print(f"step_c: {event.message}")
        return StepCCompleteEvent(message="message 3 for step_c_complete")

    @step
    async def complete(self, ctx: Context, event: StepACompleteEvent | StepBCompleteEvent | StepCCompleteEvent) -> StopEvent:
        result = ctx.collect_events(
            event, [StepACompleteEvent, StepBCompleteEvent, StepCCompleteEvent])
        if result is None:
            return None
        return StopEvent(result="all done")


async def main():
    workflow = ParallelWorkflow()
    result = await workflow.run()
    print("result: ", result)

if __name__ == "__main__":
    asyncio.run(main())
    draw_all_possible_flows(
        ParallelWorkflow, "concurrent_multitype_event.html")
