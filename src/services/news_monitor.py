import aiohttp
import json
from datetime import datetime
from typing import List, Dict
import akshare as ak
from models.schemas import StockAnalysis

class NewsMonitor:
    def __init__(self):
        self.last_news_id = None
        self.api_url = "http://zhibo.sina.com.cn/api/zhibo/feed"
        self.deepseek_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.deepseek_key = "sk-bzguagzymvuubepardjpxvqmbljfhxpmgceddsrqzjnouezw"

    async def get_latest_news(self) -> List[Dict]:
        params = {
            "page": 1,
            "page_size": 20,
            "zhibo_id": 152
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url, params=params) as response:
                data = await response.json()
                return data.get("result", {}).get("data", [])

    async def analyze_news(self, title: str, content: str) -> StockAnalysis:
        # 构建分析提示
        prompt = f"""分析以下新闻对A股市场的影响：
        标题：{title}
        内容：{content}
        
        请判断：
        1. 这个新闻是否会对特定板块产生显著影响？
        2. 如果会，影响哪些板块？
        3. 推荐5支最具投资价值的相关股票
        4. 对每支股票的具体分析和操作建议"""

        headers = {
            "Authorization": f"Bearer {self.deepseek_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.deepseek_url, headers=headers, json=payload) as response:
                result = await response.json()
                analysis = result["choices"][0]["message"]["content"]
                
                # 处理分析结果
                # TODO: 解析AI返回的文本，提取结构化信息

    async def get_stock_data(self, stock_code: str):
        """获取股票实时数据"""
        try:
            stock_data = ak.stock_zh_a_spot_em()
            return stock_data[stock_data['代码'] == stock_code].to_dict('records')[0]
        except Exception as e:
            print(f"获取股票数据失败: {str(e)}")
            return None

    async def start_monitoring(self):
        """开始监控新闻"""
        while True:
            try:
                news_list = await self.get_latest_news()
                for news in news_list:
                    if news['id'] != self.last_news_id:
                        analysis = await self.analyze_news(news['title'], news['content'])
                        if analysis and analysis.impact_level != "无影响":
                            # TODO: 保存分析结果到数据库
                            # TODO: 通过WebSocket推送到前端
                            pass
                        self.last_news_id = news['id']
            except Exception as e:
                print(f"监控过程发生错误: {str(e)}")
            
            # 等待一定时间后再次检查
            await asyncio.sleep(60)