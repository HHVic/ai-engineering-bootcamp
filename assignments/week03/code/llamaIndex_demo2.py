import os
import logging
import sys
import httpx

from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.openai_like import OpenAILikeEmbedding


# =========================
# 基础日志
# =========================
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


# =========================
# 工具函数
# =========================
def build_settings() -> None:
    """初始化 LLM 和 Embedding 配置"""
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_API_BASE")
    llm_model = os.getenv("OPENAI_MODEL")
    embed_model = os.getenv("OPENAI_MODEL_1")

    if not api_key:
        raise ValueError("缺少环境变量 OPENAI_API_KEY")
    if not base_url:
        raise ValueError("缺少环境变量 OPENAI_API_BASE")
    if not llm_model:
        raise ValueError("缺少环境变量 OPENAI_MODEL")
    if not embed_model:
        raise ValueError("缺少环境变量 OPENAI_MODEL_1")

    # 不信任系统代理，避免本地/局域网模型被代理干扰
    http_client = httpx.Client(trust_env=False, timeout=300.0)

    Settings.llm = OpenAILike(
        model=llm_model,
        api_base=base_url,
        api_key=api_key,
        is_chat_model=True,
        timeout=300.0,
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


def load_documents(data_dir: str):
    """读取文档，并给每个文档附带文件名 metadata"""
    documents = SimpleDirectoryReader(
        data_dir,
        file_metadata=lambda path: {"file_name": os.path.basename(path)},
    ).load_data()
    return documents


def build_index(data_dir: str) -> VectorStoreIndex:
    """构建索引"""
    documents = load_documents(data_dir)
    print(f"已加载文档数: {len(documents)}")
    return VectorStoreIndex.from_documents(documents)


def print_sources(resp) -> None:
    """打印 source_nodes 调试信息"""
    print("\n=== 来源 source_nodes ===")

    source_nodes = getattr(resp, "source_nodes", None)
    if not source_nodes:
        print("没有 source_nodes，可能是当前返回对象未携带来源。")
        print("你可以先打印 dir(resp) 看对象字段：")
        print(dir(resp))
        return

    for i, nws in enumerate(source_nodes, 1):
        score = getattr(nws, "score", None)
        node = getattr(nws, "node", None)

        print(f"\n[{i}] score={score}")

        if node is None:
            print("node: None")
            continue

        metadata = getattr(node, "metadata", {}) or {}
        text = getattr(node, "text", "")

        print("file_name:", metadata.get("file_name"))
        print("metadata:", metadata)
        print("text_preview:")
        print(text[:400].replace("\n", " "))
        print("-" * 60)


def ask_question(index: VectorStoreIndex, question: str, debug_retrieval: bool = False) -> None:
    """
    提问并打印结果。
    debug_retrieval=False: 正常问答
    debug_retrieval=True: 只检索，不生成答案
    """
    if debug_retrieval:
        query_engine = index.as_query_engine(
            similarity_top_k=3,
            response_mode="no_text",   # 只看检索，不让 LLM 生成
        )
        print("\n" + "=" * 80)
        print(f"问题（检索调试模式）: {question}")
        print("=" * 80)
        resp = query_engine.query(question)
        print("=== response ===")
        print(getattr(resp, "response", resp))
        print_sources(resp)
    else:
        query_engine = index.as_query_engine(
            similarity_top_k=3,
            response_mode="compact",
        )
        print("\n" + "=" * 80)
        print(f"问题: {question}")
        print("=" * 80)
        resp = query_engine.query(question)

        print("=== 回答 ===")
        # resp 本身 print 出来通常只显示文本；这里显式取 response
        if hasattr(resp, "response"):
            print(resp.response)
        else:
            print(resp)

        print_sources(resp)


def run_all_questions(index: VectorStoreIndex) -> None:
    questions = [
        "1. 哪个项目最适合承载分成结算能力？",
        "2. 如果要新增分成结算能力，应该优先看哪些模块？",
        "3. 游戏备案和实名认证属于哪个项目？",
        "4. open-app 更像主干平台，还是业务应用集合？",
        "5. 我想增加分成结算应该怎么做？",
        "6. 如果外部系统要查询结算结果，应该改哪一层？",
        "7. 分成结算有哪些高风险点？",
        "8. 哪个项目不适合优先处理分成结算？",
    ]

    for q in questions:
        ask_question(index, q, debug_retrieval=False)


def run_debug_questions(index: VectorStoreIndex) -> None:
    """
    专门用来调试检索是否命中对的文档。
    你可以先只跑这一组。
    """
    debug_questions = [
        "哪个项目最适合承载分成结算能力？",
        "如果要新增分成结算能力，应该优先看哪些模块？",
        "哪个项目不适合优先处理分成结算？",
    ]

    for q in debug_questions:
        ask_question(index, q, debug_retrieval=True)


def main():
    data_dir = "/Users/huan/workspace/ai-engineering/ai-engineering-bootcamp/assignments/week03/data"

    build_settings()
    index = build_index(data_dir)

    # 先跑检索调试，看 source_nodes 命中了哪些文档
    print("\n\n########## 第一步：只看检索结果 ##########")
    run_debug_questions(index)

    # 再跑正常问答
    print("\n\n########## 第二步：正常问答 ##########")
    run_all_questions(index)


if __name__ == "__main__":
    main()