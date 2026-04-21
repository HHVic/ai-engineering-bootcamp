import os
import logging
import sys
import httpx

from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.openai_like import OpenAILikeEmbedding

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_API_BASE")
llm_model = os.getenv("OPENAI_MODEL")      # 先别用 27B，换成更小的
embed_model = os.getenv("OPENAI_MODEL_1")

http_client = httpx.Client(trust_env=False, timeout=600.0)

Settings.llm = OpenAILike(
    model=llm_model,
    api_base=base_url,
    api_key=api_key,
    is_chat_model=True,
    timeout=600.0,
    max_retries=1,
    http_client=http_client,
)

Settings.embed_model = OpenAILikeEmbedding(
    model_name=embed_model,
    api_key=api_key,
    api_base=base_url,
    embed_batch_size=2,
    timeout=300.0,
    max_retries=1,
    http_client=http_client,
)

documents = SimpleDirectoryReader(
    "/Users/huan/workspace/ai-engineering/ai-engineering-bootcamp/assignments/week03/data"
).load_data()

index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine(
    similarity_top_k=1,
    response_mode="compact",
)

resp = query_engine.query("1. 哪个项目最适合承载分成结算能力？")
print(f"第一题结果: {resp}")

resp = query_engine.query("2. 如果要新增分成结算能力，应该优先看哪些模块？")
print(f"第二题结果: {resp}")

resp = query_engine.query("3. 游戏备案和实名认证属于哪个项目")
print(f"第三题结果: {resp}")

resp = query_engine.query("4. open-app 更像主干平台，还是业务应用集合？")
print(f"第四题结果: {resp}")

resp = query_engine.query("5. 我想增加分成结算应该怎么做？")
print(f"第五题结果: {resp}")

resp = query_engine.query("6. 如果外部系统要查询结算结果，应该改哪一层？")
print(f"第六题结果: {resp}")

resp = query_engine.query("7. 分成结算有哪些高风险点？")
print(f"第七题结果: {resp}")

resp = query_engine.query("8. 哪个项目不适合优先处理分成结算？")
print(f"第八题结果: {resp}")