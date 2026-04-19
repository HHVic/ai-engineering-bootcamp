import os
import traceback
from typing import List

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ==============================
# 🔧 加载环境变量
# ==============================

load_dotenv()

BASE_URL = os.getenv("OPENAI_API_BASE")
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL")

if not BASE_URL:
    raise ValueError("❌ OPENAI_API_BASE 未设置")

# ==============================
# 🤖 LLM
# ==============================

llm = ChatOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    model=MODEL,
    temperature=0.7,
    extra_body={
        "options": {
            "num_ctx": 8192
        }
    }
)

# ==============================
# 🧠 工具（手写）
# ==============================

def get_weather(city: str):
    return f"{city} 今天天气晴，25°C"

def get_news(topic: str):
    return f"{topic} 的最新新闻：AI 正在快速发展"

# ==============================
# 🧭 Router（核心！）
# ==============================

router_prompt = ChatPromptTemplate.from_template("""
你是一个路由器，判断用户意图。

只返回一个词：
- weather
- news
- chat

用户输入：
{input}
""")

router_chain = router_prompt | llm | StrOutputParser()

# ==============================
# 💬 Chat Chain
# ==============================

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能助手"),
    ("placeholder", "{chat_history}"),
    ("human", "{input}")
])

chat_chain = chat_prompt | llm | StrOutputParser()

# ==============================
# 💾 Memory
# ==============================

chat_history: List = []

# ==============================
# 🏁 主循环
# ==============================

print("✅ LCEL 多任务助手已启动（输入 exit 退出）")

while True:
    query = input("\n你：")

    if query.lower() == "exit":
        break

    try:
        # ===== 1. 路由判断 =====
        route = router_chain.invoke({"input": query}).strip().lower()

        used_tool = None

        # ===== 2. 执行对应逻辑 =====
        if "weather" in route:
            used_tool = "WeatherTool"
            result = get_weather(query)

        elif "news" in route:
            used_tool = "NewsTool"
            result = get_news(query)

        else:
            result = chat_chain.invoke({
                "input": query,
                "chat_history": chat_history
            })

        # ===== 3. 输出 =====
        print("\n助手：", result)
        print("🔧 使用工具：", used_tool if used_tool else "无")

        # ===== 4. 更新记忆 =====
        chat_history.append(HumanMessage(content=query))
        chat_history.append(AIMessage(content=result))

    except Exception as e:
        print("\n❌ 出错：", str(e))
        traceback.print_exc()