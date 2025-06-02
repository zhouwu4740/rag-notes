import asyncio
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import (
    AgentWorkflow,
    FunctionAgent,
)
from llama_index.core.workflow import (
    HumanResponseEvent,
    InputRequiredEvent,
    Context
)


async def dangerous_task(context: Context, name: str):
    question = "你确定要执行危险任务吗？"
    response = await context.wait_for_event(
        event_type=HumanResponseEvent,
        waiter_event=InputRequiredEvent(
            prefix=question,
            username=name,
        ),
        waiter_id=question,
        # requirements={
        #     "username": name,
        # }
    )
    if response.response.lower() == "yes":
        return "任务执行成功"
    else:
        return "取消执行任务"


llm = OpenAI(model="gpt-4o-mini")
workflow = FunctionAgent(
    tools=[dangerous_task],
    llm=llm,
    system_prompt="你是一个助手，擅长执行危险任务",
    name="危险任务助手",
    description="你是一个助手，擅长执行危险任务",
)


async def main():
    context = Context(workflow)
    handler = workflow.run(user_msg="请执行危险任务", ctx=context)
    async for event in handler.stream_events():
        if isinstance(event, InputRequiredEvent):
            response = input(event.prefix)
            context.send_event(HumanResponseEvent(response=response))

    response = await handler
    print(str(response))

if __name__ == "__main__":
    asyncio.run(main())
