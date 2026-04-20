"""天气查询工具"""
import requests
from typing import Optional
from langchain_core.tools import BaseTool
from pydantic import Field
from app.config.settings import get_settings


class WeatherTool(BaseTool):
    """天气查询工具
    
    功能：
    - 实时天气查询
    - 天气 forecast
    - 支持城市和日期参数
    """
    
    name: str = "weather_query"
    description: str = """查询指定城市的天气信息。
    适用于回答关于天气的问题，如：
    - "今天的天气怎么样"
    - "明天北京会下雨吗"
    - "上海未来三天的天气"""
    
    def _run(self, city: str, date: Optional[str] = "today") -> str:
        """
        查询天气
        
        Args:
            city: 城市名称（中文或英文）
            date: 日期（today/tomorrow/具体日期）
        """
        settings = get_settings()
        
        # 城市映射（简化版）
        city_map = {
            "北京": "Beijing",
            "上海": "Shanghai",
            "广州": "Guangzhou",
            "深圳": "Shenzhen",
            "成都": "Chengdu",
            "杭州": "Hangzhou",
        }
        
        # 城市名称标准化
        city_en = city_map.get(city, city)
        
        # 模拟天气数据（实际项目中应调用真实 API）
        weather_data = self._get_mock_weather(city_en, date)
        
        return weather_data
    
    def _get_mock_weather(self, city: str, date: str) -> str:
        """模拟天气数据（用于演示）"""
        # 实际项目中使用：
        # response = requests.get(
        #     f"https://api.weatherapi.com/v1/forecast.json",
        #     params={"key": settings.weather_api_key, "q": city, "days": 3}
        # )
        # return response.json()
        
        # 模拟数据
        mock_responses = {
            "today": f"{city} 今天天气晴朗，气温 20-28°C，湿度 60%，东南风 2 级。",
            "tomorrow": f"{city} 明天多云转晴，气温 18-26°C，湿度 55%，东北风 3 级。",
        }
        
        return mock_responses.get(date, mock_responses["today"])
