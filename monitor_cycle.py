#!/usr/bin/env python3
"""实时监控脚本 - 模拟前端的一个刷新周期"""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.realtime_manager import RealTimeManager

print("🔴 开始一个完整的监控周期...")
print("=" * 80)

rt = RealTimeManager()
start_time = time.time()

# 步骤1: 抓取新闻
print(f"[{time.strftime('%H:%M:%S')}] 🔍 步骤1: 抓取新闻...")
news_list = rt.fetch_latest_news(page=1, page_size=5)

if not news_list:
    print("❌ 没有获取到新闻")
    sys.exit(1)

print(f"[{time.strftime('%H:%M:%S')}] ✅ 获取到 {len(news_list)} 条新闻")

# 处理第一条新闻
news = news_list[0]
print(f"[{time.strftime('%H:%M:%S')}] 📰 处理新闻 ID: {news.get('id')}")
print(f"[{time.strftime('%H:%M:%S')}] 📰 标题: {news.get('title')[:60]}...")

# 步骤2: 一级分析
print(f"\n[{time.strftime('%H:%M:%S')}] 🤖 步骤2: DeepSeek一级分析...")
title = news.get('title', '')
content = news.get('content', news.get('title', ''))
prompt1 = rt.level1_prompt(title, content)

res1 = rt.call_deepseek(prompt1, max_tokens=500)

if 'error' in res1:
    print(f"[{time.strftime('%H:%M:%S')}] ❌ 一级分析失败: {res1['error']}")
    sys.exit(1)

elapsed = time.time() - start_time
print(f"[{time.strftime('%H:%M:%S')}] ✅ 一级分析完成 (耗时 {elapsed:.1f}秒)")

if 'parsed' in res1:
    impact = res1['parsed'].get('impact', '否')
    sectors = res1['parsed'].get('affected_sectors', [])
    reason = res1['parsed'].get('reason', '')
    
    print(f"[{time.strftime('%H:%M:%S')}] 📊 影响判断: {impact}")
    print(f"[{time.strftime('%H:%M:%S')}] 📊 影响板块: {', '.join(sectors)}")
    print(f"[{time.strftime('%H:%M:%S')}] 📊 影响原因: {reason[:100]}...")
    
    if impact == '是':
        # 步骤3: 获取候选股票
        print(f"\n[{time.strftime('%H:%M:%S')}] 📈 步骤3: 筛选候选股票...")
        candidates = rt.pick_candidate_stocks(5)
        print(f"[{time.strftime('%H:%M:%S')}] ✅ 筛选了 {len(candidates)} 只候选股票")
        
        for i, stock in enumerate(candidates[:3], 1):
            print(f"    {i}. {stock.get('name')} ({stock.get('code')}) - {stock.get('price')}")
        
        # 步骤4: 二级分析
        print(f"\n[{time.strftime('%H:%M:%S')}] 🚀 步骤4: DeepSeek二级分析...")
        real_time_data = {'candidates': candidates}
        prompt2 = rt.level2_prompt(title, sectors, reason, real_time_data)
        
        res2 = rt.call_deepseek(prompt2, max_tokens=1500)
        
        if 'error' in res2:
            print(f"[{time.strftime('%H:%M:%S')}] ❌ 二级分析失败: {res2['error']}")
        else:
            elapsed = time.time() - start_time
            print(f"[{time.strftime('%H:%M:%S')}] ✅ 二级分析完成 (总耗时 {elapsed:.1f}秒)")
            
            if 'parsed' in res2:
                stocks = res2['parsed'].get('recommended_stocks', [])
                print(f"[{time.strftime('%H:%M:%S')}] 💡 推荐 {len(stocks)} 只股票")
                
                for i, stock in enumerate(stocks[:2], 1):
                    print(f"\n    推荐 {i}: {stock.get('stock_name')} ({stock.get('stock_code')})")
                    print(f"       当前价: {stock.get('current_price')}")
                    print(f"       理由: {stock.get('selection_reason', '')[:80]}...")
                    timing = stock.get('operation_timing', {})
                    if timing:
                        print(f"       买入: {timing.get('buy_price_range')} @ {timing.get('buy_time')}")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] ⚠️ 二级分析返回非JSON格式")
    else:
        print(f"[{time.strftime('%H:%M:%S')}] ⏭️ 无显著影响，跳过二级分析")
else:
    print(f"[{time.strftime('%H:%M:%S')}] ⚠️ 一级分析返回非JSON格式")
    if 'raw_text' in res1:
        print(f"原始返回: {res1['raw_text'][:200]}...")

total_time = time.time() - start_time
print(f"\n" + "=" * 80)
print(f"✅ 监控周期完成！总耗时: {total_time:.1f}秒")
print(f"📱 现在打开浏览器访问: http://localhost:8501")
print(f"🔑 使用 admin/admin123 登录，应该能看到类似的数据流")
print("=" * 80)
