import asyncio
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import (
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
            user_name=name,
        ),
        waiter_id=question,
        # 指定等待带有特定用户名的事件
        requirements={
            "user_name": name,
        }
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
        # 可以将下列获取用户反馈的方法input()升级为邮件、web page ui等，此时需要序列化context，当反馈回来时再继续执行流程
        if isinstance(event, InputRequiredEvent):
            response = input(event.prefix)
            context.send_event(HumanResponseEvent(
                response=response,
                user_name=event.user_name))

    response = await handler
    print(str(response))

if __name__ == "__main__":
    asyncio.run(main())
