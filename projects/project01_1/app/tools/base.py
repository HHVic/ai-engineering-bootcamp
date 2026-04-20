"""工具基类定义"""
from abc import ABC, abstractmethod
from typing import Any
from langchain_core.tools import BaseTool
from pydantic import Field


class CustomTool(BaseTool, ABC):
    """自定义工具基类，提供统一的接口和错误处理"""
    
    name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")
    
    @abstractmethod
    def _run(self, *args: Any, **kwargs: Any) -> str:
        """执行工具逻辑"""
        pass
    
    def run_with_error_handling(self, *args: Any, **kwargs: Any) -> dict:
        """带错误处理的工具执行"""
        try:
            result = self._run(*args, **kwargs)
            return {
                "success": True,
                "result": result,
                "error": None,
            }
        except Exception as e:
            return {
                "success": False,
                "result": "",
                "error": str(e),
            }
