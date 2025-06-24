from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
from llama_index.core.agent.workflow import FunctionAgent
import asyncio


llm = OpenAI(model="gpt-4o-mini")
# llm = Ollama(model="deepseek-r1:1.5b")


def add(a: int, b: int) -> int:
    """计算两个数的和"""
    print(f"计算{a}+{b}的和")
    return a + b


def subtract(a: int, b: int) -> int:
    """计算两个数的差"""
    print(f"计算{a}-{b}的差")
    return a - b


def multiply(a: int, b: int) -> int:
    """计算两个数的积"""
    print(f"计算{a}*{b}的积")
    return a * b


def divide(a: int, b: int) -> int:
    """计算两个数的商"""
    print(f"计算{a}/{b}的商")
    return a / b


agent = FunctionAgent(
    llm=llm,
    tools=[add, subtract, multiply, divide],
    prompt="你是一个Agent，请根据用户输入问题决定使用哪个工具完成数值计算。")


async def run(q: str):
    response = await agent.run(q)
    print(response)


if __name__ == "__main__":
    # asyncio.run(run("计算199*199"))
    asyncio.run(run("计算20*(5+4)"))
