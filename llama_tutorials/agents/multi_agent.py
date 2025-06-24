import os
import re
from llama_index.tools.tavily_research import TavilyToolSpec
from llama_index.core.workflow.context import Context
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import (
    FunctionAgent,
    AgentWorkflow,
    AgentOutput,
    ToolCall,
    ToolCallResult
)


tavily_tools = TavilyToolSpec(api_key=os.getenv("TAVILY_API_KEY"))
search_web = tavily_tools.to_tool_list()[0]


async def record_notes(ctx: Context, notes: str, notes_title: str) -> str:
    """
    记录笔记
    """
    state = await ctx.get("state")
    if "research_notes" not in state:
        state["research_notes"] = {}
    state["research_notes"][notes_title] = notes
    await ctx.set("state", state)
    print(f"记录笔记: {notes_title}")
    print(f"笔记内容: {notes}")
    return "笔记记录成功"


async def write_report(ctx: Context, report_content: str) -> str:
    """写报告"""
    state = await ctx.get("state")
    state["report_content"] = report_content
    await ctx.set("state", state)
    print(f"写报告: {report_content}")
    return "报告写成功"


async def review_report(ctx: Context, review: str) -> str:
    """审查报告"""
    state = await ctx.get("state")
    state["review"] = review
    await ctx.set("state", state)
    print(f"审查报告: {review}")
    return "报告审查成功"

llm = OpenAI(model="gpt-4o-mini")

research_agent = FunctionAgent(
    # name 标识agent
    name="ResearchAgent",
    # description 描述agent的职责，其它agent可以通过description判断是否可以handoff给该agent
    description="根据用户输入的报告主题，利用网络搜索工具搜索相关信息并记录笔记",
    # system_prompt 定义agent的行为
    system_prompt="你是一个研究助手，擅长利用网络搜索工具搜索相关信息并记录笔记",
    llm=llm,
    tools=[record_notes, write_report],
    # can_handoff_to 定义agent可以handoff给哪些agent
    can_handoff_to=["WriteAgent"]
)

write_agent = FunctionAgent(
    name="WriteAgent",
    description="根据笔记内容，撰写报告",
    system_prompt="你是一个报告撰写助手，擅长根据用户给定的主题和笔记内容撰写报告。你写的报告应该是markdown格式。当你的报告写完之后，请handoff给ReviewAgent进行审查。",
    llm=llm,
    tools=[write_report],
    can_handoff_to=["ReviewAgent"]
)

review_agent = FunctionAgent(
    name="ReviewAgent",
    description="审查报告",
    system_prompt="你是一个报告审查助手，擅长审查报告的格式和内容。你审查的报告应该是markdown格式。当你的审查完成之后，如不合格请审查意见并handoff给WriteAgent进行修改，如合格请handoff给WriteAgent进行发布。",
    llm=llm,
    tools=[review_report],
    can_handoff_to=["WriteAgent"]
)

agent_workflow = AgentWorkflow(
    agents=[research_agent, write_agent, review_agent],
    root_agent=research_agent.name,
    initial_state={
        "research_notes": {},
        "report_content": "",
        "review": ""
    }
)


async def main():
    ctx = Context(agent_workflow)
    handler = agent_workflow.run(user_msg="请撰写一篇关于敏捷软件研发流程的报告", ctx=ctx)

    current_agent = None
    async for event in handler.stream_events():
        if (
            hasattr(event, "current_agent_name")
            and event.current_agent_name != current_agent
        ):
            current_agent = event.current_agent_name
            print(f"\n{'='*50}")
            print(f"🤖 Agent: {current_agent}")
            print(f"{'='*50}\n")
        elif isinstance(event, AgentOutput):
            if event.response.content:
                print("📤 Output:", event.response.content)
            if event.tool_calls:
                print(
                    "🛠️  Planning to use tools:",
                    [call.tool_name for call in event.tool_calls],
                )
        elif isinstance(event, ToolCallResult):
            print(f"🔧 Tool Result ({event.tool_name}):")
            print(f"  Arguments: {event.tool_kwargs}")
            print(f"  Output: {event.tool_output}")
        elif isinstance(event, ToolCall):
            print(f"🔨 Calling Tool: {event.tool_name}")
            print(f"  With arguments: {event.tool_kwargs}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
