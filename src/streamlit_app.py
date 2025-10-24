import streamlit as st
import pandas as pd
import os
import sys
import time
from streamlit_autorefresh import st_autorefresh

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.realtime_manager import RealTimeManager

# 配置页面
st.set_page_config(page_title="A股观察室", page_icon="📈", layout="wide")

# 只在已登录状态下启用自动刷新（每10秒）
if 'authenticated' in st.session_state and st.session_state.authenticated:
    st_autorefresh(interval=10000, key="data_refresh")

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'rt_manager' not in st.session_state:
    st.session_state.rt_manager = RealTimeManager()
if 'last_seen_id' not in st.session_state:
    st.session_state.last_seen_id = None
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []  # 存储所有一级分析结果
if 'use_reasoning_model' not in st.session_state:
    st.session_state.use_reasoning_model = False  # 默认使用快速的V3模型（现在仅用于用户强制全流程使用R1）
if 'is_analyzing' not in st.session_state:
    st.session_state.is_analyzing = False  # 标记是否正在分析中
if 'analysis_start_time' not in st.session_state:
    st.session_state.analysis_start_time = None  # 分析开始时间
if 'is_level2_analyzing' not in st.session_state:
    st.session_state.is_level2_analyzing = False  # 标记是否正在进行二级分析（R1）
if 'level2_queue' not in st.session_state:
    st.session_state.level2_queue = []  # 待处理的二级分析队列

def render_login():
    st.title("A股观察室 — 实时推荐")
    with st.form("login_form"):
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        submit = st.form_submit_button("登录")
        if submit:
            if username == "admin" and password == "admin123":
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("登录成功！")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("用户名或密码错误")

def process_level2_analysis():
    """处理二级分析队列（使用R1模型）"""
    if not st.session_state.level2_queue:
        return
    
    # 取出队列第一个任务
    task = st.session_state.level2_queue.pop(0)
    rt = st.session_state.rt_manager
    current_time = time.strftime('%H:%M:%S')
    
    title = task['title']
    sectors = task['sectors']
    reason = task['reason']
    candidates = task['candidates']
    created_time = task['created_time']
    
    st.session_state.logs.insert(0, f"[{current_time}] 🚀 开始R1二级分析 (创建于 {created_time})")
    
    try:
        # 标记开始二级分析
        st.session_state.is_level2_analyzing = True
        st.session_state.analysis_start_time = time.time()
        
        real_time_data = {'candidates': candidates}
        prompt2 = rt.level2_prompt(title, sectors, reason, real_time_data)
        
        # 强制使用R1模型进行二级分析
        res2 = rt.call_deepseek(prompt2, max_tokens=1500, use_reasoning=True)
        
    finally:
        # 确保状态总是被重置
        st.session_state.is_level2_analyzing = False
        st.session_state.analysis_start_time = None
    
    # 检查API错误
    if 'error' in res2:
        error_msg = f"[{current_time}] ❌ R1二级分析失败: {res2['error']}"
        st.session_state.logs.insert(0, error_msg)
        st.error(f"🚨 **R1二级分析失败**\n\n错误信息: {res2['error']}\n\n可能原因:\n- API超时（R1推理时间较长）\n- API配额用完\n\n建议: 等待10秒后自动重试")
        return
    
    st.session_state.logs.insert(0, f"[{current_time}] ✅ R1二级分析完成")
    
    # 保存推荐结果
    st.session_state.recommendations.insert(0, {
        'title': title,
        'time': current_time,
        'strategy': res2,
        'sectors': sectors,
        'candidates': candidates,
        'model': 'DeepSeek-R1'
    })
    
    # 成功提示
    st.success(f"✅ **R1深度分析完成！** 已生成高质量操作建议")

def process_news():
    """处理最新一条新闻并调用 DeepSeek 分析"""
    rt = st.session_state.rt_manager
    current_time = time.strftime('%H:%M:%S')
    
    # 检查是否有待处理的二级分析任务（R1模型）
    if st.session_state.level2_queue and not st.session_state.is_level2_analyzing:
        process_level2_analysis()
    
    # 如果正在进行二级分析（R1），更新状态但继续一级分析
    if st.session_state.is_level2_analyzing:
        elapsed = int(time.time() - st.session_state.analysis_start_time)
        # 更新日志中的等待时间
        if st.session_state.logs and "R1二级分析中" in st.session_state.logs[0]:
            st.session_state.logs[0] = f"[{current_time}] ⏳ R1二级分析中... 已等待 {elapsed} 秒 (一级分析继续进行)"
        else:
            st.session_state.logs.insert(0, f"[{current_time}] ⏳ R1二级分析中... 已等待 {elapsed} 秒 (一级分析继续进行)")
        # 继续执行一级分析，不return
    
    st.session_state.logs.insert(0, f"[{current_time}] 🔍 开始抓取新闻...")
    
    try:
        # ========== 步骤1: 抓取新闻 ==========
        news_items = rt.fetch_latest_news(page=1, page_size=10)
        
        if not news_items or not isinstance(news_items, list):
            error_msg = f"[{current_time}] ❌ 新闻抓取失败"
            st.session_state.logs.insert(0, error_msg)
            st.error(f"🚨 **新闻抓取失败**\n\n返回数据类型: {type(news_items)}\n\n请检查新浪财经API是否可用")
            return  # 停止处理
        
        st.session_state.logs.insert(0, f"[{current_time}] ✅ 成功获取 {len(news_items)} 条新闻")
        
        # ========== 处理第一条新闻 ==========
        for item in news_items[:1]:
            if not isinstance(item, dict):
                st.session_state.logs.insert(0, f"[{current_time}] ⚠️ 新闻格式错误，跳过")
                continue
            
            nid = str(item.get('id', ''))
            title = item.get('title', '')
            content = item.get('content', title)  # 如果没有content，使用title
            
            st.session_state.logs.insert(0, f"[{current_time}] 📰 新闻ID: {nid}")
            st.session_state.logs.insert(0, f"[{current_time}] 📰 标题: {title[:50]}...")
            
            # 检查是否是新新闻
            if nid and nid == st.session_state.last_seen_id:
                st.session_state.logs.insert(0, f"[{current_time}] ⏭️ 已处理过此新闻，跳过")
                continue
            
            # 更新最后处理的新闻ID
            st.session_state.last_seen_id = nid
            
            # ========== 步骤2: 一级分析（强制使用V3快速模型）==========
            try:
                st.session_state.logs.insert(0, f"[{current_time}] 🤖 调用DeepSeek一级分析(V3快速模型)...")
                
                prompt1 = rt.level1_prompt(title, content)
                
                # 一级分析强制使用V3快速模型
                res1 = rt.call_deepseek(prompt1, max_tokens=500, use_reasoning=False)
                
            finally:
                # 一级分析不设置阻塞状态，可以并发
                pass
            
            # 检查API错误
            if 'error' in res1:
                error_msg = f"[{current_time}] ❌ 一级分析API调用失败: {res1['error']}"
                st.session_state.logs.insert(0, error_msg)
                st.error(f"🚨 **DeepSeek API 一级分析失败**\n\n错误信息: {res1['error']}\n\n可能原因:\n- API超时（网络问题）\n- API配额用完\n- 服务暂时不可用\n\n建议: 等待10秒后自动重试")
                return  # 停止处理，等待下次刷新
            
            st.session_state.logs.insert(0, f"[{current_time}] ✅ 一级分析API调用成功")
            
            # 检查返回格式
            if 'parsed' not in res1:
                error_msg = f"[{current_time}] ⚠️ 一级分析返回非JSON格式"
                st.session_state.logs.insert(0, error_msg)
                
                # 保存非JSON格式的分析结果
                raw_text = res1.get('raw_text', str(res1))
                st.session_state.analysis_results.insert(0, {
                    'time': current_time,
                    'news_id': nid,
                    'news_title': title,
                    'impact': '未知',
                    'sectors': [],
                    'reason': f"[非JSON格式] {raw_text}",
                    'is_json': False,
                    'raw_response': raw_text
                })
                
                # 持久显示警告，不使用st.warning（会自动消失）
                # 改为在分析结果面板中显示
                return  # 停止处理
            
            # ========== 解析一级分析结果 ==========
            impact = res1['parsed'].get('impact', '否')
            sectors = res1['parsed'].get('affected_sectors', [])
            reason = res1['parsed'].get('reason', '')
            
            st.session_state.logs.insert(0, f"[{current_time}] 📊 影响判断: {impact}")
            st.session_state.logs.insert(0, f"[{current_time}] 📊 影响板块: {', '.join(sectors)}")
            st.session_state.logs.insert(0, f"[{current_time}] 📊 分析原因: {reason[:50]}...")
            
            # 保存一级分析结果
            st.session_state.analysis_results.insert(0, {
                'time': current_time,
                'news_id': nid,
                'news_title': title,
                'impact': impact,
                'sectors': sectors,
                'reason': reason,
                'is_json': True,
                'raw_response': None
            })
            
            # 不再使用临时弹窗，所有结果都在第二列持久显示
            
            if impact == '是':
                # ========== 步骤3: 筛选候选股票 ==========
                st.session_state.logs.insert(0, f"[{current_time}] � 开始筛选候选股票...")
                
                try:
                    candidates = rt.pick_candidate_stocks(5)
                    if not candidates or len(candidates) == 0:
                        error_msg = f"[{current_time}] ❌ 股票筛选失败，未获取到数据"
                        st.session_state.logs.insert(0, error_msg)
                        
                        # 保存失败信息到推荐列表（持久显示）
                        st.session_state.recommendations.insert(0, {
                            'title': title,
                            'time': current_time,
                            'strategy': {'error': 'AkShare股票数据获取失败，接口暂时不可用'},
                            'sectors': sectors,
                            'candidates': [],
                            'error_type': 'akshare_failed'
                        })
                        return  # 停止处理
                    
                    st.session_state.logs.insert(0, f"[{current_time}] ✅ 筛选了 {len(candidates)} 只候选股票")
                    for i, c in enumerate(candidates[:3], 1):
                        st.session_state.logs.insert(0, f"[{current_time}]    {i}. {c.get('name')} ({c.get('code')}) - {c.get('price')}")
                    
                except Exception as e:
                    error_msg = f"[{current_time}] ❌ 股票筛选异常: {str(e)}"
                    st.session_state.logs.insert(0, error_msg)
                    
                    # 保存异常信息到推荐列表（持久显示）
                    st.session_state.recommendations.insert(0, {
                        'title': title,
                        'time': current_time,
                        'strategy': {'error': f'AkShare异常: {str(e)}'},
                        'sectors': sectors,
                        'candidates': [],
                        'error_type': 'akshare_exception',
                        'error_detail': str(e)
                    })
                    return  # 停止处理
                
                # ========== 步骤4: 加入二级分析队列（使用R1模型）==========
                # 将任务加入队列，异步处理
                task = {
                    'title': title,
                    'sectors': sectors,
                    'reason': reason,
                    'candidates': candidates,
                    'created_time': current_time,
                    'nid': nid
                }
                st.session_state.level2_queue.append(task)
                st.session_state.logs.insert(0, f"[{current_time}] 📥 已加入R1二级分析队列 (队列长度: {len(st.session_state.level2_queue)})")
                st.info(f"✅ **一级分析完成！** 发现显著影响，已加入R1深度分析队列")
                
            else:
                st.session_state.logs.insert(0, f"[{current_time}] ⏭️ 无显著影响，继续监控")
                st.info(f"ℹ️ 该新闻对A股无显著影响，继续监控下一条")
            
            break  # 只处理第一条新闻
            
    except Exception as e:
        error_msg = f"[{current_time}] ❌ 系统异常: {str(e)}"
        st.session_state.logs.insert(0, error_msg)
        
        import traceback
        full_trace = traceback.format_exc()
        st.session_state.logs.insert(0, f"[{current_time}] 堆栈: {full_trace[:200]}")
        
        st.error(f"🚨 **系统异常**\n\n错误信息: {str(e)}\n\n详细堆栈:\n```\n{full_trace}\n```")

def render_main():
    st.title("A股观察室 — 实时监控中 🔴")
    
    # 显示刷新计数器
    refresh_count = st.session_state.get('refresh_count', 0)
    st.session_state.refresh_count = refresh_count + 1
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        # 显示混合模式状态
        queue_len = len(st.session_state.level2_queue)
        mode_info = f"一级: V3快速 | 二级: R1深度 | R1队列: {queue_len}"
        st.markdown(f"**用户：{st.session_state.username}** | 自动刷新：每10秒 | 刷新次数: {st.session_state.refresh_count}")
        st.caption(f"🔧 {mode_info}")
    with col2:
        if st.button("🔄 立即刷新"):
            st.rerun()
    with col3:
        if st.button("退出"):
            st.session_state.authenticated = False
            st.rerun()
    
    st.markdown("---")
    
    # 显示R1二级分析状态
    if st.session_state.is_level2_analyzing:
        elapsed = int(time.time() - st.session_state.analysis_start_time)
        progress_text = f"⏳ **R1二级分析中...** 已等待 **{elapsed}** 秒"
        if elapsed > 60:
            progress_text += f" ({elapsed // 60} 分 {elapsed % 60} 秒)"
        st.warning(progress_text)
        st.info("💡 R1模型正在进行深度推理，一级分析（V3）将继续监控新闻。")
    elif st.session_state.level2_queue:
        st.info(f"📥 **R1分析队列**: {len(st.session_state.level2_queue)} 个任务等待处理")
    
    # 每次页面加载时自动处理新闻
    with st.spinner('处理新闻中...'):
        process_news()
    
    # 四列布局：新闻流 | 一级分析结果 | 运行日志 | 操作推荐
    c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
    
    with c1:
        st.subheader("📰 新闻流")
        news = st.session_state.rt_manager.fetch_latest_news(1, 5)
        if news and isinstance(news, list):
            for i, n in enumerate(news):
                if isinstance(n, dict):
                    with st.expander(f"📌 {n.get('create_time', '')}", expanded=(i==0)):
                        st.markdown(f"**{n.get('title', '无标题')}**")
                        st.caption(n.get('content', n.get('title', ''))[:200] + "...")
        else:
            st.info("暂无新闻数据")
    
    with c2:
        st.subheader("🔍 一级分析结果")
        if st.session_state.analysis_results:
            for i, result in enumerate(st.session_state.analysis_results[:10]):  # 显示最近10条
                impact = result.get('impact', '未知')
                sectors = result.get('sectors', [])
                reason = result.get('reason', '')
                news_title = result.get('news_title', '')
                time_str = result.get('time', '')
                is_json = result.get('is_json', True)
                raw_response = result.get('raw_response', None)
                
                # 处理非JSON格式的响应
                if not is_json:
                    with st.expander(f"⚠️ {time_str} - 格式错误", expanded=(i==0)):
                        st.markdown(f"**新闻**: {news_title[:60]}...")
                        st.warning("⚠️ API返回了非JSON格式的内容")
                        st.markdown(f"**原始响应**:")
                        with st.container():
                            st.text_area(
                                "原始返回",
                                value=raw_response[:1000] if raw_response else "无内容",
                                height=150,
                                key=f"raw_{time_str}_{i}",
                                disabled=True
                            )
                    continue
                
                # 正常的JSON格式响应
                if impact == '是':
                    with st.expander(f"🔴 {time_str} - 有影响", expanded=(i==0)):
                        st.markdown(f"**新闻**: {news_title[:60]}...")
                        st.markdown(f"**影响判断**: :red[{impact}]")
                        st.markdown(f"**影响板块**: {', '.join(sectors)}")
                        st.markdown(f"**分析原因**:")
                        st.info(reason)
                else:
                    with st.expander(f"⚪ {time_str} - 无影响", expanded=False):
                        st.markdown(f"**新闻**: {news_title[:60]}...")
                        st.markdown(f"**影响判断**: :gray[{impact}]")
                        if sectors:
                            st.markdown(f"**相关板块**: {', '.join(sectors)}")
                        st.markdown(f"**分析原因**:")
                        st.caption(reason)
        else:
            st.info("暂无分析结果")
    
    with c3:
        st.subheader("📋 运行日志")
        log_container = st.container()
        with log_container:
            if st.session_state.logs:
                for log in st.session_state.logs[:30]:
                    st.text(log)
            else:
                st.info("暂无日志")
    
    with c4:
        st.subheader("💡 操作推荐")
        if st.session_state.recommendations:
            for i, rec in enumerate(st.session_state.recommendations[:5]):  # 显示最近5条
                error_type = rec.get('error_type', None)
                
                # 处理AkShare错误
                if error_type in ['akshare_failed', 'akshare_exception']:
                    with st.expander(f"❌ 错误 #{i+1} - {rec.get('time')}", expanded=(i==0)):
                        st.markdown(f"**新闻**: {rec.get('title', '')[:100]}")
                        st.markdown(f"**板块**: {', '.join(rec.get('sectors', []))}")
                        st.error(f"🚨 **AkShare股票数据获取失败**")
                        
                        strategy = rec.get('strategy', {})
                        if 'error' in strategy:
                            st.markdown(f"**错误信息**: {strategy['error']}")
                        
                        if error_type == 'akshare_exception':
                            error_detail = rec.get('error_detail', '')
                            with st.expander("查看详细错误"):
                                st.code(error_detail)
                        
                        st.markdown("---")
                        st.info("**可能原因**:\n- AkShare接口暂时不可用\n- 网络连接问题\n- 接口限流\n\n**建议**: 等待下次刷新自动重试")
                    continue
                
                # 正常的推荐
                model_used = rec.get('model', 'DeepSeek-V3')  # 默认V3
                model_badge = "🔬 R1深度" if model_used == 'DeepSeek-R1' else "⚡ V3快速"
                with st.expander(f"🎯 推荐 #{i+1} - {rec.get('time')} [{model_badge}]", expanded=(i==0)):
                    st.markdown(f"**新闻**: {rec.get('title', '')[:100]}")
                    st.markdown(f"**板块**: {', '.join(rec.get('sectors', []))}")
                    st.caption(f"🤖 分析模型: {model_used}")
                    
                    strategy = rec.get('strategy', {})
                    
                    # 检查是否有DeepSeek API错误
                    if 'error' in strategy:
                        st.error(f"🚨 **DeepSeek API调用失败**")
                        st.markdown(f"**错误信息**: {strategy['error']}")
                        st.info("建议: 等待10秒后自动重试")
                    
                    # 成功解析为JSON
                    elif 'parsed' in strategy:
                        parsed = strategy['parsed']
                        
                        # 显示整体策略
                        if 'overall_strategy' in parsed:
                            st.info(f"📋 **整体策略**: {parsed['overall_strategy'][:150]}")
                        
                        # 显示推荐股票
                        stocks = parsed.get('recommended_stocks', [])
                        if stocks:
                            for j, stock in enumerate(stocks[:3], 1):
                                st.markdown(f"---")
                                st.markdown(f"**{j}. {stock.get('stock_name', '未知')} ({stock.get('stock_code', 'N/A')})**")
                                
                                # 基本信息
                                current_price = stock.get('current_price', '未知')
                                risk_level = stock.get('risk_level', '未知')
                                expected_return = stock.get('expected_return', '未知')
                                
                                col_a, col_b, col_c = st.columns(3)
                                with col_a:
                                    st.metric("当前价", current_price)
                                with col_b:
                                    st.metric("风险", risk_level)
                                with col_c:
                                    st.metric("预期收益", expected_return)
                                
                                # 选股理由
                                reason = stock.get('selection_reason', '')
                                if reason:
                                    st.caption(f"💡 {reason[:150]}...")
                                
                                # 操作时机
                                timing = stock.get('operation_timing', {})
                                if timing and isinstance(timing, dict):
                                    st.success(f"✅ **买入**: {timing.get('buy_price_range', '未知')} @ {timing.get('buy_time', '未知')}")
                                    st.caption(f"建议仓位: {timing.get('position_recommendation', '未知')}")
                                    st.error(f"🛑 **止损**: {timing.get('stop_loss_price', '未知')}")
                                    st.warning(f"🎯 **卖出**: {timing.get('sell_price_range', '未知')} @ {timing.get('sell_time', '未知')}")
                                else:
                                    st.warning("⚠️ 操作时机信息不完整")
                        else:
                            st.warning("⚠️ 未返回推荐股票列表")
                    
                    # 返回文本但无法解析
                    elif 'raw_text' in strategy:
                        st.warning("⚠️ AI返回了文本，但无法解析为结构化数据")
                        with st.expander("查看原始返回"):
                            st.text(strategy['raw_text'][:800])
                    
                    # 未知格式
                    else:
                        st.error("❌ 分析结果格式异常，无法显示")
                        st.json(strategy)
        else:
            st.info("💤 暂无推荐\n\n系统正在监控中，发现显著影响时会自动生成推荐")

def main():
    if not st.session_state.authenticated:
        render_login()
    else:
        render_main()

if __name__ == '__main__':
    main()
