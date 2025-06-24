"""pip install llama-index-utils-workflow"""
from fileinput import filename
from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    step,
    Workflow
)
from llama_index.utils.workflow import draw_all_possible_flows
import asyncio


class SingleStepWorkflow(Workflow):
    @step
    def my_step(self, event: StartEvent) -> StopEvent:
        return StopEvent(result="Hello, world!")


workflow = SingleStepWorkflow()


async def main():
    # result = await workflow.run()
    # print(f"Workflow result: {result}")
    draw_all_possible_flows(SingleStepWorkflow, filename="single_step.html")

if __name__ == "__main__":
    asyncio.run(main())
