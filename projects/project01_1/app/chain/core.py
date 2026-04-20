"""核心问答链 - 使用 LangGraph 实现"""
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from app.config.settings import get_settings
from app.state.history import ConversationHistory
from app.state.cache import CacheManager
from app.tools import get_all_tools


class MultiTaskAssistant:
    """多任务问答助手
    
    核心功能：
    1. 工具自动路由：判断是否需要调用工具
    2. 防无限递归：限制最大迭代次数
    3. 对话状态管理：记录上下文和历史
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.history = ConversationHistory()
        self.cache = CacheManager()
        
        # 初始化 LLM（支持 OpenAI 和 Ollama）
        self.llm = ChatOpenAI(
            model=self.settings.openai_model,
            temperature=0.7,
            api_key=self.settings.openai_api_key,
            base_url=self.settings.openai_api_base,
        )
        
        # 初始化工具
        self.tools = get_all_tools()
        
        # 初始化 Agent (使用 LangGraph)
        self._init_agent()
        
        if self.settings.debug:
            print(f"✓ 使用模型：{self.settings.openai_model}")
            print(f"✓ API 地址：{self.settings.openai_api_base}")
    
    def _init_agent(self) -> None:
        """使用 LangGraph 初始化 Agent"""
        # 配置检查点以支持对话历史
        checkpointer = MemorySaver()
        
        # 创建 ReAct Agent
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            checkpointer=checkpointer,
        )
    
    def chat(self, query: str) -> Dict[str, Any]:
        """
        处理用户查询
        
        Args:
            query: 用户输入的问题
            
        Returns:
            包含回答和元信息的字典
        """
        # 检查缓存
        cached_result = self._check_cache(query)
        if cached_result:
            # 添加到历史
            self.history.add_user_message(query)
            self.history.add_assistant_message(cached_result, [])
            
            return {
                "answer": cached_result,
                "tools_used": [],
                "from_cache": True,
            }
        
        # 添加到历史
        self.history.add_user_message(query)
        
        try:
            # 准备配置（使用会话 ID 追踪对话）
            config = {
                "configurable": {
                    "thread_id": "default-session"
                }
            }
            
            # 准备消息（添加系统提示）
            system_msg = SystemMessage(content="""你是一个智能助手，能够根据用户问题自动选择合适的工具。

工具使用规则：
1. 如果问题需要实时数据（天气、新闻等），调用对应工具
2. 如果是一般问答，直接回答即可
3. 如果无法回答，诚实告知用户

请以友好、简洁的方式回答用户的问题。""")
            
            # 执行 Agent
            result = self.agent.invoke({
                "messages": [system_msg, {"role": "user", "content": query}]
            }, config=config)
            
            # 提取回答
            answer = ""
            tools_used = []
            
            if "messages" in result:
                last_msg = result["messages"][-1]
                if isinstance(last_msg, AIMessage):
                    answer = last_msg.content
                    # 提取工具调用
                    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                        tools_used = list(set(tc['name'] for tc in last_msg.tool_calls))
            
            # 保存到缓存
            if tools_used:
                self.cache.set(query, answer, tool_name=tools_used[0])
            
            # 添加到历史
            self.history.add_assistant_message(answer, tools_used)
            
            return {
                "answer": answer,
                "tools_used": tools_used,
                "from_cache": False,
            }
            
        except Exception as e:
            # 错误处理
            error_msg = f"抱歉，我遇到了一个问题：{str(e)}"
            self.history.add_assistant_message(error_msg, ["error"])
            
            return {
                "answer": error_msg,
                "tools_used": [],
                "from_cache": False,
                "error": str(e),
            }
    
    def _check_cache(self, query: str) -> Optional[str]:
        """检查缓存"""
        # 提取可能的工具名（简化版）
        if "天气" in query:
            return self.cache.get(query, "WeatherTool")
        elif "新闻" in query:
            return self.cache.get(query, "NewsTool")
        return None
    
    def get_history(self) -> List[Dict]:
        """获取对话历史"""
        return self.history.get_context_for_llm()
    
    def clear_history(self) -> None:
        """清空对话历史"""
        self.history.clear()
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self.cache.clear()
