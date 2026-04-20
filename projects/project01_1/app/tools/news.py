"""新闻查询工具"""
from typing import Optional, List
from langchain_core.tools import BaseTool
from pydantic import Field


class NewsTool(BaseTool):
    """新闻查询工具
    
    功能：
    - 获取最新新闻
    - 按类别筛选新闻
    - 支持关键词搜索
    """
    
    name: str = "news_query"
    description: str = """查询最新新闻。
    适用于回答关于新闻的问题，如：
    - "最近的新闻有哪些"
    - "科技新闻有什么"
    - "搜索人工智能相关的新闻"""
    
    def _run(self, category: Optional[str] = None, limit: int = 5) -> str:
        """
        查询新闻
        
        Args:
            category: 新闻类别（technology/sports/entertainment 等）
            limit: 返回新闻数量
        """
        return self._get_mock_news(category, limit)
    
    def _get_mock_news(self, category: Optional[str] = None, limit: int = 5) -> str:
        """模拟新闻数据（用于演示）"""
        # 实际项目中使用真实新闻 API
        # 如：NewsAPI, Bing News API 等
        
        news_templates = {
            "technology": [
                "OpenAI 发布 GPT-5，性能大幅提升",
                "苹果发布新款 Vision Pro 头显",
                "谷歌推出新一代 AI 芯片",
            ],
            "sports": [
                "中国男足晋级世界杯预选赛",
                "NBA 总决赛即将开打",
                "巴黎奥运会筹备工作进展顺利",
            ],
            "entertainment": [
                "某电影票房破 10 亿",
                "知名歌手宣布巡回演唱会",
                "新剧热播引发热议",
            ],
        }
        
        if category and category in news_templates:
            news_list = news_templates[category][:limit]
        else:
            # 综合新闻
            all_news = []
            for cat_news in news_templates.values():
                all_news.extend(cat_news)
            news_list = all_news[:limit]
        
        result = "最新新闻：\n"
        for i, news in enumerate(news_list, 1):
            result += f"{i}. {news}\n"
        
        return result.strip()
