"""缓存管理"""
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Optional
from app.config.settings import get_settings


class CacheManager:
    """文件缓存管理器
    
    功能：
    - 查询结果缓存
    - TTL 过期机制
    - 缓存大小限制
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.cache_dir = Path(".cache")
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, query: str, tool_name: str = "") -> str:
        """生成缓存键"""
        key_str = f"{tool_name}:{query}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, query: str, tool_name: str = "") -> Optional[Any]:
        """获取缓存"""
        if not self.settings.cache_enabled:
            return None
        
        cache_key = self._get_cache_key(query, tool_name)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 检查 TTL
            if time.time() - data.get("timestamp", 0) > self.settings.cache_ttl:
                cache_file.unlink(missing_ok=True)
                return None
            
            return data.get("result")
        except (json.JSONDecodeError, IOError):
            return None
    
    def set(self, query: str, result: Any, tool_name: str = "") -> None:
        """设置缓存"""
        if not self.settings.cache_enabled:
            return
        
        cache_key = self._get_cache_key(query, tool_name)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump({
                    "result": result,
                    "timestamp": time.time(),
                    "query": query,
                    "tool": tool_name,
                }, f, ensure_ascii=False)
        except IOError:
            pass  # 缓存失败不阻塞主流程
    
    def clear(self) -> None:
        """清空缓存"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink(missing_ok=True)
