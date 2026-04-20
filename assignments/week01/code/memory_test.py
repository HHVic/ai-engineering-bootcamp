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


