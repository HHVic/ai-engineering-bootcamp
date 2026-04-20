"""工具模块导出"""
from app.tools.weather import WeatherTool
from app.tools.news import NewsTool


def get_all_tools() -> list:
    """获取所有可用工具"""
    return [
        WeatherTool(),
        NewsTool(),
    ]
