import os
from typing import TypedDict, List, Optional

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

from langgraph.graph import StateGraph, END

# ==============================
# 🔧 环境变量
# ==============================

load_dotenv()

BASE_URL = os.getenv("OPENAI_API_BASE")
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "qwen3.5:4b")

llm = ChatOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    model=MODEL,
    temperature=0
)

# ==============================
# 🧠 State（核心）
# ==============================

class AgentState(TypedDict):
    input: str
    route: Optional[str]
    output: Optional[str]
    chat_history: List
    tool_used: Optional[str]

# ==============================
# 🔧 Tools
# ==============================

def weather_tool(query: str):
    return f"{query}：晴天 25°C"

def news_tool(query: str):
    return f"{query}：AI 相关新闻爆发增长"

# ==============================
# 🧭 Router Node
# ==============================

def router_node(state: AgentState):
    prompt = f"""
你是路由器，只返回一个词：
weather / news / chat

用户输入：
{state["input"]}
"""
    route = llm.invoke(prompt).content.strip().lower()

    return {
        "route": route
    }

# ==============================
# 🌤 Weather Node
# ==============================

def weather_node(state: AgentState):
    result = weather_tool(state["input"])
    return {
        "output": result,
        "tool_used": "WeatherTool"
    }

# ==============================
# 📰 News Node
# ==============================

def news_node(state: AgentState):
    result = news_tool(state["input"])
    return {
        "output": result,
        "tool_used": "NewsTool"
    }

# ==============================
# 💬 Chat Node
# ==============================

def chat_node(state: AgentState):
    messages = state["chat_history"] + [HumanMessage(content=state["input"])]

    response = llm.invoke(messages)

    return {
        "output": response.content,
        "tool_used": None
    }

# ==============================
# 🔀 Router Decision
# ==============================

def route_decision(state: AgentState):
    route = state["route"]

    if "weather" in route:
        return "weather"
    elif "news" in route:
        return "news"
    else:
        return "chat"

# ==============================
# 🧱 构建图
# ==============================

graph = StateGraph(AgentState)

# 添加节点
graph.add_node("router", router_node)
graph.add_node("weather", weather_node)
graph.add_node("news", news_node)
graph.add_node("chat", chat_node)

# 设置入口
graph.set_entry_point("router")

# 路由分支
graph.add_conditional_edges(
    "router",
    route_decision,
    {
        "weather": "weather",
        "news": "news",
        "chat": "chat"
    }
)

# 结束
graph.add_edge("weather", END)
graph.add_edge("news", END)
graph.add_edge("chat", END)

# 编译
app = graph.compile()

# ==============================
# 💾 Memory
# ==============================

chat_history = []

# ==============================
# 🏁 运行
# ==============================

print("🚀 LangGraph 多任务助手启动（输入 exit 退出）")

while True:
    user_input = input("\n你：")

    if user_input.lower() == "exit":
        break

    state = {
        "input": user_input,
        "route": None,
        "output": None,
        "chat_history": chat_history,
        "tool_used": None
    }

    result = app.invoke(state)

    print("\n助手：", result["output"])
    print("🔧 使用工具：", result["tool_used"] or "无")

    # 更新记忆
    chat_history.append(HumanMessage(content=user_input))
    chat_history.append(AIMessage(content=result["output"]))