"""工具模块测试"""
import pytest
from app.tools import get_all_tools, WeatherTool, NewsTool


class TestToolInitialization:
    """工具初始化测试"""
    
    def test_get_all_tools_returns_list(self):
        """测试获取所有工具"""
        tools = get_all_tools()
        assert isinstance(tools, list)
        assert len(tools) >= 2
    
    def test_weather_tool_exists(self):
        """测试天气工具"""
        tools = get_all_tools()
        weather_tools = [t for t in tools if t.name == "weather_query"]
        assert len(weather_tools) == 1
    
    def test_news_tool_exists(self):
        """测试新闻工具"""
        tools = get_all_tools()
        news_tools = [t for t in tools if t.name == "news_query"]
        assert len(news_tools) == 1


class TestWeatherTool:
    """天气工具测试"""
    
    def test_weather_query_basic(self):
        """测试基本天气查询"""
        tool = WeatherTool()
        result = tool._run("北京", "today")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_weather_query_different_city(self):
        """测试不同城市的天气查询"""
        tool = WeatherTool()
        result = tool._run("上海", "today")
        assert "上海" in result or "Shanghai" in result


class TestNewsTool:
    """新闻工具测试"""
    
    def test_news_query_basic(self):
        """测试基本新闻查询"""
        tool = NewsTool()
        result = tool._run()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_news_query_by_category(self):
        """测试按类别查询新闻"""
        tool = NewsTool()
        result = tool._run(category="technology", limit=2)
        assert isinstance(result, str)
        assert len(result) > 0
