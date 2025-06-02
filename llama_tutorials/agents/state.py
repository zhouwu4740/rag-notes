import asyncio
from json import tool
from llama_index.core.workflow.context import Context
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-4o-mini")


async def set_name(context: Context, name: str) -> str:
    state = await context.get("state")
    state["name"] = name
    await context.set("state", state)
    return f"名字已设置为{name}"


agent_workflow = AgentWorkflow.from_tools_or_functions(
    tools_or_functions=[set_name],
    llm=llm,
    system_prompt="你是我的助手，请根据我的要求完成任务",
    initial_state={"name": "未设置名字"},
)


async def main():
    context = Context(agent_workflow)
    response = await agent_workflow.run(user_msg="我叫什么名字", ctx=context)
    print(str(response))

    response = await agent_workflow.run(user_msg="我叫张三", ctx=context)
    print(str(response))

    response = await agent_workflow.run(user_msg="我叫什么名字", ctx=context)
    print(str(response))

    state = await context.get("state")
    name = state["name"]
    print(f"名字是: {name}")

    d = context.to_dict()
    ctx = Context.from_dict(
        agent_workflow,
        data=d,
    )

    response = await agent_workflow.run(user_msg="我叫什么名字", ctx=ctx)
    print(str(response))
    ctx.wait_for_event


if __name__ == "__main__":
    asyncio.run(main())
