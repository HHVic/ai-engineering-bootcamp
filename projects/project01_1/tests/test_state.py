"""状态管理测试"""
import pytest
import tempfile
import os
from pathlib import Path
from app.state.cache import CacheManager
from app.state.history import ConversationHistory, Message


class TestConversationHistory:
    """对话历史测试"""
    
    def test_add_user_message(self):
        """测试添加用户消息"""
        history = ConversationHistory()
        msg = history.add_user_message("你好")
        assert msg.role == "user"
        assert msg.content == "你好"
    
    def test_add_assistant_message(self):
        """测试添加助手消息"""
        history = ConversationHistory()
        msg = history.add_assistant_message("你好！", ["WeatherTool"])
        assert msg.role == "assistant"
        assert msg.tools_used == ["WeatherTool"]
    
    def test_history_window_limit(self):
        """测试历史窗口限制"""
        history = ConversationHistory()
        history.max_messages = 3
        
        history.add_user_message("消息 1")
        history.add_assistant_message("回答 1")
        history.add_user_message("消息 2")
        history.add_assistant_message("回答 2")
        
        assert len(history) == 3  # 只保留最近 3 条
    
    def test_get_context_for_llm(self):
        """测试获取 LLM 上下文"""
        history = ConversationHistory()
        history.add_user_message("你好")
        history.add_assistant_message("你好！")
        
        context = history.get_context_for_llm()
        assert len(context) == 2
        assert all(isinstance(msg, dict) for msg in context)
    
    def test_clear_history(self):
        """测试清空历史"""
        history = ConversationHistory()
        history.add_user_message("测试")
        history.clear()
        assert len(history) == 0


class TestCacheManager:
    """缓存管理测试"""
    
    def test_cache_set_and_get(self):
        """测试缓存读写"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager()
            cache.cache_dir = Path(tmpdir)
            
            cache.set("测试查询", "测试结果", "TestTool")
            result = cache.get("测试查询", "TestTool")
            
            assert result == "测试结果"
    
    def test_cache_miss(self):
        """测试缓存未命中"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager()
            cache.cache_dir = Path(tmpdir)
            
            result = cache.get("不存在的查询", "TestTool")
            assert result is None
    
    def test_cache_key_generation(self):
        """测试缓存键生成"""
        cache = CacheManager()
        
        key1 = cache._get_cache_key("天气", "WeatherTool")
        key2 = cache._get_cache_key("天气", "WeatherTool")
        key3 = cache._get_cache_key("新闻", "NewsTool")
        
        assert key1 == key2  # 相同输入生成相同键
        assert key1 != key3  # 不同输入生成不同键
