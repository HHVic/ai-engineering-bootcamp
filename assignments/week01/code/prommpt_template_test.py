import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# 加载环境变量
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
base_url = os.getenv('OPENAI_API_BASE')
model = os.getenv('OPENAI_MODEL')

# ========== 1. 初始化 LLM（大语言模型） ==========
# LangChain 特点：统一的 LLM 接口，支持多种模型提供商
llm = ChatOpenAI(
    base_url=base_url,
    api_key=api_key,
    model=model,
    temperature=0.7  # LangChain 特点：统一的参数配置
)

# 定义模板：{city} 是占位符
template = """
你是一个贴心的旅行助手。
请根据用户提供的城市，用以下格式回答：

【城市】{city}
【天气】晴朗，25°C
【建议】适合穿短袖，记得防晒！

注意：不要添加额外说明，严格按上述格式输出。
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | llm
response = chain.invoke({'city': '南京'})
print(response.content)

msg_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个严谨的数学老师，只回答计算题，不解释过程。"),
        ("human", "计算：{expression}")
    ]
)
chain = msg_prompt | llm
print(chain.invoke({"expression": "123 + 456"}).content)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个情感分析器，请判断用户评论的情绪，并返回 'positive' 或 'negative'。"),
    ("human", "这个手机电池太差了，一天充三次电！"),
    ("ai", "negative"),
    ("human", "屏幕超清晰，打游戏特别爽！"),
    ("ai", "positive"),
    ("human", "{comment}")
])

chain = prompt | llm
result = chain.invoke({"comment": "oh,fuck"})
print(result.content)  # 输出：negative

# 2. 定义 ChatPromptTemplate（更自然）
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个电商文案专家，擅长用吸引人的方式描述产品。"),
    ("human", "请为以下产品生成一段 50 字以内的营销文案：{product}")
])

# 3. 构建 Chain（LCEL 方式）
chain = prompt | llm

# 4. 调用
result = chain.invoke({"product": "3090显卡"})
print(result.content)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个文案专家。"),
    ("human", "用{tone}的语气，为{product}写一段营销文案。")
])

chain = prompt | llm
result = chain.invoke({
    "product": "智能手表",
    "tone": "幽默风趣"
})
print(result.content)


