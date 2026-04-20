# 多任务问答助手

基于 LangChain + LangGraph 构建的多任务问答助手，支持天气查询、新闻获取等功能。支持 OpenAI 和本地 Ollama 模型。

## 功能特性

- ✅ **工具自动路由**：根据用户意图自动选择合适工具
- ✅ **历史对话上下文**：支持多轮对话，维护会话状态
- ✅ **结果缓存**：减少重复 API 请求
- ✅ **错误处理**：优雅降级和异常捕获
- ✅ **防无限递归**：通过 LangGraph 检查点机制管理
- ✅ **双模型支持**：支持 OpenAI 和本地 Ollama

## 技术架构

```
┌───────────┐     ┌───────────┐     ┌───────────┐
│  用户输入  │ ──▶ │ LangGraph │ ──▶ │ 工具调用   │
└───────────┘     │  Agent    │     │ (weather/  │
                  └───────────┘     │  news)     │
                         │          └───────────┘
                         │             │
                         ▼             ▼
                  ┌───────────┐  ┌───────────┐
                  │  对话历史  │  │   缓存    │
                  └───────────┘  └───────────┘
```

## 快速开始

### 方式 1: 使用 OpenAI

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env:
OPENAI_API_KEY=sk-xxx
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# 2. 安装依赖
pip install -e .

# 3. 运行
python run.py
```

### 方式 2: 使用本地 Ollama (推荐)

```bash
# 1. 确保 Ollama 已启动
ollama serve

# 2. 拉取模型
ollama pull qwen2.5:7b

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env:
OPENAI_API_KEY=ollama
OPENAI_API_BASE=http://localhost:11434/v1
OPENAI_MODEL=qwen2.5:7b

# 4. 运行
python run.py
```

## 使用示例

```
=== 多任务问答助手 ===
输入 "help" 查看所有命令

> 帮我查一下今天的天气
正在查询天气...
北京今天晴，温度 20-28°C，湿度 45%。

> 那明天的呢？
北京明天多云，温度 18-26°C。

> 最近有什么新闻？
正在获取新闻...
1. 科技新闻：...
2. 社会新闻：...

> history
[对话历史]
用户：帮我查一下今天的天气
助手：北京今天晴，温度 20-28°C，湿度 45%。
...

> clear
对话历史和缓存已清空。
```

## 项目结构

```
project01_1/
├── app/
│   ├── __init__.py
│   ├── main.py              # 命令行入口
│   ├── tools/               # 工具定义
│   │   ├── base.py          # 工具基类
│   │   ├── weather.py       # 天气工具
│   │   └── news.py          # 新闻工具
│   ├── chain/               # LangGraph 链
│   │   └── core.py          # 核心问答链
│   ├── state/               # 状态管理
│   │   ├── history.py       # 对话历史
│   │   └── cache.py         # 缓存管理
│   └── config/              # 配置
│       └── settings.py      # 配置管理
├── tests/                   # 单元测试
├── pyproject.toml           # 项目配置
├── requirements.txt         # 依赖列表
├── .env.example             # 环境变量示例
└── README.md
```

## 核心模块说明

### 1. 核心问答链 (`app/chain/core.py`)

```python
class MultiTaskAssistant:
    def chat(self, query: str) -> Dict[str, Any]:
        """处理用户查询，返回回答和元信息"""
        pass
```

### 2. 工具封装 (`app/tools/`)

```python
class WeatherTool(BaseTool):
    def run(self, city: str) -> str:
        """查询天气"""
        pass
```

### 3. 状态管理 (`app/state/`)

- `ConversationHistory`: 维护对话上下文（默认 10 条消息）
- `CacheManager`: 文件缓存，TTL 过期

## 配置说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `OPENAI_API_KEY` | `ollama` | API 密钥 |
| `OPENAI_API_BASE` | `http://localhost:11434/v1` | API 地址 |
| `OPENAI_MODEL` | `qwen2.5:7b` | 模型名称 |
| `CACHE_ENABLED` | `true` | 是否启用缓存 |
| `DEBUG` | `false` | 调试模式 |

## 关键挑战解决方案

### 1. 如何判断是否需要调用工具？

使用 LangGraph 的 ReAct Agent，LLM 会自动分析用户意图：
- 如果问题包含天气、新闻等关键词 → 调用对应工具
- 如果是一般知识问答 → 直接回答

### 2. 如何防止无限递归或死循环？

- LangGraph 内置 `max_iterations` 限制
- MemorySaver 检查点机制防止状态混乱
- 缓存机制避免重复计算

### 3. 如何记录对话状态？

- `ConversationHistory` 类维护消息窗口（默认 10 条）
- LangGraph 检查点自动保存对话状态
- 支持 `history` 命令查看历史

## 扩展开发

添加新工具只需：

```python
# 1. 在 app/tools/ 创建新工具
class NewTool(BaseTool):
    def run(self, param: str) -> str:
        return "结果"

# 2. 在 get_all_tools() 中注册
def get_all_tools():
    return [WeatherTool(), NewsTool(), NewTool()]
```

## 技术栈

- **LangChain**: LLM 应用框架
- **LangGraph**: 有向图工作流引擎
- **Ollama**: 本地模型推理
- **Pydantic**: 数据验证

## License

MIT
