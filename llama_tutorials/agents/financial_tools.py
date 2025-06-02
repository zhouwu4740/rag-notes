import asyncio
from llama_index.tools.yahoo_finance import YahooFinanceToolSpec
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI


tools = YahooFinanceToolSpec().to_tool_list()

# for i, tool in enumerate(tools):
#     print(f"{i+1}: ")
#     print(f"  name: {tool.metadata.name}")
#     print(f"  description: {tool.metadata.description}")
#     print()

llm = OpenAI(model="gpt-4o-mini")
agent = FunctionAgent(
    name="财经分析师",
    description="你是一个财经分析师，擅长分析股票、基金、债券等财经数据",
    llm=llm,
    tools=tools,
    system_prompt="你是一个财经分析师，擅长分析股票、基金、债券等财经数据",
)


async def run(q: str):
    response = await agent.run(q)
    print(response)


if __name__ == "__main__":
    asyncio.run(run("What's the current stock price of NVIDIA?"))
