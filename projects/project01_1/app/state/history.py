"""对话历史管理"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
from app.config.settings import get_settings


@dataclass
class Message:
    """消息数据结构"""
    role: str  # "user" or "assistant"
    content: str
    tools_used: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=lambda: 0.0)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        return cls(**data)


class ConversationHistory:
    """对话历史管理器
    
    功能：
    - 记录对话历史
    - 维护消息窗口（限制历史长度）
    - 提供上下文提取
    """
    
    def __init__(self):
        self.messages: List[Message] = []
        self.settings = get_settings()
        self.max_messages = self.settings.max_history_messages
    
    def add_user_message(self, content: str) -> Message:
        """添加用户消息"""
        from time import time
        message = Message(
            role="user",
            content=content,
            timestamp=time(),
        )
        self._add_message(message)
        return message
    
    def add_assistant_message(
        self, 
        content: str, 
        tools_used: List[str] = None
    ) -> Message:
        """添加助手消息"""
        from time import time
        message = Message(
            role="assistant",
            content=content,
            tools_used=tools_used or [],
            timestamp=time(),
        )
        self._add_message(message)
        return message
    
    def _add_message(self, message: Message) -> None:
        """添加消息并维护窗口大小"""
        self.messages.append(message)
        
        # 维护窗口大小（保留最近的 N 条消息）
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_recent_messages(self, count: Optional[int] = None) -> List[Message]:
        """获取最近的对话消息"""
        if count is None:
            count = self.max_messages
        return self.messages[-count:]
    
    def get_context_for_llm(self) -> List[Dict]:
        """获取 LLM 可用的上下文"""
        return [msg.to_dict() for msg in self.messages]
    
    def clear(self) -> None:
        """清空对话历史"""
        self.messages.clear()
    
    def get_last_user_query(self) -> Optional[str]:
        """获取最后一条用户消息"""
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg.content
        return None
    
    def __len__(self) -> int:
        return len(self.messages)
