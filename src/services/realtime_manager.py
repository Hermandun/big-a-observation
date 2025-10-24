import os
import time
import json
import requests
from typing import List, Dict, Any, Optional
import akshare as ak
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.siliconflow.cn/v1")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEY".upper()) or os.getenv("DEEPSEEK_API")

SINA_7X24_API = "https://zhibo.sina.com.cn/api/zhibo/feed"

class RealTimeManager:
    def __init__(self):
        self.last_seen_id: Optional[str] = None

    def fetch_latest_news(self, page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        """同步请求新浪财经7x24小时实时新闻接口"""
        try:
            # 新浪财经7x24页面使用的API参数
            params = {
                "page": page,
                "page_size": page_size,
                "zhibo_id": 152,  # 财经频道ID
                "tag_id": 0,      # 0表示全部，10=A股，1=宏观等
                "dire": "f",      # f=forward向前翻页
                "dpc": 1,
                "pagesize": page_size
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Referer": "https://finance.sina.com.cn/7x24/"
            }
            resp = requests.get(SINA_7X24_API, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            # 提取新闻列表
            result = data.get("result", {})
            if isinstance(result, dict):
                news_list = result.get("data", {}).get("feed", {}).get("list", [])
            else:
                news_list = []
            
            # 格式化为统一结构
            formatted_news = []
            for item in news_list:
                if isinstance(item, dict):
                    formatted_news.append({
                        "id": item.get("id") or item.get("docid"),
                        "title": item.get("rich_text") or item.get("title", ""),
                        "content": item.get("rich_text") or item.get("content", ""),
                        "create_time": item.get("create_time", ""),
                        "source": "新浪财经7x24"
                    })
            
            return formatted_news if formatted_news else []
        except Exception as e:
            print(f"抓取新闻失败: {str(e)}")
            return []

    def call_deepseek(self, prompt: str, max_tokens: int = 800, use_reasoning: bool = False) -> Dict[str, Any]:
        """调用 DeepSeek 接口，返回解析后的 JSON（如果能解析）或原始文本
        
        Args:
            prompt: 提示词
            max_tokens: 最大token数
            use_reasoning: 是否使用推理模型R1（慢但深度思考），默认使用V3（快速）
        """
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }
        
        # 根据参数选择模型
        # DeepSeek-V3: 快速响应（5-10秒），适合高频调用
        # DeepSeek-R1: 深度推理（30-120秒），适合复杂分析
        model = "Pro/deepseek-ai/DeepSeek-R1" if use_reasoning else "Pro/deepseek-ai/DeepSeek-V3"
        timeout = 120 if use_reasoning else 30  # R1需要更长超时
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7,  # 适当的随机性
        }
        
        # 重试2次（减少重试次数，避免长时间等待）
        max_retries = 2
        for attempt in range(max_retries):
            try:
                r = requests.post(
                    DEEPSEEK_API_URL + "/chat/completions", 
                    headers=headers, 
                    json=payload, 
                    timeout=timeout
                )
                r.raise_for_status()
                res = r.json()
                
                # deepseek 返回的主文本通常在 choices[0].message.content
                content = None
                try:
                    content = res.get("choices", [])[0].get("message", {}).get("content")
                except Exception:
                    content = None
                
                if not content:
                    # 兜底：将整个响应转为字符串
                    return {"raw": res}
                
                # 清理可能的markdown代码块标记
                content_cleaned = content.strip()
                
                # 移除 ```json 和 ``` 标记
                if content_cleaned.startswith('```json'):
                    content_cleaned = content_cleaned[7:]  # 移除开头的 ```json
                elif content_cleaned.startswith('```'):
                    content_cleaned = content_cleaned[3:]  # 移除开头的 ```
                
                if content_cleaned.endswith('```'):
                    content_cleaned = content_cleaned[:-3]  # 移除结尾的 ```
                
                content_cleaned = content_cleaned.strip()
                
                # 尝试解析为 JSON
                try:
                    parsed = json.loads(content_cleaned)
                    return {"parsed": parsed, "raw_text": content}
                except json.JSONDecodeError as e:
                    # JSON解析失败，返回原始文本
                    return {"raw_text": content, "parse_error": str(e)}
                except Exception as e:
                    return {"raw_text": content, "error": str(e)}
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = 3 if use_reasoning else 1  # R1重试等待更久
                    print(f"⏱️ API超时，{wait_time}秒后重试 ({attempt + 1}/{max_retries - 1})...")
                    time.sleep(wait_time)
                    continue
                else:
                    model_name = "DeepSeek-R1(推理模型)" if use_reasoning else "DeepSeek-V3"
                    return {"error": f"{model_name}请求超时（已重试{max_retries}次）"}
            except Exception as e:
                return {"error": str(e)}
        
        return {"error": "未知错误"}

    def level1_prompt(self, title: str, content: str) -> str:
        return f"""
【分析任务】
基于以下新闻内容，判断是否会对2025年A股特定板块产生显著影响。

【新闻信息】
标题：{title}
内容：{content}

【分析要求】
1. 快速识别新闻影响的具体板块（如：新能源、半导体、医药、消费等）
2. 基于2025年当前市场环境，判断该影响是否显著
3. 严格按照以下JSON格式返回（注意：只返回纯JSON，不要用markdown代码块包裹）：

{{
  "impact": "是/否",
  "affected_sectors": ["板块1", "板块2"],
  "reason": "200字以内的详细说明，包括影响逻辑和市场预期"
}}

【判断标准】
- 返回"是"的情况：政策重大变化、行业重大突破、供需关系显著改变、龙头企业重大事件
- 返回"否"的情况：常规行业动态、已有预期的事件、影响范围有限的消息

⚠️ 重要：直接返回JSON对象，不要用```json或```包裹，不要添加任何解释文字。
请确保分析客观准确，避免过度解读。
"""

    def level2_prompt(self, title: str, affected_sectors: List[str], impact_reason: str, real_time_data: Dict[str, Any]) -> str:
        # 把实时行情数据序列化为短文本供模型参考
        rt = json.dumps(real_time_data, ensure_ascii=False)
        return f"""
你是一个资深的A股量化策略师，需要基于新闻影响和实时行情数据制定具体操作策略。

【背景信息】
新闻标题：{title}
影响板块：{affected_sectors}
影响原因：{impact_reason}

【实时行情数据】
{rt}

【分析要求】
请为每个推荐股票提供完整分析，严格返回可解析的JSON（注意：只返回纯JSON，不要用markdown代码块包裹），结构参考：

{{
  "recommended_stocks": [{{
    "stock_code": "",
    "stock_name": "",
    "current_price": "",
    "background_analysis": "",
    "selection_reason": "",
    "operation_timing": {{"buy_time": "", "buy_price_range": "", "position_recommendation": "", "sell_time": "", "sell_price_range": "", "stop_loss_price": ""}},
    "risk_level": "",
    "expected_return": ""
  }}],
  "overall_strategy": "",
  "market_outlook": ""
}}

⚠️ 重要：直接返回JSON对象，不要用```json或```包裹，不要添加任何解释文字。

操作原则：
1. 买入时机：选择早盘流动性充足时段或盘中回调时机
2. 卖出时机：选择尾盘或次日早盘冲高时机
3. 仓位控制：单只股票不超过总资金10%
4. 风险收益比：至少1:2以上
5. 持有周期：1-3个交易日

请基于实时数据给出具体可执行的操作建议。
"""

    def pick_candidate_stocks(self, num: int = 5) -> List[Dict[str, Any]]:
        """从 AkShare 获取全市场实时数据并挑选候选股票（按换手率或涨跌幅等）"""
        try:
            df = ak.stock_zh_a_spot_em()
            # 按换手率列名可能为 '换手率'，如果不存在则按绝对涨跌幅
            if '换手率' in df.columns:
                df2 = df.sort_values(by='换手率', ascending=False).head(num)
            elif '涨跌幅' in df.columns:
                df2 = df.reindex(df['涨跌幅'].abs().sort_values(ascending=False).index).head(num)
            else:
                df2 = df.head(num)
            res = []
            for _, row in df2.iterrows():
                res.append({
                    'code': str(row.get('代码') or row.get('股票代码') or row.get('code')),
                    'name': str(row.get('名称') or row.get('股票名称') or row.get('name')),
                    'price': str(row.get('最新价') or row.get('现价') or row.get('price')),
                })
            return res
        except Exception:
            return []

    def get_stock_realtime(self, stock_code: str) -> Dict[str, Any]:
        """获取单只股票的实时数据（尽量使用akshare的现有接口）"""
        try:
            df = ak.stock_zh_a_spot_em()
            row = df[df['代码'] == stock_code]
            if row.empty:
                # 有些code需带市场前缀，如 600000 -> 600000
                return {}
            r = row.iloc[0].to_dict()
            return r
        except Exception:
            return {}
