from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool

llm = OpenAI(model="gpt-4o-mini")


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


response = llm.predict_and_call(
    tools=[FunctionTool.from_defaults(add),
           FunctionTool.from_defaults(subtract),
           FunctionTool.from_defaults(multiply),
           FunctionTool.from_defaults(divide)],

    user_msg="计算100*100")

print(response)
