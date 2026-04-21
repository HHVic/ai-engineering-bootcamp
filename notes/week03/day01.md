# LlamaIndex RAG 学习日报 - Day 1
日期：2026-04-22
学习时长：约 3~4 小时

## 1. 今天的目标
- 搭建 LlamaIndex 基础运行环境
- 使用本地/兼容 OpenAI 接口模型跑通最小 RAG
- 构建一个基于 Markdown 文档的简单知识库
- 学会查看检索结果 source_nodes，判断是检索问题还是生成问题

## 2. 今天实际完成的内容
- 配置了 LlamaIndex 的 LLM 与 Embedding
- 使用 OpenAILike 和 OpenAILikeEmbedding 接入兼容 OpenAI 接口的模型服务
- 读取本地 data/ 目录中的 Markdown 文档，成功构建 VectorStoreIndex
- 初期使用 27B 本地模型时出现超时，后切换为 9B 模型，成功完成问答
- 为文档增加了 file_name metadata，方便调试来源
- 增加了两种查询模式：
  - 正常问答模式：response_mode="compact"
  - 检索调试模式：response_mode="no_text"
- 成功打印并分析了 resp.source_nodes
- 完成了 8 个测试问题的问答验证

## 3. 今天学会了什么

### 概念1：LlamaIndex 的基本 RAG 流程
#### 我的理解：LlamaIndex 的最基本流程是：先把文档读进来，再构建索引，然后通过 query engine 检索相关内容并生成回答。
#### 例子：
  我今天用 SimpleDirectoryReader -> VectorStoreIndex.from_documents -> as_query_engine -> query() 跑通了整个流程。

### 概念2：OpenAILike 和 OpenAILikeEmbedding
#### 我的理解：它们适合接兼容 OpenAI 接口的模型服务，不一定非要用 OpenAI 官方接口。
#### 例子：
  我把本地/兼容接口模型接进了 Settings.llm 和 Settings.embed_model。

### 概念3：RAG 的问题不一定出在生成，有时出在检索
#### 我的理解：如果回答不准，不能直接怪模型，要先看 source_nodes，确认检索到了哪些文档。
#### 例子：
  之前问“增加分成结算应该怎么做”时答偏，后来通过 source_nodes 发现需要检查命中的文档和排序。

### 概念4：resp.source_nodes
#### 我的理解：它表示这次回答参考了哪些检索片段，是判断检索是否准确的关键。
#### 例子：
  我今天成功打印了每个 source node 的 score、file_name 和文本预览。

### 概念5：response_mode="no_text"
#### 我的理解：这个模式只检索不生成，非常适合调试检索效果。
#### 例子：
  我用它确认“分成结算”相关问题主要命中了 01-miniapp-settlement-overview.md 和 02-miniapp-settlement-implementation-guide.md。

## 4. 今天写了什么代码
- 文件名：
  llamaIndex_demo.py / llamaIndex_demo2.py

- 主要代码功能：
  - 加载环境变量
  - 初始化 LLM 和 Embedding
  - 读取本地文档
  - 构建索引
  - 执行问答
  - 打印检索来源

- 关键代码片段：
```python
import os
import httpx
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.openai_like import OpenAILikeEmbedding

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_API_BASE")
llm_model = os.getenv("OPENAI_MODEL")
embed_model = os.getenv("OPENAI_MODEL_1")

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

documents = SimpleDirectoryReader(
    "/Users/huan/workspace/ai-engineering/ai-engineering-bootcamp/assignments/week03/data",
    file_metadata=lambda path: {"file_name": os.path.basename(path)},
).load_data()

index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine(
    similarity_top_k=3,
    response_mode="compact",
)

resp = query_engine.query("如果要新增分成结算能力，应该优先看哪些模块？")
print(resp.response)

for i, nws in enumerate(resp.source_nodes, 1):
    print(i, nws.score, nws.node.metadata.get("file_name"))
```


## 5. 运行结果
- 是否成功运行：是
- 主要结果：
  - 成功读取 8 个文档
  - 成功建立索引
  - 成功完成 embedding
  - 成功调用 chat/completions
  - 成功打印 source_nodes
- 八个测试问题中，大多数回答正确，尤其是项目归属、模块定位、风险点和实施步骤类问题表现较好

## 6. 今天遇到的问题

- 问题1：ModuleNotFoundError: No module named 'llama_index.llms.openai_like'
- 我觉得原因是什么：
  对应的 LlamaIndex 集成包没有安装，或者版本不匹配
- 我尝试过什么办法：
  安装和升级相关包后解决

- 问题2：本地 27B 模型超时
- 我觉得原因是什么：
  本地模型太大，推理速度慢，超过默认 timeout
- 我尝试过什么办法：
  调大 timeout，最后换成 9B 模型，成功跑通

- 问题3：回答内容一开始不准确
- 我觉得原因是什么：
  可能是检索命中了不合适的文档，或者题目表达不够适合当前语料
- 我尝试过什么办法：
  打印 source_nodes，增加 file_name metadata，并用 response_mode="no_text" 检查检索结果

- 问题4：不清楚 resp.source_nodes 怎么看
- 我觉得原因是什么：
  直接 print(resp) 只能看到最终回答，不会自动展示对象的所有属性
- 我尝试过什么办法：
  单独打印 resp.response 和 resp.source_nodes，并查看每个 node 的 metadata 和文本片段

## 7. 今天的作业提交
- 作业名称：
  使用 LlamaIndex 构建一个简单的 Markdown 知识库，并完成 RAG 问答测试

- 完成情况：
  已完成

- 作业内容总结：
  我使用 8 个 Markdown 文档构建了一个知识库，其中包含：
  - 4 个项目相关文档
  - 4 个无关测试文档

  我完成了索引构建、问答测试和 source_nodes 调试，并验证了：
  - 分成结算相关问题主要命中结算文档
  - 游戏备案问题主要命中游戏合规文档
  - open-app 类型问题主要命中 open-app 文档

- 运行结果：
  8 个问题中，大部分回答正确
  检索结果整体合理，已经具备基本 RAG 能力

- 你给自己的评分（满分10分）：
  8.5 分

- 你最不确定的地方：
  - 否定类问题为什么更容易答偏
  - 当前默认切片方式具体是怎么工作的
  - similarity_top_k、chunk_size、chunk_overlap 对结果的影响还没有完全吃透

## 8. 今日复盘
- 今天最重要的收获：
  我已经把 LlamaIndex 的最小 RAG 主链路跑通了，而且学会了用 source_nodes 来分析检索质量。

- 今天最容易混淆的点：
  一开始我容易把“回答不准”直接理解为“模型不行”，后来才意识到要先区分是检索问题还是生成问题。

- 今天还有什么没搞懂：
  - 否定类问题为什么向量检索不稳定
  - 怎样设计更适合检索的测试问题
  - 默认 chunk 切分是否适合当前数据集

## 9. 明天计划
- 理解 LlamaIndex 默认切片方式（SentenceSplitter、chunk_size、chunk_overlap）
- 试着手动设置 chunk_size 和 overlap，比较检索结果变化
- 继续测试“否定题 / 排除题 / 多项目比较题”
- 优化 prompt，让回答先给结论再解释
- 视情况补装 llama-index-readers-file